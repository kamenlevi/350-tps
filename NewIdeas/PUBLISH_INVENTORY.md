# Publish inventory (DRAFT, NewIdeas, Fri 6 Nov 2026 20:4x; final by Sat ~12:00)

PREPARATION ONLY. Nothing gets published until Kamen confirms the date, scope and venue; the orchestrator has asked him.
The deadline (a replacement model is expected within ~1-2 weeks) outranks the 250-330 / 90-130 trigger: the release
carries the best measured, quality-gated numbers at the freeze. Tags: [K] measured, [P] priced or modelled.

## 1. What is ours (from ~/TRIED/NOVELTY.md; one line each, with evidence, tag, owner, and whether it carries over)

Compiled Fri 20:5x from the 29 NOVELTY rows, each checked against its latest TRIED line (Tn = line n of TRIED.md).
Carries: MD = any MoE + drafter, SD = any spec-decode LLM, MAC = Apple SSD / Mac, AGPU = MoE on Apple's GPU. No row is
specific to this model's GDN / HC layers, so all of it ports to a successor MoE.

LIVE in a release config:

| item | tag | where it is live | owner | evidence | carries |
|---|---|---|---|---|---|
| SSD wake penalty + keepalive 50 us | new finding (known mechanism) | 45 GB EXACT default (Item 5, T10, +12 % with the night's levers) | MoonShots -> BigMoE | BigMoE 0365ada | MAC |
| W1-PICKUP coherent spin handoff | adapted | 45 GB EXACT default (lever 1) | Leap -> BigMoE | 5565a56 | MAC / AGPU |
| PURGE-1 volatile expert tier 64/32 | adapted | 45 GB EXACT default | Leap -> BigMoE | 0365ada | MAC |
| M-29 aligned zero-copy reads + copy split | engineering | 45 GB store (native + p11 + pad) | MoonShots -> BigMoE | 055d827, 37b9f8b | MAC |
| chat switch (drafter by task) | adapted | 45 GB EXACT default | MTP Head | 0365ada | SD |
| QOM (sure rows skip cold ranks 2-9; at thr 0 every drafted row is sure) | adapted | 45 GB FAST stack (code sets) | NewIdeas + BigMoE | 5bb2743; r57_screen_fast.py:233-240 | MD |
| 3-bit kept experts on drafted rows (U3's t3, inside QOM at thr 0) | new signal (published mechanism) | 45 GB FAST stack | NewIdeas + Breakthrough | T103, T106; r57_screen_fast.py:233-240 | MD |
| Q1-UNION (sure rows keep the check's union) | adapted (OEA) | RELAX B, code + math answers, and inside QOM (q1u) on the code sets | NewIdeas | T993, T985 | MD |
| comment rule (relaxed acceptance only in comments) | adapted (relaxed acceptance is published; the comment-only span was found nowhere in 2 web checks) | RELAX B | MoonShots | T1350, BigMoE 5b1d00f | SD |
| B12LL cold ranks half a layer late | published (KTransformers' Expert Deferral) | 12 GB default | Breakthrough | T1057 | MD |
| 11-bit scale pack (from LOSSLESS45) | published | the p11 store | MoonShots | 055d827 | AGPU |

PASSED, not live (findings): NAX hybrid padded tiles (+9 / +23 %, published practice; Leap, n7_stack.txt); the
prompt footprint as the code path's COLD table (new signal, PASS on code, T312); the wake-ahead ping (adapted, T47 /
T98); the 12 GB two-pass certificate and P1-OEA (adapted; speed PASS, but the T0 same-scores is KILL, T1039); M-28 /
M-30 / M-29b SSD measurements (engineering: material for the SSD section).

KILLED (the negative-results section): P-frame MoE output reuse (the one fully new idea; union only x0.91), the
staged check, P2-PREFETCH, expert-major / co-compute (T746, T450), 3-anchor ANE drafting (T850), the M-31 head ping
(T202), LSB-on-miss (overtaken by U3), COPYGATE (BETWEEN; only its prompt-copy rule ships, inside RELAX B). Fri's
KILLs join them: never-wait in the engine, SPLIT-NAX, CD16 on MBPP quality.

To fix before the freeze (NewIdeas):
- Refresh NOVELTY.md (last edited 3 Nov; the comment rule is now adapted, keepalive is adopted) and tag the live
  kernels and drafts: FAST-NAX, DN-KS, D7BNAX_32 / QMM32, att_single, lazy commit, DRAFT17, HC8. The NAX6 matrix-unit
  form is the candidate "ours".
- QOM's drafter certainty barely acts as shipped: it runs at cf 0, and thresholds <= 0.3 are identical (T1011). Its
  live effect is "skip what would miss", and that cache-state dependence carries the agent blunders.
- Some TRIED lines lag their evidence: QOM still says IN FLIGHT (T467), and EvalSuite's Fri verdicts are not merged.

## 2. Results we can stand behind today, and what is missing

| line | mode | workload | tok/s | quality gate | status |
|---|---|---|---|---|---|
| 45 GB | EXACT (NAX6-N) | ref14, 13-14 prompts | 49.9 [K, quiet, C 192, NATIVE-FRI run 2] | certified exact reference (Part 1 + 2 PASS, Thu 5 Nov) | stands |
| 45 GB | FAST (FAST-NAX all-in) | 12 HumanEval | 113.9 [K, quiet, C 224, palindrome] | same-scores: tonight's run on the stack | pending tonight |
| 45 GB | FAST stack (+ DN-KS, lazy, D7BNAX_32, att_single; no CD16) | 12 HumanEval | 132.6 steady = 116.9 whole decode [K, quiet, C 224, palindrome, Sat 00:2x; whole decode from the orchestrator's 05:0x table] | same-scores (runner 49 gates stackb, below) | measured |
| 45 GB | FAST stackb (the stack + B's comment rule + g2 copy) at C 256 | 12 HumanEval | 144.9 [K, quiet, palindrome 145.5 / 144.3, lifetime peak 42.8 GB; +46 % vs qall 99.1]; 142.4 in the S2 A/B (~1.7 % run to run) | runner 49 at C 224 (EvalSuite bb7094d, 3581be6): same scores vs REF2-T FAIL at the bar (HumanEval+ 90.0 vs 95.0, -3 of 60, p 0.25); vs NAX6 PASS (90.0 vs 91.7); B top-up PASS (0.30 / 10K); long code PASS (0.18 / 10K); MBPP PASS (76 vs 79, p 0.45). S4 compares vs NAX6-N (the orchestrator's (b); Kamen may reverse) | code verdicts in; S4 running |
| 45 GB | stackb + S2 (SB 2, D7BNAX_32=2, DSUB / SVH) at C 256 | 12 HumanEval | 146.8 steady [K, quiet A/B vs 142.4: +3.1 %, peak 42.8 GB]; whole decode 119.5 -> 124.8 (+4.4 %) | S4's gate (QOM run-to-run tokens differ, so no token route) | pending S4 |
| 45 GB | stackb + S2 + REF2_KEEP_CACHES at C 256 | 12 HumanEval | 164.2 steady [K, quiet A/B vs 149.1: +10.1 %; cycle 66.9 ms; peak 43.1 GB]; whole decode 126.0 -> 135.3 (+7.4 %), full period 143.6 -> 157.3 (+9.6 %); in S1's B arm: 165.3 steady = 158.5 full period = 137.8 whole decode [K, re-derived] | KEEP: EXACT proof 3 / 3 (same bits); S4 (if NW leaves v1, the second S4 slot) | v1 if NW stays BETWEEN |
| 45 GB | v1 as written for S4: the row above + NW v3 (code sets only; NW's chat map FAILED, so math / chat run without it) | 12 HumanEval | 180.3 steady [K, BigMoE f9c9fff] = 165.4 full period = 142.1 whole decode [K, re-derived Sat 04:5x]; peak 43.9 GB | NW's code map PASS (0.71 / 0.86 %). **S4 PASS** vs NAX6-N (EvalSuite a1aac9b, 05:38), both orders: HumanEval+ 88.3 vs 91.7 (53 vs 55 of 60, p 0.5), math 86 vs 88 (43 vs 44 of 50, p 1.0), long code 0 blunders in 27,488 tokens. Information: vs REF2-T, HumanEval+ 88.3 vs 95.0 (-4 of 60) would FAIL the original line | NOT the release: S1b (counters off) = BETWEEN (+6.9 % full period, +5.8 % whole decode; 149.4 whole decode with NW), so NW v3 leaves v1 (Sat 05:47) |
| 45 GB | **v1' (the release candidate)** = stackb + S2 + KEEP at C 256 (final_env dd7ad0f, snapshot 03c7782) | 12 HumanEval | **141.2 whole decode**, 164.2 full period [K, S1b's B arm, quiet, Sat 05:4x]; lifetime peak 43.8 GB | **S4 PASS** (EvalSuite 013a4a6, 06:48) vs NAX6-N: forward HumanEval+ 88.3 vs 91.7 (53 vs 55 of 60, p 0.5), math 84 vs 88 (42 vs 44 of 50, p 0.5); reverse HumanEval+ 90.0 (54), math 86 (43); long code 0 blunders in 27,014 tokens. Every discordant pair goes against the arm (small, consistent losses; none significant). vs REF2-T: FAIL (information) | gated; S5 (the final number) may go; FREEZE ~20:00; CERT from Sun 01:30 |
| 45 GB | FAST + RELAX B (code and math answers) | HumanEval+ / math | x1.49 / x1.32 vs the exact control [K, paired, C 160] | decision 4 PASS; drift PASS as registered | stands; tonight's top-up can roll it back |
| 45 GB | chat | IFEval | E x1.46 [K, paired] | E PASS alone; E + HC8 KILL (84 vs 90) | ships EXACT until E runs without HC8 |
| 45 GB | agent turns | 17 long agent turns | - | AGENTFAST FAIL (85 blunders; QOM-KEEP carries it) | ships EXACT (stated limit) |
| 45 GB | FAST | 12 MBPP | 71.3 [K, qall, C 224] | none on MBPP yet | coverage check tonight |
| 12 GB | VERIFIED GREEDY (not exact: 2-4-row verify calls round differently from one-token decoding) | 16 HumanEval | 18.42 decode geo mean [K, 12GB-CLEAN Sat 00:28, alone, quiet; pooled 18.47; 13.66 with prefill; lifetime peak 11.144 GB] | deterministic (outputs = kp2's 16 / 16); not bit-exact; the ~12x comparison withdrawn | stands as verified greedy, with that label |
| 12 GB | FAST (top-2, theta 0.95) | HumanEval | ~36 [P, modelled] | map code PASS 1.22 %; the 12 GB FAST arm's T0 same-scores was KILL on 5 Nov (HumanEval+ 80.0 vs 91.7, IFEval 84 vs 90; T1039) | needs a measured run + a new same-scores (map STEP0-P1C queued Sat night) |
| 12 GB | FAST (theta 0.8, t80ck2) | HumanEval | 38.7-40.3 [K] | map code KILL 1.63 % | not releasable |

How tok/s is measured: a geo mean over prompts. The screen's 'steady' (tpsw = kept / (c2 - c0), checks >= 2) leaves
out the host work between cycles (~2.35 ms per check, so ~4 % high) and any wait placed there (NW's counter readback,
~4.75 ms). The release reports two figures:
- Headline: whole decode (all time after prefill; prefill reported separately). The orchestrator's rule, 05:0x.
- The steady-state figure: full-period steady (all wall time after the first two checks).
'steady' rows above are labeled as such. The same-metric table for every arm is in findings note
2026-11-07_0500. On it, v1 = 142.1 whole decode (137.5 without NW v3), and 200 is x1.41 away.

Stated limits in any release: agent turns run EXACT; chat runs EXACT (or E without HC8 once its launch exists); every
code number names its workload (HumanEval is flattered by prompt copying); FAST outputs can differ between runs at
near-ties (BigMoE, Fri), so FAST quality is certified under 2 prompt orders.

Missing before a release table is complete:
- 45 GB EXACT quiet tok/s per workload (HumanEval, MBPP, math, IFEval) on the certified kernel at the release C.
- 45 GB FAST stack: MBPP, math and IFEval speed; same-scores on MBPP; the chat launch (E without HC8) and its gate.
- 12 GB: the clean verified-greedy run (alone, all 16 prompts, own footprint: Sat morning); the theta 0.95 point
  measured and gated; MBPP, math and chat numbers. No 12 GB exact claim.
- Lifetime phys_footprint for every released config (the RAM line is the lifetime peak, not MLX's peak).
- Everything at 2 prompt orders (FAST depends on cache state).

## 3. Write-ups (who writes, how long [P, the owner's estimate to confirm])

| piece | content | owners | time |
|---|---|---|---|
| Paper A (core) | exact 16-row speculative decoding of a 125B MoE on a laptop: batch-invariant kernels on the GPU and matrix units, streamed experts, the 45 GB exact line (12 GB: verified greedy, not exact) | BigMoE (engine), Leap (kernels), EvalSuite (certification), Fit12 + Breakthrough (12 GB) | ~2-3 days |
| Paper B (FAST) | drafter-certainty expert gating (Q1, Q1-UNION, QOM, U3), the comment rule, how lossy modes are gated (decision map + same-scores), and the negative results (agent turns, CD16, never-wait, split) | NewIdeas + Breakthrough + EvalSuite | ~2 days |
| Note C | SSD on Apple silicon: the wake penalty, wake-ahead ping, zero-copy reads, queue mixing | MoonShots | ~1 day |
| Note D | M5 kernels for MoE decode: NAX tiles, DN-KS (split-K per shape), att_single, QMM32 | Leap | ~1 day |
| Note E | the 12 GB two-pass certificate (P1-OEA) | Fit12 + Breakthrough | ~1 day |
| Appendix | the TRIED ledger (every idea, KILLs included), NOVELTY, PRIOR_ART | NewIdeas | ~0.5 day |

The public findings notes (~/FableGod/findings/) are the changelog; the 12 GB note already carries a dated correction.

## 4. Freeze and nights (UPDATED Fri 21:3x: Kamen wants everything finished by Sunday and published by Tuesday at the latest)

- Fri night (window open from 23:30, re-timed Fri 23:3x): the stack palindrome (+ T16 / B's rule / C 256 arms) ->
  Leap's 5-min idle check -> Fit12's clean 12 GB run (or earlier, if it fits first) -> EvalSuite's gate on the winner
  + both long-code top-ups + MBPP -> the map (nw3 first) and CERT's reference decodes.
- Saturday, each slot as soon as its input is in: S0 async post (if the idle check shows >= ~8 ms per check), S1 NW v3
  (map arm, then the engine A/B), S2 small built items, S3 leftovers, S4 short gate (by 16:00 at the latest), S5 the
  final number in the evening.
- FREEZE Saturday ~20:00: the S5 config is the release config. Anything after that is post-release research.
- Saturday night (Sun ~01:30-10:00): CERT, the release certificate on the frozen config. HumanEval+ 164, math 100 and
  MBPP 100 in 2 orders; IFEval only if a chat FAST profile ships. Plus the final quiet speed numbers per workload
  (45 GB EXACT and FAST, 12 GB verified greedy) and lifetime footprints, where the window allows.
- Sunday: fill the paper from the owners' report files. Monday night is the fallback for anything CERT misses.
- Publish by Tuesday at the latest, if Kamen confirms date, scope and venue.
