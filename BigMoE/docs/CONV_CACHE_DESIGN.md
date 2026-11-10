# Conversation cache: keep a conversation's model state between requests (design)

Design only, Tue 10 Nov 2026 20:41 EET; the build starts after Wednesday's 24 GB release. Goal (Kamen, 10 Nov 20:3x, via
the orchestrator): the model usable from Claude Code and Codex. Leap builds the server (API, templates, tool calls); this is
the engine part: a new turn prefills only its new tokens. Tags: [K] measured, or read from code / config (source given);
[P] computed from shapes or projected; [G] guess.

## 1. Why

Claude Code resends its system prompt and tool schemas (~15-20K tokens) plus the whole conversation every turn. Today every
request starts from `model.make_cache()` and prefills from token 0 in 1,024-row chunks (`prefill()`,
data/r57/snap/w24/r57_screen_w24.py:1013, "r57" below). At 24 GB the first token took 6.02 s for a 726-token prompt and
14.57 s for 2,801 tokens [K data/w24/w24e_report.txt, pc1024]. At that rate a 20K-token prompt takes about 1.4 min [P].
On the 32 GB exact config, Leap's PF-B (with the SEGALL fix) prefills 30K tokens at 555 tok/s [K Leap, 10 Nov], so 18K
tokens take about 32 s [P]. With the cache
a turn prefills three things only: the tail since the last kept checkpoint (at most 1,023 tokens), the previous reply, and
the new tokens (the tool result or the user message).

## 2. What a conversation's state is

Config: models/bare/config.json. Cache classes: .venv/lib/python3.12/site-packages/mtplx/models/qwen4_exp.py.
- The model has 48 layers: 12 QSA attention layers (every 4th) and 36 Gated-DeltaNet (GDN) layers.
- QSA attention: 2 KV heads × 256, plus an indexer (4 heads × 128, compress ratio 4, budget 2,048).
- GDN: 16 K heads and 48 V heads at 128 × 128; conv kernel 4.
- `make_cache()` gives one `QSACache` per attention layer and one `ArraysCache` (conv, recurrent; 4 entries on PLE layers)
  per GDN layer.

| piece | where it lives | trim to a shorter prefix? | size |
|---|---|---|---|
| attention K/V, 12 layers | `QSACache.kv`, the stock KVCache (bf16, 256-row steps) | yes (offset) | 24,576 B / token [P] |
| QSA indexer: raw keys, pooled blocks, fp32 mirror | `QSACache.raw_keys / pooled / pooled_f32_t`, positional on `kv.offset` | yes (MTPLX made them trimmable) | ~5.4 KB / token [P]; capacity doubles |
| GDN recurrent state, 36 layers | `ArraysCache[1]`, fp32 [1, 48, 128, 128] | **no** | 113.2 MB per position [P] |
| GDN conv state | `ArraysCache[0]`, [1, 3, 10240] | **no** | 2.2 MB [P] (MTPLX: 115.6 MB per checkpoint with the PLE tails [K checkpoint_anchors.py]) |
| positions | implicit in `kv.offset` (text-only RoPE, partial rotary 0.25) | n/a | one int |
| DFlash2 drafter context | rebuilt per prompt from taps `T[P-2047:P]` (r57:1095-1101). Taps: layers 5/15/25/35/45, 4-way mean, fp16 | n/a | 13.1 MB per checkpoint (2,047 × 3,200 × 2 B) [K code; drafter sliding_window 2048] |
| DFlash2 rotating KV (5 sliding layers) | rebuilt from the taps at the first propose | not stored | (41.9 MB if it were) [P] |
| MTP head (the chat switch's drafter) | `make_mtp_cache()`: one QSACache fed (hidden_i, token_i+1) pairs | yes | ~2.5 KB / token [P], plus the widened hidden row at c-1 (the pending pair) |
| U3C prompt footprint (FAST cold arms) | `FG["cap"]`, 48 × 512 bool, accumulated over the prefill (r57:1071) | n/a | 24.6 KB [K] |

**Not stored:**
- Expert residency (pools, sidecars, QOM keep-sets, gate state). It is process state, and a restore leaves it alone.
- SESSION-VOCAB and the copy gate's k-grams. They are rebuilt from the prompt ids, as today.
- A6 pools / warm. They come from the last prefill chunk, which a warm run also runs.
- Last logits. A restore always leaves at least 1 token to prefill.

**Per conversation [P]:** ~30 KB per token, plus ~129 MB per kept checkpoint (115.6 + 13.1 MB).

| conversation | checkpoints | size |
|---|---|---|
| 20K tokens | 2 | 0.86 GB |
| 64K tokens | 3 | 2.35 GB |
| 128K tokens | 4 | 4.4 GB |

Cross-check: Strata parks the same model at ~19.5 KB per token, and writes 430 MB to disk for a 20K-token system prompt
[K Strata docs/how-it-works.md].

## 3. Where to snapshot: the 1,024 grid, exact by construction

**Rule.** Checkpoints are taken only at multiples of PFCHUNK (1,024), during prefill.
- A warm request restores the highest kept checkpoint c with c ≤ min(matched prefix, N - 1). It then prefills [c, N) in
  1,024-row chunks starting at c.
- Every call it makes is a call the cold prefill of the whole prompt also makes: the same chunk, the same tokens, the same
  KV and GDN state before it.
- So the logits and states are bitwise those of a cold run. No new "exact" label is needed, and the cold path stays the
  gated one, byte for byte.

**Never reuse state that decode wrote.** The reply's KV and GDN states came from verify calls of at most 16 rows, not from
prefill chunks. Templates also re-render the reply (Qwen-style templates drop earlier turns' reasoning). The reply is
re-prefilled as part of the next turn's suffix.

**Which edges to keep.** This is decided before the prefill starts, since N and the hints are known. Only those edges hold
a copy, so the prefill's extra peak is at most 3 × 129 MB. The rules follow MTPLX's anchors:
1. **Prompt end:** the last edge ≤ N - g, where g is the length of the generation prompt. This is where the next turn
   diverges.
2. **Stable prefix:** the last edge ≤ the end of system + tools. Leap's server sends it; the fallback is the longest common
   prefix of the last two requests. Sub-agents and new sessions start here.
3. **Restore point:** the edge this request restored from (a rewind lands there).
4. **Coarse grid:** one edge per 8,192 tokens, thinned by halving when the budget is short (MTPLX GRID_TOKENS).
5. **Live KV:** the live cache's KV is kept whole (it is trimmable).

**Later option, not in the first build.** A checkpoint at the exact prompt end P_n saves up to 1,023 re-prefilled tokens
per turn. But its result equals a cold run split at P_n, not today's prefill (W24e: other chunk edges change tokens), so it
would need its own label. At 24 GB a short suffix costs about one chunk pass whether it is 300 or 1,000 tokens, so the
saving is small there.

## 4. Matching a request to a stored prefix

**Entry key.** Each entry is keyed by:
- the model, and the config's env-file git blob (e.g. card_w24d_env.txt e06f495e);
- the engine snapshot commit and the chat-template hash;
- PFCHUNK and the prefill mode (plain / PF-A / PF-B with SEGALL; PF-D);
- the drafter (DFlash2 / MTP).

Any mismatch is a miss (MTPLX's MODEL / TEMPLATE / POLICY_MISMATCH reasons).

**Lookup.**
- Use a block-hash chain on the grid: h_k = sha256(h_(k-1) ‖ ids[1024(k-1) : 1024k]). Each checkpoint stores its h_k, and
  the new prompt's chain is computed on the host in µs.
- The deepest k with a stored h_k wins. Order: the live entry first, then RAM, then SSD.
- Then ids [0, c) are compared exactly; a hash alone is never trusted.

**Token ids only, never text.** The server's hints are only hints:
- stable_prefix_end;
- a session key, used for eviction priority only (Codex's prompt_cache_key if it sends one; Claude Code sends none, so the
  server may derive one);
- a side-request flag, so title or summary calls never evict the main session.

**Engine call for Leap's server:**

    cache, last_logits, info = conv.prefill(ids, hints={"stable_end": int, "session": str | None, "side": bool})
    # info: matched, c, source (live / ram / ssd / none), prefilled tokens, miss_reason, restore_ms, prefill_ms

**Miss log.** Every miss logs its reason and the first divergent token, with ±20 decoded tokens of context (as MTPLX's
`_debug_prefix_divergence` does), so render drift shows up on Leap's side. Strata lost the whole prefix on every step to
clients that merge a turn's tool calls into one assistant message, and fixed it in the server (patch 13) [K].

## 5. Memory: RAM tier, SSD tier, and the three lines

**Budget** = the line minus the config's measured lifetime peak (phys_footprint) at the session's length. The live
conversation's KV is already inside that peak. The cache adds checkpoints (129 MB each) and parked conversations.

**24 GB: no room.**
- w13b peaks at 23.910 GB with 481-token prompts, 24.014 GB at 520 and 25.112 GB at 2,801 [K docs/WED_TESTS.md,
  long-prompt peak].
- A 20K-token Claude Code prompt adds ~0.6 GB of KV on top [P].
- So the cache cannot make 24 GB hold agent-length prompts. That needs a long-context 24 GB config with fewer resident slots
  (one base-slot row ≈ 0.1 GB [G, from the expert shape], so ~9 rows for 0.86 GB), priced by a W24-style A/B.
- Cache policy at 24 GB: the live session and 1 prompt-end checkpoint in RAM; anything parked goes to SSD.

**32 GB** (Leap's exact config, where PF-B's 555 tok/s was measured; its peak at agent lengths is measured in B4): reserve
~2.5 GB, enough for a 64K main session plus a 20K sub-agent or side conversation. The rest goes to SSD.

**45 GB:** reserve ~6 GB, about 170K tokens of conversations including checkpoints. (Strata: 3 GB in 8 slots holds ~160K
tokens at 19.5 KB per token.)

**SSD tier, every line** (after Strata's patches 17, 19 and 20):
- Park a conversation after the engine has been idle ~2 s: write its KV rows and checkpoints in 16 MiB blocks with
  F_NOCACHE (macOS's O_DIRECT). Stop if a request arrives.
- If the file is at most 8,192 tokens behind, append only the new rows.
- Restore in two passes: validate the checksums, then copy block by block into the cache arrays, with no whole-file buffer.
  0.86 GB reads in ~0.1 s [P].
- Cap the directory at 16 GB and delete it at exit. Keep entries across R57_HARD restarts (keyed by config blob + commit).
- No spill writes below 110 GB free disk (the health floor).

## 6. Interactions with QOM, residency, PF-A, PF-B, PF-D and the drafters

**QOM and residency.**
- Prefill runs `set_arm("slot")`, the stock path with all 10 experts (r57:1061). PF-D's rebuilt rows are bitwise the SSD
  rows (R57_PFD_CHECK). So prefill bits do not depend on residency, and the hash check holds on every line.
- Decode on FAST (R57_FAST=QOM, the 24 GB card config) does depend on pool residency and timing (EvalSuite: "drafts carry
  history"). A warm turn reads fewer experts during prefill, so its pools differ and its tokens can differ from a cold
  turn's, just as they already differ between any two prompt histories.
- The cache does not snapshot residency. The card label stays a scores label: run the gate's agent-like subset with the
  cache on before claiming the card for it.
- Speed: a warm prefill is 1-3 chunks. The decode-start miss burst (A6, from the last chunk's routing) is the same work as
  cold, and PF-D gets more hits because the conversation's experts are resident.

**Prefill modes.**
- **PF-A** (R57_PFLM=1, layer-major over the same chunks): each chunk's work per layer is unchanged, so a restore plus a
  layer-major suffix should equal a cold layer-major run [P; T1 checks it].
- **PF-B** (R57_PFLM=3): the grouped router and the shared expert span chunks, and a short last chunk changes bits (Leap,
  10 Nov). So PF-B works with the cache only with SEGALL (R57_PFLM_SEGALL=1, per-chunk slices; its port is due after the
  release). Without SEGALL the cache refuses PF-B.
- **PF-D** (R57_PFD): exact by construction. It falls back as today: on LMC, grouped prefill, no sidecar, or layout ≠ 2.
- **PFNOLOG** (no vocab head on cache-only chunks): unchanged, since the warm path's last chunk is the cold path's last
  chunk.

**Drafters.**
- **DFlash2:** its context at decode start is the taps of the last 2,047 positions. The warm path takes [c, N) from its own
  prefill and [N - 2047, c) from the checkpoint's taps. The bits are the same, because both came from the same chunks.
- **MTP head:** trim its cache to c, re-add the pending (hidden_(c-1), token_c) pair from the stored row, then feed it the
  suffix's widened rows as today.

## 7. Exactness check (the gate before Leap's server uses the cache)

**T1, lossless restore** (unit test, ~30 min, one process).
- Prompts of 3K, 20K and 60K tokens. For each kept edge c, compare a cold prefill of [0, N) with a restore at c plus a
  prefill of [c, N).
- Compare the per-chunk logits hashes (R57_LOGHASH), the last row's logits bytes, and the sha256 of every cache-state array
  after the prefill. Pass = all equal.
- Run on the 24 GB card config and the 45 GB exact config; with plain prefill, PF-A, PF-B with SEGALL and PF-D; restoring
  from RAM and from SSD.

**T2, turn replay** (~1-2 h per line, a night job over 5 GB).
- Recorded Claude Code and Codex sessions, at least 2 of each, 10-30 turns with tool calls, rendered by Leap's server.
- Each turn runs warm vs cold (cache bypassed, same process order).
- Pass: prefill hashes equal on every turn. On the 45 GB exact config, decode tokens are also equal (CAP 128).
- On FAST, report token agreement and time to first token (info only).
- Also measure: lifetime peak under the line, and SSD bytes written per turn.

**T3, stress.** Interleaved main, sub-agent and side requests; a rewind; a system-prompt edit; eviction to SSD and back; an
R57_HARD restart in the middle.

A hash mismatch is a bug until shown otherwise.

## 8. Build plan and size

| step | what | size |
|---|---|---|
| B0 | Measure the real state bytes (KV, indexer, GDN, taps, MTP) at 2K / 20K / 60K tokens on both configs | ½ day, short GPU runs |
| B1 | Capture at the chosen edges in `prefill()` (chunk-major, PF-A, PF-B with SEGALL); restore and suffix prefill; T1 | ~250 lines, 1 day |
| B2 | Store: entries, hash chain with exact compare, anchors, byte budget, LRU with FLOP-aware keeping (Marconi), miss reasons; the engine call for Leap; T2 | ~350 lines, 1 day + a night |
| B3 | SSD tier: idle spill, streamed restore, checksums, cap, survival across restarts; T3 | ~200 lines, ½-1 day + a night |
| B4 | Per-line budgets; time to first token and peak at 24 / 32 / 45 GB | measurements, nights |

**Total:** ~800 lines, 3-4 days of build, 2 nights of GPU tests. The build reuses:
- `mtplx.cache_state` snapshot and restore (the engine already uses it for verify rollback, r57:1187);
- the anchor rules of `mtplx.checkpoint_anchors`.

It does not take MTPLX's SessionBank wholesale: that is 5,192 lines wired to MTPLX's own runtime.

## 9. Prior art

**MTPLX**, the library this engine runs on (.venv/.../mtplx) [K code]:
- SessionBank: exact token-prefix entries; restores cloned state and forwards only the suffix. Its doc: "the benchmark gate
  compares the warm result against a cold full prefill".
- checkpoint_anchors.py: boundary records at chunk edges, 115.6 MB each on Flash-Next, and the anchors above.
- engine_session.py: the longest-prefix session lookup and eviction. It also spills idle sessions to SSD.
- Defaults: 24 entries, 24 GiB, 8 GiB per session, 1 h idle TTL, 256-token prefix blocks, 512-token minimum match.

**Strata** (github.com/ExTV/strata-5090-4070, docs/how-it-works.md, read 10 Nov) [K their doc]:
- Conversation parking in RAM: ~19.5 KB per token, 3 GB in 8 slots, 0.6-1.2 s switches between a 30K and a 15K chat.
- A checkpoint at each turn boundary.
- A system-prompt prefix cache on disk (#960): a 20K-token system prompt takes 0.63 s instead of 11.65 s. Restore is 250 ms
  from disk and 145 ms from RAM; the state is 430 MB per 20K tokens.
- SSD spill (patch 17), streamed restore (#1269) and idle-time writes (patch 20).
- The server fix for merged tool calls (patch 13).

**Hybrid-model caches** [K search summaries, not read in full]:
- SGLang's MambaRadixCache / Unified Radix Cache: a recurrent state can be reused only at an exact checkpoint (LMSYS blog,
  11 Aug 2026).
- vLLM RFC #55697 (Sep 2026): application-directed prefix checkpoints for hybrid GDN / Mamba models. Markers declare
  boundaries and the scheduler splits prefill chunks there; up to 7.6× on L40S.
- Marconi (arXiv 2411.19379): admission plus FLOP-aware eviction for hybrid prefix caches, 4.5-34.4× better hit rates.
- LMCache does not support GDN hybrids yet.

**Attention-only prefix caching** (vLLM APC block hashes, SGLang RadixAttention, llama.cpp slot save / restore): the source
of the hash-chain matching above.

## 10. Where we lose, and risks

1. 24 GB does not hold agent-length prompts, with or without the cache.
2. Each turn re-prefills up to 1,023 tokens plus the reply.
3. FAST decode tokens depend on history.
4. A client that rewrites its system prompt every turn falls back to a cold prefill.
