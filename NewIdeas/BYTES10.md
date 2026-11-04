# BYTES10: from 62.4 to <= 10 MB of SSD reads per kept token (NewIdeas leads; started Tue 3 Nov 2026 23:5x)

> (a quote from the project owner, kept private)
maybe some research should also get dedicated to that as well".

**The line** (= WALL1_SCOREBOARD 'BROKEN' line 2): SSD MB per kept token <= 10, first at 24 GB, then at 12 GB, judged per
track (EXACT / FAST). [K] = BigMoE's W1B untraced means (S45's six prompts, CAP 256). Replays and map prices are [P] until
measured. At ~12.7 GB/s, 10 MB per kept token leaves >= 1,270 tok/s of disk headroom: RAM stops deciding the speed.

Marks: [K] measured (source named), [P] arithmetic or replay, [G] judgement. Rule: every screen's line is written
(QUEUE.md) before it runs; no 'impossible' verdicts.

## Who does what (the orchestrator 23:5x)
- NewIdeas: chief researcher and scoreboard keeper. Owns the 10x ledger (research/TEN_X_LEDGER.md) and the
  pre-registrations, and routes each factor to its owner once the ledger shows it is real.
- Breakthrough: FLOOR, the measuring instrument (the decision map at scale: quality of every byte-cutting rule).
- MTP Head: kept per check (the drafter side of the union curve).
- MoonShots: bytes per expert (precision on demand, entropy coding at 12 GB).
- BigMoE: builds what passes; owns the [K] rows (W1B).
- Fable C: mission C5 on Kamen's go (~/FableGod/push/MISSION_C5_BYTES10.md): the ledger audit, the floor, a ranked path,
  one genuinely new mechanism. It reads this file and the ledger.

## Scoreboard (one row per RAM line and track)

| line | track | today [K] | best priced [P] | the stack behind the best price | next step |
|---|---|---|---|---|---|
| 45 GB | EXACT | 62.4 (C 256, W1B); by day at C 160 169.4, 118 with the volatile tier 64 / 32 (W1B, BigMoE's night, Wed 03:07) | 60.4 / 38.1 / 33.2 replay (calibrated on 62.4 [K]); 11-bit x0.824 -> 49.8 / 31.4 / 27.4 | 11-bit scales; the volatile tier at C 160 (-30 % [K]) | M-27b conversion Thu |
| 45 GB | FAST | - | 2.8 / 2.8 / 2.9 (2.3 / 2.3 / 2.4 with 11-bit) | QOM cf 0 + 3-bit sure rows 13.5 / 19.3 / 20.2 -> gated bonus row 5.7 / 4.5 / 4.4 -> top-1 on sure rows | map: QOM cf 0 PASS (03:26); + 3-bit PASS on code / IFEval at cf 0, multi at cf 0.5 (03:54); screens 1-2 Wed 13:45 |
| 24 GB | EXACT | W1B 24 GB baseline Wed 13:45 (BigMoE) | 245.2 / 210.2 / 182.6 (LRU); OPT bound 116.9 / 93.9 / 83.5: no exact path to 10 (the answer's working set does not fit 147 slots) | 11-bit; fewer wasted rows (x0.79 code / x0.6 chat) | screen 3: the engine vs the replay |
| 24 GB | FAST | - | map-PASS today: code 35.7 (QOM cf 0 + gated last row + 3-bit); chat 84.4 / 81.7-93.7; BETWEEN on chat 47.3 / 34.4 (4-bit) or 19.4 / 13.9 (3-bit). On paper with every lever: **7.3 / 7.2 / 5.7 unhalved; ~25 / 33 / 32 halved** | QOM cf 0 + 3-bit 61.7 / 86.1 / 83.1 -> gated bonus row 30.8 / 20.0 / 14.2 -> top-1 on sure rows 16.8 / 11.8 / 7.9 -> rank-class pools 8.8 / 8.7 / 6.9 -> 11-bit | screens 1 (bonus row) and 2 (top-1) Wed 13:45; screen 3; the pool policy -> BigMoE |
| 12 GB | EXACT | - | 461-637 / 546-622 / 445-487 (LRU, by miss-count order); OPT 351 / 387 / 304 | - | - |
| 12 GB | FAST | - | 24.3 / 26.1 / 18.6 unhalved | the 24 GB stack at 51 + 32 slots | <= 10 needs 2-bit resident sure-row records or a 2-pass check whose first pass fits |

All [P] cells: research/TEN_X_LEDGER.md (Wed 03:4x). They replace Fable C's BYTES10.md levels, which a keep-mask bug made
2-4x too low (the ledger's section 1).

## The factor ledger (details and numbers: research/TEN_X_LEDGER.md; partial rows as they land)

| factor | owner | exact? | price so far (code / IFEval / multi) | status | overlaps with |
|---|---|---|---|---|---|
| kept per check (the drafter) | MTP Head | yes | EXACT: flat in kept (x0.91 from k 1 to k 16 at 24 GB, code); wasted rows cost +27 % (code) / +61-62 % (chat) at 24 GB; FAST: the bonus row is amortized, so kept matters there | ledger A (03:28) | the gated bonus row (the same rows) |
| cache size, policy, per-request locality | BigMoE (pools) | yes | 45 GB code: 40.3 of 60.4 is the per-request compulsory set; 24 / 12 GB are capacity (OPT x0.45-0.48 of LRU on EXACT) | ledger A / B, the fixed replay | the volatile tier |
| pool policy: rank-class pools (SLRU-like) / learned replacement | BigMoE | yes (policy only) | on the FAST top-1 + bonus stack at 24 GB x0.52 / x0.74 / x0.87 (OPT room x0.29 / x0.37 / x0.51 on the bonus stack); on EXACT x1.04 (worse) | replay only; screen 3 first | priced per rule, never carried across rules |
| QOM: drafter-sure rows skip the rank 2-9 experts that would miss | NewIdeas -> Breakthrough (map) -> BigMoE | no (cache-dependent; Kamen's decision 2 = YES) | as tested (bonus row exact), 45 GB: cf 0.5 -57 / -27 / -21 %, cf 0 -59 / -32 / -27 %; 24 GB cf 0 -65 / -49 / -47 %. My earlier capture price (-60.4 / -36.9 / -33.4 %; cf 0 -64.3 / -58.5 / -62.4 %) also gated the last row (ledger section 4) | map PASS at cf 0.9 / 0.5 / 0 (cf 0: 0.42 / 2.53 / 1.77 %, Wed 03:26); at C 160 pools (cf 0.5) PASS 0.59 / 3.47 / 2.65 % (03:58) | Q1, COLD, t3, the bonus gate: priced jointly |
| 3-bit sure rows (LSB-on-miss's bound) | Breakthrough (map) | no | with QOM cf 0, bonus row exact: 45 GB -78 / -49 / -39 %, 24 GB -74 / -58 / -54 % | map: cf 0.5 + 3b PASS 0.65 / 4.42 / 3.49 %; cf 0 + 3b PASS / PASS / BETWEEN 0.71 / 4.45 / 4.14 % (Wed 03:44 / 03:54; 3-bit cost z +2.5..+7.1) | QOM (same rows) |
| gated bonus row (Fable C, tag new): the check's last row gated like a drafted row | Breakthrough (map) / MTP Head (the 16th draft) | no | on QOM cf 0 + t3 at 24 GB x0.50 / x0.23 / x0.17 (all bonus rows) | screen 1, Wed 13:45 | u8, COLD (the same row) |
| top-1 on sure rows (+ union; OEA k1 / P1-OEA family) | Breakthrough (map) | no | after the bonus gate at 24 GB x0.55 / x0.59 / x0.56 | screen 2, Wed 13:45 | QOM (the same rows) |
| COLD: unsure rows drop cold ranks >= 4 (per-request table) | Breakthrough | no | superseded at cf 0 by the bonus gate (the only unsure row is the bonus row) | map GENERAL | the bonus gate |
| 11-bit scales + native layout (M-27b) | MoonShots / Leap / BigMoE | yes | x0.824 on every byte | conversion Thu, A/B Fri | M-01 (the same fields: never both) |
| M-01 12-bit scale fields | MoonShots | yes | -4.8 % | superseded by 11-bit | 11-bit |
| volatile tier (+7.8 GB of purgeable RAM) | BigMoE | yes | -30 % MB per kept token at C 160 [K] (169 -> 118) | measured (Wed 03:07) | the pool-size line |
| entropy coding (LOSSLESS45) | MoonShots | yes | -13.1 % of the store; BETWEEN (decode cost > read saved at 45 GB) | 12 GB question open | 11-bit |
| JOINT, keepalive, zero-copy, pickup, lever 2 forecasts | BigMoE / Fable A | yes | 0 bytes: they move exposure (BROKEN line 1), not this line | Wed lever-1 arms | - |

## Log (newest first)
- Wed 05:13: qom_0_live_bq_t3 PASS / BETWEEN / BETWEEN (0.77 / 6.09 / 5.29 %). Code has a map-PASS FAST stack at 35.7
  MB per kept token at 24 GB (x0.17 of EXACT); chat's map-PASS stacks are 84-100; its BETWEEN stacks 13.9-47.3 go to
  EvalSuite. Ledger section 0 item 7 holds the status table.
- Wed 05:0x: the gated bonus row in QOM's form (qom_0_live_bq): PASS on code (no cost), BETWEEN on chat (+1.6 / +1.5
  points; under Q1 at 0.99's level). 24 GB FAST start with 3-bit sure rows: 35.7 / 19.4 / 13.9 (engine convention) once
  qom_0_live_bq_t3 confirms (running). Screen 2 (top-1, union-only): BETWEEN / KILL / BETWEEN; its QOM form (2b) 13:45.
- Wed 04:4x: screen 1 (a), the gated bonus row in its union-only form: PASS on code (+0.24 points), BETWEEN on IFEval
  (+3.59), KILL on multi (+4.73). Code's 24 GB FAST start drops to 35.7 (from 54.5); chat stays at 84.4 / 81.7 until
  QOM's own form of the gate (resident keep on that row, no extra reads) is tested: qom_0_live_bq, pre-registered.
- Wed 04:0x: the map's QOM night is complete: cf 0 PASS; + 3-bit PASS at cf 0.5 (all three) and at cf 0 on code / IFEval
  (multi BETWEEN 4.14 %); at C 160 pools PASS. The last-row reconciliation (TEN_X_LEDGER sec 4): my decision-2 price =
  QOM + the gated last row (the engine convention, reproduced within 1-4 points); as tested on the map, QOM cf 0 is
  -59 / -32 / -27 % at 45 GB; screen 1 (a) decides the rest (24 GB FAST start 54.5 / 84.4 / 81.7 -> 35.7 / 19.4 / 13.9).
- Wed 03:4x: the ledger ran (research/TEN_X_LEDGER.md). Fable C's BYTES10 replay had a keep-mask bug (layers sliced
  instead of ranks: base reads on layers 0-9 only), so its levels were 2-4x low; the fixed copy and my replay agree and
  match W1B (60.4 vs 62.4 [K] at 45 GB). 24 GB FAST on paper 7.3 / 7.2 / 5.7 with five levers (three untested), EXACT has
  no path to 10 at 24 GB. My decision-2 price gated the last row (the map's arms do not): corrected in the ledger, sec 4.
- Tue 23:5x: track opened; this file; BROKEN line on WALL1_SCOREBOARD (2917b63); ledger script written (beb18d3), runs
  after BigMoE's quiet lock (04:28) beside FLOOR.
