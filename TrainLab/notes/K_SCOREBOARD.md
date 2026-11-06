# K scoreboard by workload (MTP Head, Fri 2026-11-06 11:3x; K_PLAN_1106 item 2, for the orchestrator and Fable GOAL)

K = tokens kept per 16-row check. [K] = measured, [P] = predicted (replay). The drafter is DFlash2 L1-20 throughout
(the engine runs it as D7B, 4-bit layers, code kept x1.00).

| workload | n | exact, official loop [K] | exact, every anchor [K] | under CD16 [P, GOAL] | sources |
|---|---|---|---|---|---|
| 12 HumanEval, engine FAST-NAX, C 224 | 12 prompts | 10.36 (5.7-14.2 per prompt) | | tok/s x1.15 | BigMoE fnx_report |
| HumanEval+ walk | 24 answers | 9.57 | 11.64 (6,351 anchors) | fresh 12: 10.44 -> 12.91-13.16 | d02b_walk.txt, d23h_dfl |
| MBPP walk (held out from L1-20) | 100 answers | 5.94 | 7.07 (15,541 anchors) | 5.61 -> 10.69-10.87 | MATCH RESULT, d23h_dfl, GOAL |
| docstring-free: checks after the docstring | MBPP / HE | MBPP 5.5, HE 6.2-7.7 [P] | | MBPP 9.6-9.8, HE 10.7-10.8 | GOAL K_WALL_1106 |
| GSM8K math | 60 answers | 7.00 | 8.23 (14,260 anchors) | | d02b_walk.txt, d23h_dfl |
| agent | 12 windows | 3.01 | | | MATCH RESULT |

How to read it:
- The every-anchor mean is higher than the official loop because it weights every position equally. The official loop
  lands its anchors after misses, which are the harder spots. GOAL's 5.61 for MBPP uses the engine's 0.3 cut, my 5.94
  the uncut official loop.
- Exact K: HumanEval is ~1.6x MBPP. Under CD16 the two converge (~10.7-13), because CD16 accepts comment and docstring
  text wholesale. After CD16 the gap is the drafter's depth on code rows (GOAL: MBPP pick 0.60 at depths 12-15).
- Noise for retrain comparisons: one reseed moves code by 0.16 and math by 0.01 (SEED).

Data for CPU replays: notes/K_WALL_DATA.md. The every-anchor files are data/d02b_walk_d23h_dfl_{code,math,mbpp,multi,ifeval}.npz
(per anchor: dtok, dcf, ttok, tcf). Top-16 candidates at every anchor exist only for the 36 decision-map windows
(d02b_walk_tree3_*), not for MBPP or math.
