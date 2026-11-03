# FAST track: ideas held back only because they are not bitwise (NewIdeas, Mon 2 Nov 22:0x; updated Tue 02:4x)
> (a quote from the project owner, kept private)
lines whose reason is bits, a new reference or "not exact", not quality. Gains are each line's own measured numbers unless
marked (model). Every item needs a same-scores test before a FAST preset ships.
Novelty (Mon 22:xx, ~/TRIED/NOVELTY.md, prior-art web checks): NEW = 45 #2 (the verifier's experts keyed on drafter
certainty), 45 #7 (P-frame reuse) and 45 #4's comment loophole (as a span rule); adapted = COPYGATE (SAM-Decoding), the
12 GB two-pass (TriSpec, with a self-proxy at top-2), 3-anchor ANE drafting (SpecBranch / PEARL / Mirror-SD); published
practice = the NAX hybrid for padded tiles (MonoMoE, ORT's MoE GEMV path). Every live-default lever is published or
adapted; the new ones get their first same-scores test this week.
One new bet in flight per line: 45 GB Q1 (RELAX arm A, Thu 00:30); 24 GB Q1 at the 24 GB pools (M-18d: x0.658 PASS on
option A, option B pending); 12 GB the two-pass check's drafter-certainty arm (T0 same-scores, Tue).

## 45 GB, ranked by gain x readiness
1. The expert kernel (Fable mission 27): NAX6 42-43 ms vs 3c 50-56 ms per 16-row check. NAX7-F is KILLED, so exact NAX
   work ends at NAX6 (a new reference: -8..-13 ms, one same-scores test). FAST design C, int8 x int8 on the matrix units
   (M27-C), is a rough PASS at 1.55-1.73x bf16, i.e. the expert call ~42 -> ~25-27 ms (~-15 ms per check, model). Leap
   builds design C next (row-invariant), then one same-scores test covers NAX6 + H-1 + design C.
1b. H-1, the NAX hybrid for padded tiles (Leap TABLE_350 "H-1", af57ce6; published practice: MonoMoE, ORT's MoE GEMV
   path): its compact arm is +10.4 % on the expert call at S 16 (+15 % at S 8, which matters for chat's short checks; +6 %
   at S 32), ~-4 ms per 16-row check. Bits differ, so EvalSuite judges it with the FAST arms. It needs the small-group split
   on the GPU first (gpu_grp, no host sync). Bundle it into item 1's same-scores test: one reference change, one test.
2. Q1, top-2 experts on drafter-sure rows (cf >= 0.99), kept weights never renormalised: code SSD MB per kept token x0.60,
   implied 63.6 -> 70-76 tok/s; sure rows at 3 bits (no LSB read) x0.46 -> 72-79 (Breakthrough's arm tonight). 0.09 % of
   gated code rows flip. Test: EvalSuite RELAX arm A (Thu 00:30).
2b. Sketch-on-miss: KILL (Tue 02:1x, Breakthrough SCOREBOARD 7a79270). Whitened shadows on held-out real activations have
   output error 0.92 at rank 32 and 0.89 at rank 64 (a drop is 1.0; the GO bar was 0.5), and plain SVD 0.99 / 0.97: the
   expert spectrum is too flat for a low-rank stand-in. Gain 0.
2c. Sidecar drop (MoonShots M-26): every rank at 3 bits (plan 3333333333) and the freed sidecar RAM spent on base pools:
   code SSD MB per kept token at C 256 46.3 -> 24.5 (-47 %), with Q1 27.8 -> 11.8 (-58 %, under FLOOR's 33 MB target); C 320
   8.1 with Q1; chat 30.2 -> 17-18. Implied steady 63.6 -> 75.8, 85.3 with Q1: the largest priced FAST SSD lever. Quality
   is the whole question: all-3-bit failed the strict KLD gate before (x1.24-1.83). Breakthrough's t3_all / t4_all map runs
   Tue (second in its list), with the sure-rows-only 3-bit arm right after as the fallback.
   MAP RESULT (Tue 02:29, SCOREBOARD 8b3d8e5): code BETWEEN (+0.59 points of all-row flips over the 4-bit control; sure
   rows 0 / 2,922), chat worse (+4-5 points: mid rows flip ~5 % vs ~0.4 %). Next: EvalSuite's same-scores (IFEval first;
   proposed as an extra RELAX arm Thu), and tonight's 3-bit sure-rows arm, which keeps chat's mid rows at 4 bits.
3. REF2c (att_single -5 ms + padded GDN in_proj -0.5 ms, ~-6 ms per check, ~7 %): IFEval 85 vs 90 in Part 1, inside the
   same-weights spread; tonight's IFX re-test on 441 prompts decides.
4. Near-tie acceptance on chat (R-61N at rho 0.25: chat +8..+23 % per pass; exact-loop M-15 +14 %) + the '#'-comment
   loophole: RELAX arms B / E / F (Thu 00:30).
   Re-price the comment loophole when RELAX arm B runs: Fable B's B5 found that 49 % of code first misses are comment tokens
   (2.9x their base rate), so its kept gain may be well above the x1.06 estimate.
5. HC8 (D4): ~-2.5 ms more on the HC read; 1.44 % of rows flip, 0.00 % of sure rows; EvalSuite decision 4 PASS. In the fast
   preset (B mode).
6. bmm16 HC (L1-29, new rounding): HC mix-down 5.11 -> 2.59 ms per check (-2.5 ms). Needs a REF3 bundle; price it on top of
   HC8 / D1, which touch the same read.
7. Middle-layer MoE reuse (P-frame): KILL on bytes (the layer-wise map: union x0.91 only). New as an idea, dead as a lever.
8. 32-row checks + Q1: KILL as a global switch (M-18c: pooled code -1.3 % today / -0.6 % with NAX6; always-32 -14..-17 %).
   'Deep rows sure' +4.3 / +3.8 % (BETWEEN); only cap-bound prompts gain (HumanEval/136 +13 %). Fable B's B3 agrees: 32
   rows only as the copy-driven block inside long copies (NEXT_DRAFTER).
9. Small kernel items held only for bits: L1-31x fused GDN prework (1.51 -> 1.09 ms), chunked (WY / UT) GDN verify (the GDN
   body is only ~3 ms per check, so <= ~-1.5 ms), FUSED_CONVNORM_VERIFY (+2.7 % on the old path). Bundle them only if 1 or
   3 opens a reference change anyway.
10. One answer in 4 parallel parts (L1-32): 0.59x expert reads per accepted token, ~2x (model), but it changes the answer's
    form (Skeleton-of-Thought style): highest quality risk, last.
Closed tonight: seeded exact argmax (FEXIPRO's method, published; ~0.1 ms at 16 rows: low priority, exact);
predict-then-correct EXACT KILL (FAST predict-and-skip BETWEEN, P ~15 %); learned stop rules M-21 / M-21b KILL on code.
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
4. Q1 at 24 GB (M-18d, NEW bet; option A with DFlash2's cf as the proxy): exact v3 verify 175.0 -> 115.2 SSD MB per kept
   token (x0.658, PASS, but within 0.05 of the line, so MTP Head's per-row MTP confidences re-run it as option B). On b16
   it is KILL (x1.079): the budget already caps the union at 16, and Q1 only changes which 16 fill it. b16 stays lower in
   bytes (81.8), so Q1 is the quality-safer alternative to FM1's budget (0.09 % of gated code rows flip vs b16's IFEval
   -5.0 in run 1), not an add-on to it.

## 12 GB (FOR_KAMEN decisions 1, 2 and 6 become FAST-preset items)
1. Top-8 per verify row (TK1 / TK2): +17.4-19.8 %, 5/5 quality rules (decision 2).
2. PMIN12 (MTP cut at p_min 0.5): chat +21 %, scores identical; waits for Fit12's HT1 trim (-0.5..-0.65 GB) (decision 6).
3. Sparse prefill lane (L2-10): 64K prefill 1.47x, peak -0.9 GB, answers identical at 32K / 60K (decision 1).
4. The two-pass certification (T0, new): same-scores Tue after IFX.
   T3 TIMING (Fit12, Tue 02:29-02:38): the 2-rank pass 1 gave the same tokens and logits as the 10-rank one on all 7 prompts;
   code 56.2 tok/s vs 18.9 for the exact 16-row check (3x), but under its pre-registered KILL line of 70. Pass 1 is 145 of the
   211 ms per check, so pass 1 is what must come down; math 1.24x the exact check, IFEval 0.85x.
5. Budget b20 (+24 % geomean, speed only so far); DFlash2 at 12 GB (+14 % code / +23 % GSM, +0.35 GB); C_m 56 (+7-14 %,
   short context only).

## Test order beside the exact queue (big runs weekdays 00:30-15:00; BigMoE's day screens and nightly combined run first)
- Tue 00:30-15:00: BigMoE (01:00-05:30) -> IFX (45 #3) -> T0 same-scores (12 #4) -> Breakthrough's map arms incl. 3-bit
  sure rows (45 #2) -> RELAX smoke (every arm, by ~14:20).
- Wed 00:30: BigMoE combined -> FLOOR (~10 h). Thu 00:30: BigMoE combined -> RELAX night (the 45 GB FAST preset).
- Next free night: one same-scores test for NAX6 + H-1 + design C (45 #1 / 1b), FM1 run 2 (24 #1), the 12 GB FAST preset (top-8 +
  PMIN12 + sparse lane as one same-scores arm).
