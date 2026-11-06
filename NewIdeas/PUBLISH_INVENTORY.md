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
| QOM (sure rows skip cold ranks 2-9) | adapted | 45 GB FAST stack | NewIdeas + BigMoE | 5bb2743 | MD |
| 3-bit ranks 0-1 on drafter-sure rows (U3) | new signal (published mechanism) | 45 GB FAST stack | NewIdeas + Breakthrough | T103, T106 | MD |
| Q1-UNION (sure rows keep the check's union) | adapted (OEA) | RELAX B, code + math answers | NewIdeas | T993, T985 | MD |
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
| 45 GB | FAST stack (+ DN-KS, lazy, D7BNAX_32, att_single; no CD16) | 12 HumanEval | ~128-130 [P]; measured tonight | same-scores + 2 long-code top-ups tonight | pending tonight |
| 45 GB | FAST + RELAX B (code and math answers) | HumanEval+ / math | x1.49 / x1.32 vs the exact control [K, paired, C 160] | decision 4 PASS; drift PASS as registered | stands; tonight's top-up can roll it back |
| 45 GB | chat | IFEval | E x1.46 [K, paired] | E PASS alone; E + HC8 KILL (84 vs 90) | ships EXACT until E runs without HC8 |
| 45 GB | agent turns | 17 long agent turns | - | AGENTFAST FAIL (85 blunders; QOM-KEEP carries it) | ships EXACT (stated limit) |
| 45 GB | FAST | 12 MBPP | 71.3 [K, qall, C 224] | none on MBPP yet | coverage check tonight |
| 12 GB | EXACT (two-pass loop) | HumanEval | 18.4-18.9 [K, 11.4 GB lifetime] | exact to its own reference; near-ties depend on the draft pattern until PR1 is installed | stands, with that caveat |
| 12 GB | FAST (top-2, theta 0.95) | HumanEval | ~36 [P, modelled] | map code PASS 1.22 %; the 12 GB FAST arm's T0 same-scores was KILL on 5 Nov (HumanEval+ 80.0 vs 91.7, IFEval 84 vs 90; T1039) | needs a measured run + a new same-scores (map STEP0-P1C queued Sat night) |
| 12 GB | FAST (theta 0.8, t80ck2) | HumanEval | 38.7-40.3 [K] | map code KILL 1.63 % | not releasable |

Stated limits in any release: agent turns run EXACT; chat runs EXACT (or E without HC8 once its launch exists); every
code number names its workload (HumanEval is flattered by prompt copying); FAST outputs can differ between runs at
near-ties (BigMoE, Fri), so FAST quality is certified under 2 prompt orders.

Missing before a release table is complete:
- 45 GB EXACT quiet tok/s per workload (HumanEval, MBPP, math, IFEval) on the certified kernel at the release C.
- 45 GB FAST stack: MBPP, math and IFEval speed; same-scores on MBPP; the chat launch (E without HC8) and its gate.
- 12 GB: PR1 installed (or the caveat printed); the theta 0.95 point measured and gated; MBPP, math and chat numbers.
- Lifetime phys_footprint for every released config (the RAM line is the lifetime peak, not MLX's peak).
- Everything at 2 prompt orders (FAST depends on cache state).

## 3. Write-ups (who writes, how long [P, the owner's estimate to confirm])

| piece | content | owners | time |
|---|---|---|---|
| Paper A (core) | exact 16-row speculative decoding of a 125B MoE on a laptop: batch-invariant kernels on the GPU and matrix units, streamed experts, the 45 GB and 12 GB exact lines | BigMoE (engine), Leap (kernels), EvalSuite (certification), Fit12 + Breakthrough (12 GB) | ~2-3 days |
| Paper B (FAST) | drafter-certainty expert gating (Q1, Q1-UNION, QOM, U3), the comment rule, how lossy modes are gated (decision map + same-scores), and the negative results (agent turns, CD16, never-wait, split) | NewIdeas + Breakthrough + EvalSuite | ~2 days |
| Note C | SSD on Apple silicon: the wake penalty, wake-ahead ping, zero-copy reads, queue mixing | MoonShots | ~1 day |
| Note D | M5 kernels for MoE decode: NAX tiles, DN-KS (split-K per shape), att_single, QMM32 | Leap | ~1 day |
| Note E | the 12 GB two-pass certificate (P1-OEA) | Fit12 + Breakthrough | ~1 day |
| Appendix | the TRIED ledger (every idea, KILLs included), NOVELTY, PRIOR_ART | NewIdeas | ~0.5 day |

The public findings notes (~/FableGod/findings/) are the changelog; the 12 GB note already carries a dated correction.

## 4. Proposed freeze (the orchestrator's lean, checked against the windows)

- Fri night (now): the stack palindrome (no CD16) -> same-scores (HumanEval + math) -> both long-code top-ups -> MBPP
  coverage -> map (T1 xs arms, 24 GB arms).
- Sat night: one A/B of the dense levers that pass by Saturday (HC reads, GDN step, in_proj ks 2); the 12 GB theta 0.95
  point measured + gated; MBPP speed of the stack.
- Sun night: EvalSuite's F1; any last lever A/B; the chat launch (E without HC8) + its gate if built.
- Mon (end of day): CONFIG FREEZE. Nothing enters after it; bisects only before it.
- Mon night + Tue night: final quiet measurements of the frozen configs under 2 prompt orders: 45 GB EXACT and FAST on
  HumanEval, MBPP, math, IFEval; 12 GB EXACT and FAST on HumanEval and MBPP; lifetime footprints; any quality row still
  missing.
- Wed 11 Nov: publish, if Kamen confirms. Risk: a failed gate costs a night, and Mon / Tue have no slack, so every gate
  must have passed by Monday's freeze.
