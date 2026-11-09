# W24: which arm goes to the 24 GB card gate (pre-registered Mon 9 Nov 19:1x, before any W24 data)

Target (Kamen 18:5x via the orchestrator): 120 tok/s WHOLE DECODE on HumanEval, lifetime peak under 24.0 GB, lossy allowed,
same scores on the known benchmarks before it ships (EvalSuite's card gate: IFBench, GPQA Diamond, LiveCodeBench v6, both
orders, vs NAX6-N; ~10 h at 24 GB). Arms and code: scripts/w24.sh, data/r57/snap/w24 (commits f3caa26 .. 4911bca).

**Valid arm:** all three sets ran (12 HumanEval, 12 MBPP, 12 IFEval), FAST PATH on every set (tier_calls = tier_chunk = 0),
lifetime peak <= 24.0 GB on every set, no aborts, no cut rows. Rows with a heat freeze are counted and named in the report.

**Pick:** among valid arms, the one with the highest HumanEval whole decode (pooled). If the best QOM-rule arm (w12, w12pf,
w10, w8: optional uses served only when resident) is within 5 % of the U3 arm (w16u: optional uses never served), the QOM
arm goes: it drops fewer expert uses, so it is the smaller quality risk. If no arm is valid, the gate waits and the next
step is the fix the report names.

**Reported for every arm:** HumanEval and MBPP separately, plus IFEval (chat): whole decode / whole request / first token
median / lifetime peak; kept per check; cycle median; SSD MB per kept token; QOM drop rate (C 256: HE 11.4 %, MBPP 12.2 %);
heat freezes. The gap to 120 = 120 / (HumanEval whole decode) for the picked arm, with what closes it.

**Then:** scripts/w24_card_env.sh <arm> -> data/stack/card_w24_env.txt (+ R57_HARD=1200), committed; NewIdeas and EvalSuite
told; the orchestrator gets the first number by SendMessage.

# W24c: does the 01:25 gate switch from w13t? (pre-registered Mon 9 Nov 23:1x, before any W24c data)

Orders, both applied: the orchestrator 23:0x to BigMoE ("If it beats w13t in a same-run comparison beyond the 4.6 % noise
you measured, commit the new env before 01:25; otherwise w13t stays") and the orchestrator 23:1x via NewIdeas (>= 120 tok/s
HumanEval whole decode under 24 GB, NewIdeas' number check, EvalSuite's dry run of the new env, all by 01:20).
Arms (scripts/w24c.sh; env only on snapshot w24 = 016cb7f): w13c / w13d = w13t as gated (first and last), w14a / w14b =
140 base + 28 sidecar slots, 14 rows, R57_D7B=all (only the 4-bit DFlash2 drafter; the gated w13t also holds the bf16 one,
1.14 GB, which drafts only math / agent-typed prompts). Diagnostics after the decision passes: w13a (w13t + R57_D7B=all),
w13b (141 base slots, 13 rows + R57_D7B=all), MBPP + IFEval for w13c.

**Switch to the 14-row config only if ALL hold** (scripts/w24c_compare.py prints conditions 1-4 with their values):
1. HumanEval whole decode pooled over all 12 prompts of w14a AND w14b (sum n / sum n/tps) >= 120.0.
2. No HumanEval row of w14a / w14b has a non-empty bad field (a PAUSED row makes the claim unclean: no switch tonight).
3. Lifetime peak (max of mem[1], mem[-1], 10^9 bytes) < 24.000 GB in w14a and w14b, and in w14a's MBPP and IFEval sets.
4. The w14 pair beats the controls' mean (w13c, w13d) by more than 4.6 % on the prompts unpaused and uncut in all four.
5. w14a's MBPP and IFEval sets ran: no aborts, no cut rows, 0 measured checks over 300 ms in unpaused runs (the fast path).
6. NewIdeas' number check (its board, 'MON 23:1x GATE-SWITCH RULE') and EvalSuite's dry run of the new env pass by 01:20.
Flag only: whether the two controls agree within 2 % (thermal drift is named in the result otherwise).
If any fails, w13t runs as committed (data/stack/card_w24_env.txt at 8f76fc3) and a 120 config gets its own gate Tue night.
**Switch mechanics:** data/stack/card_w24c_env.txt (the w14a env, committed before the run for EvalSuite's dry run) is
copied over data/stack/card_w24_env.txt and committed by 01:20; EvalSuite's start script reads the committed file at 01:25.
