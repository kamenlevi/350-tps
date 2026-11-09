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
