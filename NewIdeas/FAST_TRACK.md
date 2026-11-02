# FAST track: ideas held back only because they are not bitwise (NewIdeas, Mon 2 Nov 22:0x)
> (a quote from the project owner, kept private)
lines whose reason is bits, a new reference or "not exact", not quality. Gains are each line's own measured numbers unless
marked (model). Every item needs a same-scores test before a FAST preset ships.
NOT DONE YET (usage limit): published / adapted / new tags for the ADOPTED / PASS levers, and the prior-art checks of the six
new candidates.

## 45 GB, ranked by gain x readiness
1. NAX expert kernel as a new reference (Fable mission 27): NAX6 42-43 ms vs 3c 50-56 ms per 16-row check; NAX7 ~35 ms, or
   ~26 if the probe's op rate is 2x: -8..-25 ms per check (~10-30 %). Next: Leap's 10-min probe, then a same-scores test.
2. Q1, top-2 experts on drafter-sure rows (cf >= 0.99), kept weights never renormalised: code SSD MB per kept token x0.60,
   implied 63.6 -> 70-76 tok/s; sure rows at 3 bits (no LSB read) x0.46 -> 72-79 (Breakthrough's arm tonight). 0.09 % of
   gated code rows flip. Test: EvalSuite RELAX arm A (Thu 00:30).
3. REF2c (att_single -5 ms + padded GDN in_proj -0.5 ms, ~-6 ms per check, ~7 %): IFEval 85 vs 90 in Part 1, inside the
   same-weights spread; tonight's IFX re-test on 441 prompts decides.
4. Near-tie acceptance on chat (R-61N at rho 0.25: chat +8..+23 % per pass; exact-loop M-15 +14 %) + the '#'-comment
   loophole: RELAX arms B / E / F (Thu 00:30).
5. HC8 (D4): ~-2.5 ms more on the HC read; 1.44 % of rows flip, 0.00 % of sure rows; EvalSuite decision 4 PASS. In the fast
   preset (B mode).
6. bmm16 HC (L1-29, new rounding): HC mix-down 5.11 -> 2.59 ms per check (-2.5 ms). Needs a REF3 bundle; price it on top of
   HC8 / D1, which touch the same read.
7. Middle-layer MoE reuse, at most 1 row old (P-frame, layers 8-35): 1.03 % of code-sure rows flip; bytes not replayed yet
   (Breakthrough's stage 2a re-cut). Lead.
8. 32-row checks + Q1: dense x1.24 at 32 rows (D32), MATCH kept x1.204 at 32; M-18c replay running (MoonShots).
9. Small kernel items held only for bits: L1-31x fused GDN prework (1.51 -> 1.09 ms), chunked (WY / UT) GDN verify (the GDN
   body is only ~3 ms per check, so <= ~-1.5 ms), FUSED_CONVNORM_VERIFY (+2.7 % on the old path). Bundle them only if 1 or
   3 opens a reference change anyway.
10. One answer in 4 parallel parts (L1-32): 0.59x expert reads per accepted token, ~2x (model), but it changes the answer's
    form (Skeleton-of-Thought style): highest quality risk, last.
Output-exact already (exact track, not FAST): the drafter gate + up merge (-1.6 ms draft, kept x0.9955, ~+1.5 % net).
Dead on value, not on bits: exact trees (TREE_WALL: best +1.6 % halved), MTPLX fused MoE kernels (slower), MLX 0.32.4 on
the old path (no gain; a re-test on today's path needs a download OK).

## Near misses of the strict KLD gate (quality-gated, not bit-gated; FAST judges by same-scores instead)
- Top-8 per verify row at 45 GB (M-09d, no renorm): -16 % experts, over the strict 1.10x gate; at 12 GB top-8 passed all 5
  rules (+17-20 %).
- 2-bit tails 4433332222 (TAILS2): code KLD 0.00267 vs line 0.00253 (5 % over); MSB-2 for the lowest ranks est. +20-25 %.
One same-scores arm each, after items 1-5.

## 24 GB
1. FM1 (budget b16 + budget-aware JIT prefetch + fixed 3:3:0 drafts): +33 % geomean (code 35.8 -> 48.8, edit 37.2 ->
   56.5); Eval run 1: 5/5 rules vs v3, 4/5 vs the 4-bit ref (IFEval -5.0). Needs run 2; Kamen OK'd a non-exact 24 GB
   version on 10-29.
2. POM / LPOM (cold ranks >= 6 read as 2 code planes): -12.4 % bytes, then -9.6 % more (predicted inside the gate).
3. R-30 UNIQ (drop single-use low-rank experts): bytes -17.6 % at 2.3 % gate mass; quality never measured.

## 12 GB (FOR_KAMEN decisions 1, 2 and 6 become FAST-preset items)
1. Top-8 per verify row (TK1 / TK2): +17.4-19.8 %, 5/5 quality rules (decision 2).
2. PMIN12 (MTP cut at p_min 0.5): chat +21 %, scores identical; waits for Fit12's HT1 trim (-0.5..-0.65 GB) (decision 6).
3. Sparse prefill lane (L2-10): 64K prefill 1.47x, peak -0.9 GB, answers identical at 32K / 60K (decision 1).
4. The two-pass certification (T0, new): same-scores Tue after IFX.
5. Budget b20 (+24 % geomean, speed only so far); DFlash2 at 12 GB (+14 % code / +23 % GSM, +0.35 GB); C_m 56 (+7-14 %,
   short context only).

## Test order beside the exact queue (big runs weekdays 00:30-15:00; BigMoE's day screens and nightly combined run first)
- Tue 00:30-15:00: BigMoE (01:00-05:30) -> IFX (45 #3) -> T0 same-scores (12 #4) -> Breakthrough's map arms incl. 3-bit
  sure rows (45 #2) -> RELAX smoke (every arm, by ~14:20).
- Wed 00:30: BigMoE combined -> FLOOR (~10 h). Thu 00:30: BigMoE combined -> RELAX night (the 45 GB FAST preset).
- Next free night: NAX6 / NAX7 same-scores (45 #1, if the probe passes), FM1 run 2 (24 #1), the 12 GB FAST preset (top-8 +
  PMIN12 + sparse lane as one same-scores arm).
