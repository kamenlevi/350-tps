> (a quote from the project owner, kept private)

Target (orchestrator): Thu 12 Nov 17:00, Claude Code working well on this Mac. One command starts the server and Claude
Code; tool calls reliable on EvalSuite's agent test; turns start in seconds with BigMoE's conversation cache; sessions to
64-128K tokens with compaction. Leap's parts: harden /v1/messages, compaction, wire the cache, real sessions + the
default memory setting, setup. The 1.1.0 candidate stays frozen; this is the next release (Leap release/next).

## Tue 23:0x-23:3x: /v1/messages hardened (release/next 2b03787, 243874c)

- **Several tool calls in one turn, several results back:** real Claude Code on the stand-in engine (a turn with two Read
  calls): it ran both and sent two tool_results; the next prompt held both. PASS.
- **Images / documents:** a block becomes "[an image was attached here; this model reads text only and cannot see it]"
  in user turns and in tool results (Claude Code's Read of a PNG): no error, the model is told. PASS.
- **tool_choice** auto / any / tool / none accepted (none = no tools). **stop_sequences** honoured, streamed and not
  (stop_reason stop_sequence + the sequence); OpenAI `stop` too. **max_tokens** caps the answer.
- **count_tokens** = the rendered prompt's length (275 = 275 in the check).
- **"prompt is too long: N tokens > M maximum"** (400 invalid_request_error) past --max-context: Claude Code 2.1.321 matches
  exactly `^prompt is too long: \d+ tokens > \d+ maximum$` (its own string table).
- **One engine queue, main > sub > side:** a main request queued after a side one runs first. PASS.
- **Keep-alive pings** every 10 s while a request waits or prefills (Anthropic `ping` events, SSE comments for OpenAI /
  Responses); a client that leaves mid-answer stops the answer at the next check; one that leaves while queued is dropped
  before it runs. PASS.
- Quota probes = max_tokens <= 4 (was 16: an 8-token main request was wrongly side).
- HTTP checks on the stand-in engine: **9 / 9** (harden_test.py).

## Claude Code 2.1.321's window settings (from its string table)

For a model it does not know, Claude Code assumes a window and says "set CLAUDE_CODE_MAX_CONTEXT_TOKENS to its real
window"; "To enforce it, set CLAUDE_CODE_AUTO_COMPACT_WINDOW=". claude_local.sh now sets both to EXACTSTREAM_CONTEXT
(default 131,072). A run's own usage line confirms contextWindow 131072 and maxOutputTokens 32000. Other knobs seen:
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE, CLAUDE_CODE_MAX_OUTPUT_TOKENS, CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT.

## EvalSuite's agent test (PREREG_agentcc_2026-11-11, 63218d0): Leap's runner

agentcc_night.sh <GB>: gates (Kamen idle, no lock / engine, NO-SWAP), a share lock, the pinned server (the clone's files
must match release/next/SHA256SUMS), probe_cc.py, then agentcc_tasks.py: per task a fresh folder (git init + commit), a
fresh Claude Code config folder, claude -p (stream-json, 25 turns, the manifest's timeout, process group killed on
timeout) in a sandbox (writes only in the run folder and temp; network only to localhost; ~/.ssh, ~/.claude*, ~/.codex,
Keychains, Mail, Chrome, Documents, Desktop, Downloads, ~/Papers and the chat sessions unreadable), then the check,
sandboxed. Smoke test on the stand-in engine (t01, t11): git, transcript, check, results.jsonl all as specified.
Armed: 32 GB from Wed 00:30 (Kamen's go for tonight: apps closed 00:29-07:30), then the 64K / 128K long-context runs.

## Tue 23:2x-23:4x: one command, and compaction end to end (release/next, this commit)

- **tools/claude_code.sh** starts serve.py (unless one already answers on the port), waits until it is loaded, runs
  Claude Code with claude_local.sh's settings, and stops the server it started when Claude Code exits; the server gets
  its own process group, so Ctrl-C in Claude Code does not reach it. Stand-in test: Claude Code answered, the server
  stopped afterwards, the port was free.
- **Compaction, real Claude Code on the stand-in engine:**
  - Auto-compact with a 24K window and two large reads: three compact_boundary events; Claude Code cleared old tool
    results locally (36.7K -> 12.7K tokens) and measured big results with our count_tokens. No error.
  - **/compact** (`claude -p --continue "/compact"`): the summary request uses **the session's own system turn and tools**
    (sys_end 10,017, 14 tools) plus a final instruction ("CRITICAL: Respond with TEXT ONLY. Do NOT call any tools. ...
    an <analysis> block followed by a <summary> block"); a reply with tool calls makes Claude Code retry once with a
    stronger paragraph; a proper summary is accepted and the session continues from it (13,865 -> 13,008 tokens).
  - So with the conversation cache a compaction re-prefills only its instruction. serve.py flags these requests
    (meta compact: true) for the cache.
- The billing-header line changes between requests of one session (cc_version=2.1.321.49c, then .655): dropping it from
  the rendered prompt (done on Tue) keeps the prefix stable.
- **tools/codex_code.sh** (Codex second): the same one-command pattern with codex_local.sh. Stand-in test: Codex ran its
  exec_command in its own sandbox (hello.txt written), finished, and the server stopped with the port free. Kept in
  data/agent_cc_1111/ tonight so that release/next stays at the commit EvalSuite pinned (39947b1); it moves there after
  the run.

## Tue 23:3x: BigMoE's conversation cache wired (a separate clone), T1 armed

BigMoE's convcache (BigMoE 7eb3401, conv/convcache.py; PF-A supported in one sweep, the taps lever in) is in a separate
clone, release/cleanclone/cache (release/next's server + engine/loop/convcache.py + the hook, serve_cache_hook.diff), so
tonight's pinned EvalSuite clone stays unchanged. The hook: CC.install(G()) at the first next_item (an import / install
failure logs "conversation cache off" and serve.py runs cold: checked on the stand-in engine); CC.hint(sys_end, lane, side,
conv) before each item; CC.last() into the done line and the request log. CONV_CACHE_GB defaults 0.6 / 2.5 / 6 by --mem;
DFlash2 throughout while the cache is on (BigMoE: an MTP-head turn can restore only from an MTP-head entry).
**T1** (t1_cache.sh + replay.py): serve.py --mem 32 with CONV_CACHE_CHECK=1 (every hit compared with a cold prefill),
replaying the 45 recorded requests of sessions_real_1110 in order. Night order: two quick checks -> T1 (00:29) ->
EvalSuite 32 GB cold (pin 39947b1) -> 64K / 128K runs. If T1 passes: the cached agent test on Wednesday (32, then 45 GB).

## Wed 01:01-01:13: T1 FAIL (5 of 12 hits bitwise); cause of 4 found (BigMoE's path rule); T1b armed

T1 ran at 01:01 (the 00:29 start moved to 01:00 by Kamen): serve.py --mem 32 (chat-32, PF-A, DFlash2) in the cache clone
with BigMoE's convcache 7eb3401 unchanged, CONV_CACHE_CHECK=1, the 45 recorded requests replayed in order
(data/agent_cc_1111/t1_32_1111/). 45 / 45 HTTP 200, 0 server errors, ready in 18 s. 33 misses (30 short ~700-token
requests and the 18-token quota probe: one chunk, never stored; the first prompt of each conversation), **12 hits: check
PASS 5, FAIL 7.** k = the replay index (30-36 Claude Code /v1/messages, 37-43 Codex /v1/responses):

| k | N | c (source) | new tokens | warm prefill | check |
|---|---|---|---|---|---|
| 30 | 12,302 | miss | 12,302 | 29.0 s | - |
| 31 | 12,496 | 12,288 (live) | 208 | 5.5 s | PASS |
| 32 | 12,300 | 9,216 (copy) | 3,084 | 12.4 s | FAIL B |
| 33 | 12,404 | 12,288 (live) | 116 | 4.1 s | FAIL A |
| 34 | 12,300 | 9,216 (copy) | 3,084 | 12.2 s | FAIL B |
| 35 | 12,404 | 12,288 (live) | 116 | 4.0 s | FAIL A |
| 36 | 12,627 | 12,288 (live) | 339 | 6.3 s | FAIL B |
| 37 | 8,390 | miss | 8,390 | 21.4 s | - |
| 38 | 8,491 | 8,192 (live) | 299 | 7.0 s | PASS |
| 39 | 8,388 | 8,192 (live) | 196 | 6.9 s | FAIL A |
| 40 | 8,479 | 8,192 (live) | 287 | 6.7 s | PASS |
| 41 | 8,573 | 8,192 (live) | 381 | 7.8 s | PASS |
| 42 | 8,389 | 8,192 (live) | 197 | 6.0 s | FAIL A |
| 43 | 8,617 | 8,192 (live) | 425 | 7.8 s | PASS |

(Warm prefill = the cached path alone; the check's own cold prefill, test-only, is excluded, so the logged first tokens
of 28-41 s include it.)

- **Signature A** (k 33, 35, 39, 42): "last logits, states (119 of 122), taps tail" at 116 / 116 / 196 / 197 new tokens;
  every hit with 208-425 new tokens on the same path passed. **Cause (BigMoE agrees, its bug):** convcache chose the
  prefill path by the new part (`N - c > chunk` -> PF-A), the loop by the whole prompt (r57_screen_rel1.py:987,
  `len(ids) > chunk`). A tail of one chunk or less therefore ran chunk-major (tier.prefill_call's compact scratch of the
  call's unique experts) while the cold prefill runs it inside the PF-A sweep (mode 1's full-E scratch on the original
  ids). pflm.py:15-17 already warns that E = 512 vs len(unique) changes MLX's gather kernel choice on short calls; the
  boundary (197 FAIL, 208 PASS) fits a kernel switch on the call's size; 119 of 122 leaves = from the first MoE call on.
  BigMoE's confound: all four also had N below the entry's previous prompt + reply (stale QSA rows past N); T1b replays
  the same order, so a PASS there rules it out.
- **Signature B** (k 32, 34, 36): "states (1 of 122)" only, last logits and taps tail equal: a copy restore at 9,216
  (3,084 new tokens through PF-A from c) and a live trim at 12,288 (339 new tokens chunk-major). The check did not name
  the leaf. BigMoE's suspects: the PLE layer's slots (chunk-major vs PF-A's own PLE staging), or a QSA raw / pooled leaf
  after a copy (the state setter resets the reserved capacity to c).
- **What it implies for PF-A itself:** at a hit the restored state at c is the cold PF-A's own (the 5 PASS rows) and only
  the tail's path differs, so PF-A (mode 1) and the default prefill should differ in bits whenever a prompt's last
  1,024-token chunk is short (under ~200 tokens). The earlier PF-A bitwise records never had a short last chunk (30K:
  292; 6,980: 836). Direct check below (T1b's runner, step 2).
- Ops: 01:14-01:25 the queue waited on a stale research PAUSE (fanwatch's 61-s heat pause at T1's end; its clear kept the
  file because `pgrep -f quiet_window.sh` matched a mere command line). The orchestrator fixed fanwatch and removed it.

**T1b** (t1b_pfa.sh, armed 01:28, after the two quick checks; BigMoE agreed): my copy of convcache.py = 7eb3401 + (a)
the path chosen by the whole prompt, `if PFLM and N > chunk` (PF-A from c, also for a one-chunk tail) + (b) the check
names each differing leaf (cache index:class[slot], warm vs cold shape) (convcache_t1b.diff). Step 0: BigMoE's stand-in
(conv/test_mock.py, MOCK_PFLM=1) on the patched module. Step 1: the same replay. Step 2: PF-A vs the default prefill at
exact-32 in the 1.1.0 clean clone, P = 5 x 1,024 + 116 and + 300, R57_LOGHASH=1, 64 tokens. Then the cold 32 GB agent
test (pin 39947b1, unchanged), then 64K / 128K. The cached agent runs wait for a passing T1.

## Wed 01:27-01:30: idle CPU of the 1.1.0 serve.py: one core, the extension's loader spin (lever: BIGMOE_IDLE_MS)

idle_cpu.sh (the orchestrator saw the agent server at ~100 % CPU while idle): the v110 clean clone's serve.py at --mem 24
and 32, one 16-token request, 10 s rest, then CPU time over 60 s idle: **100 % of one core at both settings** (24 GB:
47.4 -> 107.5 s; 32 GB: 68.0 -> 128.1 s; 52 threads). A 5-s `sample` (idle_cpu_1111/busy_thread_32.txt) shows one busy
thread, entirely inside bigmoe_ext's loader (no system call on its stack): the loader thread's idle pass ends in
`__builtin_arm_yield()` (engine/ext/bigmoe_ext.cpp:1804), i.e. it spins by design ("CPU (native thread): spin on the
sequence number", line 8). The ext already has the lever: **BIGMOE_IDLE_MS=n** (Breakthrough 11-02, bigmoe_ext.cpp:1521-1526,
in all three builds here): after n ms without a served call the loader naps 200 us per pass instead of yielding; calls
within a request come far less than 50 ms apart, so decoding never sees it; the first call after a long idle waits at most
~0.2 ms; timing only, so exact. Neither release/src (1.1.0) nor release/next sets it. Proposed: BIGMOE_IDLE_MS=50 as an
env default in chat.py / serve.py, after an idle-CPU + decode-speed A/B (a ~5-min job, next free slot); 1.1.0 is frozen,
so adopting it there is the orchestrator's and Kamen's call.

## Wed 01:32-01:45: T1b: signature A fixed (7 of 12 PASS); B = one leaf, QSACache keys at cache index 35, after a copy

T1b = T1 again (same replay order) on my patched copy of convcache.py (sha256 00488b23...; convcache_t1b.diff: (a) the
path chosen by the whole prompt, (b) the check names differing leaves). Data: data/agent_cc_1111/t1b_32_1111/.
- **BigMoE's stand-in** (conv/test_mock.py, one QSA + one GDN layer with the real cache classes, MOCK_PFLM=1) on the
  patched module: rc 0, 4 PASS / 0 FAIL, hits as expected (including its copy at 9,216).
- **T1b: 12 hits, PASS 7, FAIL 5; 45 / 45 HTTP 200, 0 server errors.** Signature A is gone: the Codex hits with 196 and
  197 new tokens now pass (all 6 Codex hits pass), and the 116-token Claude Code hits no longer differ in logits, taps or
  the other 119 states. Warm prefill with the fix: 2.8 s for 116 new tokens, 3.8-5.6 s for 196-425, 12.1 s for 3,084
  (cold 28.0 s for 12,302 and 21.5 s for 8,390).
- **Signature B** (all 5 FAILs): `states (1 of 122: 35:QSACache[0] (1, 2, N, 256) vs (1, 2, N, 256))`: the attention
  KEYS of the QSA cache at cache index 35 (QSACache.state = (*kv.state, raw, pooled)); same shape, different values;
  values, raw, pooled and the other 121 leaves, the last logits and the taps tail are equal. Pattern: in the Claude Code
  conversation the first live hit (before any copy) passes; the first COPY (k 32, from 9,216) fails, and so does every
  later hit, including live hits on the MAIN entry (k 33 / 35 / 36) and the second copy (k 34). The Codex conversation
  never copied and passed all 6, live trims below a decoded reply included. So the copy changes or aliases the main
  entry's layer-35 keys (or the copy's prefill writes into a buffer shared with it); the stand-in's copy passes, so it
  takes something the real engine has. Sent to BigMoE (owner) for the fix; T1c on it next.

## Wed 02:1x: T1c armed (BigMoE 134e811: my tested module + a per-row drift diagnostic for signature B)

BigMoE committed my tested file as 91c9a5f (sha256 00488b23, byte for byte) and sent 134e811 (sha256 e3434b13): the same
plus a CHECK-only diagnostic: per-row integer prints of every QSA leaf (keys, values, raw, pooled) at each prefill's end,
re-checked at the next request's start, after a restore (rows below c vs the source's prefill) and after the prefill;
the FAIL line names the warm-vs-cold rows. Read before use: logs only, nothing else changes. Installed in the cache clone
(my 00488b23 kept as convcache.py.00488b23). t1c.sh: BigMoE's stand-in, then the T1b replay; run folder
t1_runs/32_1111c (raw convcache.log + serve.log kept). Placed after the cold agent test and the pkg_110g checks, before
64K / 128K (~15 min). How to read it (BigMoE): drift at a request's start = the decode changed stored rows; a restore line
= the copy's read; FAIL rows only in [c, N) = the warm prefill itself.

Cold 32 GB agent test so far: probe 27 / 30 pass, 0 invented tools (02:11, 762 s); the 12 tasks started 02:11.

## Wed 02:3x: T1d armed after T1c (BigMoE b855883: CONV_CACHE_BRANCH=0, the orchestrator's 09:00 fallback, checked early)

The orchestrator's rule (02:1x): if there is no clean fix for signature B by 09:00, a branch (copy) becomes a miss; T1 runs
again on that at once, and if it passes, the cached 32 GB agent test goes next. BigMoE's b855883 (sha256 266f76e5) =
134e811 + CONV_CACHE_BRANCH (default 1, unchanged; 0 = a would-be copy is a cold miss and a new entry; the decision now
runs before the check's cold prefill). Read before use: the switch only. t1d.sh: after T1c, installs b855883 in the cache
clone (sha checked from BigMoE's repo and in the clone), BigMoE's stand-in with BRANCH=0, then the T1b replay with
CONV_CACHE_BRANCH=0; run folder t1_runs/32_1111d. Expected (BigMoE): 10 hits (the 2 copies at 9,216 become misses), all
PASS, unless the main entry's own decode changes its layer-35 keys (T1c's drift lines decide that).

**Correction (02:3x, BigMoE's predict_hits.py 3a2dc46, which matches T1 / T1b hit for hit):** the T1b section above says
the later failing live hits (k 33 / 35 / 36) were on the MAIN entry. They were not: by the module's rules k 33 is a live
hit on entry 1 (the copy k 32 made; it shares more with k 32 than with k 31) and k 35 / 36 on entry 2 (the copy k 34
made). All 5 FAILs are on copy-made entries; the main entry (entry 0) passed its only live hit (k 31) and was never
restored live again; Codex (entry 3, live take-overs only) passed all 6. So signature B is either (a) the copy itself, or
(b) entry 0's layer-35 keys below 9,216 changing during k 31's decode, seen only by the copies. T1c separates them: (b)
-> a `drift (request start): entry 0 ... 35[0]` line at k 32; (a) -> `restore (copy at 9216): ... 35[0]` with no start
drift; neither -> FAIL rows only in [9216, N). T1d's prediction (BigMoE data/conv/t1_predicted_branch0.json): 10 hits,
all live, 41.3 % of prompt tokens prefilled.
