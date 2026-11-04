# STATE of the project, Thu 5 Nov 2026 ~00:15 EET (orchestrator). Read after MISSION.md.

## What exists and works [K]
- **The engine** (BigMoE's r57 screen, MLX on the Apple GPU) runs the full 125B with all 512 experts.
  - RAM holds a cache of expert records: "pools" of C slots per layer. C 224-256 is ~the 45 GB line.
  - The rest streams from the SSD.
  - Exact reference REF2-T: ranks 0-1 at 4 bits, 2-9 at 3 bits.
- **Already in the engine or its presets:**
  - expert tiers;
  - out-of-order experts (resident first, misses after);
  - split-phase MoE; next-layer router look-ahead prefetch (V1); per-layer slot budgets;
  - NAX6 expert kernels (the native layout comes with Thursday's conversion: 77 % of streaming EXACT, 82-83 % FAST);
  - dense-pass levers: DENSE-N-RAM, hc_b, GDNB; FAST-only: HC8-1P, SVH;
  - an 8-bit drafter (DFlash2, 10.4 -> 5.4 ms per check);
  - DRAFT17: a 17th draft gates the bonus row;
  - FAST: QOM (sure rows skip missing experts), 3-bit sure rows, 11-bit scales;
  - relaxed acceptance (FAST, judged by EvalSuite overnight).
- **Measured:**
  - First combined FAST number: +26 % over the U3C baseline (by day, C 160).
  - EXACT +~19 % since 2 Nov.
  - The 12 GB line: 40.8 tok/s, bit-exact, in an 11.35 GB footprint. Likely the first exact >= 80B run under 12 GB.
  - 24 GB: the first chat route that keeps all quality lines: QOM cf 0.5 + gated bonus row; code 0.71 / IFEval 4.30 / multi 2.73 % flips; ~88 MB SSD per kept token on chat.
- **Tooling you can lean on:**
  - Breakthrough's decision map: teacher-forced 36 windows, flip rates vs lines.
  - MoonShots' replay frames.
  - EvalSuite: same-score tests.
  - Leap: kernels and timings, `Leap/TABLE_350.md`.

## Killed this week (don't retry without a new reason)
- The expert kernel to 90 %: twelve bitwise redesigns all KILLed (KERNEL90.md).
- The trellis-coded 2.4-bit expert store: chat quality KILL; data-aware codes cost 2-3.5x KL per unit of error.
- Parts of one answer in parallel: code answers almost never split (HumanEval / MBPP 0 %, Magicoder 1.2 %).
- A 2x bigger drafter as an engine lever: +0.18 kept for 2x drafter time (BETWEEN).
- Pre-routers, runahead slices, sibling trees, FRUGAL, dynamic top-k (tau) and adaptive-k (p 0.8): see TRIED.md.

## Alive and in flight
- Relaxed acceptance: EvalSuite quality + answer-length test overnight.
- Rule C (relax only in '#' comments): MBPP x1.125, HumanEval+ x1.074, 0 code changes. Engine arm Fri night.
- FAR foresight: a hybrid near + far draft forecaster, -20 % cache misses on CPU. GPU capture FAR-G1 Fri night.
- The NAX6 certification and the store conversion: Thursday.
- P-OFF drafter training (off-policy data): Fri night.

## The open wall that is YOUR mission
- Distinct experts per kept token. The kernel is at its ceiling and bits don't help it.
- Only fewer distinct (expert, layer) tiles per kept token cuts the ~38-43 ms expert term at 45 GB and the SSD bytes at 24 / 12 GB.
- Simple per-row top-k cuts are spent (the router is flat). The gains left are in:
  - sharing across rows;
  - the rejected rows;
  - the unsure middle rows;
  - structure across layers or positions;
  - or something nobody has looked at.
