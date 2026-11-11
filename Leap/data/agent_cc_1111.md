> (a quote from the project owner, kept private)

Target (orchestrator): Thu 12 Nov 17:00, Claude Code working well on this Mac. One command starts the server and Claude
Code; tool calls reliable on EvalSuite's agent test; turns start in seconds with BigMoE's conversation cache; sessions to
64-128K tokens with compaction. Leap's parts: harden /v1/messages, compaction, wire the cache, real sessions + the
default memory setting, setup. The 1.1.0 candidate stays frozen; this is the next release (Leap release/next).

## Tue 23:0x-23:3x: /v1/messages hardened (release/next 2b03787, 243874c)

- **Several tool calls in one turn, several results back:** real Claude Code on the stand-in engine (a turn with two Read
  calls): it ran both and sent two tool_results; the next prompt held both. PASS.
- **Images / documents:** a block becomes "[an image was attached here; this model reads text only and cannot see it]"
  in user turns and in tool results (Claude Code's Read of a PNG): no error, the model is told. PASS.
- **tool_choice** auto / any / tool / none accepted (none = no tools). **stop_sequences** honoured, streamed and not
  (stop_reason stop_sequence + the sequence); OpenAI `stop` too. **max_tokens** caps the answer.
- **count_tokens** = the rendered prompt's length (275 = 275 in the check).
- **"prompt is too long: N tokens > M maximum"** (400 invalid_request_error) past --max-context: Claude Code 2.1.321 matches
  exactly `^prompt is too long: \d+ tokens > \d+ maximum$` (its own string table).
- **One engine queue, main > sub > side:** a main request queued after a side one runs first. PASS.
- **Keep-alive pings** every 10 s while a request waits or prefills (Anthropic `ping` events, SSE comments for OpenAI /
  Responses); a client that leaves mid-answer stops the answer at the next check; one that leaves while queued is dropped
  before it runs. PASS.
- Quota probes = max_tokens <= 4 (was 16: an 8-token main request was wrongly side).
- HTTP checks on the stand-in engine: **9 / 9** (harden_test.py).

## Claude Code 2.1.321's window settings (from its string table)

For a model it does not know, Claude Code assumes a window and says "set CLAUDE_CODE_MAX_CONTEXT_TOKENS to its real
window"; "To enforce it, set CLAUDE_CODE_AUTO_COMPACT_WINDOW=". claude_local.sh now sets both to EXACTSTREAM_CONTEXT
(default 131,072). A run's own usage line confirms contextWindow 131072 and maxOutputTokens 32000. Other knobs seen:
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE, CLAUDE_CODE_MAX_OUTPUT_TOKENS, CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT.

## EvalSuite's agent test (PREREG_agentcc_2026-11-11, 63218d0): Leap's runner

agentcc_night.sh <GB>: gates (Kamen idle, no lock / engine, NO-SWAP), a share lock, the pinned server (the clone's files
must match release/next/SHA256SUMS), probe_cc.py, then agentcc_tasks.py: per task a fresh folder (git init + commit), a
fresh Claude Code config folder, claude -p (stream-json, 25 turns, the manifest's timeout, process group killed on
timeout) in a sandbox (writes only in the run folder and temp; network only to localhost; ~/.ssh, ~/.claude*, ~/.codex,
Keychains, Mail, Chrome, Documents, Desktop, Downloads, ~/Papers and the chat sessions unreadable), then the check,
sandboxed. Smoke test on the stand-in engine (t01, t11): git, transcript, check, results.jsonl all as specified.
Armed: 32 GB from Wed 00:30 (Kamen's go for tonight: apps closed 00:29-07:30), then the 64K / 128K long-context runs.

## Tue 23:2x-23:4x: one command, and compaction end to end (release/next, this commit)

- **tools/claude_code.sh** starts serve.py (unless one already answers on the port), waits until it is loaded, runs
  Claude Code with claude_local.sh's settings, and stops the server it started when Claude Code exits; the server gets
  its own process group, so Ctrl-C in Claude Code does not reach it. Stand-in test: Claude Code answered, the server
  stopped afterwards, the port was free.
- **Compaction, real Claude Code on the stand-in engine:**
  - Auto-compact with a 24K window and two large reads: three compact_boundary events; Claude Code cleared old tool
    results locally (36.7K -> 12.7K tokens) and measured big results with our count_tokens. No error.
  - **/compact** (`claude -p --continue "/compact"`): the summary request uses **the session's own system turn and tools**
    (sys_end 10,017, 14 tools) plus a final instruction ("CRITICAL: Respond with TEXT ONLY. Do NOT call any tools. ...
    an <analysis> block followed by a <summary> block"); a reply with tool calls makes Claude Code retry once with a
    stronger paragraph; a proper summary is accepted and the session continues from it (13,865 -> 13,008 tokens).
  - So with the conversation cache a compaction re-prefills only its instruction. serve.py flags these requests
    (meta compact: true) for the cache.
- The billing-header line changes between requests of one session (cc_version=2.1.321.49c, then .655): dropping it from
  the rendered prompt (done on Tue) keeps the prefix stable.
- **tools/codex_code.sh** (Codex second): the same one-command pattern with codex_local.sh. Stand-in test: Codex ran its
  exec_command in its own sandbox (hello.txt written), finished, and the server stopped with the port free. Kept in
  data/agent_cc_1111/ tonight so that release/next stays at the commit EvalSuite pinned (39947b1); it moves there after
  the run.

## Tue 23:3x: BigMoE's conversation cache wired (a separate clone), T1 armed

BigMoE's convcache (BigMoE 7eb3401, conv/convcache.py; PF-A supported in one sweep, the taps lever in) is in a separate
clone, release/cleanclone/cache (release/next's server + engine/loop/convcache.py + the hook, serve_cache_hook.diff), so
tonight's pinned EvalSuite clone stays unchanged. The hook: CC.install(G()) at the first next_item (an import / install
failure logs "conversation cache off" and serve.py runs cold: checked on the stand-in engine); CC.hint(sys_end, lane, side,
conv) before each item; CC.last() into the done line and the request log. CONV_CACHE_GB defaults 0.6 / 2.5 / 6 by --mem;
DFlash2 throughout while the cache is on (BigMoE: an MTP-head turn can restore only from an MTP-head entry).
**T1** (t1_cache.sh + replay.py): serve.py --mem 32 with CONV_CACHE_CHECK=1 (every hit compared with a cold prefill),
replaying the 45 recorded requests of sessions_real_1110 in order. Night order: two quick checks -> T1 (00:29) ->
EvalSuite 32 GB cold (pin 39947b1) -> 64K / 128K runs. If T1 passes: the cached agent test on Wednesday (32, then 45 GB).

## Wed 01:01-01:13: T1 FAIL (5 of 12 hits bitwise); cause of 4 found (BigMoE's path rule); T1b armed

T1 ran at 01:01 (the 00:29 start moved to 01:00 by Kamen): serve.py --mem 32 (chat-32, PF-A, DFlash2) in the cache clone
with BigMoE's convcache 7eb3401 unchanged, CONV_CACHE_CHECK=1, the 45 recorded requests replayed in order
(data/agent_cc_1111/t1_32_1111/). 45 / 45 HTTP 200, 0 server errors, ready in 18 s. 33 misses (30 short ~700-token
requests and the 18-token quota probe: one chunk, never stored; the first prompt of each conversation), **12 hits: check
PASS 5, FAIL 7.** k = the replay index (30-36 Claude Code /v1/messages, 37-43 Codex /v1/responses):

| k | N | c (source) | new tokens | warm prefill | check |
|---|---|---|---|---|---|
| 30 | 12,302 | miss | 12,302 | 29.0 s | - |
| 31 | 12,496 | 12,288 (live) | 208 | 5.5 s | PASS |
| 32 | 12,300 | 9,216 (copy) | 3,084 | 12.4 s | FAIL B |
| 33 | 12,404 | 12,288 (live) | 116 | 4.1 s | FAIL A |
| 34 | 12,300 | 9,216 (copy) | 3,084 | 12.2 s | FAIL B |
| 35 | 12,404 | 12,288 (live) | 116 | 4.0 s | FAIL A |
| 36 | 12,627 | 12,288 (live) | 339 | 6.3 s | FAIL B |
| 37 | 8,390 | miss | 8,390 | 21.4 s | - |
| 38 | 8,491 | 8,192 (live) | 299 | 7.0 s | PASS |
| 39 | 8,388 | 8,192 (live) | 196 | 6.9 s | FAIL A |
| 40 | 8,479 | 8,192 (live) | 287 | 6.7 s | PASS |
| 41 | 8,573 | 8,192 (live) | 381 | 7.8 s | PASS |
| 42 | 8,389 | 8,192 (live) | 197 | 6.0 s | FAIL A |
| 43 | 8,617 | 8,192 (live) | 425 | 7.8 s | PASS |

(Warm prefill = the cached path alone; the check's own cold prefill, test-only, is excluded, so the logged first tokens
of 28-41 s include it.)

- **Signature A** (k 33, 35, 39, 42): "last logits, states (119 of 122), taps tail" at 116 / 116 / 196 / 197 new tokens;
  every hit with 208-425 new tokens on the same path passed. **Cause (BigMoE agrees, its bug):** convcache chose the
  prefill path by the new part (`N - c > chunk` -> PF-A), the loop by the whole prompt (r57_screen_rel1.py:987,
  `len(ids) > chunk`). A tail of one chunk or less therefore ran chunk-major (tier.prefill_call's compact scratch of the
  call's unique experts) while the cold prefill runs it inside the PF-A sweep (mode 1's full-E scratch on the original
  ids). pflm.py:15-17 already warns that E = 512 vs len(unique) changes MLX's gather kernel choice on short calls; the
  boundary (197 FAIL, 208 PASS) fits a kernel switch on the call's size; 119 of 122 leaves = from the first MoE call on.
  BigMoE's confound: all four also had N below the entry's previous prompt + reply (stale QSA rows past N); T1b replays
  the same order, so a PASS there rules it out.
- **Signature B** (k 32, 34, 36): "states (1 of 122)" only, last logits and taps tail equal: a copy restore at 9,216
  (3,084 new tokens through PF-A from c) and a live trim at 12,288 (339 new tokens chunk-major). The check did not name
  the leaf. BigMoE's suspects: the PLE layer's slots (chunk-major vs PF-A's own PLE staging), or a QSA raw / pooled leaf
  after a copy (the state setter resets the reserved capacity to c).
- **What it implies for PF-A itself:** at a hit the restored state at c is the cold PF-A's own (the 5 PASS rows) and only
  the tail's path differs, so PF-A (mode 1) and the default prefill should differ in bits whenever a prompt's last
  1,024-token chunk is short (under ~200 tokens). The earlier PF-A bitwise records never had a short last chunk (30K:
  292; 6,980: 836). Direct check below (T1b's runner, step 2).
- Ops: 01:14-01:25 the queue waited on a stale research PAUSE (fanwatch's 61-s heat pause at T1's end; its clear kept the
  file because `pgrep -f quiet_window.sh` matched a mere command line). The orchestrator fixed fanwatch and removed it.

**T1b** (t1b_pfa.sh, armed 01:28, after the two quick checks; BigMoE agreed): my copy of convcache.py = 7eb3401 + (a)
the path chosen by the whole prompt, `if PFLM and N > chunk` (PF-A from c, also for a one-chunk tail) + (b) the check
names each differing leaf (cache index:class[slot], warm vs cold shape) (convcache_t1b.diff). Step 0: BigMoE's stand-in
(conv/test_mock.py, MOCK_PFLM=1) on the patched module. Step 1: the same replay. Step 2: PF-A vs the default prefill at
exact-32 in the 1.1.0 clean clone, P = 5 x 1,024 + 116 and + 300, R57_LOGHASH=1, 64 tokens. Then the cold 32 GB agent
test (pin 39947b1, unchanged), then 64K / 128K. The cached agent runs wait for a passing T1.

## Wed 01:27-01:30: idle CPU of the 1.1.0 serve.py: one core, the extension's loader spin (lever: BIGMOE_IDLE_MS)

idle_cpu.sh (the orchestrator saw the agent server at ~100 % CPU while idle): the v110 clean clone's serve.py at --mem 24
and 32, one 16-token request, 10 s rest, then CPU time over 60 s idle: **100 % of one core at both settings** (24 GB:
47.4 -> 107.5 s; 32 GB: 68.0 -> 128.1 s; 52 threads). A 5-s `sample` (idle_cpu_1111/busy_thread_32.txt) shows one busy
thread, entirely inside bigmoe_ext's loader (no system call on its stack): the loader thread's idle pass ends in
`__builtin_arm_yield()` (engine/ext/bigmoe_ext.cpp:1804), i.e. it spins by design ("CPU (native thread): spin on the
sequence number", line 8). The ext already has the lever: **BIGMOE_IDLE_MS=n** (Breakthrough 11-02, bigmoe_ext.cpp:1521-1526,
in all three builds here): after n ms without a served call the loader naps 200 us per pass instead of yielding; calls
within a request come far less than 50 ms apart, so decoding never sees it; the first call after a long idle waits at most
~0.2 ms; timing only, so exact. Neither release/src (1.1.0) nor release/next sets it. Proposed: BIGMOE_IDLE_MS=50 as an
env default in chat.py / serve.py, after an idle-CPU + decode-speed A/B (a ~5-min job, next free slot); 1.1.0 is frozen,
so adopting it there is the orchestrator's and Kamen's call.

## Wed 01:32-01:45: T1b: signature A fixed (7 of 12 PASS); B = one leaf, QSACache keys at cache index 35, after a copy

T1b = T1 again (same replay order) on my patched copy of convcache.py (sha256 00488b23...; convcache_t1b.diff: (a) the
path chosen by the whole prompt, (b) the check names differing leaves). Data: data/agent_cc_1111/t1b_32_1111/.
- **BigMoE's stand-in** (conv/test_mock.py, one QSA + one GDN layer with the real cache classes, MOCK_PFLM=1) on the
  patched module: rc 0, 4 PASS / 0 FAIL, hits as expected (including its copy at 9,216).
- **T1b: 12 hits, PASS 7, FAIL 5; 45 / 45 HTTP 200, 0 server errors.** Signature A is gone: the Codex hits with 196 and
  197 new tokens now pass (all 6 Codex hits pass), and the 116-token Claude Code hits no longer differ in logits, taps or
  the other 119 states. Warm prefill with the fix: 2.8 s for 116 new tokens, 3.8-5.6 s for 196-425, 12.1 s for 3,084
  (cold 28.0 s for 12,302 and 21.5 s for 8,390).
- **Signature B** (all 5 FAILs): `states (1 of 122: 35:QSACache[0] (1, 2, N, 256) vs (1, 2, N, 256))`: the attention
  KEYS of the QSA cache at cache index 35 (QSACache.state = (*kv.state, raw, pooled)); same shape, different values;
  values, raw, pooled and the other 121 leaves, the last logits and the taps tail are equal. Pattern: in the Claude Code
  conversation the first live hit (before any copy) passes; the first COPY (k 32, from 9,216) fails, and so does every
  later hit, including live hits on the MAIN entry (k 33 / 35 / 36) and the second copy (k 34). The Codex conversation
  never copied and passed all 6, live trims below a decoded reply included. So the copy changes or aliases the main
  entry's layer-35 keys (or the copy's prefill writes into a buffer shared with it); the stand-in's copy passes, so it
  takes something the real engine has. Sent to BigMoE (owner) for the fix; T1c on it next.

## Wed 02:1x: T1c armed (BigMoE 134e811: my tested module + a per-row drift diagnostic for signature B)

BigMoE committed my tested file as 91c9a5f (sha256 00488b23, byte for byte) and sent 134e811 (sha256 e3434b13): the same
plus a CHECK-only diagnostic: per-row integer prints of every QSA leaf (keys, values, raw, pooled) at each prefill's end,
re-checked at the next request's start, after a restore (rows below c vs the source's prefill) and after the prefill;
the FAIL line names the warm-vs-cold rows. Read before use: logs only, nothing else changes. Installed in the cache clone
(my 00488b23 kept as convcache.py.00488b23). t1c.sh: BigMoE's stand-in, then the T1b replay; run folder
t1_runs/32_1111c (raw convcache.log + serve.log kept). Placed after the cold agent test and the pkg_110g checks, before
64K / 128K (~15 min). How to read it (BigMoE): drift at a request's start = the decode changed stored rows; a restore line
= the copy's read; FAIL rows only in [c, N) = the warm prefill itself.

Cold 32 GB agent test so far: probe 27 / 30 pass, 0 invented tools (02:11, 762 s); the 12 tasks started 02:11.

## Wed 02:3x: T1d armed after T1c (BigMoE b855883: CONV_CACHE_BRANCH=0, the orchestrator's 09:00 fallback, checked early)

The orchestrator's rule (02:1x): if there is no clean fix for signature B by 09:00, a branch (copy) becomes a miss; T1 runs
again on that at once, and if it passes, the cached 32 GB agent test goes next. BigMoE's b855883 (sha256 266f76e5) =
134e811 + CONV_CACHE_BRANCH (default 1, unchanged; 0 = a would-be copy is a cold miss and a new entry; the decision now
runs before the check's cold prefill). Read before use: the switch only. t1d.sh: after T1c, installs b855883 in the cache
clone (sha checked from BigMoE's repo and in the clone), BigMoE's stand-in with BRANCH=0, then the T1b replay with
CONV_CACHE_BRANCH=0; run folder t1_runs/32_1111d. Expected (BigMoE): 10 hits (the 2 copies at 9,216 become misses), all
PASS, unless the main entry's own decode changes its layer-35 keys (T1c's drift lines decide that).

**Correction (02:3x, BigMoE's predict_hits.py 3a2dc46, which matches T1 / T1b hit for hit):** the T1b section above says
the later failing live hits (k 33 / 35 / 36) were on the MAIN entry. They were not: by the module's rules k 33 is a live
hit on entry 1 (the copy k 32 made; it shares more with k 32 than with k 31) and k 35 / 36 on entry 2 (the copy k 34
made). All 5 FAILs are on copy-made entries; the main entry (entry 0) passed its only live hit (k 31) and was never
restored live again; Codex (entry 3, live take-overs only) passed all 6. So signature B is either (a) the copy itself, or
(b) entry 0's layer-35 keys below 9,216 changing during k 31's decode, seen only by the copies. T1c separates them: (b)
-> a `drift (request start): entry 0 ... 35[0]` line at k 32; (a) -> `restore (copy at 9216): ... 35[0]` with no start
drift; neither -> FAIL rows only in [9216, N). T1d's prediction (BigMoE data/conv/t1_predicted_branch0.json): 10 hits,
all live, 41.3 % of prompt tokens prefilled.

## Wed 01:58-03:45: EvalSuite's cold 32 GB agent test (agentcc_runs/32_1111): ran, but Bash never worked (harness bug)

Pin: the agent clone = release/next 39947b1 (provenance.txt), serve.py --mem 32 (chat-32), claude 2.1.321, the sandbox
and launcher as in agentcc_night.sh. Records: agent_cc_1111/agentcc_32_1111/ (results, probe, serve.log, runner.log,
sandbox.sb, fanwatch_freezes.txt; transcripts/ redacted, see below). The raw request log (175 requests, 22 MB) is local
only: logs/agentcc_32_1111_server_requests.jsonl.gz (gitignored).
- **Probe (EvalSuite's 30 direct API calls): 27 / 30, 0 calls with an invented tool.** Fails: case 6 and case 10 (Bash, "case
  check failed"), case 25 (Bash instead of Write). EvalSuite: case 10's check was its own bug (it rejected `ls -la`
  looking for the substring "-a"); its pre-registered 32 GB line is 28, so the probe verdict as registered is FAIL.
- **Tasks: 11 / 12 checks passed, 0 timeouts, server 175 requests, 0 errors.** t09_refactor failed: the model extracted
  format_money() but kept the "$" in each caller, so format_money(1234.5) gives "1,234.50" (behavior-preserving, not
  what the check asks). Task walls 97-969 s, 5,619 s in all.
- **Harness bug: all 79 Bash calls failed** with `EPERM: operation not permitted, mkdir
  '/private/tmp/claude-501/<the task folder, dashed>'`: Claude Code makes a per-folder temp dir under
  /private/tmp/claude-<uid>/ before it runs any command, and the sandbox allows writes only in the run folder,
  /private/var/folders and /dev. So the 12 tasks ran with no working shell (the probe checks the call, not its run, so it
  was unaffected). EvalSuite found it at the same time (03:5x). Tool calls across the tasks (EvalSuite's count): Bash 79
  (all EPERM), Read 37, Glob 16, Edit 15, Grep 5, Write 2, Agent 1 (the subagent lane worked: exactstream-sub), ToolSearch 1.
- **What a lossy model does when the shell fails** (observed): retries with `dangerouslyDisableSandbox: true` (Claude
  Code's own sandbox is off here, so the flag changes nothing; the outer seatbelt still applies), `cd /tmp`,
  run_in_background, `ls -la /Users/kamen` (t12), and reading Claude Code's own config folder: t01 Read cc_home's
  .claude.json and its **shell snapshot (snapshot-zsh-*.sh, built from the user's ~/.zshrc: his aliases, including the
  private account names)**. All stayed on this Mac, inside the sandbox's allowed reads. The record's transcripts are
  redacted: those two tool results are withheld, and the leak pattern finds 0 hits in transcripts/. EvalSuite told
  (03:5x) not to commit that transcript or the request log as is.
- **Cold-run timing** (no conversation cache: every turn prefills the whole prompt): probe prompts ~8.7K tokens, first
  token median 21.3 s; task prompts 9.1-20.2K (median 13.8K), first token median 32.6 s (~419 prompt tok/s); answers
  median 110 tokens, whole decode median 58 tok/s (short answers); lifetime peak 37.46 GB. The 7 first tokens over 60 s
  (103-124 s) are all fanwatch heat freezes: the server was frozen 7 times for ~80 s (02:08, 02:19, 02:32, 02:46, 03:02,
  03:16, 03:31; fanwatch_freezes.txt), ~9.5 min of the 94-min task phase.

## Wed 03:5x: the Bash fix (CLAUDE_CODE_TMPDIR) and the 12-task rerun at 32 GB armed (agentcc_runs/32_1111b)

- **Fix:** `CLAUDE_CODE_TMPDIR=<run>/cctmp` in Claude Code's environment (a documented variable in Claude Code's string
  table: it moves the per-uid temp root). Claude Code then makes its per-folder temp dir inside the run folder, which the
  profile already allows; the sandbox profile is unchanged (its generator is byte-identical; nothing is written outside
  the scratchpad). With a long override Claude Code keeps child processes' TMPDIR at the system default
  (/var/folders/.../T/, allowed), since a socket path there would be too long.
- **Mock check 03:54** (bashfix_check.sh + mock_bash.py = mock_tools.py with one Bash call; no GPU, < 1 GB; output
  bashfix_check.out): V0 (as 32_1111) gives the same EPERM; V1 (the fix) runs the command: TMPDIR=/var/folders/.../T/,
  a file written in the task folder, a Python tempfile written, a write to $HOME denied (no file appeared outside).
- **Rerun** (agentcc_rerun.sh, armed 03:55 after T1d's runner, one clear poll, 10-s polls; last start 08:00): the same
  server files (the clone checked against release/next's SHA256SUMS at 39947b1, not HEAD), serve.py --mem 32 on port 8124,
  the same manifest, base config and launcher, no probe; a guard stops the run at once if t01's transcript still holds
  the EPERM. EvalSuite's PREREG_agentcc amendment 2 (e0fea3a, 03:57) covers the fix, the new folder, its corrected case
  10 check and a scorer fix (the init event names the subagent tool Task, the API array Agent).

## Wed 04:0x: no account names in tracked files; the rerun re-armed with a regex read-deny (agentcc_rerun2.sh)

The orchestrator (04:0x): the sandbox profiles in the record named the two account config folders literally, and the
public sync's leak check refuses those strings. Fixed in every tracked file (git grep for them: 0 hits):
- the ~/.claude read-deny rules (three subpaths) are now one rule, `(regex #"^/Users/[^/]+/\.claude[^/]*(/|$)")`,
  covering every ~/.claude* entry, ~/.claude.json included (the old list did not cover ~/.claude.json, which holds the
  account's config). Applied by deny_regex.py to agentcc_night.sh, agentcc_cache.sh, agentcc_rerun.sh, bashfix_check.sh
  and, as a marked record copy, agentcc_32_1111/sandbox.sb;
- scripts/copyspan_lookup.py + copyspan_width.py read the second projects folder from COPYSPAN_DIRS; HANDOVER reworded.
- **Mock check 04:05** (bashfix_check2.out, the regex profile): claude rc 0, Bash runs, file + tempfile written, write
  outside denied, `~/.claude*`: 7 entries, 0 readable; ~/.ssh denied.
- **The rerun:** agentcc_rerun.sh (pid 38588, still waiting for T1d) was stopped by SIGKILL (no trap, so no runner.done
  for EvalSuite's watcher; its log kept as 32_1111b/runner_rerun1_armed_0355.log) and agentcc_rerun2.sh armed 04:05:46
  (task b2h18m0yw): the same folder, gate and settings, only the read-deny rule as above.
- Note for the next runs: the shell snapshot that t01 read lives in the run's own Claude Code config folder (cc_home),
  which Claude Code itself must read, so no read-deny can hide it; keeping the user's aliases out of it would mean a
  neutral zsh startup (ZDOTDIR), which changes PATH (python3) for the tasks: not done without EvalSuite's call.

## Wed 03:57-04:09: T1c (BigMoE 134e811): signature B is the copy itself, layer 35 QSA keys, row 0 only

Same setup as T1b (cache clone, serve.py --mem 32, CONV_CACHE_CHECK=1, the 45 recorded requests; t1c_32_1111/). BigMoE's
stand-in on the module first: 4 PASS / 0 FAIL. Replay: 45 requests, **12 hits, 7 PASS, 5 FAIL** (as T1b), server errors 0.
- **drift lines 0**: entry 0's layer-35 keys did not change during k 31's decode (BigMoE's (b) is out).
- **restore lines 2**, one per copy (k 32, k 34): `restore (copy at 9216): rows below c differ from the source's prefill:
  35[0] rows 0..0 (1 of 9216)`: BigMoE's (a), the copy itself.
- Every FAIL (copies k 32 / 34 at c 9,216, N 12,300; live k 33 / 35 at c 12,288, N 12,404; live k 36, N 12,627) is
  `35:QSACache[0] ... QSA rows warm vs cold: 35[0] rows 0..0 (1 of N)`: one row, row 0 of layer 35's QSA keys, made by
  the copy and carried into the copy-made entries' later live hits. k 31 (live on entry 0) PASS.
- Warm prefill: copies restore 81-114 ms + 3,084 tokens in 12.2-12.3 s; live hits restore 59-102 ms + 116-339 tokens in
  2.9-4.7 s (cold: 12,302 tokens 28.2 s, 8,390 tokens 23.1 s).
Sent to BigMoE 04:1x. T1d (b855883, CONV_CACHE_BRANCH=0: no copies) started 04:09:56; its stand-in 3 PASS / 0 FAIL.

## Wed 04:1x: a neutral shell startup for the next agent runs (orchestrator 04:0x): ZDOTDIR does not work; HOME does

The orchestrator's call: tonight's 32_1111b stays as armed; from the next runs on (cached 32 GB, 45 GB) the claude
processes get a neutral zsh startup that keeps today's exact PATH, without the user's aliases or functions; checked on
the mock first (python3, git and the task tools must resolve to the same binaries).
- **ZDOTDIR=<run>/zdot (bashfix_zdot.sh / .out): no effect.** PATH and all 32 compared items equal, but aliases 5 -> 5
  and functions 8 -> 8: Claude Code builds its shell snapshot by sourcing `$HOME/.zshrc` itself (its string table: the
  snapshot script's `source "<config file>" < /dev/null`; ZDOTDIR is only read by its `alias claude=` check), so
  ZDOTDIR never reaches it.
- **HOME=<run>/home with .zshrc = `export PATH='<the exact PATH of today's runs>'` (bashfix_home.sh / .out): works.**
  All 33 compared items equal (PATH, the binary of python3 / python / pip3 / git / sh / bash / zsh / ls / cat / grep /
  sed / awk / find / wc / sort / head / tail / diff / patch / make / env / xargs / tr / cut / node / npm / pytest,
  python3 3.14 (Homebrew), git's version, the locale and Python's encodings, the env var names); aliases 5 -> 2 (zsh's
  own run-help / which-command), functions 8 -> 0. Side effects: `~` is the neutral folder (so `ls ~` no longer lists
  the user's home; absolute paths still behave as before), and git has no global identity (proposed: a .gitconfig in
  the neutral home with the template's identity, agentcc@localhost). Not adopted yet: sent to the orchestrator and
  EvalSuite (an amendment) before the cached runs.
- **Approved (orchestrator 04:2x) for the cached 32 GB and 45 GB runs; EvalSuite told for an amendment.** The home
  template is agent_cc_1111/agent_home_tpl/ (.zshrc: only the exact PATH; .gitconfig: agentcc / agentcc@localhost);
  agentcc_cache.sh copies it to <run>/home, records it in provenance.txt and runs agentcc_tasks.py (so every claude) with
  HOME=<run>/home. **Mock check of exactly that setup (bashfix_final.sh / .out), in a git repo task folder:** 32 of 33
  items equal to today's (the one difference: `git status` ok, the baseline's mock folder was no repo); aliases 2 (zsh's
  own), functions 0; `git commit` works, author agentcc@localhost. Tonight's 32_1111b keeps the old home, as armed.

## Wed 04:09-04:23: T1d (BigMoE b855883, CONV_CACHE_BRANCH=0): PASS, 10 of 10 hits bitwise

The orchestrator's 09:00 fallback, checked early: b855883 (sha256 266f76e5) installed in the cache clone, BigMoE's
stand-in with BRANCH=0 first (3 PASS / 0 FAIL), then the T1b replay with CONV_CACHE_BRANCH=0 (t1d_32_1111/).
**45 requests; 10 hits, 10 PASS, 0 FAIL; drift 0, restore 0; server errors 0**, as BigMoE predicted: the 2 would-be
copies are cold misses (`miss N 12300 c 0 (none, branch (CONV_CACHE_BRANCH=0))`, 27.5 / 28.0 s), every hit is live (c
12,288: k 31 / 33 / 35 / 36; c 8,192: the 6 Codex turns), restore 58-93 ms, 116-425 new tokens prefilled in 2.9-5.7 s.
The first long miss (N 12,302) took 135 s instead of 28 s: fanwatch froze the server 04:15:35-04:17:16 (heat pause at
die 84.3 C; fanwatch_0415.txt). Short one-chunk misses (~700 tokens, the side calls) take ~8 s each at 32 GB.
So the cache is exact with copies off; with copies on, the copy changes row 0 of layer 35's QSA keys (T1c). Under the
orchestrator's rule the cached 32 GB agent test runs on b855883 + BRANCH=0 at 09:00 unless BigMoE has a clean copy fix.

## Wed 04:2x: git in 32_1111b's setup: `git commit` fails (the user's gitconfig signs with an SSH key under ~/.ssh)

EvalSuite asked (04:2x) whether git works for the model in 32_1111b (real HOME). Mock check of exactly that setup in a
git repo (bashfix_git.sh / .out; R = 32_1111b's, F = the cached runs' neutral HOME): R: `git status`, `git log`, `git
diff` ok (so Claude Code's own startup git status works), **`git commit` FAILS**: `error: Couldn't load public key
<home>/.ssh/id_ed25519.pub` (the global gitconfig turns on commit signing with an SSH key: commit.gpgsign, gpg.format,
user.signingkey; the profile denies ~/.ssh, so a model can never sign with the user's key). F: all four ok. (The earlier
"B: GIT status FAIL" in bashfix_final.out was the mock's task folder, not a repo.) None of the 12 prompts asks for a
commit. 32_1111b had already started (04:23:49) when the answer came, so it runs as armed (EvalSuite's option b: commit
failures reported as a setup limit of that rerun); agentcc_rerun3.sh (neutral HOME) was ready but not used. The cached
runs use the neutral HOME, where commits work.
