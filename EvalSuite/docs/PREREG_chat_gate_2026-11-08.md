# PREREG: the CHAT150 chat gate, a ready same-scores line for lossy chat configs (Sun 2026-11-08 02:4x; before any row)

Written before any row of any chat candidate.
> (a quote from the project owner, kept private)
  a ready IFEval chat gate that can start within 1 h of a candidate. Candidates come from BigMoE as env files, like S4
  and C30. The first is M1-B: s5p_env + R57_QOM_SETS=humaneval,mbpp,ifeval,multi + R57_QOM_MTP=2, QOM gating the MTP
  head's chat drafts.
- **Why a gate is needed:** chat in v1' is already not exact. BigMoE's N45 found 6 of 24 IFEval runs equal to NAX6-N's
  AR; CERT amendment 3. Lossy chat levers need a same-scores line.

## Rows (RELAX arm E's form)
- IFEval, the 100 core prompts (dec_ifeval), and multi, the 24 behaviour prompts (dec_multi; max_tokens 384): 124 rows.
- Two prompt orders: forward = the keys sorted, then reverse. FAST may depend on cache state (QOM), so >= 2 histories.
- 10 prompts per process, at the C in the env file's comment.

## The config (the entry point)
- BigMoE writes ~/BigMoE/data/stack/chat_env.txt per candidate, in final_env / c30_env's format: 'Sat <C>',
  'MEM <n> GB' and 'screen data/r57/snap/<dir>/<file>.py' (a committed snapshot) in the comment.
- The runner applies S4's code checks unchanged:
  - every BigMoE module a process loads equals BigMoE's HEAD;
  - the manifests are equal across processes;
  - the store, swap, memory and the day rule.
- **Engagement:** if the env's R57_QOM_SETS holds ifeval / multi, every row of those sets must show QOM optional uses
  (else VOID).

## The lines (vs NAX6-N, the 45 GB rule)
1. **IFEval same scores:** decision 4 vs NAX6's IFEval rows (results/ref2tnax), per order: paired delta > -5 pt AND
   exact McNemar p >= 0.05, on the 100 core prompts, no stage 2. DIFFERS (HIGHER) passes. PASS = both orders.
2. **multi blunders:** the forward order's 24 multi rows, scored by tfwin against NAX6-N, as CERT and S4 score long
   code. Blunders (NAX6-N's p of a committed token < 0.01) <= 1 per 10K committed tokens.
- **Chat gate PASS = both lines.** A FAIL names its line.
- VOID: the code checks or engagement fail. INCOMPLETE: a "no free slot" abort or missing rows.

## Information
- IFEval vs REF2-T and REF.
- Rows token-identical to NAX6-N, per set and order.
- multi deviation rate.
- Token agreement between the orders.
- Cap hits.
- Rough tok/s from the runs (not an A/B).

## Runs
- Runner 59 (tools/day_runner59.sh, built from runners 54 / 58). Each candidate's outputs go to results/chat_<tag>_*,
  results/CHAT_<tag>_DONE.
- Cost: ~124 rows x 2 orders at ~45-50 tok/s ≈ 30-40 min, plus tfwin on 24 rows ≈ 10 min.
- It never runs during CERT; it starts after CERT's end, or when NewIdeas' queue says.

## Amendment 1 (Sun 09:2x, before any m1bi row): m1bi, the split of M1-B's multi FAIL
- **The candidate:** BigMoE's data/stack/chat3_env.txt (2187975), tag m1bi, dry run OK 09:19.
  - It is M1-B + COH with QOM on humaneval / mbpp / ifeval but NOT multi.
  - Same CHS4 snapshot (342f914), the same code pin as m1b (6b6a4fb64229), Sat 256, MEM 47 GB.
- **The lines are unchanged.** IFEval same scores in both orders, and multi blunders on the forward order.
- **What multi measures here:** S5' + COH with no QOM on multi. BigMoE: QOM_MTP only acts where QOM runs. That is the
  base config's first multilingual line; CERT had no multi line.
- **Reading, fixed now:**
  - multi PASS: QOM is the cause of m1b's multi FAIL.
  - multi FAIL: the cause is in S5''s own non-exact levers (the bisect is BigMoE's). The release config's multilingual
    chat would then be untested by CERT and failing.
- **Validity check (post hoc, from the screen's row stats):** every multi row must show no QOM optional uses
  (pf.qom_opt == 0). Otherwise the split is VOID.
- **A PASS is a diagnosis, not a shippable config.** In the engine, ifeval and multi are both type 'chat'. "QOM on
  English chat only" needs a request-level switch (e.g. by language or script) and its own gate.
