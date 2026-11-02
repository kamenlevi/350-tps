# Decision map, night 1: what the 125B's argmax depends on (Breakthrough, Mon 2026-11-02 05:4x)

Runner: Breakthrough, for Fable's mission 9. Raw data: `*.json`; table: `report.md`; log: `runner.log`.
Wiring notes: `../dm_common.py` (WIRED block), `../dm_ablations.py`. Cross-check against TRIED: `TRIED_NOTES.md`.

**Setup.** 36 teacher-forced windows: 12 HumanEval, 12 IFEval and 12 multilingual, each the 125B's own greedy answer.
That gives 10,316 answer positions. The model ran in D-02a's configuration (C 51, 4-bit experts, exact prefill), and
every perturbation applied at every position of the window.

**Unit.** The percentage of positions whose argmax differs from the baseline, split by the 125B's own baseline class:
- sure: p1 >= 0.99
- tie: p1 - p2 <= 0.1
- mid: everything else

Sure is 86.8 % of code positions, 31.7 % of IFEval and 40.5 % of multilingual.

**Checks.**
- Gate: the baseline's top-1 equals D-02a's stored top-1 on 10,316 / 10,316 positions.
- topk10 through the MoE wrapper is bitwise equal to the baseline (0 flips, max |dlp| 0.0).

## Results (flip %: sure / tie / mid; mean margin change in nats)

| perturbation | code | IFEval | multi | dmargin | reading |
|---|---|---|---|---|---|
| **topk2** (Q1; kept experts keep the model's own weights) | **0.21** / 62 / 25.6 | 0.65 / 65 / 34.5 | 5.07 / 78 / 44.0 | -2.34 | **Q1 opens on code-sure** (≤ 1 %); not on mid rows; multi-sure at the 5 % kill line |
| topk2r (kept top-2 rescaled to the row's routed weight) | 2.33 / 74 / 43.2 | 5.58 / 75 / 50.6 | 20.9 / 82 / 59.6 | -2.97 | renorm is 11x worse on code-sure: **Q1 must not renormalise** |
| topk5 | 0.00 / 40 / 8.6 | 0.00 / 52 / 11.7 | 0.07 / 55 / 14.5 | -0.93 | sure rows untouched; mid rows 9-15 % |
| shared_zero | 0.68 / 66 / 30.5 | 3.35 / 71 / 44.8 | 7.44 / 73 / 41.9 | -0.62 | the shared expert matters (chat-like text most) |
| moe_reuse_prev_g0 (layers 0-11) | 22.7 / 88 / 67.3 | 38.0 / 87 / 73.1 | 42.5 / 88 / 69.1 | -3.79 | early MoE: no reuse |
| **moe_reuse_prev_g1 (12-23)** | **0.14** / 56 / 16.5 | **0.09** / 58 / 19.4 | **0.00** / 59 / 13.2 | -0.41 | **middle MoE on sure rows: previous position's output nearly free** |
| **moe_reuse_prev_g2 (24-35)** | **0.10** / 56 / 20.8 | **0.00** / 58 / 22.6 | **0.00** / 61 / 15.2 | -0.69 | same |
| moe_reuse_prev_g3 (36-47) | 18.9 / 82 / 63.7 | 36.3 / 78 / 60.1 | 69.6 / 91 / 79.0 | -3.55 | late MoE: no reuse |
| att_reuse_prev | 29.0 / 54 / 29.2 | 7.06 / 61 / 25.5 | 9.87 / 61 / 19.5 | -3.19 | attention: no reuse |
| gdn_reuse_prev | 88.5 / 100 / 96.7 | 95.8 / 98 / 98.5 | 98.9 / 100 / 98.8 | -4.45 | GDN: no reuse (the recurrence breaks) |
| hc_static (chunk-mean learned gates, normed streams) | 2.87 / 64 / 25.9 | 3.25 / 62 / 31.8 | 5.77 / 69 / 29.9 | -1.88 | the dynamic HC read decides tokens |
| hc_mean_raw (Fable's literal: raw mean of the 4 streams) | 100 / 100 / 100 | 100 | 100 | -5.38 | breaks the input scale (no norm): uninformative |
| hc_q4 (4-bit HC read OUTPUT, per row) | 0.00 / 44 / 9.1 | 0.00 / 56 / 12.2 | 0.00 / 59 / 11.5 | -0.65 | sure rows untouched |
| gdn_q4 (4-bit GDN output) | 0.00 / 40 / 3.8 | 0.00 / 45 / 6.0 | 0.07 / 54 / 9.0 | -0.28 | mostly tolerant |
| att_q4 (4-bit attention output) | 0.00 / 44 / 2.3 | 0.00 / 38 / 2.2 | 0.00 / 35 / 1.8 | -0.06 | the most tolerant part |

## What it says

1. **Sure rows absorb almost any single cut.**
   - These cuts leave 0.00-0.21 % of code-sure argmaxes changed: top-2 / top-5, the middle-layer MoE reuse, and 4-bit
     outputs of attention, GDN and HC.
   - The ties (40-60 % for every perturbation, even 4-bit attention) are coin flips.
   - The mid rows carry all the measurable damage.
   - So the class decides more than the part does, which supports Fable's NEW-1 confidence-banded check.
2. **Q1 is open on code with the model's own weights, closed with renormalisation.** Multilingual-sure is at 5 %:
   chat-like text needs a stricter band.
3. **New lead: the middle layers' routed-expert outputs (layers 12-35) can come from the previous position on sure rows
   (0.10-0.14 % code-sure, ~0 % IFEval / multi-sure), while early (0-11) and late (36-47) layers cannot (19-70 %).**
   - Not yet tested: both middle groups at once, and the effect on top of top-2.
   - In a verify check, "the previous position" is the previous row of the same check, so this would skip the routed
     experts of 24 layers on sure rows. Whether that pays depends on the gate, since those rows would post no ids there.
   - Night 2's per-layer map (moe_reuse_prev_L00-L47) should say where the band starts and ends.
4. **Dead as single cuts:** reusing GDN or attention outputs, static HC reads, and zeroing the shared expert on chat.

## Caveats

- Every position ran perturbed, so the context is perturbed too. That is harsher than any banded scheme, where unsure
  rows stay exact.
- The classes are the 125B's own, not the drafter's; a drafter-sure row that is 125B-mid flips at the mid rate. Q1's
  emulation measures that.
- 4-bit config (D-02a), not the 3-bit 45 GB tiers.
- 12 windows per domain.
- "q4" here quantises layer OUTPUTS per row (activations), not weights.
