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

### 0b. CT1 (chat prefill bytes), judged 16:40 with scripts/chat/ct1_judge.py: OK vs BigMoE (acf8ac3)
45 GB chat prefill 244.94 GB / 12 prompts = 100.9 % of 12 GB's 242.65 GB; mean base residency at start 45.7 %; routed-resident
65.5 % base. PF-D's TTFT 3.1 -> ~1.6 s is [P] (BigMoE's fit 0.32 s + GB / 7.33).
