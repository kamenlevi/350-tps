# Local LLM speed research: a 125B MoE on one MacBook

Research into running the full **Qwen3.8-Flash-Next 125B** mixture-of-experts model on a single **MacBook Pro (M5 Pro, 64 GB)** as fast as possible.
- **The model:** 48 layers (36 Gated DeltaNet + 12 attention), 512 experts with top-10 routing, and an MTP head.
- **The engine:** experts stream from the internal SSD, and decoding is speculative with 16-row checks.

- **Two tracks.**
  - EXACT: every token is bit-identical to the model's own greedy output on this engine.
  - FAST: small numerical changes are allowed, judged by same-score quality tests.
- **Status (Nov 2026):** 63.6 tok/s exact on code at ~42 GB of RAM (the 45 GB line). Work continues toward a 24 GB line and a <= 12 GB line.

## Layout (one folder per research session)
| folder | what |
|---|---|
| `Leap/` | GPU kernels (Metal / MLX): split-K replicas, matrix-unit (NAX) expert kernels, 16-row 4-bit GEMMs, exactness probes. `TABLE_350.md` is its results table. |
| `BigMoE/` | the streamed 125B engine: expert caches, out-of-order expert execution, the exact reference (REF2-T), SSD read paths |
| `TrainLab/` | drafters: DFlash2 fine-tunes, the native MTP head, early-tap and two-drafter experiments |
| `Breakthrough/` | the small-RAM (<= 12 GB) line: two-pass certified checks, cache replays, the decision map |
| `EvalSuite/` | quality tests (same scores on math, code, instruction following, multilingual) for every non-exact variant |
| `NewIdeas/` | idea routing and the FAST-track list |
| `MoonShots/` | unusual ideas and their 10-minute screens |
| `FableGod/` | long-form analyses by the Fable research sessions, cloud analysis tasks and answers, and `TRIED/TRIED.md` (every idea tried, with its verdict) |

## Notes
- **What's not included:** this is a snapshot of the working repositories, without their commit history, the model weights or the large data files.
- **What was removed:** some operational and personal notes, and vendored third-party code. References to them may dangle.
- **How to read the numbers:** most documents mark them as measured, arithmetic or judgement. Estimates have historically run about 2x optimistic.
- **License:** not chosen yet.
