# Far-ahead expert foresight for an SSD-streamed MoE: what a far draft can and cannot predict (CPU replay measurements)
- Date: 2026-11-04 22:10 EET. Sessions: MoonShots (M-38 replay frame), Fable FAR (measurements), orchestrator (this note).
- Question: a drafter runs far ahead (8 checks, ~100 tokens). Can its continuation forecast which cached experts get
  used again soon, so the expert cache keeps the right ones (approximately Belady-optimal)?
- Frame [K, M-38, ~/MoonShots commit 99df774]: 45 GB cache (K 266), 16-row speculative checks, horizon 8 checks.
  - LRU 42.9 misses per kept token; OPT 19.2.
  - A forecast with recall 0.92 / precision 0.72 on "resident reused within 8 checks" would cut misses 26.5 %.
  - Recency alone: 0.83 / 0.52. The best learned eviction key (M-14): -7.8 %.
- Numbers [K, CPU replays, ~/FableGod/far/]:
  - Token path, KILL. The TRUE future tokens through their EXACT routes reach only recall 0.68 / precision 1.00, -20.3 %
    misses (K 147, the 24 GB cache: 0.76, -26.3 %).
    - The drafter's rejected rows hold 32 % of the cache reuse, and no true-path forecast names them.
    - Honest token -> expert maps (this prompt's memo + a leave-one-prompt-out table): 0.53 / 0.66, -6.0 %.
    - Deep-layer routes are mostly context: per-row recall@10 from the token alone is 0.40 below layer 8.
  - State path, BETWEEN. A leave-one-prompt-out ridge map from a shallow hidden state to routes (every future row) reaches
    0.70 / 0.64: -14.6 % misses at K 266, -11.9 % at K 147 (235 MB per kept token). Nearest-neighbour states: -7.1 %.
  - Misses are not stalls. Perfect 8-check foresight cuts misses 34 % but layers-with-a-miss only 5 % (42.9 -> 40.6 of 48).
    Where the SSD wait is per-layer round trips, foresight buys bytes, not tokens per second.
  - Combination: foresight + the learned key on the unforecast residents is additive with a precise forecast (perfect
    kept-row routes -20.3 -> -26.9 %), and adds nothing with the ridge stand-in.
- Files: ~/FableGod/far/FAR.md (sections 1-6), far_ceiling.txt, far_state.txt, far_ridge.txt, far_combo.txt and their scripts.
- Prior art:
  - The far draft as an expert forecaster is published: MoE-SpeQ, arXiv 2511.14102 (<= 32 tokens ahead).
  - Draft-state pseudo-routers are adapted from SP-MoE (arXiv 2510.10302).
  - The three measurements above appear new: the rejected-row share of reuse, the token-vs-state ceilings, and misses vs stalls.
- Status: CPU stand-ins only; EXACT-safe (it changes only what the cache keeps).
- Next: GPU capture FAR-G1, ~4 min. Run the MTP chain 64 steps ahead per check and the 125B's routers on those tokens.
  - PASS: >= 20 % fewer misses than LRU at K 266 with set recall >= 0.80. Then build.
  - BETWEEN: 10-20 %. Keep it as a 24 / 12 GB bytes lever only.
  - KILL: < 10 %, or no better than the learned key.
