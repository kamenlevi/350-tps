# PREREG: RELAX, quality-defined modes on the 16-row live loop (Mon 2026-11-02 21:0x; revision 1 at 21:3x, before any row)

Source: the orchestrator's requests of 16:15, 18:3x, 19:5x and 21:22, built on:
- Fable's RELAX_350 and mission 25 (COMMENT_LOOPHOLE.md);
- cloud task 5 ("the 350 mode"), task 9 (exact 350: the gate is the deciding lever) and task 14 (the fast-mode test
  order).

The plan is docs/PLAN_relax_2026-11-02.md sections 6-9. **Revision 1** merges cloud task 14's order: the arms and modes
below replace the first version's A / D / C / B, the gate stays code-only except in the optional arm G, and the
contract is task results (deviation is a diagnostic). No row existed at either version. This file fixes the arms, the
rules and the lines before any row exists. None of these modes is exact, so adopting one is Kamen's call.

## Question
Does cloud 14's code fast mode keep REF2-T's scores (decision 4) without blunders or drift? So do its chat rules, and
what does each buy in kept tokens per check, expert bytes per check and tok/s?
- **The code fast mode:** the gate (top-2 experts on drafter-sure rows, plus the copy gate), the comment loophole and
  HC8.
- **The chat rules:** R1, R2 and, optionally, the gate on chat.

## Arms
One process per arm. Code: `pending/relax.py`, which moves to `evalsuite/relax.py` once runner 38 ends, unchanged
except for its location. Keys: `results/relax/keys_<arm>.txt`.

| arm (cloud 14) | sets (keys) | gate | acceptance | HC8 |
|---|---|---|---|---|
| control | HumanEval+ 60, the first 10 math, the first 20 IFEval (90) | off | exact | off |
| A, the gate alone (A) | HumanEval+ 60, math 50, agent 6 (116) | cf >= 0.99 + copy | exact | off |
| B, the mode (B) | as A | cf >= 0.99 + copy | exact, + the comment rule on HumanEval+ | on |
| E (E) | IFEval 100, multi 24 (124) | off | R1(0.5) | off |
| F (F) | as E | off | R1(0.5) or R2(top-2, 0.25 p1) | off |
| C (C) | HumanEval+ 60, math 50 (110) | cf >= 0.99 + copy | R1(0.5), + the comment rule on HumanEval+ | on |
| G (G, optional) | as E | cf >= 0.999 + copy | R1(0.5) | off |

- "math" is decision 4's 50 (math500 25 + gsm8k 25).
- The agent set is bash17-19 and edit00-02, with 9-12K-token prompts and the items' own max_tokens of 128. Every other
  prompt runs to its item's max_tokens.
- The order is control, A, B, E, F, C, G. If the slot runs short, drop G first, then C.
- Cloud 14's D (8-row chat, exact) is BigMoE's measurement, not an arm here.

## The harness
- **Base:** R-56d's `ref2to_gate16`, which was bit-exact against REF2-T's AR (36/36 prompts, 15,489/15,489 rows):
  - snap/leap-faff8e5;
  - tiers 4433333333 / 3c / C_l 112;
  - BIGMOE_TIER_COMBINE=1 and BIGMOE_OOO=1;
  - BIGMOE_MAXK=160 on build_next.

  The loop, drafter and commit are live16b's: DFlash2 L1-20 + Leap's l120_ft, 16-row checks, keep k+1.
- **cf:** the drafter's selector softmax over its 16 candidates at the pick (MTP Head's d02b_walk `chain_cf`). The
  picks are unchanged.
- **The cf gate:** row j verifies draft j and uses cf[j]. A gated row keeps ranks 0-1 at the model's own weights, with
  no renormalization: Q1's "mass".
  - Its ranks 2-9 point at its own rank-0 expert at weight 0.
  - Numerically this is the same as Q1's masking (every weight-0 slot adds an exact zero), but the 16-row id union the
    loader posts shrinks.
  - The mechanism is a wrapper on the streamed switch's `__call__`, active only inside the 16-row verify.
  - Row 15, the bonus after 15 kept drafts, is always exact.
- **The copy gate:** a row the cf gate leaves exact takes top-2 when its last 8 input tokens occur in the prompt. Those
  8 tokens are the committed tokens plus this check's earlier drafts.
  - The source is the prompt only. This narrows the plan's "window". The reason is COPYGATE's rule 1 and its precision
    table (~/FableGod/copygate/GATE.md 1.2 c): copies of the answer itself are where precision drops (MBPP 75 harms in
    455 hits, HumanEval+ 6 in 26), while prompt copies carry the coverage (HumanEval+ 3,572 hits).
  - The 99.7 % "sure inside copies" is SAFARI H2's.
- **The rules on G's row (gated or not):**
  - R1(delta): draft j is kept while logit(d_j) >= max logit - delta.
  - R2(top-2, 0.25 p1): draft j is kept while it ranks first or second on its row (strictly larger logits counted) and
    p(d_j) >= 0.25 p1.
  - "R1 or R2" keeps a draft either rule keeps.
  - The bonus is row k's argmax. Every rule keeps every draft the exact rule keeps, and the log keeps both k.
- **The comment loophole (B, C; HumanEval+ only):** R2 on a row whose draft sits inside a '#' comment. This is Fable
  mission 25's engine rule (COMMENT_LOOPHOLE.md):
  - It is checked by an incremental scan of the answer's text, token by token. The scan agreed with mission 25's
    `regions()` on all 1,439 comment tokens of REF2-T's HumanEval+ answers, apart from my two cuts.
  - Only inside the answer's ``` fence, never in its first two lines, and never in docstrings, strings or code.
  - Never on a comment whose text, with the draft or with the row's argmax, is or could become a tool prefix: `# type:`,
    `# noqa`, `# pragma`, `# fmt:`, `# pylint`, `# mypy`, `# -*- coding`, a shebang.
  - My cuts: the row must already be inside the comment before its draft (a drafted '#' stays exact), and a draft
    starting with a newline stays exact.
- **HC8 (B, C):** Q3's 8-bit hyper-connection mixers and PLE, `hc8_fake` as model.load applies it for ref2th8, before
  ref2.apply.
- **Logged per check** (`results/relax_<arm>/checks/<key>.jsonl.gz`):
  - the 16 input ids, cf, the gate kind per row, G's argmax per row, k under the rule and k exact;
  - logit(d) - max and the draft's rank per row;
  - the rows open to the comment rule;
  - G's top-64 log-probs on the committed rows;
  - the expert-union bytes, as run and for the same rows exact (per layer: unique ids x the pool's bytes per expert);
  - the process's SSD bytes, the loader's misses and io_s;
  - the draft, verify and commit ms.
- **Step 0, in every G process:** humaneval/HumanEval/27 with the gate and the rule off must equal its reference row
  token for token: results/ref2t, or results/ref2th8 for the HC8 arms. Its row hashes go to `step0/`. A failure is VOID
  (exit 5).
- **The exact reference (`pending/replay.py`):** REF2-T replays each arm's logged checks on its committed prefix. It
  uses the same 16 input rows, top-10 on every row, the same k+1 commit, no drafter and no timing.
  - Per committed token: E's argmax, E's log-prob of the committed token, and KLD(E||G) against G's top-64. The tail
    outside G's top-64 is lumped into one term.
  - Its step 0 replays a G process's step-0 rows and must match them bitwise. A failure is VOID.
  - It runs for the arms with a gate or HC8 (A, B, C, G). In the control, E and F, G runs REF2-T's own numerics on its
    own prefix, so E = G: E's argmax is G's, the committed token's log-prob is G's (row max + logit gap), and KLD is 0.

## Modes and verdicts
| mode | math | HumanEval+ | IFEval |
|---|---|---|---|
| ship (cloud 14: "ship B and E Friday if they pass") | B | B | E |
| A_E (the gate alone, B's control) | A | A | E |
| C_E (+ R1 on code) | C | C | E |
| B_F (chat + R2) | B | B | F |
| B_G (chat + the gate) | B | B | G |

- **Decision 4 (the contract)** against REF2-T on the mode's 210 rows: `tools/relax_report.py --score` builds
  `results/relax_mode_<m>`, then runs `evalsuite report --variant relax_mode_<m> --decode --ref ref2t` and
  `tools/d4.py`. Per set the paired delta must be > -5 pt and the exact McNemar p >= 0.05. Each set's line also reads on
  its own: math and HumanEval+ judge the code arm, IFEval the chat arm.
- **Mission 7's bars, from the mode's arms:**
  - Blunders: E's p of the committed token < 0.01. The bar is <= 1 per 10K committed tokens on math + HumanEval+
    pooled, and none on the agent rows of A / B. Any agent blunder counts as inside a tool call; the rows are tool-call
    turns.
  - Drift: on rows of >= 512 tokens, mean KLD(E||G) in the last quarter of positions <= 1.5x the first quarter, pooled
    per set. A set with KLD 0 in both quarters (no gate and no HC8 there, so G = E bitwise) passes. KLD 0 in the first
    quarter but not the last fails.
- **Verdict per mode:**
  - PASS: decision 4 passes and both bars pass.
  - BETWEEN: decision 4 passes and a bar fails.
  - KILL: decision 4 fails.
  - VOID: a step 0 fails. The arm reruns.
- Deviated tokens are a diagnostic, not a line (cloud 14).

## Predictions (information, not lines)
- **Deviated tokens along G's own prefix (diagnostic):**
  - Code: A ~1.3-1.6 % (map 1.34 % at 0.99; cloud 14 ~1.6 %); B about the same plus HC8's and the comment rule's
    share (mission 25: R2 in comments 1.37 % of positions, all in comments); C ~2.8 % (cloud 14).
  - Chat: E ~3.7 % (RELAX_350's R1 on IFEval); F ~7 % (R2's 7.08 %, above the int4 twin's ~5 %); G ~E + 3-4 points.
- **Kept per check, real** (first-order halved):
  - E on IFEval x1.05-1.10;
  - F x1.10-1.18;
  - the comment rule on HumanEval+ ~x1.03-1.06;
  - C's R1 on code ~x1.05.
- **Expert union per check on code** (map): -40.8 % at 0.99, plus a few points from the copy gate.
- **Copy gate coverage** (measured on CPU on REF2-T's own answers, Mon 21:06): rows inside a prompt copy are 53.8 % of
  HumanEval+ rows, 2.3 % of math and 1.4 % of IFEval. Most of these are cf-sure already. SAFARI's estimate for the
  added coverage on HumanEval+ is +3-8 points.
- **tok/s against the control** (bytes only, this harness, halved): A on code x1.08-1.15; B a few % more (HC8 ~-2-3 ms
  per check); C +~5 %.
- **Cloud 14's engine numbers** (by day / night): gate 0.99 ~96 / ~110 tok/s; + R1 ~100 / ~114.
- **HC8's own run** (decision 4 against REF2-T): math -4.0, IFEval -1.0, HumanEval+ -3.3, all 5 changed answers losses.
  B and C carry that on top of the gate.
- **My P(PASS):** ship 50 %, A_E 65 %, C_E 35 %, B_F 30 %, B_G 40 %.

## Information
For each arm and set:
- deviated tokens by cause: rule; rule in a comment; gate (cf); gate (copy); other (an ungated row whose context
  differs; with HC8, every row);
- the must-fix list (numbers, and any code or agent token);
- the gated share of rows;
- kept per check against the exact rule on the same checks;
- union and SSD GB per check, and per kept token;
- GB/s, defined as (union + dense) / verify;
- tok/s, paired against the control on the keys both ran;
- the standard table of the decode report.

## What it cannot say
- **No t 0.3 cut**, as in R-56d and the walks: 2-4 % of rows sit in a different check than in the engine.
- **Chat runs DFlash2's drafts in 16-row checks,** not cloud 14's MTP chain in 8-row blocks, so the R1 / R2 decisions
  on IFEval are DFlash2's: a per-token proxy.
- **Chat runs without HC8.** If HC8 ships globally with B, chat + HC8 is untested; an E8 arm (E + HC8, ~30 min) can
  be added on request. HC8's own run covered chat: IFEval -1.0, 1/0.
- **tok/s is EvalSuite's harness**, without the engine's K-73 / per-layer sizes, and bytes only: compute does not
  shrink. The ratio against the control is the number that transfers.
- **Agent rows stop at 128 tokens.** Drift comes from the 45 REF2-T rows of >= 512 tokens, plus whatever G writes long.

## Runs
- **Smoke** (share lock, ~45 min, ~33 GB at C 192 with "MEM 34 GB" in the reason), after runner 38 ends and
  `tools/relax_wire.sh` has moved the code into evalsuite/.
  - Keys: `results/relax/smoke_keys_<arm>.txt`, with output tag `smoke`. Every arm runs; A runs again with
    EVALSUITE_RELAX_GATE=mask (tag `smokemask`); then the replays of the control, A and B.
  - Checks (`tools/relax_smoke_check.py`):
    - step 0 in each process (B and C against REF2-T + HC8);
    - A's route rows equal its mask rows bitwise (EVALSUITE_RELAX_HASH=1 logs every committed row's hash);
    - the replay's step 0 matches bitwise, and the control replays bitwise on every row;
    - the gate shrinks the union on A, B, C, G;
    - HC8 is on in B and C.
  - NewIdeas: Tue by day after IFX and BigMoE's small screens, if it can start by ~14:20; else Wed by day.
- **Night** (quiet lock, C 256): Thu 00:30, after BigMoE's nightly combined run (GO from BigMoE).
  - Control, A, B, E, F, C, G: ~3 h with loads.
  - Then the replays of A, B, C and G at C 192: ~1.6 h.
  - If the slot runs short, drop G first, then C.
- **Report:** `tools/relax_report.py --score`, and a RESULT doc.
