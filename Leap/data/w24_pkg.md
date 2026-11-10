# 24 GB package: `--mem 24` (w13b as gated) in the local clean clone (Tue 10 Nov 08:4x-)

Asked by the orchestrator (Tue 08:4x): the w24 card gate passed on w13b at 08:41, and Kamen wants the 24 GB version out by
Wednesday. Built in ~/Leap/release/cleanclone/final/clone only; nothing is pushed, and publishing waits for Kamen's word.

## What was built (CPU only, 08:46-08:55)

- **Configs:** `configs/lossy-24.env` and `configs/chat-24.env`, identical (copies in data/w24_pkg/):
  - BigMoE's data/stack/card_w24d_env.txt env line verbatim (git blob e06f495e, commit 87dd1a3).
  - `C=100`: runner 61 took C from the env comment's "Sat 100".
  - `SNAPSHOT=w24`.
  - `R57_PFCHUNK=1024` on its own line. It equals the loop's default, so the gate ran this value.
    - W24e (BigMoE, Tue 09:00) keeps it. No smaller chunk qualified under the pre-registered rule (tokens AND hashes
      equal to 1024 on all six prompts).
    - 512 matched 0/6 and peaked at 24.345 GB. 256 got under 24 GB (23.954 GB) but matched tokens on 1/6 and hashes on
      0/6, with the first token 2.0-2.9x slower.
    - The repeat at 1024 matched 6/6 (25.025 vs 24.961 GB). Source: BM:data/w24/w24e_report.txt.
    - So the label stays: under 24 GB on prompts up to about 560 tokens, up to 25.1 GB on longer ones.
  - Parsed by the package's read_config: the gate's 42 keys and values are all equal, plus R57_PFCHUNK only.
- **Engine:**
  - `engine/loop/r57_screen_w24.py`:
    - Built by applying BigMoE's `diff -u data/r57/snap/rel1/r57_screen_rel1.py data/r57/snap/w24/r57_screen_w24.py`
      (the w24 file last changed at 016cb7f; 6 hunks) to the package's rel1 copy with `patch -F0`. It applied cleanly, so
      the added code is byte-identical to BigMoE's.
    - Then make_release.py's step-4 scrub: 1 quote in a new comment redacted, AST without docstrings unchanged. One
      comment reworded, AST unchanged.
    - The helper modules (inert_span, pflm, relax_delta, relax_span) are identical between BigMoE's rel1 and w24
      snapshots.
  - `engine/bigmoe/stream.py`: the only bigmoe/ change between 0b4df8c (rel1) and 016cb7f, patched with -F0. Its AST
    equals BigMoE 016cb7f.
    - It adds an optional `gate_req` bound that only R57_GATEREQ=1 sets. w13b does not set it, so it is inert for every
      config, 24 GB included.
  - ext/ is unchanged between the two commits.
- **run.py** (diff in data/w24_pkg/run_py.diff):
  - `--mem 24`; DEFAULT_C["24"] = 100.
  - read_config merges several env lines in order. Every existing config has one line, so they parse as before.
  - `snapshot(cpath)`: a config's `SNAPSHOT=` line picks its decode loop, else engine/loop/SNAPSHOT (rel1).
- **chat.py, serve.py** (local only, not committed): `--mem 24`, and the decode loop from the config via `R.snapshot`.
- **README** (clone): a 24 GB row in the configs table, with the memory label.
- **Dry run:** `run.py --config lossy --mem 24 --keys humaneval/0 --max-tokens 2048 --dry-run` printed lossy-24, C 100,
  cap 2048, snapshot w24, and the gate's env.
- **Differences from the gate's launch** (EvalSuite tools/day_runner61.sh, arm stage):
  - BIGMOE_EXT_BUILD is "build" in the package, against build_qom. Every package config uses one extension build; the
    45 / 32 lossy configs that ran build_qom in research matched their references on it (FINAL clean-clone test).
  - run.py sets R57_PROMPTS, HF_HUB_OFFLINE and PYTHONDONTWRITEBYTECODE.
  - run.py loads the engine its own way; the gate went through tools/r57_wrap.py.
  - The GPU replay below checks whether any of this matters.

## GPU checks (armed: data/w24_pkg/runner_w24.sh, queued after W24e and c47)

1. Replay 3 IFBench + 3 GPQA gate rows at the gate's CAP 2048 (no QOM on those sets). The tokens must equal
   ~/EvalSuite/results/card_w24_fwd/decode.jsonl, and the prompt tokens n_prompt. The GPQA / IFBench items go into the
   clone only for this run and are removed after (never published).
2. BigMoE W24d's 12 HumanEval keys (w13eh_100) at CAP 256: whole decode against 130.33 pooled, lifetime peak against
   23.78-23.82 GB, first token median against 3.54 s.

### Results (Tue 09:59:40-10:02:50; share lock 'MEM 26 GB', after c47, nothing else running; NO-SWAP 48 GB; swap flat at 6,683 MB)

| check | result | reference |
|---|---|---|
| replay, 3 IFBench rows (CAP 2048) | **tokens equal on 3/3** (60, 61, 63 tokens); prompt tokens equal (71, 39, 32) | card_w24_fwd/decode.jsonl |
| replay, 3 GPQA diamond rows (CAP 2048) | **tokens equal on 3/3** (627, 714, 798 tokens); prompt tokens equal (161, 222, 183) | card_w24_fwd/decode.jsonl |
| replay process | lifetime peak 23.79 GB; first token 3.39 s median | gate max 25.112 GB (on longer prompts) |
| 12 HumanEval (BigMoE W24d keys, CAP 256) | **tokens identical on 12/12** vs both of BigMoE's runs (w13eh_100, w13fh_100); 2,610 tokens | BigMoE W24d |
| HumanEval whole decode | **135.9 tok/s** (one pass) | 130.33 pooled (130.2 / 130.5) |
| HumanEval lifetime peak / first token | 23.78 GB / 3.63 s median (3.29-4.82) | 23.78-23.82 GB / 3.54 s |

- The packaged lossy-24 reproduces w13b exactly. Its tokens equal the gate's on the no-QOM sets, and equal BigMoE's on
  HumanEval, where QOM is on (the same 12 prompts in the same process order).
- It reaches the gated speed and memory: +4.3 % on HumanEval in one pass, a share lock with nothing else running.
- Files (data/w24_pkg/): check_summary.txt; he12.out with the run's log, runs.json, tokens.json and modules.json
  (cli_1110_100130); replay_runs.json (statistics only).
- The replay's decoded GPQA answers are NOT kept: GPQA text stays out of public files, as in EvalSuite's own records.
- The GPQA / IFBench items were in the clone only for the run and were removed after it.
- ~/Leap/data/pkg24_check.done was touched at 10:03 for BigMoE's W24f.

## Not verified: a 36 GB M5 Max (not available here)

- **Memory:**
  - The engine sets `mx.set_wired_limit(max_recommended_working_set_size)` (R57_WIRED=1). It never raises the system's
    limit, and sets no MLX memory limit; the MLX cache is capped at 0.25 GB (R57_CACHE_GB).
  - Here the recommended working set is 55.7 GB of 64 GB (81 %). On a 36 GB Mac it is reported at about 27-29 GB
    (not measured), against the gate's 25.112 GB lifetime footprint, which also counts CPU-side memory.
  - With a ~25 GB engine, a 36 GB Mac has ~11 GB for macOS and apps. Long prompts reach 25.1 GB. A browser beside it can
    push other apps into swap. The engine's buffers are wired, so they are not swapped.
- **GPU type:** MLX reports this Mac's GPU as `applegpu_g17s`. A Max chip reports a different suffix, and MLX picks some
  matmul tile shapes by that suffix. The logits' last bits, and so the tokens, can differ from these references there.
  The quality gate's scores should carry over, but nothing was run on that Mac. Speed scales with its GPU and SSD.
- **SSD:** ~24 MB read per kept token (W24d) is ~3.1 GB/s at 130 tok/s. A smaller or slower SSD lowers tok/s.
- **Disk:** the 68.5 GB converted store, plus ~20 GB free for swap; the conversion needs the model's own files beside it.
- **Cores:** nothing pins core counts. The C extension uses GCD's global queues, with one spinner thread at
  QOS_USER_INTERACTIVE; R57_PFD_THREADS=12 is PF-D only, which w13b does not use.
- **This Mac's tooling:** the engine checks ~/.local/share/quiet/PAUSE (this Mac's heat guard) every 50 ms. On another
  Mac the file does not exist, so nothing pauses.
- **Thermals:** a MacBook Pro's sustained clocks under a long run were not measured.
- **Time budget:** R57_HARD=1200 (in the gated env line) stops new checks after 1,200 s in a run.py batch. chat.py and
  serve.py lift it.
