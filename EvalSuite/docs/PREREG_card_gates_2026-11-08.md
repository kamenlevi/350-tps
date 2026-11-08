# PREREG: the model card's benchmarks as fast-vs-exact gates (Sun 2026-11-08 12:0x; before any row)

Written before any row of any arm or reference.
> (a quote from the project owner, kept private)
  Not something new".
  - Scope: IFBench, LiveCodeBench v6 and GPQA Diamond. The card (models/bare/README-upstream-qwen.md, Qwen3.8-Flash-Next)
    gives 81.3, 91.9 and 91.7, in thinking mode with sampling. HLE is skipped (gated).
  - Arms: L + COH (the config we publish) vs NAX6-N first, then M1-B and the stack as time allows.
- **Placement:** NewIdeas 11:3x. The 45 GB arms run in the evening window (~4 h, ending by 22:45); the subsets are
  EvalSuite's choice.

## The sets (tools/card_items.py)
Items are in data/items and sources in data/raw; neither is pushed. All are non-thinking chat template and greedy, as
every dec_ set.
- **IFBench** (allenai/IFBench cd189a9c2889, 300 prompts).
  - The prompt is the user turn; max 1,536 tokens.
  - Grader: the official one, vendored verbatim in evalsuite/ifbench (only the package imports made relative).
  - Metric: prompt-level loose, the paper's headline. Its README generates at temperature 0. Strict is information.
  - Check: on the repo's sample outputs, EvalSuite's scorer equals the official run_eval.py flow on 300 of 300 prompts
    (strict and loose). The repo's own eval files differ on 3 of 288, from checker changes made after they were written.
- **GPQA Diamond** (198, data/raw/gpqa_diamond.csv), generative.
  - openai/simple-evals 652c89d0ca9d: QUERY_TEMPLATE_MULTICHOICE, with the options in its first-repeat permutation
    (random.Random(0), one rng.sample(range(4), 4) per row in file order).
  - Max 2,048 tokens. Score: the first ANSWER_PATTERN_MULTICHOICE match equals the gold letter.
- **LiveCodeBench v6** (livecodebench/code_generation_lite rev 0fe84c3912ea, test6.jsonl, sha256 bb4c364f7192...).
  - The window is 2025-02-01 <= contest_date < 2025-05-01, the Qwen cards' "v6 (25.02-25.05)"; this card names no window.
  - 131 problems: AtCoder 82 (easy 18, medium 19, hard 45) and LeetCode 49 (13 / 20 / 16).
  - Prompt: LCB's OpenAIChat messages (SYSTEM_MESSAGE_GENERIC + the generic question template, lcb_runner 28fef95ea8c9).
    Max 2,048 tokens.
  - Grader: LCB's run_test, vendored verbatim (evalsuite/lcb), on the public + private tests. It allows 6 s per test, uses
    the official global timeout, and passes a row only when every test passes.
  - EvalSuite's driver (evalsuite/lcb/grade.py) adds:
    - `python -I` in its own process group, in an empty temporary directory;
    - a kill above 3 GB resident memory;
    - a verdict cache keyed by (question, code sha), so identical code always gets the same verdict;
    - private tests unpickled with no globals allowed.
  - Dry run: 7 of 7 hand-written cases as expected (stdin and call-based pass, wrong answer, timeout, memory kill, no code).
- **Gate keys** (tools/card_keys.json, 381): IFBench 150 and GPQA Diamond 100 (random.Random(1108).sample of the sorted
  keys), plus all 131 LCB problems.
  - Why subsets: one arm in two orders must fit one evening window. That is ~450K tokens, at NewIdeas' 38-45 tok/s plus
    the per-process start (the chat gate ran 23-26 tok/s whole wall on ~320-token rows).

## Typing (the screens' rule())
Checked on the gate keys; the result is the same in scripts/r57_screen.py and the chs4 / chs5 / fu snapshots.
- IFBench: chat 141, math 6, code 2, agent 1.
- GPQA Diamond: chat 67, math 33.
- LCB: code 131.
- So M1-B's chat lever (MTP drafts gated by QOM) acts on IFBench and two thirds of GPQA, wherever its env puts QOM on
  those sets. Unlike MGSM (all math), these sets test it.
- **No screen's SETOF maps ifbench, gpqad or lcb6 yet.** Each arm's env must name a snapshot that does; runner 61 stops
  otherwise (dry run 11:52: it stopped on chs4).

## Reference: NAX6-N's AR -> results/ref2tnaxn.r6 (runner 61, CARD_STAGE=ref)
- The decode stage on the converted store, in the same environment as CERT's references and runner 60's stage 0.
- C is chosen by free memory: 192, 160 or 128 (need 36 / 32 / 27 GB). ref2tnax's rows were made at C 192.
- **Line check before any chunk below C 192:** 12 IFEval rows decoded at that C (results/ref2tnaxn.r<C>) must be
  token-identical to ref2tnax's. If they are not, that C is not used and the stage waits for 40 GB. A pass lets the
  reference run by day in Kamen's ~36 GB.
- Cost, estimated from NAX6-N's own rows (11-14 tok/s per row on IFEval / math): ~225K tokens (range 190-300K), ~5-6 h.
  It resumes across windows.

## Arms (runner 61, CARD_STAGE=arm), in this order
1. **L + COH (lcoh):** the config we publish.
2. **M1-B (m1b):** chat_env + COH.
3. **The stack:** as time allows.
- **Env files.** BigMoE writes one per arm, naming a snapshot whose SETOF maps the three sets. The env applies the
  per-set levers as the shipped config would apply them to these prompts: R57_QOM_SETS gains lcb6 wherever it holds the
  code sets, and ifbench / gpqad wherever it holds the chat sets. BigMoE states the mapping in the env file's comment.
- **Engagement:** every row of each set in the env's R57_QOM_SETS must show QOM optional uses, else the arm is VOID
  (runner 60's check).
- **Two orders:** forward is the keys sorted, then reverse. 20 prompts per process, the screen's CAP 2,048, each row cut
  to its item's max_tokens (r57rows).
- **Cost:** ~450K tokens (range 380-600K) for both orders, ~3.6 h (range 3-4.6 h). An arm that runs out of window
  resumes in the next one (CARD_RESUME=1).
- Runner 61 keeps runner 60's checks: code pin, manifests, the snapshot pin, memory, swap and the day rule.

## The lines (vs NAX6-N, per arm)
1. **Decision 4 per benchmark and order:** paired delta > -5 pt AND exact McNemar p >= 0.05 on the gate keys, no stage
   2. DIFFERS (HIGHER) passes. A benchmark PASSES only in both orders.
2. **Card gate PASS = all three benchmarks PASS.** A FAIL names its benchmarks and orders.
3. **Reading:**
   - A FAIL with McNemar p >= 0.05 (the delta alone) is reported as "FAIL (delta only)". It is still a FAIL.
   - VOID: the code checks or engagement fail.
   - INCOMPLETE: a "no free slot" abort or missing rows.
- **M1-B:** a PASS is a verdict on known benchmarks in its own right (the orchestrator). The typing above means it
  covers M1-B's chat lever.

## Information (no verdict)
- Scores per benchmark for the arm and NAX6-N: IFBench strict; LCB by difficulty and platform; GPQA by domain.
- Rows token-identical to NAX6-N, order agreement, cap hits, rough tok/s.
- The card's numbers, for orientation only (see the anchor below).

## Known limits
- **Non-thinking greedy.** The card's numbers are thinking mode with sampling. FAST levers on long thinking traces are
  not tested here.
- **Power at these N.** Take a lossless arm whose rows differ from NAX6-N on 10-15 % of keys, in random directions. Then
  Decision 4's -5 pt delta fails it in one order with these chances:
  - ~5 % at 10 % discordance (N 100);
  - ~15 % at 15 % discordance (N 100);
  - ~7 % at 15 % discordance (N 150).
  - Over 3 benchmarks x 2 orders, a lossless arm fails somewhere with a real chance (~25-50 %). That is the price of one
    evening per arm. The full sets (IFBench 300, GPQA 198) cut it to ~2-5 % per order. They cost ~+236K tokens per arm
    (~+1.7 h) and ~+118K on the reference (~+2.5 h).

## The card anchor (the orchestrator's question; not a gate)
- **Cost of exact in the card's mode.** That means thinking mode, sampling (temperature 1.0, top_p 0.95, top_k 20) and
  long outputs. Assumed lengths, typical for thinking models and not measured here: GPQA 6-10K tokens, LCB 12-25K,
  IFBench 1-3K.
  - The full sets, one sample each: ~4.6M tokens.
  - NAX6-N's AR at ~14 tok/s: ~90 h of 45 GB GPU. A FAST engine at ~40 tok/s: ~32 h, but that is the lossy engine.
  - The card may average several samples per item; it does not say.
- **It cannot be compared with the card at fine resolution:**
  - **The weights differ.** NAX6-N is our 45 GB tiered 3/4-bit quantization; the card's numbers come from the vendor's
    own serving stack. A card comparison measures quantization plus harness, not lossy vs exact.
  - **The settings are not stated.** For these rows the card gives no sampling settings, sample count, max length,
    prompt templates or LCB window.
  - **Sampling noise.** One sample per item leaves 95 % half-widths of ±3.8 pt (GPQA, 198 at 91.7 %), ±4.4 pt (IFBench,
    300 at 81.3 %) and ±4.7 pt (LCB, 131 at 91.9 %).
  - At best a full replication says "within ~±4-5 pt of the card": it can show gross breakage, not parity.
- **Recommendation: no card-mode run now.** If Kamen wants a sanity anchor anyway, the cheapest informative one is
  IFBench in thinking mode on NAX6-N: ~0.6M tokens, ~12 h of AR, ±4.4 pt, as information.

## Amendment 1 (Sun 12:0x, before any row): the extension rule, and the reference after Strata
- **The orchestrator 11:5x, verbatim:** "if an arm fails a single order only on the -5 pt delta (McNemar p >= 0.05), that
  benchmark is extended to its full set in both orders before it counts as a fail. A McNemar p < 0.05 stays a fail at
  once." The subsets stay as registered.
- **Reading, fixed now:**
  - **PENDING:** a benchmark where exactly one order FAILS with McNemar p >= 0.05 and the other order passes.
  - **FAIL at once:** both orders FAIL (even on the delta alone), or any order FAILS with p < 0.05.
  - **The full sets** (tools/card_keys.json "extend"):
    - IFBench: 300 (+150).
    - GPQA Diamond: 198 (+98).
    - LCB: the whole test6 file, 175 (+44 problems dated 2025-01-04 to 01-26). The gate's 131 are already the whole
      25.02-25.05 window.
  - **The extension:**
    1. NAX6-N's rows on the added keys (CARD_STAGE=ref CARD_EXTEND=<sets>).
    2. The arm's rows on the added keys in both orders (sorted, then reverse), appended to the arm's two runs
       (CARD_RESUME=1 CARD_EXTEND=<sets>).
    3. The benchmark's verdict: Decision 4 per order on the full set (set_d4 with SET_D4_N), PASS = both orders. It is
       final: there is no further extension.
  - **The card gate:**
    - PASS: all three benchmarks PASS.
    - FAIL: any benchmark FAILs.
    - PENDING: an extension is due and no benchmark FAILs. When another benchmark already FAILs, no extension runs,
      since the gate's verdict cannot change.
  - **Cost of an extension** (both orders, then the reference):
    - IFBench: ~100K tokens (~0.8 h), reference ~1.3 h.
    - GPQA: ~137K (~1 h), reference ~1.6 h.
    - LCB: ~70K (~0.5 h), reference ~0.8 h.
- **The reference waits (the orchestrator 11:5x; NewIdeas' order 11:5x).** NewIdeas' order is Strata -> BigMoE's PFB ->
  Breakthrough's two short screens -> the card reference (by day) -> an evening arm, if one fits before 22:45. Mon 07:05
  takes the arm work left over.
  - Runner 61's reference stage starts only when all three hold:
    1. Strata has ended: ~/StrataEval/h2h/logs/waiter.log's last line is WAITER END, or
       ~/StrataEval/h2h/results/DRIVER_DONE exists.
    2. BigMoE's PFB waiter (CARD_AFTER_PIDS, pid 71508: turn45.sh running scripts/pfb.sh) has exited, or 60 min have
       passed since Strata's end (CARD_AFTER_MAXWAIT: PFB had the free 47 GB first; a PFB that could not start does
       not hold the reference all day).
    3. A 10 min grace for the queue's short jobs has passed.
  - Each chunk also waits while another session's MEM job runs, as before.
- **The LCB item file** now holds all 175 test6 problems, each with a "window" flag. The gate keys and the other two item
  files are byte-identical to 9af1abb's (checked).
- **Verified, dry:**
  - The verdict block on synthetic runs: a p < 0.05 FAIL beats a pending extension, and a single-order delta-only miss
    (-6 pt, p 0.18) reads "PENDING: extend gpqad".
  - Runner 61's dry runs:
    - the reference stage shows 381 keys, or 523 with gpqad + lcb6 extended;
    - the arm refuses CARD_EXTEND without CARD_RESUME=1;
    - the arm still stops at the SETOF check.

## Amendment 2 (Sun 12:1x, before any row): the reference runs now, in short chunks, and yields to Strata
- **The orchestrator 12:0x** replaces amendment 1's "after Strata": "start the card reference now, in 10-prompt chunks,
  once Fit12's T2 is done". About 36 GB is free with Chrome open; one > 5 GB job by day.
  - Fit12's T2 (chw15p) ended 12:04; its report is written.
- **Yield rule, the orchestrator's:** before each chunk, if `pgrep -x "Google Chrome"` finds nothing, Strata is about to
  take the Mac, so no new chunk starts.
  - Resume needs Strata's waiter.log last line WAITER END (or DRIVER_DONE), then BigMoE's PFB waiter (pid 71508; at most
    60 min), then no quiet lock held.
  - Once Strata has ended, Chrome is not checked again.
- **Runner 61's reference stage:**
  - Chunks of 10 rows: `--max-rows 10`. The 12-row line check runs as one chunk.
  - Before each chunk:
    - the yield check;
    - no quiet lock held;
    - no other MEM > 5 GB shared run;
    - swap <= its value at the start + 2 GB, else the stage stops;
    - the C / line-check rule unchanged.
  - Cutoff Sun 22:45; it resumes on a rerun.
- **The reference's rows do not depend on this schedule.** Every chunk is the same exact AR decode stage. Only a C
  below 192 has its line check.
- Mock-tested: the yield function returns at once while Chrome runs or Strata has ended. With Chrome gone it waits for
  Strata, then the PFB waiter, then quiet locks, then resumes.
- **A failed start, 12:06:54 to 12:07:3x, with no row.**
  - What happened: the first line check's run name (ref2tnaxn.lc160) is not a name the decode stage takes, which is
    `<variant>.r<digits>`. The stage exited in 5 s before loading the model, and the runner kept retrying.
  - I stopped it by pid (the runner and its sleep) and ran peer unlock; no lock was left. Its log is
    results/day61_ref_runner.lcname_1206.log.
  - Fix (fdab3dd): the line-check runs are ref2tnaxn.r<C>, and a line-check decode that fails with no row now stops the
    runner.
