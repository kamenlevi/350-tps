# BYTES10 (Fable C, mission C5): from ~62 to <= 10 MB of SSD reads per kept token, at 24 GB then 12 GB

Wed 4 Nov 2026, 00:00-00:35 EET (draft complete 00:30 by the file clock; screen-1 masks 00:34). CPU only (one core at nice 15),
no GPU, no downloads; writes only in ~/FableGod/fablec/. Evidence: `bytes10_replay.py` -> `bytes10_replay.out` / `.json` (the
map's 36 windows, 140 s), `bytes10_bonus_masks.py` -> `masks/`. Inputs read: the C5
brief, NewIdeas' BYTES10.md and `scripts/ten_x_ledger.py` (the ledger itself had not run: it starts ~04:30), FLOOR night 1's
directory (no read-out yet; `FLOOR_read.txt` from Tue 06:55), TRIED/NOVELTY.md, Breakthrough's `COLD_read.txt` /
`COLD_lru.txt` / `dm_t3all_read.log`, NewIdeas' `QOM_read.txt` and `band45_capture_qom.txt`, WALL1_SCOREBOARD, SSD_WALL2,
MoonShots' FINDINGS and WED_1104_READY, my UNION_STACK.md. Marks: [K] measured (source), [P] arithmetic or replay on
recorded routing, [G] judgement. Gains are halved when deciding (the "halved" columns).

## 0. The answer in eight lines

1. **The 62.4 [K] at 45 GB is not a cache problem.** On the map's windows the 45 GB pool holds a request's working set: a
   warm session reads 18.7 MB per kept token EXACT (LRU) and the per-request compulsory set is 14.7 (decode only) or
   43.8 with the prefill's reads. W1B counts process bytes, prefill included, at the live kept of 5.9: 43.8 x 7.91 / 5.9
   = 59 [P] ~ 62.4 [K]. At 45 GB the SSD bytes are the model's per-request footprint divided by the tokens per request.
2. **At 24 and 12 GB the bytes are capacity misses** (the request's working set is 292 + 253 distinct experts per layer
   on code; the pools hold 147 / 51): EXACT 96 / 93 / 83 MB per kept token at 24 GB and 186 / 208 / 174 at 12 GB (code /
   IFEval / multi, LRU). Belady's bound (OPT) halves those; no demand policy I tried (popularity pinning, rank-class
   pools) takes more than 13 % of that gap.
3. **The ledger's factors that truly multiply: the record format (11-bit) and the drafter's wasted rows.** Kept per check
   does not multiply for EXACT: with a perfect drafter the bytes per token are flat from k 4 to k 16 (the stream's
   misses do not care how it is blocked). QOM / t3 / COLD / u8 / the two-pass check act on the same rows and must be
   replayed jointly, and QOM's cut is x0.18 at 45 GB but x0.34 at 24 GB and x0.30 at 12 GB: "-64 %" is a 45 GB number.
4. **FAST floor today's levers reach:** QOM cf 0 + 3-bit sure rows = 32.6 / 46.2 / 45.8 at 24 GB, 55.9 / 97.2 / 93.0 at
   12 GB [P]. Under 10 at 24 GB needs x0.3 more on code, x0.22 on chat.
5. **The new mechanism, THE GATED BONUS ROW:** a certainty-gated verify block has exactly one ungated row, the bonus row,
   and at cf 0 it holds 34 / 65 / 71 % of the block's expert pairs [K map]. Let the drafter propose one more token so the
   gate covers it: bytes x0.66 / x0.48 / x0.47 at 24 GB (21.5 / 22.3 / 21.3), x0.68 / x0.49 / x0.44 at 12 GB [P]. Web +
   NOVELTY check: nothing budgets the bonus position; the nearest art weights positions by reach (PSR section 7,
   AcceptMoE), not by a draft of the token. Tag: new.
6. **The ranked path to <= 10 at 24 GB** (code / chat; unhalved -> halved): gated bonus row -> 21.5 / 22 -> sure rows at
   top-1 + union -> 11.6 / 12.5 -> 11-bit scales -> **9.6 / 10.3** [P]; halved **19 / 24**. Then a learned replacement
   policy (OPT bound x0.5, realistic x0.8 [G]), fewer wasted rows and 2-bit sure-row records (x0.7) take the halved number
   to **13 / 17** (unhalved ~5).
7. **12 GB:** the same stack lands at 16.6 / 20.9 / 17.7 unhalved, ~24 halved; **<= 10 at 12 GB needs the resident set to
   hold the sure rows' top-2 working set** (115 / 85 / 80 experts per layer vs 51 slots): 2-bit resident records (x2.7
   slots) or top-1 routing on sure rows. EXACT at 12 GB is 90-120 at best [P]: physics at top-10 routing.
8. **Three screens for 13:45** (section 5): the gated bonus row on the map (two arms, ~5 min GPU each), sure rows at
   top-1 at live cuts (~5 min), and the W1B 24 GB baseline's calibration against this replay (CPU read-out).

## 1. The ledger audit: what multiplies, what overlaps

The 10x ledger (NewIdeas' BYTES10.md, `ten_x_ledger.py`) prices factors on their own and multiplies them per domain. My
replay uses the ledger's conventions (plain LRU per layer, prompt rows warm the pools, one session per domain carried
across the map's windows in walk order, live-cut blocks at t 0.3 with the p + 97 stand-in, the same three pool lines) plus
OPT, pinning, rank-class pools, the compulsory floors, a mixed-domain session, synthetic kept with the drafter's own cf, and
the bonus-row variants. All numbers below are [P] on the map's recorded routing unless marked.

| factor (ledger row) | multiplies? | evidence (code unless said; MB per kept token) | rule for the ledger |
|---|---|---|---|
| record format: 11-bit scales (-17.6 % [K MoonShots]), M-01 (-4.8 %), entropy coding (-13 %) | yes, bytes per miss | independent of routing and pools | one of 11-bit / M-01 (same fields); entropy after 11-bit is smaller than -13 % [G -5 %] |
| kept per check (the drafter) | **no for EXACT**; only through wasted rows and, for FAST, the bonus row | perfect drafter, w 0: 24 GB EXACT k 4 72.7, k 8 73.3, k 16 74.5; 45 GB 16.0-16.1; 12 GB 145-157 (flat). With 2 wasted rows per check: k 4 128.8, k 8 104.9, k 16 91.3. FAST Q1 0 t3 with the walk's cf: 24 GB k 4 38.7 -> k 16 25.6 (x0.66), all of it the bonus row's share | price the drafter as (wasted rows per check) x (bonus share), not as a union curve; today's live waste 1.74 rows per check (9.65 rows, 7.91 kept) |
| cache size / policy / locality | yes, but as the largest term at 24 / 12 GB, not a multiplier on the others | 45 GB LRU 18.7 vs compulsory per request 14.7 (prefill reuse): the pool holds the working set. 24 GB LRU 96.5 vs 14.7: 85 % capacity misses. OPT 49.3 (24 GB), 111.8 (12 GB). PIN (top C/2 by popularity) 93.5 / 165.5; RCP (rank-class pools) 103.1 / 162.3: <= 13 % of the OPT gap | the policy factor is <= x0.5 (OPT) and x0.87-1.0 for anything tried; learned replacement (FlashMoE, +51 % hit rate claimed [K paper]) is the only published route into that gap [G x0.8] |
| per-request locality: domain switches | no | MIX session (code, IFEval, multi interleaved, one pool): 45 GB EXACT 19.9 / 16.8 / 12.8 vs 18.7 / 15.4 / 12.6 single-domain; identical at 24 / 12 GB | the domain switch is not the cold-start cost; the per-request compulsory set is |
| per-request locality: the prefill's reads | the metric decides | compulsory per request: 14.7 / 18.4 / 22.2 with prefill reuse (decode bytes), 43.8 / 34.3 / 32.2 without (process bytes, W1B's definition: `WALL1_BENCH.md` line 32) | W1B's 62.4 ~ 43.8 x (7.91 / 5.9 kept) = 59 [P]: at 45 GB the line is a per-request footprint question, not a cache question |
| QOM (= Q1's reads) | jointly with the pool line | EXACT -> Q1 0 t3: 45 GB x0.18, 24 GB x0.34, 12 GB x0.30; cf 0.5 t3: x0.20 / x0.36 / x0.32. The cut shrinks as C falls because at 45 GB a sure row's rank 2-9 experts were hits anyway | never multiply a QOM ratio from one pool line onto another; the ledger's part C (per pool) is right |
| 3-bit sure rows (t3) | jointly with QOM; size set by the sidecar pool | Q1 0.5 -> Q1 0.5 t3: 45 GB 15.1 -> 3.8 (the LSB sidecar is 75 % of Q1's bytes at 45 GB), 24 GB 55.5 -> 34.4, 12 GB 86.0 -> 59.2 | a 45 GB lever first (x0.25), x0.62 / x0.69 at 24 / 12 GB |
| COLD (unsure rows drop cold ranks >= 4) | overlaps with cf 0 and with the bonus gate (same rows) | at cf 0.9: 42.9 vs u8 + t3 42.4 at 24 GB (Breakthrough's map: -14 % cached bytes at 45 GB [K]); at cf 0 the only unsure row is the bonus row: 31.6 vs 32.6 | a code lever until the bonus gate lands; then superseded |
| u8 on unsure rows | overlaps with the bonus gate | HYB 0 u8 t3 31.0 vs 32.6 (-5 %): the bonus row at 8 ranks | superseded by gating the bonus row (x0.66) |
| volatile tier (+7.8 GB purgeable) | it is the pool-size factor at 45 GB | not on the 24 / 12 GB lines (the line is the footprint) | keep it on the 45 GB row only |
| the 12 GB two-pass check (pass 1 top-1 + union, x0.465 reads [K Fit12]) | overlaps with QOM (same sure rows); its pass 2 adds reads back | my "Q1 0 k1 t3" is pass 1's reads without pass 2: 40.4 / 82.1 / 81.0 at 12 GB | price pass 1 + pass 2 jointly; QOM is its FAST twin |
| JOINT, keepalive, zero-copy, pickup, forecasts | 0 bytes | exposure, not this line | - |

Two calibration notes. (a) NewIdeas' earlier DAY9 capture replay (`band45_capture_qom.txt`: EXACT 47.0 / 31.1 / 30.7) matches
my per-request compulsory set without prefill reuse (43.8 / 34.3 / 32.2), i.e. a cold pool per window; the new ledger script
carries the pool across windows and warms it with the prompt, so its 45 GB EXACT row should land near 18.7 / 15.4 / 12.6, not
47. Both conventions are useful: the first is W1B's metric, the second the decode-time steady state. (b) The map's live cut
keeps 7.91 / 2.32 / 1.86 rows per check (code / IFEval / multi) against the engine's 5.9 on code [K cap45]: live bytes per kept
token are ~1.34x the replay's on code.

## 2. The floor: minimum SSD MB per kept token at 45 / 24 / 12 GB

Live-cut checks, LRU session (the ledger's convention) unless said; code / IFEval / multi. "Bonus" = the block's last row,
which today is always exact (10 ranks, both parts); "+bonus" = that row gated like a drafted row (section 4).

| line | track | rule | LRU | OPT (bound) | compulsory per request (decode / with prefill) | what binds |
|---|---|---|---|---|---|---|
| 45 GB | EXACT | all rows exact | 18.7 / 15.4 / 12.6 | 8.6 / 8.2 / 7.5 | 14.7 / 18.4 / 22.2 ; 43.8 / 34.3 / 32.2 | the per-request footprint (prompt 253 + answer 292 distinct experts per layer on code, of which 90 new) over ~280 answer tokens; the session floor is 2.7 / 4.2 / 4.4 |
| 45 GB | FAST | QOM cf 0 + t3 | 3.3 / 7.6 / 7.4 | 1.6 / 4.5 / 5.0 | 4.2 / 12.6 / 17.1 ; 20.5 / 26.1 / 26.2 | the bonus row and the LSB sidecar (C_l 89) |
| 45 GB | FAST | + gated bonus row | 0.5 / 0.8 / 0.9 | - | 1.2 / 2.7 / 3.6 ; 6.7 / 6.4 / 5.9 | prefill-time reads, if counted |
| 24 GB | EXACT | all rows exact | 96.5 / 92.8 / 82.5 | 49.3 / 43.3 / 38.7 | 14.7 / 18.4 / 22.2 | capacity: 147 slots vs a 292 + 253 working set per layer |
| 24 GB | FAST | QOM cf 0 + t3 | 32.6 / 46.2 / 45.8 | 15.8 / 21.2 / 21.7 | 4.2 / 12.6 / 17.1 | the bonus row (34 / 65 / 71 % of the block's pairs) and the top-2 working set (115 / 85 / 80 per layer) sharing 147 slots with the bonus rows' tails |
| 24 GB | FAST | + gated bonus row (next-draft proxy) | 21.5 / 22.3 / 21.3 | 11.4 / 10.1 / 9.9 | 1.2 / 2.7 / 3.6 | the top-2 working set's re-reads |
| 24 GB | FAST | + sure rows at top-1 (bound: every bonus row gated) | 11.6 / 12.5 / 11.7 | - (PIN 11.8 / 11.8 / 11.2) | 0.4 / 0.9 / 1.6 | the top-1 working set |
| 12 GB | EXACT | all rows exact | 185.6 / 207.6 / 173.6 | 111.8 / 133.2 / 112.5 | 14.7 / 18.4 / 22.2 | 51 slots vs 292 per layer: every check re-reads most of its union |
| 12 GB | EXACT | ranks 0-1 at 3 bits everywhere (T3ALL, a new reference; map: code +0.59 points = BETWEEN, chat +4-5 [K]) | 148.3 / 150.9 / 131.1 | 86.2 / 93.1 / 82.0 | 7.4 / 10.3 / 14.1 | as above, 62 slots |
| 12 GB | FAST | QOM cf 0 + t3 | 55.9 / 97.2 / 93.0 | 34.2 / 60.6 / 58.0 | 4.2 / 12.6 / 17.1 | the top-2 working set (115 / 85 / 80) vs 51 slots |
| 12 GB | FAST | + gated bonus row | 38.0 / 47.8 / 41.1 | 24.7 / 33.4 / 28.9 | 1.2 / 2.7 / 3.6 | same |
| 12 GB | FAST | + sure rows at top-1 (bound) | 20.1 / 25.4 / 21.5 | - (PIN 17.8 / 23.7 / 21.1) | 0.4 / 0.9 / 1.6 | the top-1 working set vs 51 slots |

Covering the brief's four items:
- **Per-request working sets** [K map, means over windows]: prompt 253 / 154 / 96 distinct experts per layer (code / IFEval /
  multi); answer 292 / 207 / 219 at ranks 0-9, 115 / 85 / 80 at ranks 0-1; answer experts the prompt never routed 90 / 107 /
  150 (18 / 33 / 44 at ranks 0-1); answer length 280 / 283 / 296 tokens. At 4 bits a code request's answer set is 292 x 48 x
  2.93 MB = 41 GB: it fits the 45 GB pool and nothing smaller.
- **Union growth with rows** [K map, EXACT, no cache]: distinct experts per layer for blocks of 1 / 2 / 4 / 8 / 16 / 32 / 64
  rows: code 10 / 17 / 29 / 47 / 75 / 111 / 158 (singletons 100 / 72 / 52 / 38 / 26 / 16 / 9 % of the block's pairs); IFEval
  10 / 16 / 27 / 44 / 69 / 102 / 140; multi 10 / 15 / 24 / 38 / 59 / 89 / 125. A 16-row block's union (75) is half the 24 GB
  pool and 1.5x the 12 GB pool: at 12 GB a block cannot even hold its own union, so cross-check reuse is what the LRU rows show.
- **Drafter acceptance**: the live cut keeps 7.91 / 2.32 / 1.86 of 9.65 / 3.68 / 2.96 rows per check; the wasted rows cost
  x1.2-1.8 at k 4 and x1.1-1.2 at k 16 (section 1); the cf 0 case treats every drafted row as sure, so QOM cf 0's quality
  (map ~05:00) is what makes these FAST rows real.
- **Record sizes**: MSB-3 part 2,162,688 B, LSB-1 sidecar 770,048 B (records3); 3-bit sure rows read the MSB only; 11-bit scales
  x0.824 on every byte [K MoonShots]; a 2-bit MSB plane would be ~1.44 MB per miss [P], the 4222222222 plan -41..-52 % of bytes
  [K MoonShots, quality open].

## 3. The ranked path to <= 10 MB per kept token

Start: QOM cf 0 + 3-bit sure rows (tonight's FAST lead; cf 0's map result ~05:00, the 3-bit bound pre-registered). Gains are
the replay's ratios on that stack; "halved" halves each lever's gain. Odds [G] are for the lever passing its quality line
in its domain. Costs name the owner.

### 24 GB (code / chat start 32.6 / ~46)

| # | lever | gain (replay) | halved | odds | cost | exact? | novelty |
|---|---|---|---|---|---|---|---|
| 1 | **gated bonus row** (section 4): the drafter proposes the bonus token too; the bonus row keeps ranks 0-1 + the block's union when that draft is sure | x0.66 / x0.48 / x0.47 -> 21.5 / 22.3 / 21.3 | x0.83 / x0.74 -> 27 / 34 | 50 % code, 35 % chat (the bonus row's flips are an unsure-row's at cf 0; at cf 0.9 the gain is x0.92 / x0.95: the next-draft proxy clears 0.9 rarely) | MTP Head: does DFlash2 already emit a 16th draft with a cf? else a walk with m + 1 drafts (~30 min GPU); Breakthrough: one map arm (5 min); BigMoE: compare the bonus row's output with the extra draft | FAST | **new**; position weighting by reach is published (PSR s7, AcceptMoE) |
| 2 | **sure rows at top-1 + union** (the oea_k1 / P1-OEA pass-1 family) | x0.74 / x0.87 / x0.87 alone; with 1: 11.6 / 12.5 / 11.7 (x0.55 / x0.58 / x0.56) | x0.77 / x0.79 -> 21 / 27 | 45 % code, 30 % chat (top-1 on sure rows: P1-OEA's certificate passes on code at x0.465 pass-1 reads [K]) | Breakthrough: masks + map arm (5 min GPU) | FAST | adapted (OEA k1, P1-OEA) |
| 3 | **11-bit scales + native layout (M-27b)** | x0.824 -> 9.6 / 10.3 (with 1 + 2) | x0.91 -> 19 / 24 | 85 % (bitwise) | MoonShots / Leap / BigMoE: conversion Thu (a 63 GB copy: the disk call), A/B Fri | EXACT | published practice |
| 4 | **learned / forecast-aware replacement** | OPT bound x0.48-0.53 (24 GB); PIN x0.97, rank-class x1.0 (KILL); realistic x0.8 [G] | x0.9 -> 17 / 22 | 30 % | BigMoE: a loader policy + a capture to fit it (FlashMoE-style); CPU replay first on the 24 GB trace (screen 3) | EXACT | published (FlashMoE, DALI, SMoE score eviction) |
| 5 | **fewer wasted rows** (the drafter: D98, Test-Time Speculation) | 2 -> 0 wasted rows per check: x0.85-0.9 on EXACT, less on the FAST stack | x0.93 -> 16 / 20 | MTP Head's program | - | EXACT | published (drafter quality) |
| 6 | **2-bit records on sure rows** (t2: a records4 MSB-2 plane served to drafter-sure rows) | x0.67 per sure-row miss -> x0.7 on this stack | x0.85 -> 13 / 17 | 30 % (sure rows at 3 bits cost 0.00 % on sure rows [K map]; 2 bits unmeasured) | MoonShots: records4 (prototype exists); Breakthrough: a t2 map arm; BigMoE: a third pool | FAST | new signal (the drafter's certainty) on a published mechanism (mixed precision by rank, 2512.17073; SliceMoE) |
| 7 | COLD / the prompt footprint on the bonus row | x0.97 at cf 0 (superseded by 1); -14 % cached bytes vs u8 + t3 at cf 0.9 [K map] | - | - | built (Breakthrough) | FAST | new signal on a published mechanism |
| 8 | entropy coding (LOSSLESS45) | x0.87 of the store [K]; decode cost KILL at 45 GB; after 11-bit ~x0.95 [G] | x0.97 | 20 % | MoonShots | EXACT | published |

Product at 24 GB on code: unhalved 32.6 -> 21.5 (1) -> 11.6 (2) -> 9.6 (3) -> 7.7 (4) -> 7 (5) -> 4.9 (6); **halved 32.6 -> 27 ->
21 -> 19 -> 17 -> 16 -> 13.** Chat: unhalved 46 -> 22 -> 12.5 -> 10.3 -> 8.2 -> 7.6 -> 5.3; **halved 46 -> 34 -> 27 -> 24 -> 22 -> 20 ->
17.** The decision-grade reading: levers 1-3 bring 24 GB to the line at face value and to ~19-24 halved; 10 halved needs 4 + 6.

EXACT at 24 GB: 96.5 -> 11-bit 79.5 -> no waste 72 -> policy x0.8 57 -> ranks 0-1 at 3 bits as a new reference x0.8 46 -> entropy
x0.95 44 [P, unhalved]: **~45-60 is the EXACT 24 GB floor with every exact lever; 10 needs the request's working set (41 GB at
4 bits) to fit, which it cannot at 24 GB.** Next step: screen 3 (is the engine's 24 GB number LRU-like or OPT-like?), then
11-bit; the disk headroom at 45-60 MB per kept token is still ~210-280 tok/s.

### 12 GB (start 55.9 / 97.2 / 93.0; T3ALL pools: 62 base slots, no sidecar)

| # | lever | gain | halved | note |
|---|---|---|---|---|
| 1 | gated bonus row | x0.68 / x0.49 / x0.44 -> 38.0 / 47.8 / 41.1 | x0.84 / x0.75 | as at 24 GB |
| 2 | sure rows at top-1 (bound with 1) | 20.1 / 25.4 / 21.5 (x0.53 / x0.53 / x0.52) | x0.76 | the top-1 working set is the first that approaches 51 slots |
| 3 | 11-bit | 16.6 / 20.9 / 17.7 | x0.91 | |
| 4 | no sidecar: ranks 0-1 at 3 bits on every row (T3ALL) -> 62 base slots | x0.89 (49.7 vs 55.9 on the QOM stack) | x0.95 | BETWEEN on code (+0.59 points), KILL-grade on chat (+4-5) [K map]: code only, or 4 bits on unsure rows only |
| 5 | **2-bit resident records for sure rows** | x0.7 on the stack's bytes, and x2.7 slots for the sure rows' working set (115 -> fits in ~135 at 2 bits [P]) | x0.85 | the one lever that changes what binds at 12 GB |
| 6 | learned replacement | OPT x0.60-0.65 at 12 GB; realistic x0.8 [G] | x0.9 | |

Product on code: unhalved 55.9 -> 38 -> 20 -> 16.6 -> 14.8 -> 10.4 -> 8.3; **halved 55.9 -> 47 -> 36 -> 32 -> 31 -> 26 -> 24.**
Chat halved ~30. **At 12 GB, <= 10 is reachable only when the resident set holds the sure rows' working set:** today 115 / 85
/ 80 top-2 experts per layer against 51 slots; 2-bit resident copies (lever 5) or top-1 routing on sure rows (lever 2) are the
two ways, and both are FAST. EXACT at 12 GB: 186 -> T3ALL 148 -> 11-bit 122 -> policy 98 -> no waste 88 [P]: **~90-120**, a
floor set by top-10 routing over 512 experts with 10 % of them resident; the disk headroom there is ~105-140 tok/s, which is
the roadmap's 120-150 at <= 12 GB only if the SSD is fully hidden (SSD_WALL2's designs 1-2).

### 45 GB (for completeness)

Decode-time EXACT in a session is 18.7 / 15.4 / 12.6 (LRU) with a floor of 14.7 / 18.4 / 22.2 (compulsory per request); 11-bit
and fewer wasted rows take it to ~14 / 14 / 12 [P]: **the line is met EXACT at 45 GB on decode bytes to within ~1.4x, and the
remaining bytes are the per-request footprint.** On W1B's process-bytes metric (prefill included, live kept 5.9) the same
floor is ~44-59: no cache lever moves it; longer requests, the FAST footprint (QOM cf 0 + t3 3.3 / 7.6 / 7.4; + the bonus gate
0.5 / 0.8 / 0.9) and a session's hot set (2.7 / 4.2 / 4.4) do. The metric's definition (decode vs process bytes) is a call for
> (a quote from the project owner, kept private)

## 4. The new mechanism: the gated bonus row (and two tested policies that fail)

**Observation [K map].** In every certainty-gated verify block one row is never gated: the bonus row, whose output token has
no draft to compare with, so every union arm (Q1-UNION, OEA hybrids, QOM, REACH-CUT, COLD) keeps it at all 10 ranks and both
precision parts. With the live cut at t 0.3 every segment ends in one. At cf 0 (QOM's every-drafted-row-sure case) the bonus
row is 1 of 9.65 rows on code but 34 % of the block's expert pairs; on IFEval 65 %, on multi 71 % (3.68 / 2.96 rows per
check). After QOM + t3 the bonus row is the largest single consumer of SSD bytes on chat and a third of them on code.

**Mechanism.** The drafter proposes m + 1 tokens instead of m (DFlash2 drafts a block in one pass; MTP Head can say whether
the 16th draft and its cf already exist). The verify block keeps m + 1 rows as today; the last row's output is compared with
the extra draft and the row is gated by that draft's certainty exactly like a drafted row: ranks 0-1 + the block's union
members when sure, all 10 when not (+ 3-bit when the stack says so, + QOM's resident keep). Accepted: the token is the draft
(right with probability ~cf, as for any sure row). Rejected: the row's gated argmax is the correction, as at any first miss.
The row is still computed, so the drafter's next state is unchanged; nothing runs one token behind. In EXACT mode nothing
changes (every row exact). Token count per block is unchanged.

**Price [P, section 2]:** on the QOM cf 0 + t3 stack, 24 GB 32.6 / 46.2 / 45.8 -> 21.5 / 22.3 / 21.3 with the next segment's
first draft as the cf proxy (-> 21.2 / 21.5 / 20.9 if every bonus row is sure); 12 GB 55.9 / 97.2 / 93.0 -> 38.0 / 47.8 /
41.1; 45 GB 3.3 / 7.6 / 7.4 -> 0.5 / 0.8 / 0.9. At cf 0.9 the proxy clears the gate on few bonus rows (x0.92 / x0.95): the
gain lives at the cf the FAST mode adopts (QOM's candidate is cf 0.5 pending cf 0).

**Quality prior [G]:** a gated bonus row is a drafted row with one more draft, so its flips are the gate's flips at that cf:
sure rows at cf >= 0.999 flip 0.00 % (FLOOR gate_bands [K]); at cf 0 the row behaves like QOM cf 0's rows (map ~05:00). The
only new failure mode: the extra draft is one position deeper (position 16 vs 15), where DFlash2's cf is lowest; the
walk's cf at position 15 is the proxy to read.

**Prior art (NOVELTY.md + web, Wed 00:2x).** No paper found budgets the bonus position's experts or gates it by a draft: the
MoE + speculative decoding systems (DraftExpert 2607.24434, MoE-Spec 2602.16052, SP-MoE 2510.10302, MoE-SpeQ 2511.14102,
SpecMoEOff 2508.21706) budget or prefetch per block and leave the last position as is. The nearest art weights each
position's expert demand by the probability the block reaches it (PSR 2610.34721 s7 with the drafter's running confidence;
AcceptMoE 2608.02989 with offline commitment rates), which also touches the last position, but by reach, with a reroute,
and never by a draft of the token itself; PEARL (2408.11850) drafts ahead for latency, not for gating. Tag: **new** (the
signal and the cut); if a reviewer reads PSR s7 as covering it, the fallback tag is "new signal on a published mechanism".

**In a paper:** (1) the bonus-row share of a gated block's expert pairs on the three domains (section 2, D); (2) SSD MB per kept
token at 24 / 12 GB with and without the gate on the same replay (section 2); (3) teacher-forced flips of the gated bonus row at
cf 0.9 / 0.5 / 0 on the decision map, paired McNemar against the same stack without the gate; (4) EvalSuite same-scores under
two prompt orders in BigMoE's engine; (5) W1B's MB per kept token and tok/s at 24 GB, A/B. The claim: "a certainty-gated
verify block has exactly one ungated row; drafting one token further removes it, halving the SSD bytes of chat checks."

**Two policies tested and killed here [P]:** popularity pinning (the top C/2 experts of each layer by the domain's
leave-one-window-out popularity pinned, LRU for the rest): x0.97 at 24 GB, x0.89 at 12 GB on EXACT; rank-class pools
(experts last needed at ranks 0-1 in 70 % of the slots, the exact rows' tails in 30 %, promotion on a rank 0-1 need): x1.07 at
24 GB, x0.87 at 12 GB, worse at 45 GB. The OPT gap (x0.5) is not the bonus rows' tails flushing the working set; it is the
working set itself not fitting, which only the future knows how to schedule. Tag: adapted (SMoE's score-based eviction,
2508.18983, is the published form); KILL as a lever. This is consistent with MoonShots' closed cache-policy line.

## 5. Three pre-registered screens for Wed 13:45 (each <= 10 min of GPU; lines written now, before any run)

**Screen 1: the gated bonus row on the map (FAST).** Masks: the existing arm's masks with the bonus row of every live segment
set to ranks 0-1 + the block's union members at that layer when the next segment's first draft cf >= theta (the proxy; a walk
with m + 1 drafts replaces it when MTP Head has one). Two arms, ~5 min GPU each in Breakthrough's harness (`PERT.update(rmask=
<abs>, renorm=False)`): (a) `qom_0_live_bonus` = qom_0_live's reads with every drafted bonus row gated (the price x0.66 / x0.48
/ x0.47); (b) `q1u_0.9_live_bonus` = q1u_0.9_live with the bonus row gated at 0.9. Lines, per domain: all-row flips <= the
same arm without the gate + 0.3 points AND <= Q1 at 0.99's level (1.34 / 5.42 / 3.69 %) = PASS; <= 1.5x that level =
BETWEEN; above = KILL; paired McNemar vs the ungated arm. Prediction [G]: (a) PASS on code (QOM cf 0's own result + 0.1-0.3
points), BETWEEN on chat; (b) PASS everywhere it already passes (few bonus rows clear 0.9). **Masks are built** (`bytes10_bonus_masks.py`,
Wed 00:34, from NewIdeas' live arms; 36 windows each, 1,368 real bonus rows = 13 % of the 10,316 answer rows):
`~/FableGod/fablec/masks/qom_0_live_bonus` (every bonus row gated: their (row, layer, rank) pairs x0.48),
`.../qom_0.5_live_bonus5` (922 gated by the proxy cf >= 0.5, x0.50 on those) and `.../q1u_0.9_live_bonus9` (453 gated at 0.9,
x0.54). The gated bonus row keeps ranks 0-1 + the block's union members; QOM's resident keep is not reproduced on that row,
so on the qom arms the masks drop more than the engine would: a PASS is conservative. Run order: (a) after qom_0_live's own
result is read, (c) qom_0.5_live_bonus5 beside the adopted cf 0.5, (b) last.

**Screen 2: sure rows at top-1 + union at live cuts (FAST; `hyb_0.9_k1_live_t3`).** Sure rows (cf >= 0.9) keep rank 0 + the
block's union members, 3-bit on that rank; unsure rows and the bonus row exact. Price [P]: 24 GB x0.74 on code vs top-2 at the
same gate (24.1 vs 32.6 at cf 0), 12 GB x0.72. Lines: all-row flips <= Q1 at 0.99's level = PASS; <= 1.5x = BETWEEN; paired
McNemar vs q1u_cf09_t3 (the top-2 twin). Prediction [G]: BETWEEN on code (+0.3-0.6 points over top-2), KILL on chat. ~5 min
GPU (NewIdeas' dm_oea_masks parse() takes `hyb_<thr>_u<k>`; the k1 form needs ks 1, a two-line change in the builder, or my
builder's rule table).

**Screen 3: the W1B 24 GB baseline against this replay (CPU read-out of BigMoE's 13:45 run, no extra GPU).** From the traced arm,
split the process SSD bytes into prefill and decode, and compute decode MB per kept token on the six prompts. Lines: decode MB
per kept token within 0.8-1.25x of this replay's LRU rows scaled by kept (96.5 x 7.91 / kept_live on code) = the ledger's
convention is calibrated at 24 GB and the section 3 prices stand; below 0.8x = the engine's LRU + popularity beats plain LRU
and the policy lever (section 3, #4) is partly already cashed (re-price); above 1.25x = the engine reads more than its unions
(prefetch waste or the K-73 phases) and that is the first byte lever at 24 GB. Prediction [G]: 0.9-1.1x.

Not screens (they need builds first): 11-bit (Thu), 2-bit sure-row records (records4 + a t2 arm), the learned policy.

## 6. Caveats

- One capture: the map's 36 windows (12 per domain, ~280 answer tokens each, HumanEval / IFEval / multilingual prompts). Code
  is one task family; the per-request footprints of agent turns with long prompts are larger (prompt 253 of 512 already).
- The replay's live cut keeps 7.91 rows per code check vs the engine's 5.9 [K cap45]: multiply code numbers by ~1.34 for
  today's engine; chat kept matches the engine's 3-4 rows.
- Plain LRU, prefill warm-up, one session per domain: the engine's LRU + popularity reads 1.05-1.25x fewer base misses
  (NewIdeas' QOM note) and the mixed protocol +5 %; prefill reads are outside the decode numbers and inside W1B's.
- The bonus-row gate's cf is a proxy (the next segment's first draft); its quality is unmeasured until screen 1 runs, and the
  mechanism needs the drafter's extra draft in the engine.
- Halving is per lever; the halved products in section 3 are products of halved factors, which is harsher than halving the
  product. Decide on the halved column.
- Nothing here is GPU-timed; bytes only. Exposure (the other BROKEN line) is Fable A's and BigMoE's.

Sources (web pass, Wed 00:2x): DraftExpert https://arxiv.org/abs/2607.24434 ; MoE-Spec https://www.arxiv.org/pdf/2602.16052 ;
SP-MoE https://arxiv.org/abs/2510.10302 ; MoE-SpeQ https://arxiv.org/abs/2511.14102 ; SpecMoEOff https://arxiv.org/html/2508.21706v2 ;
HOBBIT https://arxiv.org/abs/2411.01433 ; FlashMoE https://arxiv.org/html/2601.17063v1 ; DALI https://arxiv.org/html/2602.03495v1 ;
SMoE https://arxiv.org/pdf/2508.18983 ; local routing consistency https://arxiv.org/html/2505.16056v3 ; PSR, AcceptMoE, PEARL as
in TRIED/NOVELTY.md.
