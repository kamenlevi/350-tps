# PREREG: does Claude Code work with our local model? A tool-call probe and 12 coding tasks per memory setting (written Tue 2026-11-10 23:xx; before any run)

Written and committed before any run of this test.

- **Request:** Kamen's top priority, relayed by the orchestrator at 23:0x: full Claude Code support with our local model by
  Thu 12 Nov 17:00. This test says whether it works.
- **Who:** EvalSuite designs and scores it. Leap owns the server and the sandbox, and its runner runs the test.

## What runs
- **Claude Code:** the real binary /Users/kamen/.local/bin/claude (its version goes into the run log), with an isolated
  CLAUDE_CONFIG_DIR and Leap's environment (tools/claude_local.sh):
  - ANTHROPIC_BASE_URL set to the local server, ANTHROPIC_AUTH_TOKEN=local;
  - model exactstream, side lane exactstream-side, subagents exactstream-sub;
  - Leap's context-window variables, and CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1.
- **The call:** `claude -p "<prompt>" --output-format stream-json --verbose --max-turns 25 --allowedTools Bash Edit Glob
  Grep Read Write`.
- **The server:** Leap's tool-mapping serve.py and agentio.py (working copy ~/Leap/release/cleanclone/agent/clone). It is
  pinned at a Leap commit on Wed morning; the hash goes below as a dated line before the first run. The runner starts it
  per setting with `serve.py --mem 45 | 32 | 24`.
- **The sandbox (Leap's sandbox-exec profile):** it covers Claude Code's whole process tree.
  - Writes go only to the task folder, the isolated config folders and the temp folder.
  - Network goes only to localhost, and private home folders are unreadable.
  - Bash, python3 and git run inside it.

- **Pinned server (dated line, Tue 23:2x, before any run):** Leap commit **39947b1** (2026-11-10 23:23:19, ~/Leap,
  release/next, with SHA256SUMS). Its SHA256SUMS lists serve.py c9d0e5b5051fbea1..., agentio.py 60e4520efc8de3e3...,
  tools/claude_local.sh e5b900fae5fada10... and tools/claude_code.sh 0752be2a042cc66f....
  - **Re-pinned before any run:** Leap first named 243874c, then 39947b1 at 23:2x.
  - Between them serve.py and claude_local.sh are unchanged (EvalSuite checked SHA256SUMS and the diff). agentio.py only
    adds a `compact` flag to the request metadata meant for BigMoE's cache, which marks Claude Code's compaction
    requests. The rendering, tools and lanes are unchanged. tools/claude_code.sh is a new launcher helper.
  - The other changed files are Leap's notes, tests and its runner (data/agent_cc_1111). EvalSuite spot-checked
    agentcc_tasks.py against this PREREG: the per-setting timeout, the process-group kill, the check copied in after
    claude, and the results.jsonl fields.
  - The runner stops if the clone's files differ from those sums. Each run folder records provenance.txt: the sha256
    checks, the commit, `claude --version`, the manifest's sha256, the setting and the port.
  - Leap's smoke test with a stand-in engine (t01, t11) checked the plumbing only: git commit, transcript, check rc 1,
    results.jsonl. It is not a run of this test.
  - The task runs send a tools array byte-identical to data/agentcc/cc_tools_2.1.321.json. Neither Python has pytest, so
    the tasks rely on unittest.
- **Schedule (Leap):** 32 GB from 00:30 Wed (last start 04:00); run folder
  /private/tmp/claude-501/-Users-kamen-OjoX/f2971937-6c95-4e86-a049-05beff6a8e32/scratchpad/agent/agentcc_runs/32_1111.
  45 GB on Wed night. 24 GB tonight only if time is left.
  - **Schedule moved (dated line, Wed 01:2x, before any run; the design is unchanged):** the night window is now
    01:00-14:00 (Kamen, via the orchestrator). Leap re-armed the same runner on the same folder and pin (its runner.log:
    "from 2026-11-11 01:00:00, last start 2026-11-11 08:00:00"). Two short Leap jobs go first, so the start is expected
    around 02:15-02:30.
  - Leap's cached runs (BigMoE's conversation cache) are on hold. Any such run is a new server config, and it gets its own
    amendment here before it starts.

## Settings and order
| Setting | Role | Timeout per task |
|---|---|---|
| 32 GB | verdict (the fast setting today) | 1,200 s |
| 45 GB | verdict, if it completes by Thu 12:00 | 3,000 s |
| 24 GB | information, if time allows | 1,200 s |

- **Order:** 32, then 45, then 24. A setting missing any of the 30 probe calls or the 12 tasks has no verdict.
- **Why 45 GB gets a longer timeout:** without a conversation cache every turn re-prefills ~12K tokens. Leap measured or
  priced the time to first token at 30.5-32.2 s at 24 GB, ~28 s at 32 GB (PF-A) and ~95 s at 45 GB.

## 1. The tool-call probe (tools/probe_cc.py)
- **The calls:** 30 calls on the server's Anthropic endpoint (/v1/messages). Each carries Claude Code's real tools array,
  which Leap took verbatim from a Claude Code 2.1.321 session.
  - The file is data/agentcc/cc_tools_2.1.321.json (14 tools, sha256 2a0590bd15df5ef4...). It is not committed, because
    it is Claude Code's own text.
  - A short system prompt names the working directory.
- **The cases:** 5 each for Read, Bash, Grep, Glob, Write and Edit. Each Edit case carries a prior Read turn, as Claude
  Code requires.
- **A call passes when all of these hold:**
  - a tool_use comes back;
  - every tool name used is in the array (no invented tool);
  - the first tool_use is the expected tool;
  - its input fits that tool's input_schema (required keys, types, enums);
  - the case's own checks hold;
  - file_path is absolute for Read, Write and Edit.
- **The scorer was self-tested** on ideal inputs (all pass) and on bad ones (a wrong type, a missing key and a relative
  path are all flagged).
- **Line, per setting:** at least 28 of 30 pass AND 0 calls with an invented tool.

## 2. The tasks (tools/agentcc_build.py -> agentcc/manifest.json)
| Id | Task | The hidden check |
|---|---|---|
| t01_fix_test | fix the bug a failing test shows | the tests pass, the test is unchanged, extra cases hold |
| t02_add_function | add slugify() and its unit test | hidden cases, a test added, the tests pass |
| t03_config | two edits in config.json | the exact final JSON (other keys unchanged) |
| t04_traceback | fix a bug from a pasted KeyError traceback | hidden cases, report.py prints 23.0 |
| t05_rename | rename a function in 4 files, tests included | no old name left, call sites and tests work |
| t06_cli_flag | add an argparse --shout flag | both outputs exact |
| t07_import | fix an import after a module move | no file moved, the import and a call work |
| t08_readme | add a Usage section with a fenced command | heading, fenced command, old text kept |
| t09_refactor | extract a duplicated formatter | the helper exists, the outputs are unchanged, one copy left |
| t10_type_hints | annotate every function | the AST has every annotation, the behaviour is unchanged |
| t11_shell | fix a line-count shell script for subfolders | prints 7 |
| t12_requirements | add a pinned line to sorted requirements | the exact final file |

- **Validated:** `python3 tools/agentcc_build.py --validate` shows that each check fails on its template and passes on
  template + reference solution, for all 12 tasks.
- **The checks:** /usr/bin/python3 (3.9), standard library only.
- **Per task, Leap's runner:**
  1. copies the template to a fresh folder (git init and an initial commit);
  2. runs claude under the setting's timeout;
  3. copies the hidden check in as .agentcc_check.py (so the agent never sees it) and runs `/usr/bin/python3 -I -B
     .agentcc_check.py`, sandboxed;
  4. saves claude's stream-json transcript as <run>/<id>.jsonl, the server's request log, the check output, and one line
     in <run>/results.jsonl: id, claude_rc, timed_out, wall_s, check_rc.
- **A task passes** when its check exits 0 on the final repo state.
- **Line, per setting:** at least 10 of 12 pass (83 %).

## The verdict
- Per setting: **Claude Code works at that setting when both lines pass** (tools/agentcc_score.py prints AGENTCC <setting>:
  PASS / FAIL / INCOMPLETE).
- There is no reference run, because the cloud model is not run. Everything below is information.

## Information (no verdict)
- **Per task:** turns (the result's num_turns), time per turn (wall / turns), tool calls, tool errors, invented tools, and
  how claude ended.
- **Failure type** for each failed task; the first match wins:
  1. timeout;
  2. loop (ended at max turns, or 3 identical tool calls in a row);
  3. bad tool call (a tool name outside the session's tools, or a tool error that reports invalid input);
  4. gave up (no Edit or Write call);
  5. wrong edit (the rest).
- **Per probe call:** the reason for each failure.
- **From the server log:** time to first token.
- The scorer was tested on a synthetic run with one task of each type, and it labelled each one as defined.

## Amendment 1 (Wed 2026-11-11 03:53: after the 32 GB run, before any other run)
- **Why:** the 32 GB run (docs/RESULT_agentcc_32_2026-11-11.md) exposed two scorer bugs, both EvalSuite's.
  - Probe case 10's check rejected a correct `ls -la`, because it looked for the substring "-a".
  - The scorer flagged a false "invented" tool: the init event lists the subagent tool as Task, while the tools array
    sent to the model calls it Agent.
- **The changes** (tools/probe_cc.py and tools/agentcc_score.py, in this commit):
  1. Case 10's check accepts `ls` with any flag group containing a or A, or --all.
     - It was self-tested on 11 commands.
     - Re-checked on the 32 GB run's stored calls, only case 10 changes result.
  2. The scorer counts Agent as a session tool when the init event lists Task.
- **Disclosure:** both changes were written after seeing the 32 GB outputs.
  - The 32 GB verdict was scored under the registered checks, and it is not re-scored: it stays FAIL, 27 / 30.
  - The changes apply to every later run: a 32 GB task rerun, 45 GB and 24 GB.
- **Unchanged:** the lines (probe at least 28 / 30 with 0 invented; tasks at least 10 / 12), the cases, the tasks and the
  failure types.
- **Next:** the sandbox fix and any 32 GB task rerun get amendment 2. It is written when Leap sends the profile change,
  the folder and the start time, and before that run starts.

## Amendment 2 (Wed 2026-11-11 03:57: before the 32 GB task rerun starts)
- **What runs:** the 12 tasks again at 32 GB, in Leap's folder agentcc_runs/32_1111b.
  - Leap's runner is scratchpad/agent/agentcc_rerun.sh (sha256 d13479ba447ef9f4...).
  - There is no probe. It calls the API directly, so the sandbox could not have affected it.
- **The one change:** Claude Code's environment gets CLAUDE_CODE_TMPDIR=<run>/cctmp.
  - Claude Code then makes its temp folder for each working folder inside the run folder, which the profile already
    allows.
  - The profile generator is unchanged; only the run folder's path differs.
  - Leap's mock check (scratchpad/agent/bashfix_check.sh, 03:54, no GPU): without the fix it gives the same EPERM. With
    it the command runs, and a write to $HOME is denied.
- **Unchanged from 32_1111:**
  - the clone's serve.py, agentio.py and tools/claude_local.sh at pin 39947b1, checked against that commit's
    SHA256SUMS;
  - serve.py --mem 32 with its request log, on port 8124;
  - agentcc_tasks.py (sha256 3e84be3864b4017b..., the cold run's file), the manifest a44aaeeeefea, the base config and
    the launcher;
  - claude 2.1.321, the 1,200 s timeout, --max-turns 25 and the allowed tools.
- **Validity:** the run counts only if Bash works, meaning no Bash result in any task holds the EPERM mkdir error. Leap's
  runner stops at once if t01's transcript holds it.
- **Role:** information. The 32 GB verdict stays FAIL; it was set by 32_1111's probe half.
  - The tasks are scored against the registered task line (at least 10 / 12) with tools/agentcc_score.py under
    amendment 1. This is the task half, run as designed.
  - The scorer's AGENTCC line will read INCOMPLETE, because the folder has no probe. Only its TASKS line is used.
- **Information reported, as in the first run:** turns, time per turn, tool calls and errors, failure types, the Bash
  calls that ran, time to first token, and the server's lifetime peak.
  - Wall times include heat pauses: fanwatch freezes the server when it runs hot. The RESULT lists them from fanwatch's
    log.
- **Schedule:** it starts once T1d's runner (pid 75700) has exited and the Mac is free, expected ~04:45-05:00. The last
  start is 08:00, and the run takes about 95 min.

## Known limits
- **Small N:** 12 tasks and 30 calls bound the failure rate only loosely.
- **Small tasks:** they are single-step, Python plus one shell task, with no long sessions and no large repos.
- **Single-turn probe:** the probe tests the choice of tool and its arguments, not multi-step plans.
- **Timing:** these are times without a conversation cache. They are information for this build, not a speed claim.
