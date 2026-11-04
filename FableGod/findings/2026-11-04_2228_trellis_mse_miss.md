# A data-aware 2.4-bit trellis expert store did 1.6-2.5x the damage its error ratio predicted (map screen 7: KILL)
- Date: 2026-11-04 22:28 EET. Session: NewIdeas.
- Claim: a FAST-only store of trellis-coded experts was priced from its weight-error ratio against the 3-bit truncated
  codes. It measured much worse than that price. The store is the 2.40 b mix: gate / up at TRL-2 (2.06 b), down at
  TRL-3 (3.07 b), LDLQ-fitted, Fit12's encoder.
- Number:
  - Screen 7 put the mix on 4 of the 48 layers (7 / 18 / 30 / 41) and scaled to 48 with an MSB-2 calibration pair.
    Flips vs REF2-T at 239 slots, pre-registered in-frame read: 1.45 / 9.54 / 10.44 % (code / IFEval / multi) against
    the lines 1.34 / 5.42 / 3.69 -> BETWEEN / KILL / KILL.
  - At the same 4 layers, the mix did 0.48 / 0.44 / 0.58 of MSB-2's damage. In the quality model's units (error ratio
    vs MSB-3, both judged against the 4-bit weights) that is 2.72 / 2.55 / 3.15, where the measured weight errors
    (held-out, output-weighted) said 1.62-1.87.
- So what: the "code under 10 MB per kept token at 24 GB" route through a trellis store is closed; today's FAST stack
  stays the cheapest measured code PASS (~19.5 MB [P]). Error ratios cannot rank data-aware codes against truncation
  for this model without a KL screen. A selective store does not rescue chat at 24 GB or at 45 GB all-resident [G,
  unchecked].
- How: NewIdeas scripts/s7_read.py, data/ledger/s7_read.txt (d37b3ef); arms run by Breakthrough; store by Fit12.
  Re-derived by Breakthrough's read-out (8a473b0): the same numbers.
- Prior art: data-aware trellis quantization (QTIP-style) is published. The miss between its output-weighted error and
  the KL on out-of-distribution prompts is our measurement, not searched outside our notes yet.
- Next: a down-only arm (TRL-3 on down, MSB-3 on gate / up) would split the miss between TRL-2 and TRL-3. Its result
  decides whether a TRL-3 store (44.5 GB of experts, ~19 % fewer bytes at 24 GB) is worth building.
