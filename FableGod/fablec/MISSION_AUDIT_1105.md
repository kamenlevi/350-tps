# AUDIT, Thu 5 Nov 07:00: check the three new sessions' answers before anything is built

> (a quote from the project owner, kept private)

## Inputs
Three fresh Fable sessions answered overnight, each with a different amount of context:
- ~/FableGod/zero/ZERO.md (ZERO: the raw problem only, no project knowledge);
- ~/FableGod/goal/GOAL.md (GOAL: the goals + today's measured facts, no methods);
- ~/FableGod/full/FULL.md (FULL: everything).
Their briefs are the MISSION_*.md files beside each answer.

## For every idea (each session gives up to 3 + its bet)
1. **Numbers:** re-derive its arithmetic against our measured data.
   - Sources: ~/FableGod/KERNEL90.md, ~/NewIdeas/research/SWEEP.md, ~/TrainLab/notes/DRAFTER_PLAN_1104.md,
     ~/FableGod/RELAX_350.md, BigMoE's data, today's ~/FableGod/DAY9_2026-11-02.md.
   - Flag every number that is wrong or unsupported.
2. **Already tried?** Search ~/TRIED/TRIED.md and NOVELTY.md. Mark it tried-and-killed (with why), tried-and-alive, or
   untried.
3. **Prior art:** the closest published work you know, or "none found". MoonShots does the full web check afterwards.
4. **Value:** expected gain on our lines (tok/s at 45 GB code FAST / EXACT; MB per kept token at 24 GB), halved, times
   the odds.

## Deliver (by ~09:00; one file: ~/FableGod/fablec/AUDIT_1105.md)
- A ranked table of every idea: gain (halved), odds, cost, tried / untried, the number errors you found.
- Your top 1-3 picks for a <= 10-min test each, with the PASS / KILL line written now.
- One paragraph comparing the three context levels: did knowing less or more help, and how?
- Then one message to the orchestrator: your top pick in one line.

## Rules
Thinking and writing only: no GPU, no downloads, write only in ~/FableGod/fablec/. Marks [K] / [P] / [G].

## Added Wed 21:0x (orchestrator)
- If they have landed, also read MoonShots' two CPU screens from tonight (verdicts in ~/TRIED/TRIED.md):
  - FAR-AHEAD FORESIGHT: a drafter 8-16 checks ahead feeding Belady-like retention;
  - FULL's section 5: the comment-span relax test.
- Prior art the orchestrator found (standard web search; abstracts and summaries only):
  - Foresight:
    - MoE-SpeQ (arXiv 2511.14102): a quantized draft predicts future experts; a lookahead buffer plus lookahead-aware eviction.
    - SP-MoE (2510.10302): draft-based prefetch for the verify pass; deeper prefetch thrashed.
    - SPICE (2608.21240): confidence-aware adaptive lookahead.
    - Only an 8-16-check horizon may be new.
  - FULL's bet:
    - No paper found that relaxes acceptance only in code comments.
    - Lossy verification can inflate output length: arXiv 2610.23818 ("acceptance is not speed"; reported 1.34x accepted tokens per round but 1.54x longer completions at the most relaxed settings) and 2607.26627.
    - Check whether FULL's tok/s math survives longer comments. Require tokens per task and seconds per task in its engine test, not only tok/s.
