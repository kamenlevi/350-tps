# PREREG: plain FAST on long agent turns, against the agent bar (Fri 2026-11-06 08:09; before any row)

Written before any row of this check.
- **Request:** the orchestrator, Fri 08:0x-08:2x, after RELAX's agentlong finding (docs/RESULT_relax_drift_2026-11-06.md):
  - B (Q1-UNION gate + copy + comment rule + HC8) commits 20 blunders in 8,842 tokens of long agent writes (22.6 per
    10K, 16 inside the written code). Mission 7's agent bar is "none".
  - The orchestrator's call: B ships for plain code answers only. Agent turns run without the RELAX gate until they pass
    the agent bar.
  - This check decides how agent turns run: plain FAST, or exact.
- **The orchestrator accepted the line as written below (Fri 08:3x).** It goes before the code-only drift top-up.

## What runs
- **Mode:** today's plain FAST = QOM-KEEP + DRAFT17, no RELAX gate, on the exact base that ships:
  - NAX6-N if BigMoE's FAST-NAX A/B (Fri ~08:35) passes, else REF2-T.
  - It runs through BigMoE's `scripts/r57_screen_fast.py`.
  - BigMoE supplies the env, the commit and the exact base. They are added here, under "Recipe", before any row. The
    runner pins those files and stops if they change.
- **Rows:** dec_agentlong's 17 write / edit turns (data/items/dec_agentlong.jsonl, sha256 ea6211b4933c; built Thu by
  tools/drift_build.py from dec_agent):
  - real tool-call answers with 1.6-12K-token contexts;
  - max_tokens 1024, greedy.
- **Two prompt orders,** forward (key order) and reverse, each in its own process. QOM-KEEP's keep set depends on the
  cache state, so per docs/PREREG_TEMPLATE_cachedep.md the certificate needs two histories. 34 rows in all.

## Scoring: the mode's exact reference along FAST's own tokens
- A new stage replays each FAST row's committed tokens through the base's exact reference (`ref2tnaxn` = NAX6-N on the
  converted store, or `ref2tf0` = REF2-T):
  - the prompt is prefilled as replay.py does;
  - the committed tokens then go through in 16-row verify windows, all rows kept.
- This is the exact verify path. Its rows equal the reference's own one-token AR bit for bit: R-56c for REF2-T, NAX6
  Part 2 for NAX6-N.
- Per committed token it records:
  - the reference's probability p of that token;
  - the reference's argmax.
- **Self-check before any FAST row is scored:** the stage scores three of an exact run's own rows; every token must be
  the reference's argmax. The rows are results/ref2tnax's HumanEval/27 and ifeval/3409 for NAX6-N, or
  results/relax_control's agent rows for REF2-T. Else VOID.

## The line
- **PASS:** 0 blunders, i.e. no committed token with the reference's p < 0.01, over all 34 rows (both orders).
- **FAIL:** 1 or more blunders.
- **VOID:**
  - the self-check fails;
  - FAST's own counters show QOM-KEEP or DRAFT17 not engaged;
  - or a row is missing.
- **What it means:**
  - PASS: agent turns run plain FAST, without the RELAX gate.
  - FAIL: agent turns run exact.

## Information (no lines)
- The deviation rate (committed token != the reference's argmax), per order and per row.
- Where any blunder sits: the first tool-call parameter (the command / code) or later text (the description), as for
  B.
- Token agreement between the two orders. QOM-KEEP's cache dependence shows here.
- The first divergence from the exact control: the reference's own AR on the 17 turns, decoded when a slot allows.
- On the 11 edit turns: whether a copied span breaks off early.

## Runs and cost
- **GPU** (rough, from RELAX's measured agent rows; ~90 s prefill per turn):
  - FAST rows: 2 x 17 turns, ~50 min.
  - The scoring replays: 34 rows, ~85 min.
  - About 2.5 h on a shared lock, MEM ~36-45 GB, no timing line.
- **Slot:** today by day if the build is ready by ~12:00, ending by 15:00 (the orchestrator). Otherwise tonight, first.
- **Code:** the new scoring stage in evalsuite/, the runner, and BigMoE's script under a pin.
