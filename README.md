# 350-tps

- Model: Qwen3.8-Flash-Next 125B (MoE, all 512 experts)
- Hardware: MacBook Pro, M5 Pro, 64 GB
- Now: 63.6 tok/s, exact
- Best case (estimate): ~350 tok/s

## Dated findings (newest first)
- 2026-11-04 22:40: [Near + far draft forecasting for MoE expert caching](FableGod/findings/2026-11-04_2240_near-far-expert-forecasting.md). Four new measurements, including the SSD wait law; CPU replays, GPU test pending.
- 2026-11-04 22:28: [Trellis-coded experts miss on chat by more than their MSE predicts; the family is closed for this model](FableGod/findings/2026-11-04_2228_trellis_mse_miss.md).
- 2026-11-04 22:16: [A chat route that keeps quality at the 24 GB split](FableGod/findings/2026-11-04_2216_chat_route_24gb.md).
- 2026-11-04 22:10: [Far-ahead expert foresight, lab log](FableGod/findings/2026-11-04_2210_far-ahead-foresight.md).
- 2026-11-04 14:39: [The 125B MoE at 40.8 tok/s in an 11.35 GB footprint, bit-exact](FableGod/findings/2026-11-04_1439_12gb-exact-40tps.md).
- 2026-11-04 14:35: [HC8: one-pass HC read](FableGod/findings/2026-11-04_1435_hc8-one-pass-hc-read.md).
- 2026-11-04 14:34: [DRAFT17: a 17th draft gates the last row](FableGod/findings/2026-11-04_1434_draft17.md).
