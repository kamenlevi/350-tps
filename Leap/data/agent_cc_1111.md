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
