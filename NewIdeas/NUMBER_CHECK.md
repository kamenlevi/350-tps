# NUMBER CHECK ledger (NewIdeas; brief ~/Papers/BRIEF.md: every headline in every paper re-derived from raw rows by Tue 12:00)

Method: for each headline I open the raw rows (runs.json / requests.jsonl / decode.jsonl), recompute the number with a script
in scripts/numcheck/ (or a named earlier script), and mark it here: OK (same to the shown digits), DIFF (what the rows say), or
SOURCE? (no raw rows found). Marks follow the brief: [K] measured, [P] priced, [G] judgement. A paper's number is OK only if
its raw source is named and its mode label (exact to what / lossy gated on what / lossy ungated) matches the run's env.

## 0. Inputs the papers will quote (checked before the drafts exist)

### 0a. findings/2026-11-08_1630_strata-head-to-head.md (the brief's rule 4 cites it for the abstracts)
Ours (12 IFEval = chat, N45 keys, C 256, one pass per arm, quiet), from BigMoE's CHS reports:
| note says | source row | check |
|---|---|---|
| chat lossy certified 44.2 | CHS4 y0 43.8 + y0b 44.5 (L, QOM on code sets only = the CERT config on chat); mean 44.15 | OK as the mean of two passes; the paper must say "mean of 2 passes" |
| chat exact 38.3 | CHS4 yes1 38.3 (E + SB1; SB1 bit-exact: 676 / 676 logits hashes, CHS5) | OK; label "exact to NAX6-N AR (E + SB1)" |
| M1-B + COH 49.9 | CHS5 z0b 49.9 (second pass; z0 49.7) | OK; IFEval gate PASS both orders (RESULT_chat_m1b 70b5cf8), card gates pending |
| stack 56.0 | CHS5 zsgcr 56.0 (56.05 by my runs.json read) | OK; lossy UNGATED |
| 32 GB lossy 51.3 at 31.2 GB, exact 33.8 at 30.6 GB | BigMoE c32 runs.json: 51.33 / 33.81, footprint 31.22 / 30.62 GB (NewIdeas 16:3x) | OK |
| 32 GB first token ~2.9 s, whole request 22.5 / 19.8 | c32 runs.json: TTFT mean 3.09 (zs) / 2.93 (E); e2e 22.52 / 19.82 | OK (the note's "~2.9 s" is E's mean; zs is 3.09) |
| whole request chat 24.4 (M1-B + COH) | [[to run: CHS5 z0 / z0b runs.json e2e]] | pending |
| our chat first token median 2.92 s (2.34-3.81), "1.7 s + 22 ms per prompt token" | [[to run: CHS5 z0 runs.json pfs + P]] | pending |
| break-even ~530 answer tokens | derived; [[to recompute from the two lines]] | pending |
| Strata side (all arms, both caches, all sets) | scripts/numcheck/strata_h2h.py (written 16:5x; runs after the orchestrator's quiet window) | pending |

Already re-derived today by NewIdeas (Strata, IFEval pooled decode): A1 28.0, A2 25.6, B1 37.4, B2 37.1, C1 25.5, C2 25.3,
D1 36.1, D2 35.6 (default cache); B 41.8, D 40.6 (full cache, peaks 40.76 / 41.15 GB). Matches REPORT.md's pooled column.

### 0a-2. RESULT (scripts/numcheck/ours_runs.py + strata_h2h.py, run after 17:13; outputs transcribed below)
FINDING 1 (affects every paper): the older c45-runner reports (S5', E5, N45: data/s5p/s5p_report.txt, data/e5/e5_report.txt,
data/n45/n45_report.txt) print WHOLE DECODE as the GEOMETRIC MEAN over prompts per pass (reproduced exactly: spb1 168.6,
spb2 179.6, spx1 181.7, spx2 180.9, spmb1 118.3, spmb2 121.9, nie1 39.9, nie2 39.8, nil1 45.2, nil2 44.8), not pooled.
STYLE.md section 3 requires pooled headlines ("geo" only when labelled). Their END TO END column is a third definition
(below both the pooled whole request and the mean of per-prompt rates). The CHS / C32 reports print pooled first: those
match. Pooled triples, passes pooled (whole decode / whole request / first token median, lifetime peak):
| row | report headline (geo) | POOLED [K] | == AR |
|---|---|---|---|
| S5' B HumanEval (cert config, lossy) | 174.4 | 171.0 / 36.0 / 4.56 s, 42.91 GB | - |
| S5' X HumanEval (lossy FAST) | 181.4 | 181.3 / 36.6 / 4.51 s, 42.91 GB | - |
| S5' B MBPP12 (cert, lossy) | 120.2 | 114.5 / 25.8 / 3.79 s, 42.55 GB | - |
| S5' X MBPP12 (lossy FAST) | 123.6 | 119.8 / 25.3 / 3.76 s, 42.57 GB | - |
| E5 E HumanEval (exact) | 99.4 | 97.8 / 31.7 / 4.59 s, 42.23 GB | 24 / 24 |
| E5 EB HumanEval (exact + bundle) | 102.7 | 101.4 / 32.6 / 4.41 s, 42.24 GB | 24 / 24 |
| E5 E MBPP12 (exact) | 71.3 | 68.4 / 21.8 / 3.73 s, 41.86 GB | 24 / 24 |
| E5 EB MBPP12 (exact + bundle) | 73.3 | 70.4 / 21.7 / 3.80 s, 41.92 GB | 24 / 24 |
| N45 E(B) IFEval (exact) | 39.9 | 37.1 / 20.8 / 2.89 s, 41.70 GB | 24 / 24 |
| N45 L IFEval (lossy cert) | 45.0 | 43.4 / 21.1 / 3.00 s, 42.37 GB | 6 / 24 |
| N45 E(B) math (exact) | 78.8 | 77.9 / 38.9 / 2.73 s, 42.50 GB | 24 / 24 |
| N45 L math (lossy cert) | 87.9 | 86.9 / 39.6 / 2.96 s, 43.10 GB | 7 / 24 |
| CHS4 y0 + y0b IFEval (L, cert on chat) | 43.8 / 44.5 | 44.2 / 20.8 / 3.05 s, 42.39 GB | - |
| CHS4 yes1 IFEval (E + SB1, exact) | 38.3 | 38.3 / 21.3 / 2.82 s, 41.69 GB | (E: 12 / 12 by CHS) |
| CHS5 z0 + z0b IFEval (M1-B + COH) | 49.7 / 49.9 | 49.8 / 24.4 / 2.92 s, 42.38 GB | - |
| CHS5 zs IFEval (M1-B + COH + SB1) | 51.9 | 51.9 / 24.8 / 2.98 s, 42.35 GB | - |
| CHS5 zsgcr IFEval (best stack, ungated) | 56.0 | 56.0 / 24.6 / 2.94 s, 42.37 GB | - |
| C32 e32 IFEval, C 160 (exact) | 33.8 | 33.8 / 19.8 / 2.83 s, 30.62 GB | 12 / 12 (BigMoE) |
| C32 zs32 IFEval, C 160 (lossy, ungated) | 51.3 | 51.3 / 22.5 / 2.99 s, 31.22 GB | - |
Note: S5' B's two HumanEval passes differ by 9 % pooled (163.9 vs 178.8); cause not checked.

FINDING 2, the Strata note (0a) against the rows:
- Strata side: OK to the digit (every arm, both caches, every set; decode, whole request, first token median), e.g. full
  cache B 47.0 / 45.6 / 41.8 / 47.1 decode and 40.9 / 36.9 / 33.7 / 40.5 whole request (HE / MBPP / chat / math); default
  B chat 37.3, D chat 35.8, first token 0.98 s, whole request 29.5 / 28.2; MTP +53 % (25.3 -> 38.7, all sets); cache
  25-28 -> 33 GB +12-21 % (B); B1 vs B2 38.4 / 38.2.
- DIFF: "the Q8_0 lossy read adds only 3-4 % over exact (38.7 vs 37.7)": those numbers are +2.7 %; per set +1.3-4.9 %.
- DIFF: our code / math decode numbers in the note (HE 181.4 / 174.4 / 102.7, MBPP 123.6 / 120.2 / 73.3, math 87.9 /
  78.8) are the geo headlines beside Strata's pooled ones. Pooled: HE 181.3 / 171.0 / 101.4, MBPP 119.8 / 114.5 / 70.4,
  math 86.9 / 77.9. Ratios vs Strata full cache move a little (HE x3.9 -> x3.86 FAST; MBPP x2.7 -> x2.63).
- DIFF: our code / math whole request in the note (HE 34.8-35.4, MBPP 23.4-23.6, math 40.3) are the old END TO END
  column. Pooled whole request: HE 36.0-36.6, MBPP 25.3-25.8, math 39.6 (L) / 38.9 (E). Strata still wins HE (40.9) and
  MBPP (36.9); math is level (40.5).
- OK: chat 44.2 (cert, mean of y0 / y0b), exact 38.3 (yes1), 49.9 (z0b; pooled z0 + z0b 49.8), 56.0, whole request 24.4,
  first token median 2.92 s; 32 GB 51.3 / 33.8 at 31.2 / 30.6 GB, whole request 22.5 / 19.8. 32 GB first token: the note's
  "~2.9 s" is E's mean (2.93); medians E 2.83 / zs 2.99 s.
- CORRECTION OF MY OWN 16:39 MESSAGE: I gave "exact, ours 39.9 vs Strata 40.6 = 0.98x" at 45 GB. 39.9 is N45's geo. Pooled:
  38.3 (CHS4 yes1) or 37.1 (N45, 2 passes) -> 0.91-0.94x. The note's "exact chat decode is behind" stands.
- Pending: "1.7 s + 22 ms per prompt token" and the ~530-token break-even (need the per-prompt fit; CPU, after 18:16).

### 0b. CT1 (chat prefill bytes), judged 16:40 with scripts/chat/ct1_judge.py: OK vs BigMoE (acf8ac3)
45 GB chat prefill 244.94 GB / 12 prompts = 100.9 % of 12 GB's 242.65 GB; mean base residency at start 45.7 %; routed-resident
65.5 % base. PF-D's TTFT 3.1 -> ~1.6 s is [P] (BigMoE's fit 0.32 s + GB / 7.33).
