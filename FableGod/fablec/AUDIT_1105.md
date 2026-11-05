# AUDIT 1105: the overnight answers, checked before anything is built (Fable C, Thu 5 Nov 2026, 07:0x-08:4x EET)

> (a quote from the project owner, kept private)
Inputs: `~/FableGod/cloud3/live/cloud3/REPORT_P0..P3.md` + `REQUESTS.md` (Cloud Fable 3), `~/FableGod/far/FAR.md`,
`~/FableGod/zero/ZERO.md`, `~/FableGod/goal/GOAL.md`, `~/FableGod/full/FULL.md` (+ Round 2). Measured sources used for the
re-derivations: `~/FableGod/KERNEL90.md` (lines 97-114), `~/FableGod/DAY9_2026-11-02.md` (line 93, the C0 timeline; line 875,
BigMoE 5b), `~/FableGod/BUILD_DAY_1104.md`, `~/FableGod/far/FAR.md` section 7b (the SSD wait law), `~/TRIED/TRIED.md`
(lines 36-37, 48, 69, 101, 108, 121, 349, 364, 425, 446, 724, 848, 886, 941, 1226, 1256), `~/TRIED/NOVELTY.md`,
`~/NewIdeas/QUEUE.md` line 588 (the OEA k8 map result), `~/Breakthrough/keepset/qom_keep.py` (the engine's QOM rule),
`~/TrainLab/notes/DRAFTER_PLAN_1104.md`, `~/MoonShots/research/FAR_NOVELTY_CHECK.md`. Marks: [K] measured (source named),
[P] arithmetic on [K], [G] judgement. Thinking and writing only: no GPU, no downloads, no script run; every number below is
either quoted from a named file or derived in the text. Gains are HALVED where the table says so (Kamen's rule).

Lines: code FAST at 45 GB = tok/s (today 110-117 [K DAY9 875, brief 3.4]); code EXACT at 45 GB = tok/s (83); 24 GB = SSD MB
per kept token (code 19.5, chat ~88 [K brief 3.4]). Map lines: all-row flips <= 1.34 / 5.42 / 3.69 % (code / IFEval / multi).

## 0. The three findings that change the ranking (read these first)

**F1. "Same bytes" is true against the wrong baseline [K cloud3's own replay].** The strict band table reads the same
bytes as its resident-keep TWIN (REPORT_P3 section 20: within 0.5 MB), but the twin is not what runs today. Today's 45 GB
FAST preset is QOM at cf 0 + the gated bonus row (`qom_keep.py`: THR 0.0, KS 2, "a sure row keeps ranks 0-1 and each rank 2-9
expert that is in the block's loads or resident"; FULL.md 2.1 line 3; DAY9 875). Against that preset, cloud3's section 8 / 20
tables give, at the 45 GB pools, SSD MB per kept token code / IFEval / multi:

| rule (cloud3's replay, sections 8 and 20) [K] | 45 GB MB | 45 GB tiles |
|---|---|---|
| QOM cf 0 + BQ (today's preset) | 6.9 / 4.5 / 4.5 | 290 / 482 / 474 |
| strict c3_b2d | 14.7 / 16.8 / 17.6 | 155 / 382 / 403 |
| strict c3_b2c | 16.1 / 17.1 / 17.7 | 169 / 391 / 409 |

So c3_b2d reads x2.1 / x3.7 / x3.9 the bytes of today's preset [P]; the x0.41 / 0.52 / 0.58 "of today's tiles" are ratios to
EXACT's 315 / 530 / 532, and against today's QOM tiles they are x0.44 / 0.57 / 0.65 [P]. The extra bytes are the ranks 2-4 of the
0.9-0.99 rows and ranks 2-7 of the 0.3-0.9 rows that QOM does not load (it keeps only their resident ranks). Priced with FAR's
wait law (section 7b: ~12 ms floor + 0.155 ms per miss, bandwidth-bound at the margin; the band table's extra loads are
demand reads, not QOM's optional ones): code +7.8 MB x 8.5 kept = +66 MB = +31 misses = **+4.8 ms per check** (+5-9 ms if the
by-day per-miss cost of 0.15-0.29 ms applies); IFEval +2.1 ms, multi +1.8 ms [P]. Cloud3's cost model (section 13: t(r) = 90 -
(1 - r) E - (1 - r) 12) CREDITS an SSD saving of (1 - r) x 12 ms that does not exist: the sign is wrong.

**F2. The expert term being cut is 22-27 ms, not 38-43 [K KERNEL90 113-114; DAY9 93; LIVE-CUT AUDIT].** The brief's "experts
~38-43 ms = 3,700-3,840 tiles" is the 16-row EXACT figure (KERNEL90: ~43 ms on NAX6 per 16-row check at C2, 7.30 GB; NAX6-NH
30.9-33.2). The live default verifies 9.7 rows on code (TRIED 941) with ~54 distinct experts per layer instead of 73-79 (cloud3
P2 section 2: x0.69-0.74 of the groups), and QOM keeps ~92 % of those tiles: 43 x 0.72 x 0.92 = ~28 ms on NAX6, ~22 ms on
NAX6-NH; DAY9's per-pair C0 timeline (2.9-3.2 ms per row x ~10 live rows x QOM's kept pairs) lands in the same 22-27 ms, as does
FULL.md's table (experts 22-23 ms). Cloud3 saw the ambiguity (section 13: "24-43 ms") and kept both ends; the high end is
not the live check. Re-priced on code at 45 GB FAST [P]: c3_b2d_reach07 tiles x0.44 of today's -> saves 12-15 ms of 22-27;
minus F1's +5-9 ms -> **net -3 to -10 ms per check = +3 to +12 % tok/s (110-117 -> 115-130), halved +2 to +6 %**, not
"117 -> 140-165". c3_b2d alone: x0.53 -> saves 10-13, net -1 to -8 ms = +1 to +9 %, halved +1 to +4 %.

**F3. "Top-8 on every other drafted row is free" is contradicted by a measured arm cloud3 cites as its warrant [K QUEUE.md
588].** The band table's chat pricing takes k = 8 rows at 0.00 % direct flips because "OEA k8 is a map PASS on every domain"
(section 16). The arm's numbers: oea_k8 (top-8 + union members on EVERY row, 16-row unions, map Tue 10:16) = **0.62 / 3.83 /
3.07 % all-row flips** (code / IFEval / multi) [K]: PASS by the lines, but 71 % of the IFEval line and 83 % of the multi line on
its own, at 16-row unions where members are plentiful (live unions have fewer members: LIVE-CUT AUDIT, TRIED 941). Since the
sure rows (cf >= 0.99: 23 / 21 % of chat rows) flip ~0 under k 8, the k-8 cost sits on the unsure rows: ~5 % per row on
IFEval, ~4 % on multi at 16 rows [P: 3.83 / 0.77, 3.07 / 0.79]. c3_b2d puts 61 % of IFEval's and 68 % of multi's realized rows
at k 8 (cloud3's band shares, section 16): ~3-4 points on each chat domain before the top-5 and top-2 bands and before the
context factor, versus the 0.87 / 1.14 % cloud3 priced. Corrected expectation [P/G]: c3_b2d IFEval ~5-6 % (line 5.42:
BETWEEN), multi ~4-5 % (line 3.69: BETWEEN, KILL above 5.54); c3_b2d_reach07 at tau 0.7 adds +0.85 / +1.3 -> IFEval ~6-7
(BETWEEN), multi ~5-6 (KILL-likely); the "PASS x3" and "PASS / PASS / BETWEEN-PASS" predictions are unsupported on chat. On
code the k-8 band is 17 % of rows and the arm's code cost is 0.62 % on ALL rows, so the code prediction (~0.6-0.9 % all-row vs
1.34) stands: PASS likely. The lever is code-only, like Q1-UNION 0.9 and REACH-CUT before it (TRIED 108, 941), and on chat the
tiles buy ~+1-2 % tok/s anyway [P: a 3-4 row chat check's expert term is ~10 ms; x0.57-0.65 saves 3.5-4.5 ms, minus F1's 2 ms].

Consequence: the Friday-night map arm is still worth running (masks ready; 5-10 min; code is the line that pays), but with the
pre-registration corrected (section 2, test 1) and with C3-R8's group count logged in the same window, because the whole tile
lever is worth 22-27 ms x (1 - r), not 40 x (1 - r). Nothing in the engine should be built on "same bytes".

## 1. The ranked table (every idea; gain halved; "value" = halved gain x odds, on the three lines)

Tried-status key: T-K tried and killed; T-A tried and alive (or adopted); U untried. Prior art: the nearest published work I
know (MoonShots does the web check). Cost: the cheapest decisive test.

| # | idea (session) | gain on our lines, HALVED [P] | odds the test passes [G] | cost | tried? | number errors found |
|---|---|---|---|---|---|---|
| 1 | **Rule C comment relax** (FULL, re-registered R2.1; measured by MoonShots M-41) | code FAST and EXACT-side kept x1.04 HumanEval+ (x1.074 profile, halved) / x1.06 MBPP (x1.125); tok/s by the same factor at ANY engine; 24 GB code bytes x0.96 | engine PASS (median S <= 0.92, T <= 1.05, C <= 1.15) ~50 %; the kept gain itself is measured | 10 min GPU (BigMoE 12 HumanEval C 224, A-B-A-B) | T-A: M-41 BETWEEN HumanEval+ (x1.074 < its PASS 1.10), PASS MBPP; R1 killed by M-40 | FULL's "12.0 halved" multiplied in COPYGATE G2 (x1.041) and the outside-span R1 (x1.016), both separate levers; the rule's own halved gain was x1.08, measured x1.074 profile (~x1.04 real by Mission 25's own halving); its PASS line 11.6 was missed |
| 2 | **c3_b2d, strict three-band table at 45 GB FAST** (cloud3 P3 16-19) | code tok/s +1 to +4 % (raw +1 to +9 % net of F1's bytes); chat +0.5-1 %; 24 GB: none (the strict tables read MORE bytes there, cloud3 section 20: 72.8 vs 46.5 MB code) | map PASS code ~60 %; chat ~25 % (F3); the engine cash-in needs the per-GROUP kernel (NAX6-NH, Thursday's conversion) and C3-R8's confirmation that QOM computes ~92 % of the tiles | map arm 5-10 min (masks ready) + R8's one log line + an engine A/B 10 min | U as a table; its pieces T-A (Q1-UNION 0.9 PASS code, OEA k8 PASS, QOM-BQ PASS/BETWEEN/BETWEEN) | F1 (bytes x2.1-3.9 vs today's preset; the SSD credit with the wrong sign), F2 (expert term 38-43 -> 22-27 ms; 140-165 tok/s -> 115-130), F3 (k 8 "0 %" direct; measured arm 0.62 / 3.83 / 3.07), "of today's tiles" = of EXACT's (x0.44 / 0.57 / 0.65 of QOM's) |
| 3 | **c3_b2d_reach07** (cloud3; the arm named for Friday) | code +2 to +6 %; chat ~+1 %; 24 GB none | map PASS code ~50 % (reach's +0.07 on top of b2d's margin; the X rule's unmeasured false accepts on 0.07 reached cheap rows per check); chat ~15 % | as #2 (masks ready) | U as a stack; REACH-CUT itself T-A (PASS code only, BETWEEN chat, TRIED 108) | as #2, plus: the headline x0.52 / 0.58 on chat is the tau-0.7 form that cloud3 itself says not to use on chat (tau 0.5 gives x0.60 / 0.65); the kept loss x0.997 on IFEval is unpriced in tok/s (-0.3 %) |
| 4 | **The split form** (this audit; cloud3 did not price it): strict (top-2 + members, NO resident keep) on the cf >= 0.99 rows only; QOM's resident keep on every other row; loads unchanged | code +2 to +3 % (tiles ~x0.69 of today's [G, from cloud3's attribution: 65 % of code rows are >= 0.99 and their resident rank 2-9 tails are the bulk of the 290 - 155 tiles QOM computes beyond strict]; saves 7-9 ms of 22-27 at TRULY the same bytes); chat +0.5 % | map PASS code ~65 % (quality = QOM cf 0's measured 0.42 % + the >= 0.99 band's top-2 cost 0.0-1.2 % direct on 18 % of rows, ~+0.3 all-row [P]); chat ~55 % (the >= 0.99 band flips 0.0 / 0.4 % under top-2 on chat) | 10 min CPU replay (bytes and tiles, `bytes10_replay.py` or cloud3's `sim_lru3.py` with a per-band resident clause) then one map arm 5 min | U | none to find yet: my [G] tile ratio is the number the CPU replay must replace |
| 5 | **Chat bytes lever at 24 / 12 GB** (cloud3 section 21 / 25: the QOM 0.5 chat route + top-8 on its unsure rows, then + REACH-CUT 0.5, resident keep) | 24 GB chat SSD MB per kept token x0.91 (u8 alone, raw x0.82) / x0.82 (both, raw x0.64); chat tok/s at 24 GB +2-4 % [P: ~113 misses per chat check x 0.155 ms; -36 % = -6 ms of ~70]; code untouched | u8 PASS ~70 % (expect +0.2-0.4 points, not "+0 to +0.1": the arm drops the non-resident ranks 8-9 of 26-34 % of rows, ~1/5 of OEA k8's cut); + reach 0.5 PASS ~50 % (multi 2.73 + 0.54 + 0.3 = ~3.6 vs 3.69) | 5 + 5 min map arms (C3-R15, R15b); masks need dm_oea_masks' qom form with `_u8` (one line) | U as a combination; pieces T-A (OEA k8 PASS, REACH-CUT BETWEEN chat, the chat route PASS 0.71 / 4.30 / 2.73 at 147 slots) | the u8 quality price "+0 to +0.1" rests on the same k-8-is-free reading (F3), softened here by the resident keep; the multi margin for R15b is ~0.1 point, not "within the route's lines" |
| 6 | **FAR-HYBRID near / far tiered eviction** (FAR section 8; Kamen's idea) | 45 GB EXACT tok/s +2-3 % (raw: -20 % of 100-200 live misses = -3 to -6 ms of 85-126); 24 GB code bytes x0.89 (raw x0.78); FAST: ~0 (QOM's optional misses) | FAR-G1 PASS (>= 20 % fewer misses at K 266 with set recall >= 0.80) ~30 % (FAR's own 25 %); the near tier is a noise model at V1's recall, the far map an oracle-state stand-in | FAR-G1 capture 6-7 min GPU (BigMoE builds it Thursday) + CPU read-out | T-A on CPU stand-ins (TRIED 36-37: FAR-COMBO, FAR-HYBRID "PASS on CPU stand-in"); the single-window form T-K/BETWEEN (Rnd17#2, R-57b) | FAR section 4 inherits GOAL's "EXACT SSD wait 55-60 ms": by day at C 224-256 the exposed wait is ~27-45 ms (FULL table, BUILD_DAY, FAR 7b's own io 29-53 ms), so its +7-18 % tok/s column is x0.5-0.75 of that: +4-9 % for perfect H 8, +2-5 % for the stand-in |
| 7 | **GOAL lever 1: the SSD off the critical path** (draft-state prefetch A, stride prefetch B, one command buffer C; "fit" at <= 2.8 bpw) | beyond owned work: ~0. A/B = the project's lever 2 (look-ahead prefetch into the volatile tier, IN FLIGHT, TRIED 39; EXACT +9 % expected at recall 0.823, FAST -5 ms [K BUILD_DAY]); ROUTEPRED / Rnd23 (draft-state route prediction) KILL (recall 0.09-0.24); C = the megakernel KILL (grid barrier 2.0-2.5 us vs dispatch 1.3-1.6 [K FULL]); "fit" = the 2.4-bit trellis store (chat quality FAIL [K brief 3.7]; a code bytes lever at 24 GB) | n/a | the oracle-replay test is good and cheap (issue all of a logged check's reads at t = 0, QD 16) and still worth 10 min to measure the floor directly | T-A (lever 2), T-K (megakernel, ROUTEPRED, trellis chat) | dense ~6 ms [P] vs measured ~32-36 ms of GPU per check (DAY9 93: GDN 12.4 + HC reads 11.4 + attention 7.3 + router / shared / tail 5); "EXACT SSD wait 55-60 ms = 45 %" is the residual of that error (measured remainder ~27 ms at C 224 [K FULL table; BUILD_DAY]); "latency problem, not bandwidth" is half right (FAR 7b: bandwidth-bound above a ~12 ms floor; the floor moves only with stalled layers, which perfect foresight cuts 5 %); so lever 1 FAST +36-45 % -> ~+5 %, EXACT +60-85 % -> +9-15 % [P]; "fit" re-bases EXACT on a lossy model, against the two-track rule |
| 8 | **GOAL lever 2: confidence-tiered k (sure rows k 4, unsure 10)** | subsumed by #2 / #4 (the Q1 / QOM family: QOM adopted; strict k 2 at cf 0.5 predicted KILL by cloud3's section 16; k 4-5 on the 0.9-0.99 band is cloud3's middle band) | as #2 | as #2 | T-A (QOM, Q1-UNION), U (k 4 strict) | "tiles -35-45 %" agrees with cloud3's x0.49-0.59; GOAL's quality argument (Expert-Sample, HookMoE) ignores the map's own band rates (cf 0.5-0.9 rows flip 15-37 % under top-2) |
| 9 | **GOAL lever 3: adaptive draft length / drafter parallel commit / one buffer / FR-Spec** | beyond owned: ~0 (the live cut at t 0.3 is the adopted form, rows 9.7 / 3.7 / 3.0; CALSTOP / STOPCLS / BWIDTH KILL; Mission 29 design D owned, -2.5 ms; megakernel KILL; FR-Spec ADOPTED: SC1, BP-1c PASS at 98K) | n/a | none | T-A / T-K | "chat x1.6-2 from adaptive length" is already in the default (chat rows 3-4 per check); "24 GB 19.5 -> 14.6" credits the live cut twice |
| 10 | **ZERO Design B** (3-bit experts, gate-threshold k, in-expert activation sparsity, cache-aware selection bias) | 3-bit: adopted as bytes (3-bit sure rows / tail; bits do not buy ms at 45 GB [K KERNEL90, L1-30 x1.22 where bytes allow 1.80]); gate-threshold k: T-K (R-26 tau 0.06, L1-17b/c); selection bias toward residents: T-K by orthogonality (REROUTE b25, I6, SERE fallback, MoEPrefetch substitution; |cos| 0.024); **in-expert activation sparsity on the experts: U** (TEAL on GDN projections PARKED, TRIED 364): if it held, expert ms x0.7 = -7 ms = +8 %, halved +4 %, x odds 0.15 = ~+0.6 % expected | TEAL on experts ~15 % (2-bit sure rows went BETWEEN / KILL / KILL: these experts are not tolerant; the kernel needs a two-phase gather inside packed 3-4-bit blocks, KERNEL90's territory) | TEAL: 10 min CPU on D2's recorded MoE inputs (one window per domain) x a few experts' weights: output error at 50 % sparsity vs the 3-bit tier's error (L1-17c's bar) | mostly T-K / T-A; one U | expert 1.84-2.76 MB (records: 2.16 MB MSB-3 + 0.77 sidecar); EXACT ceiling "130-170" assumes an MTP chain at k 4 (A 3.9): the drafter keeps 10.5 per 16 rows and the floor engine is 210-280 at that kept [K FULL table]; time = DRAM bytes / (0.8 x 286) ignores the per-group compute knee (77-83 % of streaming, per group not per byte); "10 MB needs 99 % hits" ignores the gate (19.5 MB today at far lower hit rates); Design C (REAP 55-60 %) is dead by Kamen's rule (TRIED 425, PRUNE26) |
| 11 | **c3_b2b_band5** (cloud3 R12: cf < 0.9 rows at k 5 in layers 8-35) | code +1 % (x0.91 more tiles) | ~35 % (1.03 % direct + context ~1.6 -> BETWEEN) | 5-10 min map, after #2 | U | none beyond F2 |
| 12 | **c3_b2b_top1** (R13) / **c3_b2d_reach07_u7** (R17) | +0.5-1 % / chat only | 40 % / ~10 % (k 7 drops 3 ranks of rows that cost 4-5 % per row at k 8 by F3) | 5 min each | U | u7's "quality unbounded" should read "KILL-likely by the oea_k8 arm" |
| 13 | **cloud3's strict cf 0.5 / 0 forms** (R1, R2, R4, R5, T1-T5) | n/a | KILL predicted by cloud3 itself (2.8-3.5 / 14-17 / 15-18 % direct); F3 makes it worse | do not run | predicted T-K | the P1 / early-P3 tok/s numbers (220-244) are the superseded pricing |
| 14 | **FULL R1: parts of one answer in one pass** | n/a | KILL (M-40 census: 0 % of HumanEval+ and MBPP answers have >= 2 independent parts; 1.2 % Magicoder) | done | T-K | FULL's x1.4-2.1 was conditional on a workload that does not exist on the lines |
| 15 | **FULL R2: the capacity drafter (DFlash3, 2-4B)** | kept 12-12.5 if it works (+15-20 %), halved +8 %, on both tracks; earliest live Nov 20-25 [K DRAFTER_PLAN corrected] | P-CAP >= +0.3 kept ~30 % | one night (armed by MTP Head) | T-A (P-CAP armed) | DRAFTER_PLAN's own corrections (prefill 56-230 tok/s, training 35-45 h per epoch) postdate FULL's "Nov 13-18" |
| 16 | **GOAL / ZERO: tree drafts, a bigger standalone drafter, kernel redesign #13, 2-bit for speed** (their own "would not spend" lists) | agree: T-K (TREES, KERNEL90's twelve KILLs, L1-30) | | | T-K | none |

Reading the table: nothing here moves a line by >= 1.3x; the two largest halved gains are measured levers (Rule C, +4-6 %
kept) and the strict tile family (+2-6 % on code tok/s, net of its bytes), and they multiply. The only untried piece with a
sizeable upside is in-expert activation sparsity (ZERO), at low odds. GOAL's first bet is already owned (lever 2 in flight).

## 2. Top 3 tests (each <= 10 min; the PASS / KILL lines written now)

**Test 1 (first): c3_b2d on the decision map, code first, with C3-R8's log in the same window.** Arms: `c3_b2d` and
`c3_b2c` (masks in cloud3/masks; dm_oea_masks' format; PERT.update(rmask=..., renorm=False)); the 24 chat windows run as the
control. In parallel (free, one log line): BigMoE's r57 screen under the 45 GB FAST preset logs the expert GROUP count per
layer call next to the miss count for 12 HumanEval prompts, exact vs QOM (C3-R8).
- PASS (code): all-row flips <= 1.34 % for c3_b2d (prediction [P]: 0.7-0.9 %) AND R8 shows QOM's group count >= 0.85x exact's
  (then the tile lever is real: ~22-27 ms x (1 - r) on code). BETWEEN: 1.34-2.0 %, or R8 at 0.6-0.85x (then the term is
  already partly cut and the gain halves again). KILL: > 2.0 % on code, or R8 <= 0.6x (QOM already computes few tiles; the
  strict form has nothing to cut).
- Chat (recorded, not decisive): prediction IFEval 5-6 %, multi 4-5 % (BETWEEN); if both land under 3 % the k-8 reading of
  F3 is wrong and the chat form is alive after all.
- Do NOT run c3_b2d_reach07 before c3_b2d's code read is in; if c3_b2d PASSes on code, run reach07 on code only (prediction
  0.8-1.0 %; PASS <= 1.34, KILL > 2.0) with tau 0.7 as built.

**Test 2: Rule C's engine arm (FULL R2.1's lines, now the one that matters).** BigMoE, 12 HumanEval at C 224, qall vs qall +
SPAN (rule C, the causal tagger, the line-end guard), A-B-A-B, same prompts; per task T = generated tokens to EOS, S = wall
seconds, K = kept per check, C = the share of generated tokens inside '#' comments.
- PASS: median S ratio <= 0.92 AND median T ratio <= 1.05 AND C ratio <= 1.15 (prediction [G]: S 0.93-0.96, T 1.00-1.03, K
  1.04-1.07: BETWEEN is the likelier read). BETWEEN: S <= 0.97. KILL: S >= 0.97 or T >= 1.15 (the arXiv 2610.23818 regime).
- Why second and not first: the kept gain is measured (M-41) and the engine arm decides whether it is time or length; it is
  the lever that multiplies with every cycle gain, including test 1's.

**Test 3: the split form, CPU then one map arm.** (a) CPU, 10 min, no GPU: replay the 36 windows at the 45 GB pools
(`bytes10_replay.py`'s LRU, or cloud3's `sim_lru3.py` with a per-band resident clause) for three rules: QOM cf 0 + BQ (today),
strict c3_b2d, and SPLIT = rows with cf >= 0.99 at ranks 0-1 + union members (no resident keep), every other drafted row as
QOM (ranks 0-1 + members + residents), the bonus row by its next draft's band. Report bytes and tiles per kept token.
- PASS (a): SPLIT's bytes within +3 % of today's AND tiles <= x0.72 of today's on code (prediction [G]: x0.66-0.72). KILL:
  tiles > x0.85 (the resident tails of the sure rows are not where the tiles are; then the strict table's bytes are the price
  of the lever and #2 stands alone).
- (b) if (a) passes: one map arm (`split_0.99`, masks by dm_oea_masks with the resident flag at the 45 GB pool), 5 min: PASS
  all-row flips <= 1.34 / 5.42 / 3.69 and within +0.4 of qom_0_live_bq's 0.39 / 4.09 / 3.26 [K TRIED 101] on code and IFEval
  (prediction: +0.2-0.4 on code, +0.1-0.3 on chat). KILL: code > 1.34 or chat beyond the lines.
- If (a) and (b) pass, this is the 45 GB engine form to build (QOM's gate with "no resident clause on the >= 0.99 band"),
  not c3_b2d: same bytes as today, ~x0.7 tiles, one flag.

Also worth its 5 minutes, lower in the order: C3-R15 (the chat route + u8 at 147 slots; PASS: within +0.5 of 0.71 / 4.30 /
2.73 and under the lines; KILL: IFEval or multi over its line) for the 24 GB chat bytes line.

## 3. Cloud Fable 3's request list, audited (REQUESTS.md; "run" = as filed, "fix" = with the change named, "no" = do not spend GPU)

| request | verdict | why |
|---|---|---|
| C3-R11 := c3_b2d (map) | run (code decisive; chat control) | test 1; re-register chat as BETWEEN-expected (F3) |
| C3-R14 := c3_b2c (map) | run with R11 | the safe form: if b2d BETWEENs on code, b2c (x0.53 of exact, 0.16 % direct) is the fallback |
| the reach arm c3_b2d_reach07 (map) | fix: code only, after R11's read | F3; tau 0.5 form for chat does not exist as masks and would not change the chat verdict |
| C3-R8 (engine log, 1 line) | run first, it is free | decides F2's bracket; without it no tok/s claim for the tile lever is priced |
| C3-R10 REACH-CUT-X engine rule (Friday) | hold until R11 / reach PASS on code | its tok/s line (+5 %) is on the 22-27 ms term; also log the X rule's kept loss and false-accept count |
| C3-R15 / R15b (chat route + u8 / + reach 0.5, 147 slots) | run R15; R15b after it | #5; PASS lines as in section 2's last paragraph |
| C3-R12 c3_b2b_band5 | after R11, code only | BETWEEN-likely (1.03 % direct) |
| C3-R13 c3_b2b_top1 | after R11 | probe; k 1 unmeasured |
| C3-R17 c3_b2d_reach07_u7 | no | KILL-likely on chat by the oea_k8 arm (k 7 drops 3 ranks) |
| C3-R1, R2, R4, R5 (strict cf 0.5 / 0) | no (cloud3 agrees) | predicted KILL by its own section 16; F3 makes it worse |
| C3-R6 massB_0.5 (MoE-Spec budget) | low priority; (a) form is fine | a 5-min arm; the b16 family was BETWEEN at tighter budgets |
| C3-R7 scores export (13 MB) | yes if cheap (CPU) | needed only for mass-budget pricing; not on the path of tests 1-3 |
| C3-R9 | withdrawn by cloud3 (correct: the live masks already count realized rows only) | |
| paper requests (29 PDFs) | delivered (P1b) | no action |

## 4. Prior art, in one place (for MoonShots' full check)

- The three-band k table keyed on the DRAFTER's confidence, plus union members: adapted. PSR section 7 (arXiv 2610.34721:
  expert demand weighted by drafter confidence; the table is its discretization), AcceptMoE (2608.02989: commitment
  probability -> expert budget), OEA (2511.02237: the union step), LExI (2509.02753) / Yang et al. ACL Findings 2026 /
  HookMoE for per-layer k. Cloud3's own tag ("adapted, new as a table") is right; nothing is NEW by Mission 34's filter.
- REACH-CUT-X (end the check at the previous row when the first miss lands on a cheap row): the escalation idea of
  TriSpec-style proxy verification (NOVELTY.md line 47) applied inside one check; adapted.
- The split form (#4): a per-band resident clause on QOM; engineering on QOM (itself adapted from cache-conditional routing).
- The chat bytes lever: OEA k8 + REACH-CUT on QOM; engineering.
- Rule C: NEW as a span rule (NOVELTY.md: no paper relaxes acceptance only inside code comments); the inflation risk is
  published (arXiv 2610.23818, 2607.26627).
- FAR-HYBRID / the ~100-token horizon: adapted (MoonShots FAR_NOVELTY_CHECK: fMoE, MoE-SpAc, MoE-SpeQ, SeqMoE; tournament
  predictors); FAR's four measurements tagged new (measurement).
- GOAL lever 1: published (SP-MoE, MoE-SpeQ, DraftExpert, ProMoE, Pre-gated MoE, HOBBIT); GOAL lever 2: published family
  (AdapMoE, Lu et al. 2402.14800, CALM, Expert-Sample, HookMoE, LExI, PCoMoE); GOAL lever 3: published (SpecDec++, AdaEDL,
  FR-Spec, EAGLE-3).
- ZERO: TEAL (2408.14690) / CATS for in-expert sparsity (untried here on experts); loss-free balancing bias (2408.15664)
  as a cache-aware selection bias (the project's substitution KILLs apply); REAP (2510.13999, dead by rule).

## 5. The three context levels, compared (one paragraph)

Knowing nothing (ZERO) reproduced the project's own measurement programme (its T1-T6 are the decision map, cap45, KERNEL90's
bandwidth probes, the DFlash2 acceptance walks and FAR-WAIT) and most of the adopted stack (3-bit experts as a bytes lever,
gate-mass LFU, next-layer router prefetch, FR-Spec, GPU-driven stepping), but it priced the machine by DRAM bytes and so missed
the two facts that set this project's walls, that expert time is per group not per byte and that the drafter already keeps
10.5 of 16, which put its EXACT ceiling at 130-170 instead of the measured floor engine's 210-280; its three untried knobs are
two kills (selection bias, pruning) and one long shot (in-expert sparsity). Knowing the goals and the facts (GOAL) found the
right shape in one page, that at 45 GB the wall is tiles and bits buy nothing, that wasted rows are 40-85 % of rows and that
kept is capped, and then mispriced the pieces it could not see (dense 6 ms for a measured 32-36, an SSD wait twice its size,
latency where the law says bandwidth) and proposed as its bet a lever the project already has in flight. Knowing everything
(FULL) produced the one lever in this audit that is new, cheap and now measured (rule C: PASS MBPP, BETWEEN HumanEval+), killed
its own runner-up with a five-minute census, and priced the engine within the measured brackets; its error was multiplicative
optimism in its own halving. Knowing everything plus the data and compute (cloud3) did the most precise work of the night and
made the largest unverified claim, and its one unchecked assumption (k 8 free) sat beside a measured number it had cited as
its warrant: more context raised the quality of the questions and the precision of the arithmetic, not the probability of
checking the one load-bearing number; the value of the fresh levels was calibration (ZERO) and framing (GOAL's tiles, which
cloud3 then quantified), and every priced lever in the three fresh answers was either owned, killed, or cloud3's.

## 6. What this audit did not do, and the next step

Not done: a CPU replay of the split form (test 3a) and a per-row re-derivation of cloud3's band flip rates from
`floor_rows.json` (its section 12 reports a corrected join that matches p1 100 %; I accepted it). Both are 10-minute CPU jobs
on data on disk and would turn two [G] numbers in the table (#4's x0.66-0.72; F3's ~5 % per unsure row at k 8) into [P].
Next step for the orchestrator: order tests 1-3; the Friday-night map arm stays c3_b2d (then reach07 on code), not
c3_b2d_reach07 alone, with C3-R8's log and a corrected chat pre-registration.
