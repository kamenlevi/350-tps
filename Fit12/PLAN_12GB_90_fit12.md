# 12 GB LOSSY to 90-130 tok/s: Fit12's section (Thu 5 Nov 19:4x; for Breakthrough's ~/Breakthrough/PLAN_12GB_90.md)

Goal (Kamen 19:4x via the orchestrator): 12 GB LOSSY at 90-130 tok/s (today ~57 on code), then publish. Constraint: code
quality (T0, the top-2 two-pass at 12 GB: HumanEval+ 80.0 vs 91.7 = KILL, IFEval -6.0; math PASS; memory 10.84 GB PASS).
Fit12 cannot write in ~/Breakthrough (standing rule), so this file is for Breakthrough to merge or link.

## Where the 57 tok/s check goes [K: T3R2's run, Wed 4 Nov 13:05, /Users/kamen/Fit12/data/scr/t3r2/p47_layers.txt]
Arm t80ck1u (P1-K1 pass 1, KU 4; certificate theta 0.8 + cf gate 0.9; the exact pass at REF2-T's tiers 4433333333, which is
not REF2-T's tokens: the 12 GB loop is verified greedy, corrected Sat 7 Nov), HumanEval prompts, quiet lock.
Per check ~261 ms for ~15 kept tokens (57.3 tok/s):
| part | ms per check | share | inside |
|---|---|---|---|
| draft | 13 | 5 % | 11.1 ms per draft phase |
| pass 1 (P1-K1, 16 rows) | 130 | 50 % | loader wait 53, compute gaps 71, edge 6; 341 misses, 461 MB |
| exact passes (46 % of checks, 1.56 passes each) | 105 | 40 % | wait 75, gaps 26, edge 4 per check; 568 misses, 1,072 MB per pass |
| commit | 12 | 5 % | |
Exposed SSD wait ~128 ms (49 %), compute ~97 ms (37 %). The SSD time is all exposed (1.23 GB per check at ~9.6 GB/s).

## Levers (factor = check-time arithmetic on the table above, tokens per check held)
1. EXACT-PASS DIET (FAST; Fit12 builds it, on its own T3 two-pass code): exact passes are 105 of 261 ms. Halving their
   cost or count = x1.25; removing them = x1.67 (T0-like, KILL on code). Routes: (a) a certificate calibrated on code so
   fewer rows go exact (today 46 % of checks); (b) a mid pass for the moderately unsure rows (4-bit top-4 of those rows
   only) before any full REF2-T pass. First test: CPU, from T3R2's logged checks: why rows go exact (margin, cf, which
   rows) and what each threshold would save. Then a T3R2-style A/B (16 HumanEval prompts, ~20 min quiet) and a map screen
   on code before EvalSuite. Expected x1.15-1.3.
2. PASS-1 COST (exact kernels + cache): pass 1 is 130 ms, 71 of them compute for 16 rows x ~2.4 experts. Kernel levers
   (Leap's NAX / FAST-NAX at 12 GB) and keeping likely rank-0 experts resident (pass 1 reads only the rows' rank-0
   experts: 341 misses per pass). Expected x1.1-1.2. First test: Leap's kernel arms on the T3R2 harness; a residency replay
   of rank-0 misses (CPU).
3. TOKENS PER CHECK (drafter): every component is per check, so +20 % kept per check = ~x1.15-1.2 after the extra rows'
   misses. Owner: MTP Head (P-OFF / D98), DFlash2. First test: kept per check on the T3R2 prompts with the new drafter.
Stack: x1.15-1.3 x x1.1-1.2 x x1.15-1.2 = x1.45-1.87, so 57 -> 83-107 tok/s on code. 130 needs more: the exact passes
nearly gone with code quality intact, or the SSD wait hidden (12 GB look-ahead prefetch was KILLED in its frugal form:
TRIED 'PREFETCH (frugal)'; recall@10 0.61-0.73).
Not levers here: the trellis / data-aware stores (screen 7 KILL, family stopped 4 Nov); HALF-K (a compute lever: whole
experts still stream from SSD).

## Lever 1, first numbers (Thu 5 Nov 19:5x; /Users/kamen/Fit12/scripts/t3_exact_split.py on T3R2's own logs, CPU)
t80ck1u, 16 HumanEval prompts, full outputs (44.9 tok/s; the 57.3 is the shared-text prefix), 357 checks:
| check mode | checks | kept per check | ms per check | MB per check | time | tokens |
|---|---|---|---|---|---|---|
| pass 1 certified | 55 % | 12.7 | 158 | 614 | 41 % | 72 % (~80 tok/s inside) |
| pass 1 + exact pass 2 | 28 % | 7.3 | 308 (pass 2 163) | 1,655 | 41 % | 22 % |
| cf gate -> exact check | 17 % | 3.4 | 236 | 1,778 | 19 % | 6 % |
So 59 % of the time buys 28 % of the tokens; the exact parts read 1.7-1.8 GB per check. Today's certificate = max softmax
>= 0.8 per row + the draft's cf >= 0.9; a sharper certificate that certifies more rows at the same divergence count vs
REF2-T is the lever (halving the slow modes' extra cost = x1.25-1.35).
First test (built, waits for a GPU slot): arm g1k1u + F12_CAL=1 in /Users/kamen/Fit12/scripts/fit_t3.py: t80ck1u's
pass 1 on every check, then the exact check (outputs = ex), logging per row p1 / top-2 margin / argmax / the draft's cf
beside the exact tokens (~8 min, 12 GB, share lock). Then an offline replay (CPU) prices any (theta, margin, cfmin)
rule: tokens per check, time per check from the table above, and divergences vs REF2-T at the first draft miss.

## Lever 1 RESULT (Thu 5 Nov 19:52; calibration run 19:40:55-19:51:37, 640 s, rc 0, swap flat; replay t3cal_replay.py)
- Run: arms g1k1u (P1-K1 pass 1) + g1k2 (top-2 pass 1), each = pass 1 on every check, then the exact check; 16 HumanEval
  prompts, 343 checks per arm; all 32 runs = ex tokens (as designed). Data /Users/kamen/Fit12/data/scr/t3cal.
- The time model is calibrated: today's rules replay to 45.8 (t80ck1u) / 40.2 (t80ck2) tok/s vs 44.2-44.9 / 40.8 measured
  on full outputs (T3R2).
- The certificate is already token-exact: committed tokens differ from the exact model's in 0-1 of ~3,400 at every theta
  and cf gate. So a sharper certificate has nothing to trade (lever 1 as framed: KILL). The map's damage is the context
  (pass 1's KV in certified rows; Breakthrough 19:4x).
- Speed by theta, cf gate 0.9 on (full outputs; modelled):
  | pass 1 | theta 0.8 | 0.9 | 0.95 | 0.98 |
  | P1-K1 (t80ck1u's) | 45.8 | 41.0 | 37.9 | 35.3 |
  | top-2 (t80ck2's) | 40.2 | 37.6 | 35.9 | 33.4 |
  Without the cf gate every point is ~8 % slower.
- With the map's code line (1.34 %): top-2 at theta 0.95 (1.22 %, PASS) is the code-valid point the map has: ~36 tok/s
  full outputs, ~20 % under t80ck1u's 45.8 (whose map screen is pending; Breakthrough expects it over the line).
- Next: price a wider pass 1 (map: top-5 at theta 0.9 = 0.92 %, PASS, 89.8 % of rows certified). It needs a new pass-1 form
  in t3_twopass.py (ranks 0-4) and its cost at 12 GB. The replay prices it once those are measured.

## Lever 2 (the wider pass 1, Breakthrough 19:5x) RESULT (Thu 5 Nov 20:0x; top-k form built in t3_twopass.py _TOPK)
- Form: each row's ranks 0..k-1 at REF2-T's tiers (0-1 at 4 bits, 2..k-1 at 3 bits), top-10 mass weights, no renorm; the
  map's topk sources use the same weights at 4 bits (Breakthrough 20:0x: no switch needed). Needs BIGMOE_MAXK=80 (the
  pinned engine's default 40 < k x 16 ids; supported to 92; Breakthrough's B12 variants run 80).
- top-4 / top-5 cannot run as one 16-row pass at 12 GB: the per-layer union reaches 54-80 experts > the pool's C_m 47
  slots ("bigmoe: 54 experts > C=47 at layer 0", abort 20:00:28, run c52, after its first top-3 prompt = ex).
- top-3 calibration (c53, 20:01-20:06, 305 s, 16 / 16 = ex): pass 1 ~207 ms (G1 mode) vs ~170 for top-2.
  Speed (full outputs, cf 0.9) at theta 0.8 / 0.9 / 0.95 / 0.98:
  | pass 1 | 0.8 | 0.9 | 0.95 | 0.98 |
  | P1-K1 | 45.8 | 41.0 | 37.9 | 35.3 |
  | top-2 | 40.2 | 37.6 | 35.9 | 33.4 |
  | top-3 | 36.3 | 34.5 | 33.1 | 31.3 |
- Verdict: a wider pass 1 LOSES speed at 12 GB (its extra reads cost more than the extra certified rows save). The
  code-valid two-pass ceiling on these prompts is ~34-38 tok/s full outputs, whichever narrow form passes the map.
  90-130 needs fewer bytes per kept token or a cheaper exact pass, not a pass-1 width. Options for top-4/5, if a map
  result ever needs them: 2 x 8-row pass-1 calls (slower) or an adaptive per-row width (needs its own map arm).

## Lever 3: Leap's Friday kernel switches on the 12 GB path (Fri 6 Nov 09:4x; the orchestrator 09:3x)
- Code read: the 12 GB T3 path (pinned bt_b12 8db71cc537 + v3p tier engine + MTPLX's own dense and attention calls + the
  d7b_live drafter on MLX's quantized_matmul) reads NONE of Leap's switches as they are: it loads no ref2, d7b_nax or r57.
  - REF2_DN_KS rides ref2's native dense path (qmm16n, +~1.5 GB native copy: too big for 12 GB).
  - D7BNAX_32 is a d7b_nax switch; my drafter block is 16 rows, so only its <= 16-row rule (qmm16c + per-shape ks) applies.
  - att_single / fs4 are ref2 CFG switches. MTPLX head-chunks the verify SDPA for 3-32 query rows (16 rows: 12 calls).
  - The exact check runs <= 4-row calls on MLX's kernels (B12's invariance), so attention / dense ports can only act on
    pass 1, the FAST part. FAST-NAX (R57_NAX / REF2_NAX_1CQ) has no counterpart: v3p's experts are gather_qmm on records3m.
- Ported in my copy (/Users/kamen/Fit12/scripts/f12_kports.py; pinned kernels /Users/kamen/Fit12/pinned/leap_1106):
  dnax = the drafter's 4-bit projections on qmm16c + per-shape ks (exact for the target: drafts are verified); att1 = pass
  1's 16-row SDPA as one call; dn1 = pass 1's 4-bit g64 dense (N >= 1024) on qmm16c + per-shape ks (no extra memory).
  GPU self-test: qmm16c+ks vs MLX 0.8-7e-3 max relative; one SDPA == the 12 chunks bitwise at 300 keys, not at 700.
- PRE-REGISTERED (before the run; share lock, ROUGH timings): arms ex, exd, t80ck2, t80ck2a, t80ck2n, t80ck2f on T3R2's 16
  HumanEval prompts (256 tokens, C_m 47 / C_l 32, F12_ALT=1).
  - exd: tokens = ex on 16 / 16, else a bug. Its price = the draft phase's ms per check.
  - A FAST port PAYS if its arm's tok/s is >= +3 % against t80ck2 (geo mean per prompt) with the saving visible in pass 1's
    ms per run; NOTHING if < +1 %. Quality stays the map's question (the ports change pass 1 only).
- kp1 (09:42) was stopped by my swap guard (+1.08 GB in 50 s beside a 39 GB job); kp2 waits for a clear memory slot.

## Lever 3 RESULT (Fri 6 Nov 13:2x; kp2 ran 12:59:03-13:17:31 under a share lock, rc 0, swap flat 11.99 -> 11.93 GB, 96 / 96 arm outputs; ROUGH)
- Data /Users/kamen/Fit12/data/scr/kp2 (kp2.txt, kp2_read.json = all 16, kp2_read_skip.json = 14 clean); reader
  /Users/kamen/Fit12/scripts/kp1_read.py (KP_SKIP=...). Breakthrough's never-wait self-check ran beside the run 13:00:50-
  13:02:15 (full GPU; it told me): prompts HumanEval/42 and /68 are left out of the numbers below (their arms fell in it).
- 14 clean prompts, full outputs (256 cap), C_m 47 / C_l 32, lifetime 11.39 GB in every arm (the ports add no memory):

  | arm | tok/s | vs base (geo / prompt) | kept | ms per check: draft / pass 1 / exact / commit / total | pass 1 per run |
  |---|---|---|---|---|---|
  | ex (exact loop) | 18.58 | - | 9.71 | 11.2 / - / 510.7 / - / 522.5 | - |
  | exd (+ drafter port) | 18.93 | x1.020 (warm-order bias) | 9.67 | 8.4 / - / 501.6 / - / 510.6 | - |
  | t80ck2 (FAST base) | 38.72 | - | 9.32 | 11.1 / 124.4 / 91.1 / 11.0 / 240.6 | 156.9 ms, 935 MB |
  | t80ck2a (+ att1) | 39.16 | x1.013 | 9.32 | 11.1 / 121.9 / 90.9 / 10.9 / 238.0 | 153.8 |
  | t80ck2n (+ dn1) | 40.28 | x1.054 | 9.22 | 11.2 / 114.5 / 88.9 / 11.3 / 229.0 | 139.7, 908 MB |
  | t80ck2f (all three) | 40.10 | x1.047 | 9.17 | 8.1 / 112.5 / 94.1 / 10.9 / 228.7 | 139.2 |

- Per phase, paired by prompt (the cleaner read: the FAST arms write different texts, so their tok/s ratios spread
  x0.59-1.47): dn1 pass 1 -17.5 ms per run (median, lower on 14 / 14); att1 -1.0 (10 / 14, noisy); all three -15.8 (14 /
  14); the drafter port's draft -3.2 ms per check (13 / 14), -3.0 inside t80ck2f (14 / 14). SSD bytes unchanged.
- Engaged per run: dn1 ~181 qmm16c calls per pass 1 (N >= 1024; ~496 other quantized calls stayed on MLX: 8-bit, N < 1024,
  not broken down); att1 ~12 per pass 1 (one per attention layer); dnax every drafter projection of <= 16 rows (ks > 1).
- VERDICTS (lines above): dn1 PAYS (+5.4 %); att1 BETWEEN (+1.3 %, ~nothing: 16-row attention at 300-600 keys is small
  here); all three PAYS (+4.7 %, no better than dn1 alone within noise); the drafter port is ~-3 ms per check (+0.5 % on
  the exact loop's 522 ms check, ~+1.3 % on t80ck2's 240 ms). The 12 GB check is bytes-bound (t80ck2 ~1.47 GB per check,
  ex ~4.2 GB), so dense kernels move it ~5 %.
- exd = ex on 14 / 16 (12 / 14 clean), against my pre-registered 16 / 16. Not a port bug: ex itself is reproducible (kp2's
  ex = Thursday's c51 on 16 / 16), and both divergences follow the known keep-1 replay dependence (WV3, Oct: MTPLX's commit
  replays the PLE layer at width 1 when a <= 4-row call keeps 1 row, so B12's exact tokens depend on the draft pattern at
  near-ties). HumanEval/17: exd has extra keep-1 commits at tokens 133 / 146, divergence at 178; HumanEval/77: ex has an
  extra one at 28, divergence at 134. PR1 (2-row replay, PASS in Oct: draft-policy-invariant) is not in the pinned engine,
  so any drafter change on the 12 GB exact line moves tokens at near-ties until PR1 is installed. My 16 / 16 line forgot it.
- CORRECTION for the shared plan: t80ck2 is not the exact mode. It commits pass-1-certified rows (theta 0.8, cf 0.9) without
  the exact check (= ex on 5 / 16 here), and the map scored top-2 at theta 0.8 a code KILL (1.63 %). The 12 GB exact loop
  (ex) runs 18.4-18.9 tok/s on HumanEval (T3t 18.9 and T3R 18.42, both quiet; kp2 18.58 share). The 40.8 quoted as the
  12 GB exact line is T3R2's t80ck2 full-output number.

## What the 12 GB exact loop (arm ex) is exact to (Fri 6 Nov 21:3x; fact-check for FULL's paper, from code + records, no run)
- ex = DFlash2 L1-20 (4-bit) drafts 15 tokens per check; the exact check verifies them in <= 4-row calls (4 rows nearly
  always), stopping at the first miss. Pinned bt_b12 8db71cc537 with the suite's env (B12_LATE3=2,10): multi-row calls take
  the verify flags FL_MR, every one of the top-10 ranks read and waited for (NF = 10; bt_b12.py l.370-373, 459-463). Tier
  plan 4433333333: ranks 0-1 at 4 bits, ranks 2-9 at 3 bits (MSB-3). No rank is late in ex.
- The late rule (cold MSB-3 ranks 2-9 read after phase A and added half a layer late) is the 1-row path with B12_ALLWAIT=0
  (the default): AR decode, and in ex only a possible 1-row tail call at the token cap, where drafts are truncated.
- So ex is not bit-identical to the line's one-token decoding. The 1-row path keeps the late rule (pool-dependent bits)
  and uses decode-width arithmetic (WV1: widths 2-4 are bitwise equal; WV3: a width-1 forward differs). What holds: ex is
  deterministic and independent of pool state (Fri kp2 ex = Thu c51's g1 arms on 16 / 16), and every committed token is
  the greedy argmax of the 12 GB computation at 2-4 rows per call. Near-tie tokens depend on the draft pattern through
  keep-1 replays until PR1 (Lever 3 RESULT).
- Amendment (Fri 21:3x, found while testing the new reader on kp2's log): the harness also recorded a 40-s PAUSE (171-211 s
  into kp2), inside HumanEval/68's arms (its t80ck2a took 48 s). /68 was already left out, so the numbers above stand.

## 12GB-CLEAN (pre-registered Fri 6 Nov 21:3x; the orchestrator 21:3x, NewIdeas QUEUE f2243e8; runs Saturday morning)
- One clean number for the release: the 12 GB VERIFIED-GREEDY loop (arm ex; not exact) ALONE in its own process, so its
  lifetime peak footprint is its own. Replaces the mix of four runs and subsets (18.38-18.9; 11.39 GB from a six-arm process).
- Run: /Users/kamen/Fit12/scripts/ex16.sh (task b8qfeow0m, armed 21:37) -> fit_t3.py arm ex only, no ports, F12_RERUN=1,
  all 16 of T3R2's HumanEval prompts, greedy, cap 256, C_m 47 / C_l 32, quiet lock (~8 min). Start: Saturday from 06:00 at
  the first 10 clear minutes (no other quiet lock / ticket, no MEM > 5 GB lock, no PAUSE / HOLD; 1 minute once
  /Users/kamen/Fit12/data/scr/ex16/GO exists); deadline 18:00. Guards: swap +1 GB, 30 min. DONE file at the end.
- Reported by /Users/kamen/Fit12/scripts/ex16_read.py (tested on kp2's log and on two FAKE runs, one with a PAUSE):
  decode tok/s per prompt and their GEOMETRIC MEAN (the headline), pooled tok/s, end-to-end tok/s, tokens and ms per
  check, SSD GB per check (own reads), the process's lifetime peak phys_footprint (RUSAGE_INFO_V4, GB and GiB), the
  engine's settings lines verbatim (tier plan, C_m / C_l, pools, HC, late ranks), and any voided prompt.
- No pass / fail line: a measurement. Validity: every counted prompt PAUSE-free (a paused prompt is re-run once, then left
  out and named); the lifetime peak must be under 12 GB (the line); rc 0 and a 'done' line.
- AMENDMENT Fri 23:34 (the slot only; arm, prompts, settings, report and validity unchanged): the orchestrator 23:3x: the
  window opened at 23:30, so it may run before 06:00 in a GPU gap. Re-armed as task b6utph004 with NOT_BEFORE = Fri 23:34
  (same gate: 10 clear minutes); /Users/kamen/Fit12/data/scr/ex16/WAIT (NewIdeas may touch it to keep the slot for later)
  blocks the gate like HOLD.

## 12GB-CLEAN RESULT (Sat 7 Nov 00:3x; ex16 ran 00:28:27-00:32:42 under a quiet lock, rc 0, swap flat 6742 MB, 16 / 16 counted)
- The 12 GB VERIFIED-GREEDY loop (arm ex; not exact) alone in its own process, all 16 HumanEval prompts, greedy, cap 256:
  **18.42 tok/s decode, geometric mean** (pooled 18.47: 3,456 tokens in 187.11 s; min 17.16 on /16, max 20.30 on /156).
  End to end with prefill (3.4-5.2 s per prompt of 103-367 tokens): 13.66 (geometric mean).
- Lifetime peak phys_footprint of the process (RUSAGE_INFO_V4): **11.144 GB = 10.379 GiB**, under the 12 GB line (valid);
  10.583 GB after load.
- Settings (the engine's lines verbatim in /Users/kamen/Fit12/data/scr/ex16/ex16_report.txt): tier plan 4433333333 (ranks
  0-1 at 4 bits, 2-9 at 3 bits MSB-3), C_m 47 / C_l 32 expert slots per layer (9 %), pools 6.03 GB, HC 8, embedding 4-bit
  g64, engine v3p (bt_b12 8db71cc537); late MSB-3 ranks (2, 10) apply to one-row calls only, verify calls of 2-4 rows wait
  for all ten ranks; drafter DFlash2 L1-20 at 4 bits (0.928 GB), 15 drafts per check, SW 2048.
- Per check (343 checks): 10.08 tokens kept, 11.2 ms draft + 533.7 ms verify, 4.42 GB of the process's own SSD reads.
- Decode tok/s per prompt: /156 20.30, /42 19.19, /68 17.49, /91 18.26, /16 17.16, /6 18.86, /79 17.95, /19 19.97,
  /161 18.42, /17 18.51, /56 17.43, /141 18.17, /101 19.19, /63 18.65, /114 17.75, /77 17.80 (the harness's own print
  differs by 0.01 on four prompts: rounding of the decode seconds; same geometric mean).
- Validity: rc 0, a 'done' line, no PAUSE interval (nothing re-run or excluded), no Error / Traceback, swap flat, GPU 0 %
  at the start under the quiet lock (NewIdeas' slot: after BigMoE's 200 STACK and Leap's slot, before runner 49). Outputs
  token-identical (count + sha) to kp2's ex arm on 16 / 16, from a different process, arm mix and cache history.
- Against the earlier mix: kp2 18.38 on all 16 (share lock, six-arm process, two prompts disturbed) / 18.58 on its 14
  clean prompts; T3R 18.42 (8 prompts); T3t 18.9 (4 prompts). The release number is 18.42 (geometric mean) / 18.47
  (pooled) at 11.144 GB; the six-arm process's 11.39 GB held the other arms' state too.
- Data: /Users/kamen/Fit12/data/scr/ex16 (ex16.txt, ex16_report.txt / .json, MANIFEST.txt with shasums + ENV, per-prompt
  _ex / _ex_toks / _ex_ph json). Sent to the orchestrator 00:3x.

## t80ck1u MEASURED (Sat 7 Nov 08:2x; the orchestrator 08:1x; c1u16 ran 08:19:27-08:21:48 under a quiet lock, rc 0, swap flat)
- The 12 GB FAST candidate (Breakthrough's map step 0, be2c175: P1-K1 theta 0.8 KU 4 passes the code line, 45.8 tok/s [P])
  ALONE in its own process, on 12GB-CLEAN's footing: all 16 HumanEval prompts, greedy, cap 256, full outputs, C_m 47 / C_l 32,
  F12_RERUN=1, F12_PHLOG=1. Runner /Users/kamen/Fit12/scripts/c1u16.sh; reader /Users/kamen/Fit12/scripts/c1u16_read.py (the
  orchestrator's metrics since 05:0x); data /Users/kamen/Fit12/data/scr/c1u16 (c1u16_report.txt / .json, MANIFEST.txt).
- WHOLE DECODE (n / decode wall time, prefill excluded): **46.33 tok/s geometric mean**, pooled 44.34 (3,415 tokens in 77.01 s),
  per prompt 29.81 (/91) to 86.83 (/68). FULL-PERIOD STEADY (wall time after each prompt's first check): 49.14 geometric mean,
  45.66 pooled. END TO END with prefill: 24.49 geometric mean, 24.92 pooled.
- Lifetime peak phys_footprint (RUSAGE_INFO_V4): **11.245 GB = 10.473 GiB**, under the 12 GB line.
- Per check (357 checks): 9.57 tokens kept; draft 11.1, pass 1 106.4, pass 2 / exact 83.8, commit 11.3 ms; 101 checks with a
  pass 2 and 60 exact checks after the cf gate. The first check + setup costs ~473 ms per prompt (mean; ~175-230 ms when
  pass 1 certifies check 0, ~630-910 ms when it goes exact).
- Validity: rc 0, a 'done' line, no PAUSE (16 / 16 counted), no Error / Traceback, swap flat at 6797 MB, GPU 0 % at the start.
- Against the replay: the measured pooled 44.34 sits within the earlier measured 44.2-44.9 and 3 % under the replay's 45.8
  [P]; the geometric mean (the headline form) is 46.33. Against 12GB-CLEAN (18.42 / 18.47 at 11.144 GB): x2.52 geometric
  mean, x2.40 pooled.
- Tokens (information): = the verified-greedy loop (ex16) on 4 / 16 prompts (first divergences at 104-252); = REF2-T through
  256 tokens on 4 / 16. ex16 = REF2-T on 13 / 16 (divergences /101 @164, /6 @117, /77 @134: verified greedy, near-ties).
- Quality is EvalSuite's code same-scores (docs/PREREG_t80ck1u_2026-11-07.md, HumanEval+ 60 x 2 orders). Entry point
  (Sat 08:3x): fit_t3.py with F12_IDS_OUT (one arm: t80ck1u / t90ck1u / ex), F12_CAP=item, F12_KEYS in run order; it writes
  {key: ids} + _meta.json after every prompt. Tested in FAKE mode. Backup fit_t3.py.bak_es; new sha256 7ebdce481ea5....
  EvalSuite told: the VOID rule "ex reproduces REF2-T on 4 rows" can fail without an engine bug (see above).
- Findings note: /Users/kamen/FableGod/findings/2026-11-07_0823_12gb-fast-t80ck1u-46tps.md.
- Sat 10:5x: the entry point now writes r57rows.py's input ({key: {arm: [ids]}}; fit_t3.py sha256 ec0964f190b7), and
  F12_WIRED=1 adds Leap's wired-limit call. WIRED A/B pre-registered (no pass / fail; an engine A/B): /Users/kamen/Fit12/scripts/
  wab.sh runs t80ck1u W (F12_WIRED=1) then B in separate processes on this section's footing. [P] from c1u16's phase logs:
  check 0 runs ~500 ms over the later same-mode checks when it goes to pass 2 / exact, 3.6 s in all = 4.7 % of decode, so
  W <= +4.9 % whole decode; tokens W = B expected. On the verified-greedy loop (ex16) the same excess is 2.0 % of decode.
  Starts once /Users/kamen/Fit12/data/scr/wab/GO exists (after the usage hold) and 10 minutes are clear.

## WIRED A/B RESULT (Sat 7 Nov 15:5x; wab.sh ran 15:49:51-15:55:07 under a quiet lock, rc 0, swap flat, no PAUSE; GO 14:01)
- t80ck1u W (F12_WIRED=1: mx.set_wired_limit(55.66 GB), was 0) then B, each alone in its own process, 16 HumanEval, cap 256:
  whole decode W 46.34 vs B 46.16 geometric mean (W / B x1.0039 per prompt), pooled 44.34 vs 44.21; full-period 49.18 vs 49.12
  (x1.0013); end to end 24.33 vs 24.58 (x0.990: W's prefill 60.87 vs 59.25 s, +2.7 %, W ran first); lifetime 11.242 vs
  11.244 GB; tokens W = B on 16 / 16 (= c1u16 too: three runs, one output).
- Check 0 unchanged: the excess over later same-mode checks is 3.64 s (W) vs 3.82 s (B) = 4.7 % vs 4.9 % of decode; per
  prompt 850 / 861, 888 / 914, 899 / 925, 896 / 912, 865 / 887, 815 / 833, 627 / 659 ms when check 0 goes exact.
- VERDICT: KILL at 12 GB (no gain). The 12 GB first-check excess is not IOGPU un-wiring (Leap's 45 GB cause). It looks like
  the first exact pass after prefill filling ranks 2-9 into cold pools (an expert-cache warm-up). Open lever, not routed:
  prefetch the first check's ranks 2-9 during the prefill's tail (<= ~4.9 % whole decode [P]).
- Findings note: /Users/kamen/FableGod/findings/2026-11-07_1555_12gb-wired-limit-null.md. Data /Users/kamen/Fit12/data/scr/wab.

## TABLE 12 GB CELLS 12E + 12F (pre-registered Sat 7 Nov 17:2x; the orchestrator 17:1x, NewIdeas 17:2x QUEUE c8dfaac)
- Kamen's 45 / 24 / 12 GB x exact / lossy table (Sun ~08:00). The 12 GB cells run on BigMoE's S5 prompt set so the rows
  compare: 12 HumanEval (68, 16, 91, 6, 79, 19, 161, 17, 56, 141, 101, 63) + MBPP12 (16, 100, 146, 161, 183, 208, 224, 246,
  268, 296, 305, 319), CAP 256 as S5, greedy, full outputs to EOS / cap.
  - 12E (slot 3): arm ex, the verified-greedy loop (NOT bit-exact; 12GB-CLEAN's 18.42 was on 16 HumanEval).
  - 12F (slot 4): arm t95ck1u = P1-K1 KU 4, cf 0.9, theta 0.95 (t80ck1u -11.7 and t90ck1u -8.3 pt failed EvalSuite's code
    gate; the map passes theta 0.95 at 1.10 % code flips, 37.9 tok/s [P] on 16 HumanEval). FAST.
- Runner /Users/kamen/Fit12/scripts/tab12.sh: each arm alone in its own process, back to back under one quiet lock, 12GB-CLEAN's
  footing (C_m 47 / C_l 32, F12_RERUN=1, F12_PHLOG=1). Each run writes r57rows-form ids for EvalSuite (tab12{e,f}_ids.json).
- Report (c1u16_read.py): whole decode (headline), full period, end to end, each as geometric mean and pooled, overall and per
  set (HumanEval / MBPP); lifetime peak; 12E's tokens vs ex16 (12 shared HumanEval keys: same arm and cap, so they should
  match), 12F's tokens vs 12E. No pass / fail: measurements. Validity: rc 0, a 'done' line, PAUSE-free counted prompts,
  lifetime < 12 GB. 12F's quality verdict is EvalSuite's gate (slot 7, its own pre-registration).
- fit_t3.py sha256 11cadf9ec149: + the t95ck1u arm; keys missing from b12llff4's rows (MBPP) come from EvalSuite's
  data/items/dec_<set>.jsonl. FAKE-tested 17:23 (both arms, the reader's per-set split, r57rows-form ids).
- RESULT (Sat 17:4x; tab12.sh 17:36:52-17:46:44, one quiet lock, rc 0 both, no PAUSE, swap flat 6733 MB; GO 17:24):
  - 12E verified greedy (ex): whole decode 12 HE geo 18.58 / pooled 18.64, MBPP12 18.18 / 17.79 (all 24: 18.38 / 18.34);
    full period 18.57 / 18.43; end to end 13.87 / 11.15; lifetime 11.140 GB = 10.375 GiB; 450 checks, 8.86 kept, 471 ms
    each. Tokens = ex16 on the 12 shared HumanEval keys (12 / 12).
  - 12F theta 0.95 (t95ck1u): whole decode 12 HE geo 40.59 / pooled 39.87, MBPP12 18.74 / 18.66 (all 24: 27.58 / 27.90);
    full period 45.33 / 18.97; end to end 22.73 / 11.56; lifetime 11.280 GB = 10.505 GiB; 529 checks, 7.74 kept; per check
    pass 1 98.3, pass 2 / exact 158.5 ms; checks with a pass 2 261, exact 129. Tokens = 12E on 6 / 24.
  - Reading: FAST x2.18 over verified greedy on HumanEval, x1.03 on MBPP. MBPP keeps 5-8 tokens per check, so pass 1
    rarely certifies, and some MBPP prompts run slower than verified greedy (/268 13.9 vs 17.5, /224 17.0 vs 19.8).
  - Findings note: /Users/kamen/FableGod/findings/2026-11-07_1747_12gb-table-cells.md. Ids for EvalSuite:
    /Users/kamen/Fit12/data/scr/tab12/tab12{e,f}_ids.json (r57rows form, CAP 256).
