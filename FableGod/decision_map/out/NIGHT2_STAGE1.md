# Decision map, night 2 stage 1: can the middle layers' MoE output really be reused? (Breakthrough, Mon 2026-11-02 07:2x)

Ordered by NewIdeas (06:4x: stages, the speed answer first). The orchestrator's point, tested here as `chain`: night 1
copied the previous row's COMPUTED output, so every row's experts still ran. An engine that skips sure rows instead
chains back to the last row it computed, and code has long sure runs.

**Setup** as night 1: 36 teacher-forced windows, 10,316 answer positions, D-02a configuration, flip % vs the baseline
argmax by the 125B's own class (sure p1 >= 0.99 / tie p1 - p2 <= 0.1 / mid).
- Run: one quiet ticket, 06:53-07:18, attached. Gate 10316 / 10316 again.
- The new reuse code (`dm_common._reuse`) passed a CPU unit test before the model loaded (`test_reuse.py`).
- Row counts per layer were checked on every window; there were no misalignment warnings.
- The lag now carries across chunk calls. Night 1 restarted it at each call, so about one row per chunk boundary
  differs between the two nights.
- `chain`: rows whose baseline class is sure take the output of the last unflagged row (prompt rows and non-sure rows
  compute). The 125B's own class is the oracle. Sure runs (consecutive sure rows; the mean is the number of rows a
  chain spans):

| domain | answer rows skipped | runs | mean run | longest |
|---|---|---|---|---|
| code | 86.8 % | 213 | 13.7 rows | 398 |
| IFEval | 31.7 % | 573 | 1.9 rows | 16 |
| multi | 40.5 % | 793 | 1.8 rows | 15 |

## Results (flip %: sure / tie / mid; mean margin change in nats)

| run | code | IFEval | multi | dmargin |
|---|---|---|---|---|
| night 1: g1 (12-23) / g2 (24-35), lag 1, one group at a time | 0.14 / 0.10 sure | 0.09 / 0.00 sure | 0.00 / 0.00 sure | -0.41 / -0.69 |
| **12-35 at once, lag 1** | **1.03** / 66 / 33.0 | **1.77** / 67 / 39.8 | 0.69 / 71 / 29.7 | -1.59 |
| 12-35, lag 2 (copy from t-2) | 2.46 / 66 / 40.4 | 4.83 / 73 / 51.8 | 2.85 / 69 / 39.7 | -2.30 |
| 12-35, lag 4 (copy from t-4) | 4.76 / 74 / 50.5 | 10.04 / 80 / 60.0 | 5.28 / 78 / 50.5 | -3.11 |
| **12-35 chained (sure rows skip, reuse the last computed row)** | **8.11** / 48 / 21.8 | 1.67 / 44 / 10.0 | 0.69 / 45 / 8.6 | -1.89 |
| **edge 8-11, lag 1** | **0.00** / 46 / 4.3 | **0.00** / 46 / 5.8 | **0.00** / 43 / 4.2 | **-0.04** |
| edge 36-39, lag 1 | 0.82 / 62 / 16.0 | 1.67 / 56 / 19.9 | 2.43 / 59 / 21.4 | -0.77 |

In the chained run the sure column is the skipped rows; the tie / mid columns are computed rows, hit only through the
context.

Chained run, flip % on the skipped rows by staleness (rows since the last computed row; `stage1_extra.txt`):

| domain | 1 | 2-4 | 5-16 | 17-64 | 65+ |
|---|---|---|---|---|---|
| code | 1.41 (3/213) | 5.80 (17/293) | 10.26 (43/419) | 5.17 (35/677) | 10.53 (139/1320) |
| IFEval | 0.52 (3/573) | 2.96 (12/405) | 3.06 (3/98) | - | - |
| multi | 0.13 (1/793) | 1.22 (7/572) | 2.70 (2/74) | - | - |

## What it says

1. **The two middle groups compound.** Together, 12-35 flips 1.03 % of code-sure rows: about 4x the sum of the halves
   (0.24 %), and 1.77 % on IFEval-sure. The full band at once sits at the 1 % "open" line: BETWEEN, not free.
2. **Staleness kills it.**
   - Lag 2 is 2.4x lag 1 on code-sure, and lag 4 is 4.6x.
   - In the chained run, code's skipped rows flip 1.4 % at one row of staleness and 5.8 % at 2-4 rows.
3. **The engine pattern (chained) is dead on code.**
   - Code-sure flips 8.11 %, past the 5 % kill line, because code's sure runs are long (mean 13.7 rows).
   - On chat it holds (IFEval-sure 1.67 %, multi-sure 0.69 %), because its runs are about 2 rows long.
   - Computed rows suffer less than under lag 1 (code-mid 21.8 vs 33.0 %).
4. **The band is about 8-35.**
   - Layers 8-11 are free on their own: 0.00 % sure on all three domains, the smallest margin change of any MoE cut.
   - 36-39 already cost 0.8-2.4 % sure with only 4 layers.
   - Night 1's 0-11 damage (22.7 %) is therefore in layers 0-7.
5. **What survives:** reuse at most one row old. Sure rows skip only when the previous row computed, so at most every
   other sure row skips. Expected skip share: about half of the sure rows (code ~43 % of rows, chat ~15-20 %). Not
   exact.

## Stage 2a, proposed (~30-min ticket, wired: `dm_ablations.ablation`)

- `moe_reuse_chain1_L12_35` and `moe_reuse_chain1_L08_35`: the bounded scheme (every 2nd row of a sure run refreshes),
  on the stage-1 band and on the widened band.
- `moe_reuse_chain2_L08_35`: at most 2 rows stale (2 of 3 sure rows skip). This is the trade-off point.
- `moe_reuse_chain1_L08_35_topk2`: stacked with Q1's top-2 on every row.
- `moe_reuse_prev_L04_07` and `moe_reuse_prev_L00_03`: where the band's low edge is.

Caveats as night 1: an oracle class (not the drafter's), a 4-bit configuration, 12 windows per domain.
