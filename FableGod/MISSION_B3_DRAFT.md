# MISSION B3 (Fable B): THE FAST DENSE PASS, AND 32 ROWS. What crosses 17 ms?

(Draft by the orchestrator for Kamen, Mon 2 Nov 2026 ~21:5x.)

**Why.** Your BOUNDARIES.md proved the EXACT dense pass floors at ~19-21 ms per 16-row check, so <= 17 isn't reachable exactly. You named the two things that cross it: the 32-row check (the dense pass is flat in rows) and reference changes.
- Kamen's rule since 21:3x tonight: two first-class tracks, EXACT and FAST (judged by same-scores tests), both published.
- Cloud's ladder (task 15) ranks the dense reference change as the second most critical piece: ~275 tok/s without it, 327-353 with everything at target.

**Deliver**
1. **The FAST dense pass, piece by piece.** For each lever give ms per check (bound, then halved), what changes numerically, and its quality evidence and risk:
   - att_single, the attention kernel: -5 ms claimed; quality re-test (IFX) runs tonight
   - HC8: same-scores PASS with a lean
   - the chunked / WY GDN verify: killed only "for exact modes"
   - MTPLX's fused GDN prework at 16 rows: 1.09 vs 1.51 ms, killed only for bits
   - E1 / E3 without the bitwise constraint (reordered sums, a looser megakernel)
   - anything else in TRIED that died only for bits

   Give the FAST dense floor.
2. **The 32-row check, on both tracks, at the floor engine.** The dense pass per token halves. Weigh that against:
   - the expert union growing x1.5-1.6 per doubling (B3: ~2.0 ms per added row at 32 rows today)
   - kept at 32 rows (the copy override pays x1.211 on HumanEval+ at 32, x1.041 at 16)
   - BigMoE's caveat: beyond 16 rows the check leaves REF2-T's certified 1-16-row verify, so the token check decides exactness

   Cloud predicts 32 rows lose on this week's engine (66 vs 78 tok/s). Find the crossover: at which dense ms and expert-kernel efficiency do 32 rows win?
3. **The dense piece of the ladder:** the best FAST combination and its tok/s effect at the floor engine, next to the EXACT one. Order the tests by quality risk, cheapest first.

**Rules**
- CPU only; writes only in ~/FableGod/fableb/; no downloads; GPU timing is Leap's.
- Check TRIED for every lever. Halve gains. Mark every number [K] / [P] / [G].
- Adopting a FAST lever is Kamen's call. Price them all; drop none for being non-exact.
