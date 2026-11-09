# What 90 tok/s whole decode on code at 12 GB requires (pricing, Mon 9 Nov 2026 19:1x)

Target (Kamen, via the orchestrator, Mon 18:5x): 90 tok/s **whole decode** on **code**, lifetime peak <= 12 GB, gated
on the known benchmarks. This note prices the requirement from measured 12 GB runs; no new run was made for it.

## Inputs [K] (Fit12/data/paper/small_ram_12gb_rows.txt, by Fit12/scripts/paper_rows.py: "kept" = kept tokens per check,
"MB/token" = SSD MB per output token inside the decode phases)

| run | label | tok/s (pooled) | kept / check | MB / token | peak GB |
|---|---|---|---|---|---|
| ex16 | verified, 16 HumanEval | 18.47 | 10.08 | 439 | 11.144 |
| tab12e | verified, 12 HumanEval + 12 MBPP | 18.34 | 8.86 | 436 | 11.140 |
| tab12f | two-pass FAST theta 0.95 (failed its gate) | 27.90 | 7.74 | 203 | 11.280 |
| c1u16 | two-pass FAST theta 0.8 (failed its gate), 16 HumanEval | 44.34 | 9.57 | 117 | 11.245 |

Read cost [K]: 83.7 ms per GB read (SMALL_RAM section 7's fit of the 12 GB loop's calls, ~12 GB/s; chat, 1-4 rows).

## Per-check budget today [P from the rows]
check ms = kept / tok/s; GB per check = MB/token x kept; read ms = 83.7 x GB; non-read ms = the rest.

| run | check ms | GB read / check | read ms | non-read ms |
|---|---|---|---|---|
| ex16 (verified) | 546 | 4.43 | 370 | ~175 |
| tab12e (verified) | 483 | 3.86 | 323 | ~160 |
| tab12f (FAST 0.95) | 277 | 1.57 | 132 | ~146 |
| c1u16 (FAST 0.8) | 216 | 1.12 | 94 | ~122 |

The non-read part (16-row verify compute, Python, GPU handoffs, stalls) is 122-175 ms per check at 12 GB, against the
chat fit's 42-59 ms at 1-4 rows: code checks are 16 rows wide.

## What 90 needs [P]
At kept K per check, a check may take K / 90 s. With reads at 83.7 ms / GB, bytes per check B (GB) and non-read N (ms)
must satisfy N + 83.7 B <= 1000 K / 90.

| kept K | check budget ms | B max at N = 40 | N = 60 | N = 80 | N = 120 |
|---|---|---|---|---|---|
| 8 | 89 | 0.58 GB (73 MB/tok) | 0.35 (43) | 0.11 (13) | none |
| 10 | 111 | 0.85 GB (85 MB/tok) | 0.61 (61) | 0.37 (37) | none |
| 12 | 133 | 1.12 GB (93 MB/tok) | 0.88 (73) | 0.64 (53) | 0.16 (13) |
| 14 | 156 | 1.38 GB (99 MB/tok) | 1.14 (82) | 0.90 (64) | 0.42 (30) |

So, at today's kept (~10):
- **Exact cannot reach 90 at 12 GB** on this loop: it reads 4.4 GB per check (370 ms) before any compute. Even with
  N = 0 it would need <= 1.33 GB per check, a 3.3x cut in bytes with no loss.
- **Both terms must fall**: non-read time to ~40-60 ms per 16-row check (from 122-175 ms) AND bytes to ~60-85 MB per
  kept token (from 117 at the failed theta-0.8 point, 439 exact). Or kept per check must rise to 12-14.

## Levers to price next (sources to read before any run)
1. **Non-read time.** The 45 GB engine's chat check is ~40 ms at C 256 (BM:chs2 x2qm2: check 40.5, cycle 48.8 ms) and its
   code runs reach 164-181 tok/s. Running the 12 GB route in that engine (its kernels, fused checks, no per-layer Python)
   is the obvious way to 40-60 ms; the question is its footprint and miss handling at a ~12 GB pool (BigMoE's C-sweeps:
   C 160 is the ~32 GB line).
2. **Bytes.** Code needs <= 60-85 MB / kept token. Known cuts: the two-pass FAST family (117 at theta 0.8, gate FAILED);
   QOM on drafted rows (3-bit, cold sidecars skipped; the 45 GB code path uses it, gated); rank cuts on sure rows; pool
   shaping (BYTES10). The chat replay at 12 GB reached 75.7 MB / kept token with every lossy cut (SMALL_RAM 5.3); a code
   replay at 12 GB is missing (my replays are chat only): **first CPU task**.
3. **Kept per check.** Wider blocks raise kept but also bytes: the expert union grows about k^0.67 with rows (MAIN 12,
   union law), so 2x rows = 1.6x bytes per check; worth it only if kept rises > 1.6x.

Next: Fit12's per-call records for code (asked 19:0x), a code-window replay at 12 GB (CPU), then GPU screens via NewIdeas
after the 24 GB work.

## Code bytes at 12 GB pools [P, CPU replay] (Mon 19:2x; scripts/m1/code12_replay.py -> data/m1/code12_replay.out)
The decision map's 12 HumanEval windows, live-cut blocks (t 0.3: 9.65 rows, 7.91 kept per check), LRU pools of the 12 GB
line (C_m 51 base + C_l 32 sidecar slots per layer), bytes10_core's rules:

| rule | MB per kept token | GB per check | vs EXACT |
|---|---|---|---|
| EXACT | 636.8 (OPT 351.2) | 5.04 | 0 |
| Q1 0.5 (sure rows ranks 0-1) | 173.6 | 1.37 | -73 % |
| QOM0+ball (drafted rows and the last row skip non-resident ranks 2-9; the 45 GB code rule) | 101.8 (OPT 54.2) | 0.81 | -84 % |
| TOP8 | 499.3 | 3.95 | -22 % |
| Q1 0 t3 +bonus all (sure rows ranks 0-1 at 3 bits, every row) | 69.6 | 0.55 | -89 % |

Base-pool sweep (C_l scaled 32/51): EXACT 723 / 694 / 669 / 580 / 466 / 318 and QOM0+ball 155 / 133 / 117 / 88 / 76 / 58
MB per kept token at C_m 24 / 32 / 40 / 64 / 80 / 112.

Check against the engine [K]: Fit12's A' on 16 HumanEval reads 441 MB per kept token at kept 10.09 = 4.45 GB per check;
the replay's EXACT reads 5.04 GB per check (1.13x) at kept 7.91 (1.44x per kept token). Per check the replay is within
15 % of the engine; the per-kept gap is the map's shorter blocks.

Priced route to 90 [P]: one exact 16-row call per check (the 45 GB engine's batch-invariant check, non-read ~50 ms) plus a
QOM0+ball-class cut (~0.7-0.8 GB per check -> ~60-70 ms of reads) gives ~110-120 ms per check at kept ~10: about 85-90
tok/s. The Q1 0 t3 cut (0.55 GB) gives ~95-100 ms: about 100 tok/s. Both are lossy: QOM on code is certified at 45 GB (in
CERT), but at a 12 GB pool it skips far more experts, so it needs its own HumanEval+ / MBPP gate at 12 GB (map screen
first). Footprint: these pools are ~6.5 GB of expert records; Fit12's 12 GB route holds them at 11.1 GB, so a 12 GB port of
the 45 GB engine needs its non-expert part near ~4.5-5 GB (it is ~8 GB at 45 GB).

## The map's code line at the 12 GB pool [K, map arms; information only: known-benchmark gates decide] (Mon 19:4x;
data/m1/code12_quality.out, read-only from the decision map's existing arms)
Code line (VERDICT2): all-row flips <= 1.34 % and non-tie <= 0.87 % (3,366 code rows).

| arm | pool | code all-row [non-tie] | code verdict |
|---|---|---|---|
| qom_0_live (QOM cf 0, bonus row exact) | 45 GB | 0.42 % [0.06] | PASS |
| qom_0_live_ball (+ the last row gated) | 45 GB | 0.51 % [0.21] | PASS |
| qom_0_live_c51 | 51 slots (12 GB) | 1.16 % [0.54] | PASS |
| qom_0_live_ball_c51 | 51 slots (12 GB) | 1.40 % [0.93] | FAIL (just over) |

At 45 GB the 3-bit variants add ~0.3 points on code (qom_0_live_t3 0.71 % [0.21]); at 51 slots that would likely cross the
line. So the map-passing candidate at 12 GB is QOM0 with the bonus row exact: 1.29 GB per check (-74 % vs exact).

Priced with and without read / compute overlap [P]: QOM0's 1.29 GB is 92-108 ms of reads at 12-14 GB/s. If reads add to a
~50 ms compute (the 12 GB loop's fit has no overlap), a check is ~150-160 ms: ~63 tok/s at kept 10. If the 45 GB engine's
out-of-order loads hide the compute under the reads, a check is ~100-110 ms: ~90-100 tok/s. So the two measurements
that decide 90 are (1) whether the 45 GB engine fits Fit12's 12 GB pools (non-expert part <= ~5 GB) and (2) its overlap
at a 12 GB pool's miss rate (SSD queue depth near the drive's 12-14 GB/s).

## The 45 GB engine at 12 GB: not today (BigMoE, Mon 19:5x) [K, BM:data/f24k, data/c30]
- Its lifetime peak outside the expert pools is ~10.1-10.6 GB: F24k at C 100 peaked 23.7 GB with 13.19 GB of pools; C30 at
  C 160 peaked 31.8 GB with 21.21 GB. Of it: 5.6 GB non-pool weights after load (dense layers, embeddings / head,
  drafters, MTP head), ~2.8-3.0 GB of MLX arrays in decode, a 0.3-0.8 GB MLX buffer cache, ~1.1-1.3 GB outside MLX; the
  peak is set in prefill (MLX peak 22.3-22.8 GB in prefill vs 21.7 in decode).
- In its slot sizes (records3 index: MSB 2.064 MB, LSB 0.721 MB per expert, 48 layers) Fit12's 51 + 32 pools are
  6.16 GB, so the non-pool part must fall to ~5.5 GB: a ~5 GB diet, not built (candidates: the 4-bit DFlash2 drafter only,
  no or streamed MTP head on code, a capped MLX cache, a capped prefill transient, embeddings / head on SSD or at 4 bits).
- Its fast path needs rows x 10 <= base slots (or <= 92 ids): at 51 slots only 5-row checks fit, unless BigMoE's U3 rule
  (R57_GATEREQ, BM 742758e) is used: a 16-row check then carries <= 10 x unsure + 2 x sure <= 40 distinct ids. W24's arm
  w16u (Tue 00:30, at 120 slots) is its first run.

So the single-call route has two forms: (a) the 45 GB engine with a ~5 GB non-pool diet (BigMoE prices it after W24), or
(b) batch-invariant 16-row calls inside Fit12's 12 GB loop, which already holds the pools at 11.1 GB (non-pool ~4.6 GB):
the loop's <= 4-row exact calls exist because its kernels are not batch-invariant at wider widths; the 45 GB engine's
kernel set (KERNELS) is. Which is cheaper to build is the next question, for Fit12 and Leap.
