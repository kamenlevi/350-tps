# 12 GB LOSSY to 90-130 tok/s: Fit12's section (Thu 5 Nov 19:4x; for Breakthrough's ~/Breakthrough/PLAN_12GB_90.md)

Goal (Kamen 19:4x via the orchestrator): 12 GB LOSSY at 90-130 tok/s (today ~57 on code), then publish. Constraint: code
quality (T0, the top-2 two-pass at 12 GB: HumanEval+ 80.0 vs 91.7 = KILL, IFEval -6.0; math PASS; memory 10.84 GB PASS).
Fit12 cannot write in ~/Breakthrough (standing rule), so this file is for Breakthrough to merge or link.

## Where the 57 tok/s check goes [K: T3R2's run, Wed 4 Nov 13:05, /Users/kamen/Fit12/data/scr/t3r2/p47_layers.txt]
Arm t80ck1u (P1-K1 pass 1, KU 4; certificate theta 0.8 + cf gate 0.9; exact = REF2-T), HumanEval prompts, quiet lock.
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
