# THE SWEEP: old "lossy" and error-bar kills, re-priced under today's FAST stack (v1, Wed 4 Nov 2026 14:4x)

> (a quote from the project owner, kept private)
are the kinds of things which we should be searching for." Every KILL / PARKED from before the 11-02 two-track rule
that was judged on an exact or error bar, and every published method set aside as "lossy", priced under today's FAST
stack. The candidates with sources are in research/SWEEP_CANDIDATES.md (33 rows).

Status: v1. Every number below is [P] (a replay or arithmetic on measured numbers) or [G] (a model). Nothing goes to
Kamen before MoonShots' independent re-derivation (the orchestrator's rule). DRAFT17 already has it (x0.723 vs x0.706).

## How each candidate is priced

- **Bytes [P]:** the ledger replay (live-cut checks of the 36 decision-map windows, plain LRU per layer). The stack is
  QOM cf 0 + every last row gated (DRAFT17), so every row is sure and loads its top-2. One pool per layer holds the
  store's base records at equal RAM: 24 GB = 147 x 2,162,688 + 46 x 770,048 B per layer, 12 GB = 51 / 32. Unit: SSD MB
  per kept token in decode (code / IFEval / multi). Scripts: trellis_draft17.py, draft17.py, pool_split.py,
  prefill_bytes.py.
- **Quality [G]:** a KL model built from measured map arms (scripts/map_kl.py, data/ledger/map_kl_fit.txt).
  - Flips = a + b sqrt(KL) per domain over ten full-model arms (rms 0.07 / 0.37 / 0.15 points).
  - KL at the lines (1.34 / 5.42 / 3.69 %): 0.0082 / 0.0164 / 0.0114.
- **The KL model's terms**, measured at the 45 GB pool unless noted:
  - base (QOM cf 0 + gated last row, 4-bit sure rows) = qom_0_live_bq: 0.0013 / 0.0093 / 0.0101.
  - ranks 0-1 of sure rows at a store with error ratio r vs MSB-3: r x 0.0020 / 0.0113 / 0.0128 (the measured MSB-3
    term bq_t3 - bq; MSB-2's measured term fits r ~3.9-5.2).
  - ranks 2-9 at ratio r instead of MSB-3: (r - 1) x 0.0004 / 0.0025 / 0.0021 (t4_all's KL: ranks 2-9 MSB-3 -> 4-bit).
  - the pool: (1 - g) x 0.0024 / 0.0180 / 0.0084, where g = the replay's keep gap closed toward the 45 GB pool. The
    147-slot cost is measured (C at 147 minus bq_t3).
  - DRAFT17 on code: +0.0006 (between bq's +0.0004 at 68 % coverage and the union-only all-bonus gate's +0.0023).
  - Check: the model gives C at 147 = 0.0057 / 0.0386 / 0.0313, as measured (by construction).

## Ranked (24 GB first; the BYTES10 line is <= 10 MB per kept token in decode)

| # | candidate (old verdict, bar) | FAST form | 24 GB MB per kept [P] | 12 GB [P] | est. flips % [G] (lines 1.34 / 5.42 / 3.69) | what it needs |
|---|---|---|---|---|---|---|
| 0 | today's FAST stack (reference): MSB-3 11-bit + POOLSPLIT + DRAFT17 | - | 19.5 / 14.3 / 10.6 | 52.0 / 54.4 / 39.4 | 1.12 / 7.67 / 6.01 (PASS / BETWEEN / KILL) | screen 6 tonight (DRAFT17's code cost) |
| 1 | B10 TRL-2 (KILL 10-25, 1.5x MSB-3 error bar) | a FAST-only store, 276 slots | **4.0 / 3.0 / 2.7** | 21.7 / 18.0 / 13.0 | 1.16 / 7.55 / 6.65 (PASS / BETWEEN / KILL) | screen 7 (the mix) tonight; full encode ~31 GB disk |
| 2 | the 2.40 b mix (gate / up TRL-2, down TRL-3; same B10 bar) | a FAST-only store, 239 slots | **7.2 / 5.0 / 4.1** | 28.5 / 25.3 / 18.4 | 1.15-1.21 / 7.58 / 6.47 (PASS / BETWEEN / KILL) | screen 7 (4 layers, KL read-out) tonight |
| 3 | TRL-3 / T3R (PARKED / KILL on a 12 GB bytes line; quality passed: ranks 2-9 at 0.5x MSB-3) | a FAST-only store, 185 slots | 15.8 / 11.4 / 8.5 | 44.9 / 45.2 / 32.8 | 0.95 / 6.62 / 5.03 (PASS / BETWEEN / BETWEEN) | the best chat quality of any store; ~47 GB disk; 3INST decode at ~3c speed |
| 4 | GPTQ-3 g64 (HOBBIT-style copy; "lossy", T:368 0.61x MSB-3 at 3.5 b) | a FAST-only store, 171 slots (MSB-3's size) | 19.5 / 14.3 / 10.6 | 52.0 / 54.4 / 39.4 | 1.01 / 7.08 / 5.36 (PASS / BETWEEN / BETWEEN) | the cheapest encoder (GPTQ, not trellis); quality at no byte cost |
| 5 | FAST 3-bit prefill (KILL on paper 10-20, exactness) | prompt rows read MSB-3 only | prefill x0.74: code 117.9 -> 87.4 | - | unknown (the prompt's KV at 3 bits; not on the map) | a map arm with 3-bit prompt rows (harness) |
| 6 | dense / trunk diet, e.g. 8-bit HC + PLE (KILL on hard KLD) | -627 MB of trunk to expert slots (+3.7 %) | ~x0.96 [P, elasticity ~1] | ~x0.96 | small, unknown | a map arm (HC8 was FAST-judged already) |
| 7 | Rnd19#5 plane-aware prefetch (PARKED, never run) | prefetch only the MSB-2 plane of predicted experts | engine reads -5-9 % (prefetch waste 18-26 % at 24 GB [K]) | - | none (prefetch only) | an engine arm (BigMoE) |
| 8 | B9 / B7 2-bit warm tier for ranks 4-9 (killed by a bytes line; quality never measured) | under QOM: low-bit residents raise the rank 2-9 keep | not priced (needs a two-tier replay) | - | the chat lever in principle (the pool term is 0.0180 of IFEval's 0.0386) | a two-tier replay design |
| 9 | Rnd19#2 gate-mass-adaptive tiers / HOBBIT on-miss low precision (PASS on 35B, never built) | rank 1 at 2 bits when its gate mass is small | ~x0.9 [G] | ~x0.9 | between C and lever 6 for those rows | gate masses (not in the routing files) |

Subsumed or dead under today's stack (no re-test):
- Subsumed by QOM at cf 0, which already drops every non-resident rank 2-9 expert on a sure row: dynamic / adaptive
  top-k (DYNK, top-8, ACE, M-09d), UNIQ, expert substitution / cache-aware rerouting.
- Dead on physics (each measured): sketch / low-rank shadow tiers (the expert spectrum is flat: r32 0.920), activation
  sparsity inside experts (0.769 energy at 30 % neurons), expert merging / shared bases (0.20-0.36 % shared energy).
- Out of bounds: static pruning (all 512 experts stay).
- Small or superseded: super-block scales (~5 %; 11-bit already x0.955), salient-group refinement, ASTC / BC texture
  formats, 12-bit scale fields, RARE2 (-4.3 % at 45 GB), POM / LP1 (smaller reads, not fewer; speed KILL).
- Plane-granular caches / LSB-on-miss: their FAST bound is on the map already (3-bit sure rows, t3_all).

## What the sweep says

1. **Code at 24 GB has a route under 10 MB per kept token with an estimated PASS:** a FAST-only trellis store (TRL-2
   4.0, the mix 7.2), est. code flips 1.15-1.21 % [G]. It was killed on 10-25 on an EXACT error bar and never priced as
   a FAST copy. Screen 7 tonight measures the mix on 4 layers with the KL read-out.
2. **Chat is quality-bound at 24 GB, and no single store reaches PASS in the model [G].** The KL budget at the IFEval
   line is 0.0164, and the base alone (QOM + the gated row) uses 0.0093. The two other terms:
   - the sure rows' ranks 0-1 precision (0.0113 at MSB-3);
   - the pool (0.0139 at 171 slots).
   Better codes (TRL-3, GPTQ-3) cut the first; more slots (TRL-2, the mix) cut the second, but at worse precision. The
   best chat stores (TRL-3, GPTQ-3) land BETWEEN on both chat domains at 8.5-14.3 MB.
3. **The FAST stack's 3-bit records are a truncation of the EXACT 4-bit codes,** kept nested so EXACT = MSB-3 + LSB. A
   re-quantized 3-bit code has ~half the error at the same or smaller size (GPTQ-3 0.61x, TRL-3 0.50x). FAST does not
   need the nesting, so this is quality at no byte cost.
4. **In the FAST stack, prefill now dominates process bytes for these prompts:** at 24 GB, prefill is 117.9 / 43.1 / 17.0
   MB per kept token vs decode 19.5 / 14.3 / 10.6 (86 / 75 / 62 % of the total) [P]. BYTES10 counts decode only. If
   Kamen's 10 MB counts the prompt too, the next wall is prefill, and FAST 3-bit prefill (x0.74) is only a start.
5. The 11-02 sweep (FAST_TRACK) took only kills "not on quality", which by design filtered out every KLD and error-ratio
   kill. That is why B10 / T3R / TRL-3 / GPTQ-3 were never re-priced as FAST copies. The answer to "why didn't we find
   it earlier" is that filter.

## Next (cheapest first)

- Tonight: screens 6 + 7 (DRAFT17's quality; the mix on 4 layers, KL read-out).
- MoonShots: re-derive rows 1-4's bytes (the trellis / GPTQ-3 / TRL-3 store prices) before any of them goes to Kamen.
- If screen 7's code estimate PASSes: Kamen's call on the full mix store (encoder + ~36 GB disk). TRL-3 / GPTQ-3 are
  the chat-side follow-ups (a GPTQ-3 store needs Hessians for all experts: the capture question).
- A two-tier replay (row 8) and a 3-bit-prompt map arm (row 5): designs, not runs, until the above land.
