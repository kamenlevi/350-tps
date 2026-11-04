# BigMoE handover (re-read first after any compaction)

Updated 2026-10-20 07:40. Repo ~/BigMoE (git, no remote). Commit as Kamen <kamenlevi@users.noreply.github.com> with
"Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". Ledger of every result: LEDGER.md (rows by id). Orchestrator
session: local_b2dc3286 ("AI/LLM project recommendations"); RESULTs only when final, at most one combined per ~2 h.

## BIG-FINDINGS RULE (Kamen Thu 29 Oct 18:17; bar RAISED 19:27; full text ~/.local/share/usage-pace/briefs/big_findings_rule_1029.txt)
Kamen 19:27: "report to me when there is a find from the "next" caliber. i mean not a 2% gain somewhere. but if somewhere
somebody found something which could potentially unlock very much and seems very promising. or if we got a +20 percent. or
the mtp head wall was broken. or all of the other hundreds of walls". The moment a next-caliber find lands, SendMessage
the address `~/.local/share/usage-pace/orch_addr.sh` prints (by session id; 42262 died at the 10-30 00:40 app restart,
now 7333). Never by name: two main sessions are called "AI/LLM project recommendations" (7366 is the wrong one). First line: `BIG BigMoE HH:MM: <what, with the number>. Exact or not exact.
Result or lead. Evidence: <commit or file>. Next: <one line>.` Don't wait for summaries / NewIdeas / handovers.
Kamen 19:32: "the 20 percent was just an example not an exact number": NO hard cutoff. Judge the caliber: does the
find change what's possible, or could it unlock a lot? A 2 % gain never counts. The numbers below are examples of the
size he means, not thresholds. When unsure, send it with one line on why it might be next caliber; the orchestrator
decides what reaches him. Examples of BIG: (a) ~+20 %, measured, on a line's headline number (tok/s at 45 / 24 / 12 GB, or 20 % less RAM), exact or
not; stacked small gains count once the line is +20 % above what Kamen last heard (today 45 GB ~64 tok/s code, 24 GB ~29,
12 GB ~16.4 at an 8.5K prompt; so 24 GB needs ~35); (b) a wall broken, measured (e.g. drafter +1 kept token per 16-guess
check on any text kind; bytes per 16-row check -20 % (13.2 GB today) with the speed following; REF2 bit-exact inside the
live drafting loop at 45 GB; a new smaller RAM line for the full 125B); (c) a very promising LEAD (early measured evidence
of a credible path to +20 % or a broken wall; say it is a lead); (d) a decision only Kamen can make; (e) serious laptop
risk only (heat emergency, disk near its floor, a runaway the guards missed). NOT big any more: gains under 20 %, small
defaults, bug root causes, single kills, non-exact passes with small gains, guarded swap spikes, queue moves,
pre-registrations: keep those in LEDGER / HANDOVER (NewIdeas' SUMMARY_FOR_KAMEN.md carries them). Sent under the old bar:
M-01 + PF1 (Thu 18:22), b45 (19:24).
KAMEN DECISION Thu 19:27 (via the orchestrator): "im fine with another not bit identical 24gb version": a second,
non-exact 24 GB version may be built and shipped NEXT TO the exact default (M-01 stack stays). It still needs a real speed
gain and the Eval suite's strict verdict. VD / variable-slot work is no longer parked on his call (priority: NewIdeas + us).

## KAMEN 31 Oct 17:44 / 17:49: 350 tok/s, "no compromise"
The goal: 350 tok/s on his Mac, with a breakthrough that carries to other models (exact, general methods count
double). 17:49, verbatim: "so now we must definitely 100 percent do this, no compromise". For the 350 work the TWO WALLS
come first: bytes per check and guesses kept per check. Judge every next step by whether it moves one; smaller exact
wins come second. (BigMoE's walls: bytes per 16-row check = expert reads + pool slots; kept per check = drafter / MTP head,
e.g. R-60 MTPDROP.)

## FAST INTEGRATION + SHARED GPU (Kamen Fri 30 Oct ~18:45, standing; full text ~/.local/share/usage-pace/briefs/fast_integration_1030.txt; wins over older lock rules)
Kamen: "everything published is good to use ... combine everything already published faster"; "for every small test which
just needs a proof of concept not exact numbers ... run multiple sessions at the same time on the gpu ... for the things
which are actually important, im fine with them being seperate".
- Proof-of-concept screens ("does it work / big gain / bit-equal") run under `peer lock share <t> --cpu n --gpu n "<why>"`
  beside others; label their timings "shared GPU, rough"; never send one as a result (a big gain gets one quiet-lock
  confirmation first; send it as a lead meanwhile). Exactness checks never need a quiet Mac.
- Quiet locks only for important numbers: a tok/s / ms figure for Kamen, an adoption decision, a pre-registered speed or
  final verdict.
- Memory decides concurrency: start only if the expected lifetime peak fits with >= 8 GB spare; never two 45 GB-route
  processes (36-40 GB) at once; >= 50 GB free for a ~45 GB load; swap guard (+2 GB) stays; PAUSE / lid rules stay.
- Published methods first, in batches: exact-safe changes (caching, read patterns, slot banks, prefetch, gates) stack in
  one run with one every-token check, split only on a fail; non-exact: one combined same-scores test per batch. Owners
  build straight from NewIdeas' ranked list (BigMoE = engine / SSD / cache). Pre-register in a few lines.
- claudesub sessions (BigMoE) keep usage-pace as before.
- 45 GB MEMORY TURNS (the orchestrator Fri 23:2x-23:5x, standing; RULES.md): a 36-45 GB run (data-only too) takes a QUIET
  ticket first (a queued ticket stops new shared runs, the grant waits for running ones), then 30 s settle, then
  NO-SWAP = free + speculative + purgeable + file-backed pages (vm_stat; NOT "available": inactive holds anonymous pages)
  >= lifetime peak + 4 GB (shared lock: + 8), else release, wait 2 min, retry (scripts/turn45.sh gives up after 2
  failed grants). One 45 GB ticket at a time across sessions, 15 min apart (EvalSuite's REF2b chunks use the gaps).
  Kamen's own apps decide what fits: C 224 needs ~44.5 GB no-swap (4 swap trips on 10-30); C 160 ~33 GB.

## Rules that bite
- Pace with `usage-pace check --session bigmoe --pct <5h %> --resets <resetsAt>` (get_usage) each turn; SLEEP N = commit,
  `bash -c 'exec -a sleep_until_reset sleep N'` in the background, end the turn. Night gap 03:08–07:15: no Claude.
- GPU jobs only under `peer lock quiet --queue`; ONE lock per batch (scripts/batch_runner.sh pattern); detached runners
  stamp active_at in ~/.claude-peers/locks/$CLAUDE_PID.json every ~3 min (keepalive) and stop if the lock is gone;
  memory gate: ≥85 % free and no other >8 GB process. Never `peer lock/unlock` from the session while a runner of
  this session is queued or running (shared CLAUDE_PID). Stop runners by PID only (a pkill -f pattern once killed
  every session's night_runner.sh).
- Never rebuild ext/build while a process has bigmoe_ext loaded (lsof the .so first).
- Disk floor 100 GB (stop at 110). records/ is 63 GB.
- Research first (prior-art pass) before building new ideas. Exactness: our dup-row + compiled-HC reference (v1,
  sha c09a8163f9 at 0.50/64 code prompt) is the truth; every fast path must be bit-identical to it.
- Ledger edits: ASSERT the anchor exists (str.replace silently no-ops; a day of rows was lost once).

## Exact stack (env flags)
Reference: BIGMOE_DUPROW=1 BIGMOE_COMPILE_HC=1 BIGMOE_HC_VREAD=1 BIGMOE_ASYNC_EVERY=1
Prefetch: BIGMOE_PF_JIT=1 BIGMOE_PF_QD=4 BIGMOE_PREFETCH=12 ; S≤8 verify band: BIGMOE_DUPROW_CHUNK=5 BIGMOE_MAXK=80
Drafts: BIGMOE_FRSPEC=1 (Scout; SC1b per request in spec125), BIGMOE_SCOUT_BUNDLE=1 + MTPLX_QWEN4_VERIFY_GLUE=1
24 GB mode (C=128): + BIGMOE_MTP_STREAM=1 BIGMOE_RECORDS=3   (records/ is gone since 10-20 19:52: RECORDS=1 fails;
  RECORDS=3 = records3 + CPU rebuild, exact, −10–13 % vs the old records/ path; or exact via plane pools:
  BIGMOE_TIER=4444444444 BIGMOE_TIER_GLU=3c BIGMOE_TIER_COMBINE=1, bitwise, B8). PF_GROUP / PF_SEG are NOT exact (v2 only).
v3 fast mode (validated V3, 10-21: GSM8K 450/472 vs exact 452): BIGMOE_TIER=4433333333 BIGMOE_TIER_GLU=3c
  BIGMOE_TIER_COMBINE=1 BIGMOE_OOO=1 BIGMOE_GDN_EXACT=1 BIGMOE_TIER_PF_GROUP=64 BIGMOE_PF_NOLOGITS=1 BIGMOE_EVICT_LFU=0.99 BIGMOE_VERIFY_ROWS_SDPA=1
  BIGMOE_JOINT=1 (JT1 10-25: base + sidecar reads in one burst per layer, bitwise, +7-8 % tok/s at 24 GB)
  BIGMOE_MTP_PF_GROUP=48 (R-38 10-28: grouped prefill for the streamed MTP layer only; spec prefill peak 24.17 -> 21.97
  GB, verified tokens exact, drafts may differ; pool growth to C_m 159 / C_l 49 waits for the budget call)
  BIGMOE_M01=1 (R-44 a, DEFAULT since NewIdeas Thu 17:3x: records3m/ = records3 with fixed-width per-group fields, the ext
  unpacks them; bitwise, rusage bytes/tok -4.8 %, tok/s +2.0 %, b44. Needs an ext from 6753d83+ (tier.make_pools asserts
  ext.m01_on()); records3 stays on disk while Breakthrough checks records3m for 12 GB, R-48) (+ the 24 GB
  flags minus RECORDS; GDN_EXACT also in exact mode); v3b shas at 0.25/96 code ce5981c55d,
  prose a159046545, edit cd4289b64d. +21–23 % vs exact at equal pool bytes (B5) + OoO 4–6 %.
Repetition guard: on by default everywhere (bigmoe/repguard.py; BIGMOE_LOOP_GUARD=0 off), R1 (LaTeX masked) default.
BOTH stacks (exact and v3) also take: BIGMOE_GDN_EXACT=1 BIGMOE_EVICT_LFU=0.99 BIGMOE_VERIFY_ROWS_SDPA=1 (all bitwise;
  VERIFY_ROWS_SDPA is REQUIRED for spec == plain past ~1K tokens, LEDGER LONG1b; T > 2048 still open).
Prefill: BIGMOE_PF_PREFILL=1 BIGMOE_PF_FULLSCR=1 BIGMOE_PREFILL=lmp4pd (greedy, prompts > 2048; pool warm-up default)
Optional exact: BIGMOE_SORT_VERIFY=1 (sorted gather at verify, exact, speed unproven); split-phase MoE = MoEPrefetch fork.
Not exact / v2 only: BIGMOE_PF_GROUP (prose sha differs), GDN CONVNORM (changes 32K plain), fused GDN in_proj, PF3, MLX 0.32.4, pack4, QSA gather/flash lanes.

## Key numbers
- 0.50 (C=256): spec k=3 ~39–40, lookup md7 ~41–43 (code), edit ~44, prose ~35–36 tok/s exact.
- 24 GB mode (C=128): spec 26.7 / lookup 28.6 tok/s at 22.2 GB MLX peak (night: code 28.9, edit 32.5, prose 22.5).
- Prefill exact: 16K 23.7–26.8 s (613–692 tok/s), 32K ~55–60 s.
- Record loader (REC2): +7 % at 25 % (io 16.0 → 14.0 ms/tok).
- **45 GB DEFAULT since Mon 11-02 07:3x = R57_PRESET=45 at C 256** (NewIdeas: owner's call; r57_screen's preset default C):
  REF2-T + gate + t 0.3 + OOO / TIER_COMBINE + K-73 + M-17 per-layer sizes = 63.6 tok/s steady (56.4 whole run) at a 41.7 GB
  lifetime peak, every token == REF2-T (C50). C 224 = the 37.4 GB setting (C45: L 58.4 steady). REF2-T stays the 45 GB
  reference: REF2c-T failed decision 4 (EvalSuite 11-02 07:24, IFEval -5.0).

## 10-25: this session now runs on claudesub (cwd ~/OjoX; use absolute paths), pacing `--account sub`
- Never message main-account sessions about the project except the orchestrator ("AI/LLM project recommendations"), and
  that only for ACT / hardware risk / Kamen-only decisions. Results go to NewIdeas (chief researcher). No hourly summaries.
- STANDING DUTY: 3-hourly laptop + research health review (ops/HEALTH_REVIEW.md, ops/health_review.py). It runs as a
  session cron (CronCreate "11 1-22/3 * * *", job e782b287 re-created Thu 29 Oct 15:4x): session-only, dies with the
  process and expires after 7 days (~11-05) -> RECREATE it after any restart / compaction (CronList to check). First
  review logged 10-25 10:05 in ~/.local/share/quiet/health_reviews.log. The orchestrator's address changes when the
  Claude app restarts (the cron prompt's 20139.sock is dead): urgent alerts -> SendMessage to the uds address of the
  orchestrator as printed by `~/.local/share/usage-pace/orch_addr.sh` (10-30 00:40: 7333; 42262 is gone). Two main
  sessions are named "AI/LLM project recommendations" (7366 is NOT the orchestrator), so never pick it by name. 19:13 review WATCH: fanwatch fell back to Baro's raw curves at
  13:56:28 (fixed-mode check failed after the ACT restart, never retries) -> fans swing under CPU jobs; owner told
  (peer send 19:54); not mine to restart. Re-check at the next review (`grep 'fixed mode' ~/Library/Logs/fanwatch.log`).
- SSD heat: my back-to-back 24 GB arms took the SSD to 80 C (13:46 ACT cooldown) and 76-77 C (b29, b30). Every runner
  from b31 on sources scripts/ssd_gate.sh: ssd_wait before each arm (cool line 66 C), ssd_check after (stop at 73 C).
- gated.new_pass now waits on ~/.local/share/quiet/PAUSE (5918b42), as RULES.md asks of every engine.
- GS1 gate stamps done (41bb474 / fc20ff6). Idle otherwise until NewIdeas assigns work.
- S10 + B5s (NewIdeas QUEUE.md 350 STACK row S10) DONE 10-25 14:58 (LEDGER S10a, JT1, SB1-24, OR1, B5s):
  step 1 anatomy (b27): code check 81 ms = gate wait 52 + GPU 30, SSD busy 93 % at 3.8 reads in flight (~9-10 GB/s);
  63 % of misses unpredicted, 24 % prefetched in time. Step 2: JOINT ADOPTED (BIGMOE_JOINT=1, bitwise, +6.7 / +8.0 / +7.2 %
  code / prose / edit, b29 3 clean rounds); SB1 neutral at 24 GB; B5s already in place (ASYNC_EVERY=1). S10 ceiling
  (oracle, b29, fixed widths): perfect forecasts 3 layers ahead +35-44 % code, +33-48 % prose, +19 % edit -> the rest
  of S10 is forecast recall + lead time (Fit12 has the trace-side predictability item since 13:20).
  Harness note: s10_anatomy (3 prompts per process after an 8-token warm-up) is a colder cache than test_spec125
  (ar2 of the same 256 tokens first): EV1's 40.6 / 34.1 / 47.3 tok/s and today's ~35 / 24 / 30 are not comparable.
  Timing hygiene (203c76d, d60f771): gated.PAUSED counts PAUSE waits + > 15 s gaps; s10_anatomy flags prompts they
  touched ("NOT CLEAN"); quiet_auto windows SIGSTOP whole batches (b28 round 2 was frozen 13:46-13:56). Adaptive width
  can also collapse after slow checks (b30 j2 prose S 1.30): unflagged, so keep a stable within-harness reference.
- b30 (NewIdeas follow-ups, pre-registered rule; LEDGER TH1 / FC1) 15:26: THETA 0.3, ranked lists, L+2 forecasts, the new
  per-distance queue BIGMOE_PF_QD_FAR: NONE adopted. New per-distance forecast log (ext.stats fc_* / iss_*; s10_anatomy
  "forecasts:" line): raw recall of misses at lead 1 / 2 / 3 = code 58 / 27 / 15 %, prose 63 / 40 / 26 %, edit 52 / 17 /
  ~1 %, precision ~40 %. Zsh note: run stack env lines through bash (zsh does not split "$X" for env).
- S10b GO (NewIdeas 15:27, QUEUE row S10b): AT THE NEXT WAKE write + run the trace: layer L's MoE input (bf16, 2560),
  true top-10 of L+1..L+3 and each row's resident set (score on MISSES), ~12K verify rows over code / prose / edit /
  math, ~3 min GPU, <= ~5 GB (delete after the verdict); write the layout into the S10b row for TrainLab (offline fit).
  Kill: lead-2 recall@16 of misses (held-out prompts) < 55 %; >= 65 % -> engine A/B, adopt at >= +5 % code, shas
  identical; 55-65 -> NewIdeas decides. Runtime predictor: per-layer linear on router_{L+2} first, MLP only if needed.
  10-26 03:09 STATE: slim spec (NewIdeas 00:xx: <= ~1 GB, ~8 predictor layers + all layers' ids; disk at ~101 GB) CODED
  in 6809e3e (bigmoe/s10b.py, stream.py hook, ext BIGMOE_S10B_MISS, scripts/s10b_trace.py, s10b_check.py, b31_runner.sh;
  capture + checker tested on fake data, CPU; the ext build was blocked by the peer hook during Fit12's lock: the runner
  builds under its lock and stops cleanly on a failed build). Layout written into QUEUE row S10b. Lock queued as a
  background task (peer lock quiet --queue 30m; a queue ticket expires after PEER_QUEUE_TIMEOUT, default 2 h: the 03:10
  one did at 05:10, re-queued 05:11 with PEER_QUEUE_TIMEOUT=21600, #2 behind Breakthrough; if it lapses or the session
  restarts, re-queue the same way) -> ON GRANT launch at once (RULES: GPU launches always go):
  `cd ~/BigMoE && HAVE_LOCK=1 CLAUDE_PID=65439 nohup bash scripts/b31_runner.sh > /dev/null 2>&1 &` (it checks disk >=
  100.8 GB at grant time), then read data/b31/b31.log, trace.txt, check.txt (plain router baseline at lead 1/2/3), report
  to NewIdeas + TrainLab; delete data/b31/s10b/ after TrainLab's verdict.
  10-26 08:22 CAPTURED (b31: lock 08:14, ext built OK, GPU 08:15:40-08:22:36, unlocked 08:22:46): 439 MB, 20 prompts x
  400 tok (18-34 tok/s, cold per-prompt cache), 4405 verify passes, 8834 verify rows; disk 100.4 GB after. First check
  (data/b31/check.txt, 3838 passes): 0 trace/ext union mismatches, 0 missing / duplicate ext records; misses 15.5 / 11.6
  / 15.7 / 14.1 % of routed ids (code / prose / edit / math); PLAIN ROUTER recall@16 of misses lead 1 / 2 / 3 = 57.6 /
  49.1 / 46.4 % (lead 2: code 53.0, prose 52.1, edit 42.7, math 49.4). The 567 'unequal rows' passes = MTPLX's commit
  re-running layer 1 over the kept rows after a partly accepted verify (same seq, fewer rows, all resident, not in
  miss.bin): first call per layer -> all 4405 passes equal (awk recount); checker fixed + held-out split (310cf27), its
  rerun waits for a free Mac (python blocked by the peer hook while others measure): `peer wait --timeout 5h` in the
  background, then `cd ~/BigMoE && OMP_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4 taskpolicy -b .venv/bin/python
  scripts/s10b_check.py data/b31/s10b > data/b31/check2.txt`, send the final numbers to NewIdeas + TrainLab. Reported
  08:31 (SendMessage ojox-01 / ojox-ef); join rule in QUEUE row S10b. Delete data/b31/s10b/ after TrainLab's verdict.
  09:0x TRAINLAB VERDICT (pre-registered): ALIVE, below the A/B line: held-out (prompt 4) lead-2 recall@16 of misses
  55.6 % (MLP on x_L, hidden 512, on top of router_T) vs plain router 49.6 %; all-pass plain router 58.5 / 50.2 / 47.7 %
  (lead 1/2/3, reproduces my checker). 55-65 -> NewIdeas decides. KEEP the trace until TrainLab says (exploratory
  misses-only fit ~09:13-09:55). Asked NewIdeas for GO on b32 = re-capture with resident bitmaps (ext: at each (seq, L)
  service snapshot pools L+1..L+3, ~40 MB; deployable score = recall of misses by the top-16 NON-resident predictions);
  code it only on GO, capture only after b31's trace is deleted (disk floor 100 GB).
  09:05 HARDWARE note to the orchestrator (uds 15086): lid closed 08:45:15 (clamshell sleep), DarkWake thermal emergency
  -> 'Thermal Emergency Sleep' 08:45:49-09:00:26 (TrainLab turn21 lost a sequence: 2 spin gates timed out); since 09:00
  the lid is still closed (AppleClamshellState Yes, CausesSleep No: caffeinate -s on AC) with GPU jobs at 97 %. Kamen
  decides whether jobs pause while the lid is closed (not in RULES.md: I changed nothing). Check: `ioreg -r -k
  AppleClamshellState -d 4 | grep Clamshell`, `pmset -g log | grep -i "thermal emergency"`. 09:07 orchestrator: the
  keep-awake was NewIdeas' caffeinate -s (dropped); a closed lid now HOLDS research (quiet window, lid_release.sh ends it
  when the lid opens). Lid open again by 09:44.
  09:08 NEWIDEAS GO b32 (exploratory; the 55.6 % ALIVE verdict stands): score = held-out lead-2 recall of the row's misses
  by the top-16 among experts NOT resident at the decision, TrainLab's MLP vs plain router, also leads 1/3 + per domain.
  Lines: >= 65 % -> engine A/B (mine), 55-65 -> NewIdeas, < 55 -> stop S10b. CODE 3eb8ada (ext BIGMOE_S10B_RES before
  each schedule(); s10b_check.py DEPLOYABLE lines; b32_runner.sh refuses while data/b31/s10b exists, needs >= 100.6 GB).
  09:46 b31's trace deleted (TrainLab released it; meta/check kept as data/b31/s10b_*.json); disk 101.0 GB. b32 lock
  queued #4 (bpcitem2p, PEER_QUEUE_TIMEOUT=21600) -> ON GRANT: `cd ~/BigMoE && HAVE_LOCK=1 CLAUDE_PID=65439 nohup bash
  scripts/b32_runner.sh > /dev/null 2>&1 &` (builds the untested ext first), then data/b32/b32.log, trace.txt, check.txt;
  tell TrainLab (x kept for all 20 prompts; layout in QUEUE row S10b) + NewIdeas; TrainLab scores its MLP + a miss-target fit.
  10:13 B32 CAPTURED (lock 10:06, ext built OK, GPU 10:07:00-10:13:45, unlocked 10:13:51): 482 MB in data/b32/s10b/, 4363
  verify passes, 8861 rows; disk 100.5 GB. Checker CLEAN: 0 unequal passes (605 L1 re-runs skipped), 0 trace/ext
  mismatches, 0 missing / duplicate records, every scored (pass, L -> T) has a residency snapshot (602,646 records). Plain
  router all-512 held-out lead 1/2/3 = 58.7 / 49.4 / 47.1 % (reproduces b31). DEPLOYABLE plain router (top-16 among
  non-resident) held-out 75.3 / 63.9 / 63.1 % (all prompts 74.9 / 64.1 / 63.5; lead 2 code 67.8, prose 66.6, edit 58.9,
  math 63.8): the router ALONE is 1.1 points under the 65 % A/B line. CAVEAT sent to NewIdeas + TrainLab: k = 16
  non-resident per row = ~16-32 unique reads per pass-layer vs ~2-3 misses; the shipped engine forecasts lead 1 only
  (PREFETCH=12 = top-12 per row over all 512, resident skipped; PREFETCH2/3 off). Read-budget sweep in s10b_check.py
  (3e0445c + 1f6b6df "unused" = reads never routed at T in the pass) RAN 13:11 (56 s, data/b32/check2.txt; old lines
  reproduce exactly). Lead 2 per pass-layer (union over the pass's rows), all | held-out: k2 29.3 | 28.4 % for 3.5 reads
  (2.7 unused), k4 42.3 | 41.4 % / 6.8 (5.7), k8 55.3 | 54.3 % / 12.9 (11.5), k16 67.2 | 66.7 % / 24.5 (22.8); 2.6 misses
  per pass-layer. Shipped lead-1 policy (approx., trace x): picks 51 % of lead-1 misses, 4.8 reads (3.7 unused).
  LABEL CAVEAT (scripts/s10b_intime.py, data/b32/intime.txt): S10b's "miss" = not in the table at T's service, and the
  ext promotes prefetches only in ensure() there, so ON-TIME prefetches are labelled misses: of routed experts not resident
  at L's decision, 0.0 % were in the table at service (leads 1-3, all 47 layers). Oct-19 engine runs' split: 27 % on time,
  27-29 % late, 43-47 % demand (data/runs/C256_ar2_N64.json, C128_ar2_N64.json). Full note: data/b32/budget_note.txt,
  left 13:2x for NewIdeas + TrainLab via peer say (not woken; both wake ~13:35). Offered b33 (2-bit labels on time / late
  / demand + ext stats in meta; ~8 min GPU; joins b32's x by (prompt, seq, L) if seq numbering reproduces): NewIdeas'
  call. Delete data/b32/s10b/ after TrainLab's + NewIdeas' verdict (and not before a b33 join, if one runs).
  NewIdeas ~13:40 (lounge): S10b bar RE-ANCHORED TO READS: per pass at ~4.8 reads per pass-layer, lead 2, held-out, the
  MLP must catch >= 50.4 % of the misses (the shipped lead-1 catch). b33 waits for TrainLab's per-pass MLP numbers: GO b33
  if >= 50.4 % or 45-50 %; < 45 % -> S10b parks, no b33. (Plain router at ~4.8 reads: ~34-35 %, interpolated k2 / k4.)
  TrainLab (msg to me, after 13:47; ~/TrainLab/data/s10b_fit_b32.txt, REPORT 'S10b on b32'): M1a (linear + affinity),
  held-out lead 2 per pass-layer, MLP vs router: k2 38.4 vs 28.4 % (3.7 reads), k4 54.3 vs 41.4 % (7.1), k8 68.0 vs
  54.3 % (13.5); engine rule (top-K over all 512, resident skipped) top-12 44.6 % with 2.8 reads at 43.4 % precision
  (router 43.2 % / 6.6 reads), top-16 51.9 % with 4.31 reads vs the shipped lead-1 engine12 50.4 % with 5.14 reads on
  the same passes. At 4.8 reads: top-k 44.4 % (pre-registered primary, < 45 -> park), engine rule 53.3 %; leave-one-out
  46.2 / 55.6. Their router lines reproduce check2.txt exactly. NewIdeas decides: park, or b33 + an engine A/B on the
  engine rule (mine). KEEP data/b32/s10b/ until then (b33 joins to its x). If GO: read TrainLab's REPORT for M1a's form
  (per-layer weights, size in RAM) before designing the A/B; replace-vs-add the lead-1 forecast is the key A/B choice.
  S10c GO (NewIdeas ~16:00, QUEUE S10b row; pass/kill in scripts/b33_runner.sh's header). b33 LAUNCHED 16:16 (detached
  runner, 10-min quiet lock granted at once; capture 16:16-~16:23): miss.bin entries now e | miss << 16 | kind << 17
  (ext s10b_rec: 0 demand, 1 on time = prefetch bytes ready, 2 late = issued not ready, 3 queued = cancelled to
  demand), meta.json gets ext_stats, x kept for all prompts (self-contained, ~0.5 GB). After the unlock + `peer wait`:
  data/b33/labels.txt (scripts/s10b_labels.py: kind split per pass-layer, labels vs the ext counters, passes vs b32),
  check.txt (all misses), check_ld.txt (S10B_LABEL=ld: late + demand only). Smoke test on b32: 4363 passes identical
  to itself, 2.63 misses per pass-layer. TrainLab scores M1a vs router on late + demand. Then delete b32 (and b33 after
  the verdict). KP pricing question (NewIdeas 14:20, QUEUE row KP: Leap's kernels vs what ships, per line, bitwise?)
  is OPEN: price with Leap from Leap's tables + b28 anatomy, no build.
  b33 RESULT (16:16-16:24, rc 0, 477 MB, disk 102.5 GB; note data/b33/b33_note.txt, left for TrainLab + NewIdeas via
  peer say): all 20 output shas = b32 (exact), consistency clean. Misses per verify pass-layer 2.70 = on time 13.7 % +
  late 21.0 % + queued 11.1 % + demand 54.3 %. Labels vs ext counters: on time + late and queued match exactly (the ext
  calls 28,884 more "on time": it checks inside ensure()'s loop after waiting on earlier late ones). NO JOIN to b32: pass
  segmentation is timing-dependent (4228 vs 4363 passes, 13 identical), so b33 is self-contained (x for all prompts).
  Router on late + demand (check_ld.txt) held-out: DEPLOYABLE lead 2 60.7 %; per pass lead 2 k2 25.2 / k4 38.1 / k8
  51.3 / k16 64.4 %; shipped lead-1 approx 43.4 % with 4.9 reads. NEXT: TrainLab's S10c score (PASS >= router + 10,
  KILL < +5); if PASS, design + pre-register the engine A/B (M1a lead-2 picks replace lead-1 router picks). 18:55: b32
  KEPT until the S10c verdict: TrainLab's sticky/s10b_fit.py saves no model, so M1a is retrained from data/b32/s10b
  when it scores b33. Delete b32 and b33 traces after the verdict.
  Mon 22:12 disk ACT (97 GB, Kamen's Cellar Steam install) -> orchestrator; Kamen cleared it (320 GB) and set a quiet
  window to Wed 08:01, lifted Tue 19:17 ("continue researching in the new way": rapid screens).
  KP PRICED Tue 19:20 (data/kp_pricing.txt, QUEUE KP row): exact levers only on 45 GB (R-09 X5 HC -9.7 + gmr24 -3.7 =
  ~-13.4 ms per 16-row check). 24 GB: no exact lever, and the SSD caps ANY GPU saving at the SSD-idle time per pass
  (b28: 5.1 / 6.3 / 3.8 ms code / prose / edit); Leap's kernels don't cover 3c. 12 GB: none exact.
  S10c step-2 PRICE (if TrainLab's S10c-1 lands between +5 and +10): NOT small. b32/b33 hold x only at 8 source layers
  (2, 8, ..., 44), so M1a exists for 8 layers; the A/B needs x at all layers (a new ~7-min capture, ~2 GB), TrainLab
  training 46 per-layer models (M1 = a * router_{L+2}(x) + x dW + b, + affinity table over L's 10 routed ids), a weight
  export, and an engine wrapper: stream.py's sw._bm["next"] = [(gate_{L+d}, ratio, Bd)] already supports d = 2
  (BIGMOE_PREFETCH2), but d = 1 must become skippable (the loop needs B > 0 and breaks at the first width 0), and the
  wrapper needs L's routed ids for the affinity term. Also: the 24 GB pass is SSD-busy 90-98 %, so a lead-2 gain must
  come from fewer wasted reads or more reads in flight, not from on-time rate alone.
  R-18 PAR24 KILL Tue 19:41 (NewIdeas' screen; scripts/par24.py, data/par24/par24.txt; CPU replay through MoonShots'
  wall24 LFU at C_m 147 / C_l 46, capped pool): lockstep answer streams don't cut bytes / token at 24 GB. 2 same-answer
  streams +3.4 % at 16-row checks (116.1 -> 120.0 MB/token; wall24's own baseline 117.4), -2.3 % at 4-row checks;
  4 streams +7.4 / -3.1 %. Unrelated streams +50 / +130 %. Same-answer streams share experts, but only enough to break
  even with one stream.
  S10c-1 PASS (TrainLab Tue 19:48): frozen M1a 52.5 % vs router 33.7 % of b33's late + demand misses, held-out (+18.8;
  LOO +18.9). S10c step 2 = b34 (NewIdeas' rapid-screen size; pre-registered + amended in the QUEUE S10b row): runs A1
  B12 B16 A2, prompt 4 of each domain, 400 tok; B = TrainLab's export ~/TrainLab/data/m1a_8pairs.npz (judge models, b32
  prompts 0-3; verified: the engine's M1a gives TrainLab's top-12 in 13/13 check rows, |s| diff <= 5e-6) at L = 2, 8,
  .., 44 -> T = L + 2 replacing T's lead-1 router lists (bigmoe/m1a.py, BIGMOE_M1A / M1A_K; PRED_LINES=3 + PRED_CAP=61
  in all runs; BIGMOE_TRACE for gate wait + per-layer reads; s10b_trace.py S10B_IDX + rusage disk bytes). Scorer
  scripts/s10c_ab.py -> data/b34/ab.txt. Runner scripts/b34_runner.sh launched 20:09 detached, queued #3. b32/s10b
  DELETED 20:09 (TrainLab released it; s10b_meta.json + s10b_check.json kept). Delete data/b33/s10b after b34's verdict.
  NEXT exact lever after b34 (NewIdeas): port MoonShots' R-16 (W24-ec rANS MSB-3 codes, 32K chunks, bit-exact GPU
  decode, a layer's misses in one dispatch, + 11-bit scales; SSD-only format) = -11.4 % bytes per token at 24 GB.
  R-16 PRICED Tue 20:11 (data/r16_port_price.txt): the GPU decode (~12 ms per pass at 46 GB/s) must overlap the SSD
  waits; after each gate it nets ~-5 % tok/s, decode-while-waiting keeps ~+10-12 %. A 10-min screen of that kernel first.
  b34 RESULT Tue 20:41 (runs 20:16-20:23, data/b34/ab.txt + b34_note.txt): BETWEEN for both arms, exact. Per token at
  the 8 target layers, B12 / B16 vs A: late + demand -8.6 / -7.9 % (noise 0.4), on time +21 / +19 %, their SSD bytes
  -8.8 / +1.2 % (noise 1.2; B12 issues 15 % fewer prefetch reads); whole process within noise (bytes -0.4, gate wait
  -0.4, tok/s +2.3 % with noise 3.9). Sent to NewIdeas (its call: all-layer capture + 46 fits, or stop; extrapolated
  ~-7..-8 % bytes per token on all layers). NOT logged in the QUEUE yet (NewIdeas was editing it). Keep b33 + b34
  traces until NewIdeas decides. Also queued for me: R-27 config A/B (MoonShots' per-layer C_m / C_l, ~-9 % bytes
  per token in its strict replay, data ~/MoonShots/data/laysz_*_lfus.txt).
  NewIdeas GO (Tue ~20:50) on b34 BETWEEN: all-layer confirmation, K = 12 only. Lines: PASS whole-process SSD bytes /
  token <= -5 % at tok/s >= -1 %; KILL > -2 %. b35 = all-layer x capture (x at L = 0..45, BIGMOE_S10B_LAYERS) DONE
  21:11-21:18 (2.1 GB in data/b35/s10b, 20 shas = b33, exact; first try failed 21:01 on BSD seq's trailing comma,
  data/b35_failed_2108). TrainLab fits 46 pairs -> ~/TrainLab/data/m1a_all.npz; then the confirmation A/B (bigmoe/m1a.py
  takes any pair set: chained pairs drop every covered lead-1 list). Delete data/b35/s10b (+ b33) after TrainLab's fits.
  b36 = R-27 per-layer pools A/B (MoonShots' ~/MoonShots/data/laysz_engine_147_46.json via BIGMOE_TIER_SIZES) KILL
  21:01-21:08: bytes/tok -1.5 % (noise 1.0), tok/s -0.6 %, late + demand -3.3 %, exact (data/b36/ab.txt). R-34 RAM24
  probe (scripts/ram24_probe.py, data/b36/ram24.json): spec prefill peaks 24.26 GB vs AR 22.16 (the +2.2 GB is the
  prefill path), decode active 21.35, footprint 22.9; HC mixers 1.26 GB, embed / lm_head 0.32 each. Sent to MoonShots.
  b37 = R-37 SB-24 A/B (Leap's R-11c: BIGMOE_VERIFY_MIDLOOP=4 + SPEC125_COMMIT_ASYNC=1; ~/SpecDecode 2d4fa7b) queued:
  8 runs ABBAABBA of s10_anatomy (3 prompts x 256 tok); PASS >= +2 % tok/s with equal shas, KILL < +0.5 %.
  Runners now stop each run's whole process group (set -m + kill -- -PID, orchestrator's rule 20:5x).
  QUEUED R-38 PF24 (NewIdeas Tue ~21:25, exact, from the RAM24 trace; after b37, order mine): (1) take spec125's
  prefill transient out (~2.2 GB over AR: prefill through the AR path, or chunked; spec == ar2 holds by shas), (2)
  embed_tokens on the SSD (0.318 GB, a row read per token), (3) give the ~2.4 GB to the pools and A/B. PASS: peak
  <= 23.9 GB with all shas equal AND bytes/token <= -5 % at the bigger pools. KILL: still > 24 GB, or better than -2 %
  only. Step (1) alone (staying inside 24 GB) is worth keeping even if the pool half fails. Start: find what spec125's
  prefill holds that greedy's doesn't (ram24_probe: 1-token spec generate peaks 24.26 vs greedy 22.16). Lead (code
  read, 22:15): spec125._prefill_call returns the hidden of EVERY prompt row (return_hidden=True), then
  _MTPHead.append runs mtp_update_cache over all prompt rows (the MTP layer's MoE = gate layer 48, prefill-style over
  n rows); greedy does neither. Next: one probe splitting the peak into trunk prefill / kept hidden / MTP append.
  b37 KILL 21:26 (tok/s -0.3 %, exact). b38 (all-layer M1a confirmation) running 22:12 under a lock queued with
  `peer lock` (the hook blocks runner launches while others measure; queue the lock first, then HAVE_LOCK=1).
  b38 RESULT Tue 22:25 (runs 22:12-22:18, data/b38/ab.txt): PASS on the confirmation lines, exact. All 46 pairs, K = 12
  vs A: SSD bytes/tok -7.9 % (noise 0.2), late + demand -14.3 %, on time +34 %, SSD busy -10.3 %, gate wait -9.8 %
  (noise 9.8), tok/s +0.3 % (noise 2.3; code +1.1, prose +0.7, edit +2.3, math -4.0). Why tok/s stays flat: gate wait
  per token -1.9 ms (19.6 -> 17.7) but the rest +2.0 ms (32.5 -> 34.5): M1a's own cost. m1a.py upcasts each layer's
  Wf to f32 every pass (2560 x 512: ~8 MB of traffic per layer per pass) + ~7 small kernels per layer, ~3-4 ms per pass.
  NEXT (b39): a cheap M1a (f16 weights, f16 matmul, no per-call upcast; A folded in as one [x, onehot(ids)] @ [Wf; A]
  matmul) vs A, same lines + tok/s. Adoption (exact, +145 MB RAM) waits for b39 and R-38's RAM headroom.
  b39 BUILT (bigmoe/m1a.py BIGMOE_M1A_F16=1: f16 scores in one mx.compile'd function, = the f32 top-12 on random
  inputs; scripts/b39_runner.sh, lines PASS tok/s >= +3 % AND bytes <= -5 %, KILL tok/s < +1 %), ran 22:27-22:34.
  b39 RESULT 22:34: KILL on its lines, exact. bytes/tok -8.7 % (noise 0.5), late + demand -14.2 %, SSD busy -10.5 %,
  gate wait -7.9 %, tok/s +0.9 % (noise 0.6). Per token: gate wait -1.5 ms (19.25 -> 17.75), the rest +0.9 ms (b38:
  +2.0): the cheap path halves M1a's cost but the wall gain stays ~1 %. Gate wait is only ~19 of ~51.5 ms per token
  (wall incl. prefill; decode ~42 ms/token), so at 24 GB the bigger share is non-gate time (verify GPU, MTP draft,
  commit, Python), and part of the SSD cut became SSD idle. M1a stays an exact BYTES lever (-8.7 %): worth more where
  the SSD dominates (12 GB line). NOT adopted at 24 GB.
  ASKED (NewIdeas ~22:40, light, no rush): one line splitting ~51 ms/token into gate wait / verify GPU / MTP draft /
  commit / Python / other, to pick the next 24 GB screen (Leap's kernels vs cheaper draft vs Python trimming). Plan:
  s10_anatomy.py saves only part of spec125's stats; save all of `s` (t_verify, t_commit, t_head, ...) per prompt,
  one traced run (BIGMOE_TRACE=1) on code / prose / edit under a 10-min lock; verify GPU = t_verify - gate wait.
  DONE b40 (23:22-23:24, data/b40/split.txt): decode 34.1 ms/tok = gate wait 19.2 (56 %) + verify GPU 10.9 (32 %) +
  outside verify ~4 (draft 1.5, commit 0.8, head 0.1, Python ~1.6). R-38 probe: the +2.1 GB prefill peak is the MTP
  head over the prompt rows (its non-tier _sync_call builds a full-union expert scratch); evaluating hid first is
  bitwise but no help. FIX: BIGMOE_MTP_PF_GROUP=48 (grouped prefill for the MTP layer only; MTP drafts only, so the
  verified tokens stay exact): b41a 23:35 spec prefill peak 24.17 -> 21.97 GB (= trunk only), same prefill time.
  b41b = R-38 A/B (A shipped vs S = MTP_PF_GROUP 48 + C_m 159 / C_l 49): GPU runs DONE 23:45-23:52 (before Kamen's
  quiet night 23:53-08:01, so valid) + ram24 probe on S; its CPU scoring (r27_ab.py AB_LINES=r38 -> data/b41b/ab.txt)
  is frozen with the runner (pid 41607) and runs when PAUSE clears after 08:01. Start nothing until then.
  b41b RESULT Wed 08:17 (data/b41b/ab.txt, ram24_S.json): R-38 PASS on NewIdeas' lines, exact (all shas equal). S
  (MTP_PF_GROUP 48 + C_m 159 / C_l 49, pools 18.41 vs 17.07 GB) vs A: MLX peak per prompt 23.79 vs 23.49 GB; code
  prompt 0 (ram24 on S): spec decode peak 23.60 GB (shipped 24.36); SSD bytes/tok -5.4 % (noise 1.1), gate wait -4.6 %,
  late + demand -7.2 %, tok/s +2.7 % (noise 1.6). CAVEAT for the budget definition: phys_footprint at the decode end
  24.25 GB on S vs 22.91 shipped (= the +1.34 GB pools); if "24 GB" means footprint, C_m ~156 / C_l ~48. Adoption
  (exact): MTP_PF_GROUP=48 alone is a pure win (-2.2 GB prefill peak); the pool size waits for NewIdeas' budget call.
  BUDGET = LIFETIME PEAK phys_footprint (NewIdeas Wed ~09:10: RUSAGE_INFO_V4 u28 over load + prefill + decode, one mode
  per process, worst prompt = code prompt 0; line <= 23.9 GB, 24.0 hard). b41c (Wed 15:34-15:37, data/b41c/*.txt):
  A0 = OLD SHIPPED (147 / 46, no MTP group): 25.36 GB, OVER the hard line by 1.36 GB (25.20 already in the spec
  prefill) -> every earlier 24 GB tok/s was measured over budget. A1 = + MTP_PF_GROUP=48: spec-mode lifetime peak
  23.16 GB (inside); the probe's later AR phase in the same process lifts it to 23.66 (two modes in one process, not the
  budget mode). S at C_m 148 (auto-sized from the 23.66, too conservative): 23.23 spec / 23.71 with AR. Re-size from the
  spec-mode 23.16: ~0.69 GB of pool room -> C_m 152 / C_l 47 (expect ~-3 % bytes, short of R-38's -5 % line;
  embed_tokens on the SSD would add 0.32 GB). Next: a spec-only probe (no AR phase) at 152 / 47, then the A/B A1 vs S.
  b41d RESULT Wed 16:03 (runs 15:39-15:47, data/b41d/ab.txt + probeS.txt): S = MTP group + C_m 152 / C_l 47 (pools 17.62
  GB): spec-mode lifetime peak 23.63 GB on code prompt 0 (inside 23.9), exact; SSD bytes/tok -0.9 % (noise 1.6) ->
  R-38 pool half KILL (tok/s +5.9 % but A1-A2 noise 7.4 %). R-38 FINAL: MTP_PF_GROUP=48 (adopted) is the win: the 24 GB
  stack goes from 25.36 GB (over budget) to 23.16 GB; pools stay 147 / 46. embed_tokens on SSD: not built (NewIdeas).
  ROLES (Kamen Wed 15:47, STATE.md): BigMoE = the 24 GB line; Leap = kernels; TrainLab = MTP head (D-05 MTPHYB moved
  there: share per-depth MTP logs if asked); Breakthrough + Fit12 = 12 GB; EvalSuite = verdicts; NewIdeas + MoonShots =
  ideas. Next for me: the R-16 overlap screen (data/r16_port_price.txt).
  b42 RESULT Wed 16:19 (R-16 overlap screen, runs 16:12-16:19, data/b42/ab.txt + bg_B*.log; scripts/r16_bg.py,
  b42_runner.sh): KILL, exact. A second process ran MoonShots' GPU rANS decode of real MSB-3 codes paced to 6 GB/s
  (= the engine's MSB read rate) beside the engine: it held 6.00 GB/s, 0 mismatching bytes (31-38 GB/s while decoding
  vs 46 alone), but the engine lost 7.1 % tok/s (code -7.1, prose -9.1, edit -5.3; verify +9-12 ms per pass). The
  decode competes with the verify GPU work; a ~7 % cost eats most of what the -11.4 % bytes could buy (gate wait is
  ~half of decode time). R-16's port is NOT worth it at 24 GB as measured; it may still pay on the more SSD-bound 12 GB
  line (Breakthrough / Fit12).
  R-43 DFL24 (NewIdeas Wed ~16:25: DFlash2 16-row checks in the 24 GB engine; pricing, no build) = b43 (16:32-16:34,
  data/b43/price.txt): KILL on the pricing. The gate row carries <= 92 expert ids (MAXK 92 = 9 rows), so 16-row gated
  checks need a build (gate-row lines + ext); b43 swept the verify width on copy prompts (fixed widths, long n-gram
  drafts). Per pass on code text, 3.76 -> 6.74 rows: gate 61 -> 97 ms, GPU 29 -> 44, commit 7.6 -> 13.9, reads 533 -> 856
  (~12 ms of gate wait, ~108 reads, ~5 ms GPU, ~2 ms commit per extra row; rejected rows cost the same as kept ones; MAXK
  92 itself adds ~19 ms GPU per pass). At 16 rows with D-02b's kept 9.57 (code) / 7.00 (math) and 12.5 / 7.9 ms drafting:
  code 22.8-27.3 tok/s vs A 25.1 (-9..+9 %), math 16.8-20.1 vs 19.9 (-16..+1 %); break-even kept per check code ~8.9-10.5,
  math ~7.0-8.3; +25 % on code needs ~11-13 kept of 16. At 24 GB the extra rows' expert reads eat the per-pass savings.
  NEXT: R-44 REPACK24 (NewIdeas Wed ~16:40, confirmation build; QUEUE row): (a) M-01 exact re-pack of the scale / bias
  fields (sign + 2-bit exponent with escape + 7 raw mantissa bits; b as a 3-bit residual), plain unpack at load; default
  on NewIdeas' word if every sha equal AND rusage bytes/tok <= -2.5 %, any mismatch kills. (b) M-03 POM behind a switch
  (plane-separated records top-2 / plane 3 / LSB, a tier-2 path in the expert kernel, per-slot plane state + upgrade
  reads; non-exact): to EvalSuite's strict verdict if bytes/tok <= -12 % at equal pools and tok/s not worse; > -6 % kills.
  Disk: stop at 110 GB (313 now). Send NewIdeas rough hours BEFORE starting if > 1 day. Read MoonShots' M-01 / M-03 rows,
  ~/MoonShots/scripts/pom24.py, data/kl125/screen_pom.txt first.
  Hours sent (data/r44_hours.txt, ~3-4 days). NewIdeas GO Wed 18:43: (a) M-01 first; (b) POM only after (a) passes, on the
  same converter; df before each write; spread the hours on usage-pace (no rush on b); report (a)'s verdict with its file.
  POM 2-plane slot = 3-bit slot with plane 3 = 1 and bias b3 - s3*(1 - mean_g(p3)) (MoonShots 17:34: the group's mean of
  plane-3 bits, NOT the midpoint -s3/2; ~22 KB/expert of 7-bit counts). Before (b)'s A/B: check on a few experts that the
  slot reproduces MoonShots' measured tier-2 values exactly.
  MoonShots 21:xx: POM re-priced on the shipped narrow MTP path (~/MoonShots/data/pom24_r4a3_159_44.txt, _r8a5_): R2 4
  = -18.1 % (4/3) / -17.9 % (8/5), inside the confirmed run -> start POM at R2 4, not 6.
  NewIdeas 21:2x: Leap will ask BigMoE for the 48-layer streamed REF2 + SB A/B at 45 GB after MTP Head's D-09 tonight;
  keep M-01's SSD / CPU load out of that A/B's quiet lock. (Info: EvalSuite saw results/ref (10-20, 7dfe9d1+dirty) differ
  from today's stock d0daa68 on 10 / 210 rows, scores equal; baselines moved to ref.r2 + REF2; no chase asked.)
  FULL STOP (Kamen Thu 02:05, relayed by the orchestrator 02:11; STATE.md last section): nothing runs or starts until
  Kamen says start (not 08:00, not Thursday). At 02:12 BigMoE had NOTHING mid-flight: no runner, no queued lock, no
  watcher; R-44 had not started (pacing kept claudesub's sleeps going all night). Stopped: pacing sleep bxa6rz0my
  (TaskStop) and the health-review cron f0eb3f70 (CronDelete; the reviews wait too).
  RESUMED Thu 15:35 (Kamen; orchestrator 15:4x): health cron re-created (e782b287, :11 every 3 h); R-44 (a) M-01 started:
  - scripts/m01_fields.py: s3 / b exponents fit a 3-bit window per expert (span <= 6 / 7), b3 exponent - s3 exponent in
    {+1, +2, +3}, b3 sign == NOT s3 sign everywhere, no zeros / denormals. Self-contained parts (b cannot use s3 / b3:
    the tier pools read MSB and LSB parts separately; a cross-part b residual would add only ~0.5 % more).
  - records3m/ (scripts/m01_convert.py, 108 s, every expert unpacked + compared bitwise): MSB 2,162,688 -> 2,048,000 B
    (132 -> 125 blocks), LSB 770,048 -> 720,896 (47 -> 44); 68 GB; disk 246 GiB free. Index keys r3_recsz / r3_msb_sz
    (records3's index already has src_recsz = the old records/ size: never use that key for sizing).
  - ext: BIGMOE_M01=1 -> read_expert unpacks M-01 parts / full records (m01_expert); off = unchanged paths. tier.py picks
    records3m under BIGMOE_M01; stream._tier_layer sizes pools from r3_* (equal pools 147 / 46). Build ext/build_m01.
  - Expected (b41d split: 117 MSB + 27 LSB reads / tok of 350 MB rusage): ~-4.5 % bytes/tok.
  - 16:39 loader tests PASS bitwise (data/m01/build_test.txt). NOTE: test reads without F_NOCACHE had left records3 pages
    cached (54 GB/s "loads"); evicted with mmap MAP_SHARED + msync(MS_INVALIDATE) and the test now uses F_NOCACHE.
  - b44 17:01-17:08 **PASS** (data/b44/ab.txt, 700e969, LEDGER R-44a): every sha equal (4 runs), rusage bytes/tok
    353.1 -> 336.2 MB (-4.8 %, noise 0.1 %), gate wait -5.0 %, tok/s +2.0 %, pools 17.07 GB both, lifetime peak 23.10 GB.
    Reported to NewIdeas (ojox-bd, now on claudesub2: `peer send ojox-bd`, SendMessage cannot reach it) 17:18. Default on
    its word: the shipped env gained BIGMOE_M01=1 (runners; mtp_depth.sh Thu 19:3x); ext/build rebuilt 17:56 (has M-01,
    POM, LP1).
  - (b) GO + LP1 (NewIdeas 17:3x): one A/B A P L L P A at equal pools (b45_runner.sh, scorer r44b_ab.py). Lines: P vs A
    PASS <= -12 % rusage bytes/tok with tok/s not worse, KILL < 6 %; L vs P PASS a further <= -6 %, KILL < 3 %. Log the
    shares rank >= 4 uses at 2 planes (replay 20 %) and rank-1 uses w/o LSB (26 %). Non-exact -> EvalSuite, then Kamen.
  - POM design (Thu 17:xx): the Eval suite's tier 2 (model.py tier_weights n=2: codes q4 & 12 at s4, bias
    bf16(b4 + s4 * mean(q4 & 3))) == a 3-bit slot with codes 2 m2 + 0 (plane 3 = 0, NOT 1) and bias2 in the b3 piece,
    bitwise, no kernel change. records3p/ (scripts/m03_convert.py) = seg1 (q2 planes + M-01 fields with bias2, 87
    blocks) + seg2 (p3 plane + 9-bit b3, 43 blocks), no LSB part; full misses + sidecars still read records3m (a
    rebuild_w4-class CPU spread costs 0.084 ms/projection on P-cores, 4x a memcpy: only 2-plane reads / upgrades pay it).
    ext: rank = position % K in the routing row; misses used only at rank >= R2 -> seg1 (2-plane slot); a rank < R2 use
    of a 2-plane slot -> seg2 upgrade in place; 2-plane slots are NEVER published (OoO phase 1 / fast path never see
    them, so upgrades cannot race the GPU); JIT prefetch mode from bit 20 of each forecast (stream.py: sorted top-b per
    row under POM). LP1: sidecar rank-1-only misses -> no read / no insert, slot -2 (spin kernel decodes 0x3FFFFE), and
    tier.py patches tierglu's 7 kernel sources: a 4-bit pair with lsb_slot < 0 runs at tier 3. Counters ext.pom_stats().
    Tests: m03_suite_check.py (2-plane == the suite), test_records3p.py (ext paths + GPU LP1 kernel); m03_build_test.sh.
  - b45 18:17-18:27 (ce9a5e8, data/b45/ab.txt, LEDGER R-44b): P **BETWEEN** (bytes/tok 342.2 -> 277.3 MB, -19.0 %;
    tok/s -1.9 % with A1-A2 tok/s noise 3.0 %; gate wait -5.8 %), L **BETWEEN** (a further -4.5 %, tok/s -0.6 %; L vs A
    -22.6 % / -2.5 %). Shares: rank >= 4 uses at 2 planes 31 % (replay 20 %), rank-1 uses w/o LSB 37.5 % (replay 26 %);
    30 % of 2-plane reads upgraded later. SSD busy ms/tok only -6.5 % for -19 % bytes (per-read cost; upgrade reads on
    the critical path). The s10b harness's lifetime footprint is 24.1-24.5 GB in EVERY arm (b44's A: 24.5 harness vs
    23.10 probe), so not a POM effect; L's probe skipped (NOPROBE). Sent: BIG 19:24, NewIdeas 19:2x with the choice:
    stop POM at 24 GB, or one screen with full-precision prefetch (2-plane only for sync misses used only at rank >= 4).
    WAITING for NewIdeas' call. Runner note: its `peer wait` before the CPU-only scorer sat 55 min behind others' locks;
    the scorer only reads meta.json, so drop that wait in future runners.
  - NewIdeas 19:0x (Fit12 R-45T): the bounce buffers in pom_read / read_expert were raw thread_local pointers, never
    freed; GCD retires idle workers, so a long-lived server leaked ~one buffer per worker per idle gap. NewIdeas 19:3x:
    POM STOPPED at 24 GB (agreed); bounce pool fix GO (exact); VD + LP1 to be priced by SSD time first (R-51,
    MoonShots), then BigMoE builds it (Kamen 19:27 OK'd a 2nd non-exact 24 GB version).
  - BOUNCE POOL FIX (b46, in progress Thu 19:4x): ext/bigmoe_ext.cpp `struct Bounce` = one shared, mutex-guarded pool
    (LIFO; a buffer grows to the largest part it carried; ext.bounce_stats()). Built into ext/build_next (my staging dir) only; the
    pre-fix binary is kept as ext/build_tl (copy of build_m01's 17:56 .so). scripts/b46_runner.sh (one quiet lock):
    loader tests bitwise on build_bp, scripts/test_bounce_pool.py (ext-only, 64 reads per cycle, 12-s idle gaps) old vs
    new, s10b_trace on both builds with S10B_GAPS=4:12 (new: every sha must equal b45 A's 4633d70e77 5f2c200e62
    8f02448059 2ae4ee95ae). ext/build + build_m01 take the fix at their next make. Result -> NewIdeas (+ Fit12 FYI).
    b46 DONE 20:15 (9f6c4f5, data/b46/ab.txt, LEDGER BP1): exact (4 shas = b45 A; loader tests PASS); ext-only: old
    +32 MB per 12-s gap (14 of 18 GCD workers retired each gap), new flat (pool 18 x 2.05 MB); engine: old +139 MB /
    gap, new +92 (rest = frspec pruned head per request in a GC cycle: gc.collect() per request would bound it; told
    NewIdeas). b47 20:33-20:35: official ram24_probe new 23.090 / 23.074 vs old 23.082 / 23.131 GB = UNCHANGED (the
    harness's 23.89 vs 24.19 hint was noise); ext/build_m01 and ext/build rebuilt with the pool (exact).
  - NEXT (NewIdeas 20:4x, both exact, in order; start at the 21:10 pacing wake):
    (1) DONE b48 PASS 21:41 (LEDGER FRS1; FIX growth <= +4.9 MB per request vs NOFIX +95; shas equal). Was: GO port Breakthrough's B12_FRS_NOCYCLE (SCOREBOARD 127fdf8: frees replaced FR-Spec heads without gc; 6-row
        creep 0.107 vs 0.631 GB) to the 24 GB engine. PASS: every sha = the b47 default AND footprint growth <= 0.02 GB
        per request over the 4 x (12-s gap + 16-token generate) run (S10B_GAPS=4:12). Fallback: gc.collect() per request.
    (2) GO R-52 SCRATCH24: audit first (CPU, no lock): in the shipped 24 GB and 45 GB configs, which decode / prefill
        calls take _sync_call / _sync_grouped / _sync_segment / tier.prefill_call; fresh scratch bytes per decoded token
        and per prefill chunk. Screen only if >= ~0.2 GB per token or per chunk: one reused scratch per layer (no
        clear_cache in the loop). PASS: every sha equal AND tok/s or TTFT +5 % AND peak within +0.1 GB -> default on its
        word; KILL under 2 %. NewIdeas sends MLX's fresh-allocation cost per GB (micro-bench).
  - Thu 21:1x KAMEN (via the orchestrator): 45 GB to 350 FIRST, then 24 GB (RULES.md '45 GB FIRST'). Engine work for
    the 45 GB route goes first: R-50's adoption (Leap merges scripts/ref2_slot_patch.py into its ref2.py after 3u /
    R-50b; it swaps BigMoE's stream._sync_call -> keep _sync_call / _STAGE / _stage_drop / SYNC / ext stable), Leap's
    scratch reuse (45 GB prefill: PF1's [pool; staging] gathers ~1.1-1.4 GB per layer call + clear_cache), PF1 fix (PASS).
  - R-51 (MoonShots 21:16, ~/MoonShots/data/r51_busy.txt): DON'T build VD + LP1 (demand reads = POM's; over the KLD
    gate at the engine's real shares F 43.5 % / F1 37.5 %). Leads: lazy upgrades off the critical path, fewer unused
    prefetches. Sidecar reads look free in SSD time (L = P in busy / gate wait despite -54 % sidecar reads).
  - NIGHT 10-29/30 (Kamen 22:3x, going to bed): NO new work before 00:00; from 00:00 research as usual (45 GB first,
    usage-pace) in quiet research mode FAN_CAP 3500 rpm; heat pauses jobs (check ~/.local/share/quiet/PAUSE between
    passes); lid closed = pause. Next-caliber finds to the orch_addr.sh address.
  - Kamen 22:06: the 45 GB is an ESTIMATE, not a hard cap: more RAM (more experts resident, a larger C) is OK on the
    45 GB route when it pays; guards stay (wait for free memory before a load, stop on swap growth > 2 GB). The 24 GB
    line's limit is unchanged.
  - R-52b PASS 22:03 (data/r52b/r52b_screen.txt, LEDGER R-52b): BIGMOE_SCRATCH_KEEP=1 on the stock 16-row check path at
    C 192: warm checks 1077 -> 342 ms (HumanEval/68) and 1079 -> 386 ms (prealgebra/1640), bit-equal on every window;
    footprint +0.45 GB (MLX cache keeps the 9 recycled buffers). First try 21:59 was stopped by the swap guard during
    the C 192 load (10.2 -> 12.6 GB); the retry passed it. DEFAULT since NewIdeas 22:1x (=0 restores the fresh
    scratch; Leap / EvalSuite told). NEXT (NewIdeas 22:1x, 45 GB first): (1) live-loop tok/s at 45 GB, stock arms base
    vs keep (Leap's R-50 live harness or my own spec loop), /68 + prealgebra/1640, every sha equal, information only;
    (2) R-55 GATE16 (sync-free 16-row gate) if Leap's Metal-timestamp split shows a sync bubble >= 80 ms of its ~200 ms
    warm REF2 check (Leap: ~80-100 ms -> ~90-110 tok/s exact on code at 45 GB, a lead); (3) the 24 GB TTFT screen.
    Leap R-50c 22:2x (~/Leap/data/r50c_screen.txt): warm exact 16-row check at C 192 (REF2 + SB, slot call) = 185 ms;
    GPU-idle bubble ~60 ms (ensure 22.7 [44 misses, ~123 MB + 48 calls] + Python 12.1 + 97 syncs x 0.256 ms); experts
    + sync 77.7 (~13.4 GB at ~173 GB/s), pre-router GPU work 64.6. 60 < 80 = BETWEEN on R-55's line: NewIdeas decides.
    A sync-free gate recovers at most ~60 ms (185 -> ~125) and only with ensure's misses prefetched as the gated path does.
    R-55 GO (NewIdeas 22:50, after 00:00): build the sync-free 16-row gate + prefetch ensure's misses. PASS: logits
    hashes equal AND warm check <= 135 ms; KILL > 165 ms. Leap S45 00:29 (~/Leap/data/s45_speed.txt, Leap 23abf98):
    REF2's exact live DFlash2 loop at C 192 = 25.1 tok/s code / 19.2 math, median cycle 320 ms (drafter ~13 + check
    and commit 266-397 ms); 413-779 misses per check = 111-194 ms of SSD reads, serial with the ~185 ms warm compute
    (ensure sits between router and experts). My read: overlapping those misses is the bigger half (~1.5x if fully
    hidden), the sync bubble the smaller. usage-pace SLEEP 00:43 -> ~06:01 (weekly 73 % > line 70 %): build at wake.
    R-57 PREFETCH16 (NewIdeas ~01:2x, after R-55): lookahead prefetch of layer L+1's experts on the 16-row path. PASS:
    SSD wait per check -50 % AND check+commit -25 %, tokens == REF2. PIN: EvalSuite's runner 29 (R-56 LIVE16) shasums
    bigmoe/*.py/.so/.metal until ~/EvalSuite/results/R56_DONE (~02:00-03:00 + heat pauses): an edit there stops it, so
    build R-55 / R-57 in a git worktree until then (or ask EvalSuite to re-pin between arms).
    PIN LIFTED 02:5x (EvalSuite: R-56's stock arm deferred, NewIdeas' call): build in place. R-56 result: REF2's live loop
    is exact only under ~512 keys (QSA attention, Leap's 4a; ~/EvalSuite/docs/RESULT_r56_2026-10-30.md). LID CLOSED since
    ~02:57 (lid_guard quiet window to 14:57 or lid open): check `ioreg -r -k AppleClamshellState -d 1` before GPU runs.
  - **R-55 GATE16 PASS Fri 16:29 (data/r55/r55_screen.txt; build 4be3b31)**: the sync-free gate now carries up to 185 ids
    (BIGMOE_MAXK 93..185: 2-4 more id lines per routing row, 2+k-line release entries; MAXK <= 92 layouts unchanged;
    ext only in ext/build_next so far; stream.GATE_N[0] = per-call cap, default MAXK). With BIGMOE_MAXK=160 a 16-row
    check takes the gate instead of _sync_call (REF2's experts kernel on the same pool slots). Warm check + commit at
    C 192 (REF2 + SB, ABBA in one process): HumanEval/68 232.6 -> 117.3 ms, prealgebra/1640 213.7 -> 106.2 ms (gate
    111.8 vs slot 223.1; line <= 135), logits bitwise equal on every window of all 4 passes; 48 loader-served gates per
    check, no timeouts. Ext-only smoke test scripts/test_gate_wide.py: 300 passes each at MAXK 40 / 80 / 160, all rows
    right. BIG sent 16:3x to the orchestrator (7333) + NewIdeas told. NOT default: needs MAXK 160 + the new ext in
    ext/build (rebuild) and EvalSuite's live audit; NewIdeas decides. NEXT: R-57 (scripts/r57_screen.py + r57_runner.sh,
    queued for a 15-min quiet lock): live DFlash2 loop at C 192, slot vs gate vs gate + ranked look-ahead prefetch of
    L+1 (B 96, PRED_LINES 4, PF_JIT, QD 4, VICTIM 24; predictors attached in the script because EvalSuite refuses
    BIGMOE_PREFETCH). Committed d7106c0.
  - **R-57 screen Fri 17:00 (data/r57/r57_run.txt)**: live DFlash2 loop at C 192, REF2 + SB, 256 tokens, every run's tokens
    == REF2's row (12 / 12). R-55 LIVE (slot -> gate): HumanEval/68 25.6 -> 40.4 / 39.6 tok/s, prealgebra/1640 17.1 /
    17.4 -> 23.0 / 23.6 (prompt means 21.4 -> 31.7 tok/s, +48 %); median cycle 416 -> 343 ms (/68), 291 -> 217 ms
    (1640). One slot run lost 323 s to a heat pause (excluded; the script's INVALID flag is that run). R-57 (gate + ranked
    L+1 look-ahead, B 96, PRED_LINES 4, PF_JIT, QD 4, VICTIM 24) vs gate: demand SSD per check -20 % (151 -> 121 ms) but
    misses +10 % (597 -> 658: wrong guesses evict useful experts at C 192), check + commit -1.2 %, cycle -1.4 % ->
    KILL on its line (< -10 %). BIG follow-up (live +48 %) sent 17:0x to 7333; NewIdeas told, offered (a) a narrow R-57
    variant, (b) the 24 GB TTFT screen, (c) 16-row verify on the 24 GB tier path with MAXK 160. NewIdeas 17:04: R-57
    KILL recorded, no variant (no cache slack at C 192); next (1) GATE16 on REF2-T tiers, (2) 24 GB TTFT, (c) later.
    The orchestrator 17:0x: headline the steady-state cycle; +48 % leaned on a cold code slot run.
  - **R-58G PASS Fri 17:46 (data/r58g/r58g_invt_screen.txt)**: Leap's R-58 INV-T (~/Leap/scripts/r58_invt_screen.py) copied
    as scripts/r58g_invt_screen.py with the check's 16-row tier calls on the gate (MAXK 160, build_next, GATE_N 160 ->
    tier.tier_call, the same 3c kernel on gate slots; TIER_COMBINE popped): HumanEval/68 (383 keys) and geometry/702 (536
    keys) 16/16 rows bitwise + every DecoderLayer equal vs REF2's AR; 48 gated tier calls per check, ref2's slot branch 0;
    control (gate off + tiers branch off) 0/16 from layer 0. Leap's runner 43 PASSED the same on _tier_slots (standard
    ext), so gate == _tier_slots on BIGMOE_TIER 4433333333 / 3c at C 192. No code change was needed for tiers.
  - **R-55L Fri 17:57 (data/r57/r55l_summary.txt; the settled live number)**: slot vs gate on S45's six prompts, C 192,
    REF2 + SB, DFlash2: steady-state tok/s (checks >= 2, prompt means) 23.7 -> 32.0 (+35 %; per prompt +31..+38 %),
    whole 256-token runs 21.9 -> 31.0 (+41 %), median cycle -23 %; every token == REF2's row. The screen's 690 s alarm
    cut gsm8k/708 after one run per arm (/91's second slot run lost 365 s to a heat pause: excluded). Settled number sent
    to 7333 at 17:5x (BIG), NewIdeas + Leap told. Committed eda7586.
  - **S45-T (NewIdeas 18:2x; scripts/s45t_runner.sh, r57_screen.py R57_TIER=1)**: A = REF2b gate at C 224, B = REF2-T
    4433333333 / 3c on the gate (C_l 112 -> C_m from C 224's bytes, M-08: C_l >= 96), + arm gate+t (Leap's t 0.3
    truncation) in B's process. Try 1 (19:17, data/r57/s45t_try1/): A1 swap-guarded at C 224, so not a verdict;
    within B (clean): + t 0.3 = 47.6 vs 40.4 steady tok/s (+18 %), tokens equal. Try 2 (19:37): A1 swap-guarded again,
    B frozen by a heat pause; stopped by me at the 19:41 review (swap 24 GB, Kamen's own apps busy: iOS 13 GB, Steam).
    Runner now needs >= 78 % free (~50 GB) and skips an arm otherwise. RE-RUN when memory allows.
  - **CAP45 for Fit12's R-57b-R** (scripts/cap45_runner.sh, shared lock, data not timing): live loop at C 192 on the gate,
    S10b x for all 48 layers + ids + res0 (slots per expert at loop start) + tokens per prompt, routers.npz (w1..w47
    f16), miss.bin -> data/cap45/. Fit12 waits for it (told 19:4x it is delayed by memory). Launch when memory allows
    (the runner waits for >= 78 % free and no other process > 20 GB).
  - **CAP45 DONE 01:09 at C 160** (data/cap45/, 876 MB, npz not in git; every token == REF2): Fit12's R-57b-R replay
    matched miss.bin within +0.30 %: at C 224 (424 misses / check) 16 RESERVED slots per layer + corrected L+1 forecast
    cut demand misses 44 % (raw 40 %, oracle 55 %; wasted 98 / check); recall 0.693 corrected (0.605 raw). Upper bound.
  - **R-57b GO (NewIdeas 01:2x, at my next wake; exact: reads only)**: N 16 reserved slots per layer = the ext's spare pool
    (BIGMOE_SPARE=16; EvalSuite's env forces 0: override before the ext loads) + BIGMOE_PF_VICTIM=0 (prefetches never evict
    main slots; JIT cap = spare) + PF_JIT / QD 4 + the ranked L+1 list with Fit12's correction (raw @ W{T} + b{T}, asked
    Fit12 01:3x to export ~/Fit12/data/r57b/corr.npz). Equal RAM at C 176: A = no reserve (C_main 176) vs B = C_main 160
    (the 16-row gate needs C_main >= 160, else ensure aborts) + 16 reserved; A-B-A processes, live REF2b gate loop, every
    token == REF2b; shared first, then C 224 when memory allows. PASS demand SSD/check -25 % AND cycle -10 %; KILL cycle
    under -4 %; PASS -> one quiet confirmation. Order vs S45-T: whichever fits memory first.
  - **S45-T DONE Sat 03:21 (69aa3ca, data/r57/s45t_screen.txt)**: at C 224's RAM, REF2-T tiers on the gate +15.5 % steady
    tok/s over the REF2b gate (37.0 -> 42.8; median cycle -10 %; per prompt +2..+32 %), + t 0.3 50.9 (+37.5 %); tokens
    equal across runs of each arm. Reported to NewIdeas (not BIG: tiers alone +15.5 %, non-exact).
  - **R-57b KILL Sat 07:12 (a8abb2e, data/r57/r57b_screen.txt)**: equal RAM C 176, 16 reserved slots + Fit12's held-out
    corrected forecast: SSD -9.4 %, cycle -3.7 % (5 prompts), exact. Late reads + the smaller main pool eat the replay's
    -44 % misses (in-time completion not modelled). NewIdeas + Fit12 told.
  - **R-55 ADOPTED Sun 04:0x (NewIdeas; 8e2b22e)**: default BIGMOE_MAXK 160 (gated.py setdefault before the ext loads),
    ext/build rebuilt from the R-55 source (old .so in the scratchpad); a > 92-id call takes the gate only if
    indices.size <= bm["C"] (else the sync path). The 45 GB path (EvalSuite REF env, Leap: MAXK unset) is now on the gate.
    ext/build_m01 (24 GB default) was NOT rebuilt (not asked; R-55 changes nothing at MAXK <= 92).
  - **R-52P (NewIdeas Sun)**: adopt PF_REUSE=1 if the official ram24_probe peak <= 23.4 GB: scripts/r52p_runner.sh
    started 04:1x (queued lock). R-60 at 24 GB: only if a shared slot is idle (Breakthrough: +0.5 % at 12 GB).
  - **R-52 ADOPTED Sun 04:0x (ce25fe6)**: BIGMOE_PF_REUSE=1 is tier.py's default (official ram24_probe 22.97 GB <= 23.4).
  - **R-60 MTPDROP Sun 05:36 (691ab74, data/r60/)**: D-22 b3 head via scripts/mtphead.py (BIGMOE_MTP_HEAD, hooked in
    s10b_trace.py + ram24_probe.py; NOT in bigmoe/ while EvalSuite pins it). Quiet: tokens per pass +5.2 % (code +11.6,
    math +14.2, prose -4.9), exact, tok/s flat (+0.4 %), official peak 23.03 GB. Recommended to NewIdeas: no default as
    is; next 8-bit g64 (BIGMOE_MTP_HEAD_BITS=8) + recompiling the MTP prepare graph on the new weights, one quiet A/B.
  - **R-60b Sun 05:42 (5e39275)**: 8-bit g64 + compiled prepare: tokens per pass +7.6 %, tok/s +0.6 %; trunk misses per
    token unchanged (85): 24 GB decode is SSD-bound per token, so kept-per-pass gains don't convert. No 24 GB default.
  - **bytes45 study Sun 05:4x (1363df4, data/bytes45/bytes_study.txt)**: 71.6 distinct experts / layer / 16-row check =
    10.0 GB (4-bit); rows 1/2/4/8/12/16 = 14/23/38/63/83/100 %; REF2-T -20 %; GB per kept token 0.76 (code) .. 1.81 (math),
    mean ~1.36; 350 tok/s needs <= ~0.8 (at ~280 GB/s). Offered NewIdeas a per-prompt lever table (tiers x truncation x C).
  - **THE 45 GB DEFAULT (NewIdeas Sun 06:1x; 1f7c243)**: R57_PRESET=45 = REF2-T 4433333333 / 3c (C_l 112, COMBINE off) +
    the R-55 gate + t 0.3 truncation + ref2's defaults (REF2b key buckets, GDNX); REF2b 4-bit exact = preset unset.
    C TBD by C45 tonight (scripts/c45_runner.sh "224 240 256 272" in one quiet memory turn, ticket 40 min; each C only if
    NO-SWAP >= peak + 8; peak ~33.2 GB at C 192 + 0.14 GB per C; Leap: 29.7 at C 160, 38.0 at C 224, so a 45 GB peak =
    C ~278): this Mac's NO-SWAP (42 day, ~48 clear night) caps it near C 224-240. The runner now keeps the lock alive and
    gates on SSD heat.
    Scoreboard (bytes_study.txt): kept per check mean 7.48; SSD GB per check C 192 1.59 .. 320 0.78 (Fit12's misses).
  - **SEED45 Sun 07:0x-07:3x (MoonShots M-13's pointer "seed the cache by popularity"; CPU replays of cap45, prompts
    chained as one process serves them; data/seed45/)**: (1) THE 45 GB LOOP RUNS LRU: BIGMOE_EVICT_LFU is only in the 24 GB
    env strings, and here LRU beats LFU 0.99 by ~9 % (keep it off at 45 GB). (2) LRU + popularity prior (victim key =
    last-use stamp + 30 x leave-one-out share of checks): misses per kept token -9.6 / -9.8 / -9.4 % vs LRU at C 224 /
    240 / 256 (K 246 / 266 / 287 resident MSB slots), every prompt -5.5 % or better: BETWEEN (PASS >= 10 %); about what
    +8 C units (~1 GB) buy. LFU + prior only matches LRU; pinning the top experts is weak; router near misses KILL. (3)
    Belady's optimum is -60 % at the same C: real headroom, no cheap signal for it. (4) C dominates: misses per kept
    token 52 / 44 / 36 (LRU) at C 224 / 240 / 256. BUILT opt-in (default off, exact: residency only): ext source
    BIGMOE_EVICT_PRIOR=b + set_prior(L, E floats); ext/build_prior only (ext/build untouched); scripts/test_prior_evict.py
    PASS (off = LRU, on = popular kept, LFU + prior too, bytes right); data/seed45/prior45.npz (loo_<prompt> + all);
    r57_screen R57_PRIOR=<npz> sets each prompt's held-out prior. Live arm C45_PRIOR=1 (C 224 again with the prior)
    ONLY on NewIdeas' yes (asked 07:19); pre-registered: PASS = median misses per check -7 % or more, tokens identical,
    steady tok/s not lower.
  - **R-69 (Leap, Sun 07:2x)**: TIER_COMBINE + BIGMOE_OOO are bitwise == today's REF2-T tier path (tensor test at S
    1-16, ~/Leap scripts/r69_ooo_exact.py). Answered Leap 07:32: _ooo_call DOES run on the R-55 gate path (tier_call gets
    post= there; post_ids returns 1 + n slots for up to 185 ids; with PF_JIT off the loader publishes each layer's table
    for the next pass, so phase 1 has real hits). Leap's live R-69L (k69_live.py, A-B-A at C 160, shared) runs till
    08:10. r57_screen: R57_COMBINE=1 keeps TIER_COMBINE (otherwise popped under R57_TIER); R57_REFTOK=<tokens.json>[:arm]
    checks every token against a stored reference (S45-T's REF2-T: data/r57/s45t_B_tokens.json:gate+t); the tier
    flags line reports OOO calls. c45_runner: every run checks REFTOK; C45_OOO=1 adds an OOO + COMBINE arm at the first C
    (only once R-69L passes); C45_PRIOR=1 the prior arm (only on NewIdeas' yes). Tonight's turn: ticket 45 min.
  - **R-69L VOID (Leap 07:3x)**: OOO never engaged in the EvalSuite harness (OOO calls 0): EM.load's SparseMoeBlock
    (evalsuite/model.py `block`, sorted top-k + MLX combine) replaces BigMoE's tier.install_block _call, so tier_call never
    got the scores. Fix in OUR harness (r57_screen, R57_COMBINE=1 only): _fused_block = EvalSuite's sorted block op for op,
    the scores (+ the shared expert for OOO's spin edge) handed to tier_call at 1-16 rows, MLX's combine if a path left
    them unused; wider calls (prefill) go to EvalSuite's block untouched. Leap's R-69b (k69b_live.py, same hook without the
    shared edge, A-B-A at C 160 shared) runs now; the C45 OOO arm runs only if R-69b is bit-identical with OOO calls > 0.
    NATIVE-PATH BUG (not in any EvalSuite-based number): bigmoe/tier.py install_block's _call takes only calls of 8 rows or fewer
    (x.shape[-2] <= 8); MTPLX's stock block does NOT sort the top-k, so 9-16-row calls on a NON-uniform tier plan (REF2-T
    4433333333 at 16-row checks, or K15 verify on a 3-bit plan) get tiers by argpartition position. Widen to 16 (and
    check the shared-expert form: _call uses attention_gate in decode_verify) before the 45 GB default runs natively;
    not while Leap's A-B-A imports bigmoe/. FIXED 07:5x: _call takes up to 16 rows on rank plans (uniform plans keep 8:
    the exact 24 GB stacks are untouched). MTPLX's stock _verify_call also uses attention_gate, so the only change for
    9-16-row rank-plan calls is the score sort. Caveat: EvalSuite's block uses a standalone sigmoid for the shared
    expert, attention_gate the verify-gate lowering (MTPLX: they can differ at rare bf16 inputs), so compare native
    REF2-T runs with a native reference, not with EvalSuite's token rows.
  - **OOO + TIER_COMBINE ADOPTED into R57_PRESET=45 (NewIdeas Sun 11:4x on EvalSuite's R-56d PASS: e1981e9, full
    length, 36/36, AR bits = R-56c's; 3faa0dc)**: the preset setdefaults R57_COMBINE=1 BIGMOE_TIER_COMBINE=1 BIGMOE_OOO=1;
    the no-OOO control = R57_COMBINE=0 BIGMOE_OOO=0. r57_screen's _fused_block also hands the shared expert (OOO's spin
    edge, as tier.install_block does natively; EvalSuite's block hands only the scores): scheduling only, same values.
    Kamen 11:02 "Keep 3-bit": REF2-T stays the 45 GB default. Leap's / MTP Head's copies (k69_live, d23_switchdef) keep
    their own preset blocks.
  - **Day Sun 1 Nov (Kamen 11:3x via the orchestrator: active research now, small day tests only; usage-pace lets
    claudesub run a day ahead)**: no open BigMoE day row (all my levers need the 125B on the GPU = night). Memory
    anatomy added to r57_screen (b9049b0): per prompt MLX peak in prefill vs decode, end cache, lifetime-peak rise per
    phase. At C 224 the lifetime peak is 38.0 GB vs pools 29.5 GB (load 33.4 active, end footprint 36.1): if the +1.9 GB
    over the end footprint is a prefill transient (as R-34 found at 24 GB, +2.2 GB), removing it = ~+14 C units (~-10 %
    misses) at equal RAM -> an exact follow-up after tonight. Prior-art pass (2026 papers): SpecMD's Least-Stale
    (2602.03921, ICML 2026) fixes a CROSS-LAYER cache (experts of already-run layers are stale; collision misses): n/a to
    our per-layer pools; DraftExpert (2607.24434: self-speculative near-twin drafter, 84-87 % acceptance, 86-88 %
    prefetch hits) / SPICE / MoE-SpeQ / SP-MoE / Speculating Experts / cache-conditional experts are in MoonShots'
    PRIOR_ART (substitution = Breakthrough's 12 GB line + MoonShots' M-16 RUNAHEAD). R-27 per-layer pools stayed KILL
    (24 GB b36: -1.5 %); MoonShots' finding 3 closed online eviction policies (<= ~6 %).
  - **Sun 16:35 TRIED part done** (Kamen 15:4x via the orchestrator: a cheat sheet of every idea tried): ~/TRIED/bigmoe.md,
    165 lines (HANDOVER + LEDGER + FINDINGS + DESIGN_*, deduped; NewIdeas merges into ~/TRIED/TRIED.md). Merge script:
    scratchpad tried/merge.py. Health 13:41 + 16:41 WATCH (heat pauses: SSD >= 70 C by day; protection working).
    16:44 usage-pace SLEEP to ~22:51 (weekly 25 % vs line 21 %): the 19:41 / 22:41 health-review crons still fire;
    launch C45 at the 22:41 one as planned.
    Orchestrator 18:xx lead (~/.local/share/usage-pace/leads/2026-11-01_per_row_cost_opus.md, optional): split the 7.82 ms
    per verified row into SSD vs GPU. Not tonight as a warm replay (new harness, ~30 min, ticket full); instead
    r57_screen now logs every check (rows, kept, check / draft / SSD-busy / gate-service ms, misses, SSD MB) to
    data/r57/<tag>_checks.json at no machine cost: in the morning regress check ms on rows + misses / MB per arm (A no-OOO
    vs B OOO at C 224, and per C) = the lead's step 3 and a cold per-row split; the warm replay stays a candidate.
  - **DAY9 (Kamen Mon ~10:3x via the orchestrator, verbatim "okay, add them and continue doing tests during the whole day. i
    want to day to run all 9 tests it needs"; plan ~/FableGod/DAY9_2026-11-02.md; day = small-tests rule lifted today, memory
    gates stay; report ONE line per result (condition #, PASS / BETWEEN / KILL, evidence file) to the orchestrator AND write
    it into the DAY9 file; NewIdeas sleeps to Tue 18:3x and routes then)**. Mine: #7 A6 (start-up split by cause; Leap's
    K-80 read-out in ~/Leap/TABLE_350.md "Runner 62 read-out": first cycle after a ~9K agent prefill +128-132 ms = miss burst
    58-73 % when cold, a one-time non-SSD build cost 74 % on a warm repeat, drafter window prefill +24-29 ms), #9 B2 (C 300 /
    320 tonight), #4 C1 harness (Leap 101573d: ref2.CFG["tier_nax_ooo"]; NAX6 = its own reference: determinism only, fit
    the per-row slope; kill < 1.2x on the row term), + the chat switch (a/b/c) + NewIdeas' warm split + P on L.
    BUILT (commits 6b9d097, 15e160a, 23184f0): r57_screen R57_CHATSW / R57_KEYS ('+' ok) / R57_A6 (ctl, rep, keep, dummy,
    dwin, pools) / R57_WARMSPLIT=N / R57_NAX=1, {TAG}_runs.json + _warmsplit.json, per-check build vs wait ms;
    c45_runner C45_CAP / C45_ALARM / C45_REFTOK / C45_SCREEN (frozen copy) + the PAUSE-clear race fix; turn45 NOTAFTER;
    scripts/guarded.sh; scripts/night_day9.sh (tonight's ONE ticket: C 300/320 -> chat A/B -> C1 + warm split + P on L ->
    touch ~/EvalSuite/results/ifx/GO -> A6 at C 256); scripts/day9_report.py (all groups + the lead's SSD regression).
    Reference tokens data/r57/chat23_ref_tokens.json (D-23d's 19 chat + 4 agent, S45's six, K-80's bash18).
    The tier pools need C >= ~154 (MAXK 160): C 64 aborts ("77 experts > C=41"). DAY TURN (C 160, needs NO-SWAP 37 GB,
    NOTAFTER 21:30, frozen copies data/r57/snap/*_a6.*): chsw_160 / wss_160 / naxs_160 smokes + a6c / a6r / a6k / a6w /
    a6p -> data/a6/; Breakthrough's run_map.py held ~12 GB and NO-SWAP was 17-19 GB at 10:4x; Leap's quiet window next.
    13:47 RE-GATED (the orchestrator 13:4x: EvalSuite holds its HC8 decode ~13:57-16:00; in that gap MTP Head's E2 capture
    FIRST, then my A6): task bkav4hp7f = the same arms, ticket 40 min, AFTER=data/r57/snap/after_e2.sh (E2's x2 data
    >= 16,171 MBPP code tokens in ~/TrainLab/data/dlog/d1102mbpp, or its chain moved on) + WAITMEM 37. E2 training (~15
    GB) leaves ~22 GB NO-SWAP, so A6 runs right after the capture or after E2's x2; not by 21:30 -> the night's group 4.
    turn45 (13:4x): NOTBEFORE / NOTAFTER fixed to clock times at the start (the old HH:MM compare read an evening launch,
    22:00 >= 05:30, as past NOTAFTER and exited 3 at once); AFTER='<sh condition>' gate. The night can be armed any time.
    NIGHT: arm night_day9.sh via turn45 (frozen copies *_n9.*: refreeze r57_screen / c45_runner / turn45 right before)
    with PEAK 44, MIN 75, NOTBEFORE 01:00, WAITMEM 48, NOTAFTER 05:30, MARGIN 4, NOWAIT45=1, GAP0=0, GAP=0.
    DONE 15:18-15:38 (commit f508954): smokes OK (chsw / wss / naxs: tokens equal, NAX6 engaged, 30.2 GB at C 160 with
    both drafters). #7 A6 at C 160 = PASS on the split, reported (DAY9 file 15:44, the orchestrator, NewIdeas): control
    excess 465 / 1131 / 1681 ms; keep (no end-of-request mx.clear_cache) 211 / 154 / 130 (= K-80's ~130); left: burst
    ~55 % cold, non-SSD 28-73 %, draft ~30 ms; pools cut the SSD part. a6w crashed: dwin's rotating drafter cache one
    position short (SWIN-1 buffer not full -> negative growth); fixed (prefill from P - SWIN), unit-tested
    (scripts/test_dwin_cache.py, CPU). NIGHT ARMED 15:44 as task b5mp98b33 (frozen *_n9 incl. night_day9_n9.sh; window
    Tue 01:00-05:30 confirmed in data/turn45.log). After it: day9_report.py (256) -> #9 / #4 / #7 lines + chat a/b/c.
    #7 is judged END TO END (the orchestrator 16:3x): prefill end -> 1st commit, pre-paid pools / dwin / dummy counted
    (they run after the prefill); day9_report prints it per prompt + per arm vs a6c + the <= 2-5 ms check. On the C 160
    data: keep 211 / 154 / 130 ms, pools 302 / 227 / 273 (their 93-139 ms pre-loop costs more than it saves vs keep).
    NEW LAPTOP SCHEDULE (Kamen 19:3x, RULES.md top): Mon-Fri big tests 00:30 -> 15:00 (16:30 / 18:00 only when he says);
    then -> 00:00 his day, small only. Weekend: his day ~10:00 -> 00:45 / 01:30, big tests after. Memory gates unchanged.
    MISSION 20 ARMED 19:52 (the orchestrator 19:4x: Fable's ~/FableGod/CACHE.md 5, "after A6"): task b52sfw0tf =
    turn45_pw.sh 45 60, AFTER data/r57/snap/after_night.sh (the night turn pid 11291 gone), window Tue 01:00-13:30, WAITMEM
    50 -> data/r57/snap/mission20_pw_pw.sh: R57_A6=warm (NEW flag in scripts/r57_screen.py, frozen as r57_screen_pw.py: the
    whole prompt's routing -> each layer's experts into its base pool by frequency, the most used most recent, up to C_m;
    4-bit ranks into the LSB sidecar up to C_l) vs R57_A6=ctl, c-w-c-w at C 160 and C 256, HumanEval 68 / 91 / 16 + agent
    bash18 / text23 / bash17, CAP 64, MG 7. Report: scripts/pw_report.py -> data/pw/pw_report.txt (its log data/pw/pw.log).
    Line on C 256: first-3-check misses <= -8 % with every token equal = PASS, > -3 % = KILL (HumanEval/16 has no stored
    REF2-T tokens: checked across its runs). Never smoked on the GPU (the day was small-only): a crash costs its arms only.
    BUILD WEEK (the orchestrator 19:4x, tomorrow by day): COPYGATE's G2 gate (~/FableGod/copygate/GATE.md 4, copygate.py;
    TrainLab 9d9ae1e; MTP Head's walk = BETWEEN, agent short) as a host-side hook between the drafter and the check in
    r57_screen's loop (exact: the check decides); token equality vs REF2-T on every prompt.
    CLOUD TASK 12 + THE COMBINATION (the orchestrator 21:0x / 21:1x; its address MOVES on app restarts: resolve it with
    orch_addr.sh at send time, 88684 at 21:07). (1) Rank-priority replay (protect ranks 0-1) = KILL, pre-registered (fe338f0;
    data/rankprio/RANKPRIO_read.txt): +2.7 % MB per check at code C 320 + gate 0.99, worse than LRU in every cell. FINDING:
    the LSB sidecar (C_l mean 89 / 126) misses 101-166 times per check on code, 60-70 % of all reads. (2) Measurement 2 rides
    tonight as night group 1b (added 21:1x to night_day9_n9.sh before it ran): c45t_320 = default + BIGMOE_TRACE=1 +
    R57_STALL=1 (frozen harness r57_screen_tr.py; dumps data/r57/c45t_320_stall.json) and c45tj_320 = the same +
    BIGMOE_JOINT=1 (base + sidecar reads in one burst; +7-8 % at 24 GB, never run at 45 GB). Morning: .venv/bin/python
    scripts/stall_report.py -> data/r57/stall_report.txt (per layer: misses, service, issue delay, the GPU's stall from the
    cadence fit; latency vs bytes; JOINT vs not) -> one line to the orchestrator + NewIdeas. (3) THE COMBINATION: I am the
    integrator and the ONLY writer of R57_PRESET=45. Goal by Thu 15:00: one exact 45 GB default with every exact lever that
    passed, measured each night (code / chat / agent; day C 256, night C 300 / 320), + a separate quality-defined "fast"
    preset (gate + copy override + comment loophole) for EvalSuite's same-scores test and Kamen. Tue by day (big window to
    15:00; one memory-heavy job at a time across sessions, a share lock with "MEM n GB"): one switch group at a time, every
    token == REF2-T after each, each logged with its own delta: chat switch (tonight's a/b/c) -> A6 keep (tonight's #7) ->
    COPYGATE R57_COPY=g2 (BUILT cc74272: vendored scripts/copygate.py, copies count as sure in the t cut; g2t = the cut on
    the drafter's cf; off on math) -> D7b R57_D7B=code (BUILT cc74272: Leap's d7b_live.apply before bind; a second 4-bit
    drafter for code prompts; K-83's forms stay on the bf16 one) -> JOINT (if tonight's pair is exact) -> K-83 (tonight's
    c1k). Also a 32-row variant (the copy pays most there): needs R57_ROWS and a wider gate (MAXK 320 = an ext layout change;
    on the slot path it is exact but slow). Warm split = a measurement, stays out. NAX6 = its own reference (NOT bitwise to
    3c; told the orchestrator 21:1x): its own preset, the default only after a certification + Kamen's OK. A lever that
    does not speed up the combined default stays off. Wed 00:30-15:00: FLOOR first, then the combined default under a quiet
    lock (tok/s per domain), then EvalSuite's slot (NewIdeas sets the sequence). One line per merge and per night to the
    orchestrator. W18 (NewIdeas): day9_report prints SSD GB/s per check per arm (ef0d384).
    !! TUE 01:4x NIGHT BLOCKED BY MEMORY: night_apps.sh closed Chrome + Spotify at 01:00 but NO-SWAP stayed 34.6 GB (38
    claude CLIs ~15 GB footprint, Terminal 3.3, PyCharm 2.3, wine 1.5): every 45 GB-route arm needs 47-55 GB, so my night
    turn (pid 11291, WAITMEM 48, to 05:30) and mission 20 (WAITMEM 50) never queued. Told the orchestrator; NewIdeas re-ordered
    the night GPU to jobs < ~30 GB (Breakthrough's map, Leap's screens, Fit12's T3); my GO watcher (task bm885c004,
    scratchpad go_watch.sh, log data/day9/go_watch.log) touches EvalSuite's GO 15 min after their last lock or at 04:00.
    The orchestrator puts a night memory plan to Kamen at 07:15. The same memory wall blocks Tuesday's combination chain
    (~47-49 GB) unless memory is freed: re-plan the 45 GB items around his decision (nothing night-related is lost: the
    frozen chain + its additions 1b / 1c / c45j_320 stay armed-ready).
    NewIdeas' GPU ORDER from Tue (21:3x): by day my small screens first; each night from 00:30 MY combined-default
    measurement first, then the night's big item (Wed FLOOR ~10 h, Thu EvalSuite RELAX). Tonight unchanged.
    MORNING (Tue, after the night turn b5mp98b33 ends): (1) day9_report.py (256) + stall_report.py + pr_report.py; (2) one line each to
    the orchestrator (orch_addr.sh) + NewIdeas + the DAY9 file's Results: #9 B2, #4 C1, #7 A6 (end to end), chat a/b/c,
    K-83 (adopt into R57_PRESET=45 if exact and not slower), P on L, measurement 2 (+ JOINT exact? delta?); (3) EvalSuite's
    GO is touched by the chain after group 3 (check data/day9/night.log); (4) ARM THE COMBINATION: edit
    scripts/combo_tue.sh's groups from the verdicts (drop any lever that differs; D7B=code adds a 2nd drafter, so check
    chB's peak first: the ticket must stay <= ~45 GB), refreeze r57_screen / c45_runner / turn45 as data/r57/snap/*_cmb.*
    + combo_tue_cmb.sh, arm turn45_cmb.sh (quiet memory turn: PEAK 45, MIN ~130 (19 arms x ~6 min: the quiet lock ENDS at grant + MIN and c45_runner stops at its next arm), WAITMEM ~47, NOTAFTER 14:20, AFTER =
    mission 20's turn gone) attached via run_in_background; report data/cmb/combo_report.txt one line per lever.
    Mission 20's line after its turn: data/pw/pw_report.txt. Harness switches (cc74272, d903fd3, c69f3c0): R57_COPY,
    R57_D7B, R57_ROWS=32 (copy prompts only), R57_CHATROWS=8; R57_STALL (fc74c90).
    TWO TRACKS (Kamen 21:31, RULES.md top): EXACT (bitwise default) + FAST (quality-defined, EvalSuite same scores), both
    first-class and published; never drop an idea only for bits. FAST preset BUILT (c33a86b, 886762e): R57_FAST=<arm>
    applies EvalSuite's RELAX rules (vendored scripts/relax_core.py from ~/EvalSuite/pending) per prompt set as its arms
    A/B/C/E/F/G (+ BE / CE = code mode + chat R1): cf gate 0.99 + copy gate (top-2, dropped ranks routed to rank 0 = never
    read), R1 / R2, the comment loophole; no HC8; 16 rows; arms without R57_REFTOK. Tuesday's chain ends with fastBE /
    fastCE on the full stack. SIDECAR x1.5 (9f1309b): equal-RAM size files data/seed45/laysz45_{256,300,320}_sc15.json
    (replay: reads -7..-25 %; MB +4.6 % on ungated code, -0.4..-5 % chat / gated) = arm cmbsc. R-57 LOOK-AHEAD at 45 GB =
    my next build right behind the combination (the orchestrator 21:4x: cloud task 15 makes my SSD stack -23 of the
    ladder's -48 ms): the tier path already forwards L+1 preds (gate+pf); to build: a gate+t+pf arm, R57_SPARE reserved
    slots, sidecar prefetch (ext change in its own build dir). Line: misses <= 60 / check, recall >= 0.69, waste <= 0.5x
    saved, cycle +5 % = PASS; < +2 % = KILL. Measurement 2's line goes out FIRST in the morning.
    LOOK-AHEAD BUILT (0e092fe, ba5db78): R57_ARMS=gate+t+pf (the t cut + ranked L+1 preds), BIGMOE_PF_SIDE=m in the ext
    (non-JIT: L+1's sidecar planes for the m most likely ids, into the sidecar's spare slots) built as ext/build_la
    (BIGMOE_EXT_BUILD=build_la; its defaults == ext/build: the only other source change since ext/build is SEED45's
    opt-in prior). Screen = scripts/la45_tue.sh (la0..la4 at C 256, S45's six, tokens vs REF2-T; line in the script):
    arm it right after the combination chain (freeze *_la.* copies; AFTER = the combination's turn gone). The runs log
    the look-ahead's issued / used reads (st.stats pf_*) and JOINT's reads. Note: BIGMOE_SPARE reserves sidecar slots too.
    M-20 SSDWAKE (MoonShots, the orchestrator 22:1x; 6c7cc5a): BIGMOE_SSD_KEEPALIVE_US=50 in ext/build_la (a 4 KB
    F_NOCACHE read every 50 us while the loader served a call in the last 50 ms; exact); the ext counts demand bursts and
    those after >= 0.25 / >= 1 ms SSD idle (st.stats bursts / burst_gap025 / burst_gap1, logged per run); stall_report.py
    measures the same gaps from tonight's trace (report it with measurement 2). A/B = la45_tue.sh's ka0 / ka1 / ka0r / ka1r
    (PASS >= +2 % steady on code with tokens equal, KILL <= +0.5 %).
    PRE-ROUTE CAPTURE (the orchestrator 22:2x, cloud's pick #1 'pre-route on the partial sum', exact) = NIGHT GROUP 1c
    (added 22:3x, frozen r57_screen_pr.py = f4c2ddd's harness; R57_PREROUTE=1 at C 256, 12 HumanEval + 6 chat, CAP 128):
    OOO's combine re-run with ranks >= 3 / >= 6 zeroed -> L+1's HC read + router -> top-10, vs r57 (L's MoE input) and
    full, all vs L+1's true top-10. Morning: .venv/bin/python scripts/pr_report.py -> data/r57/pr_256_preroute.txt; line
    PASS p3 >= 0.85 and p6 >= 0.90 per-row recall@10, KILL p3 < 0.75; report with measurement 2. If PASS: build it into
    OOO's phase 2 as the look-ahead's forecast (issue L+1's reads while L waits on its misses).
    IDLE BACKOFF (Breakthrough 22:3x: the idle loader spins ~1 core, e.g. in pausewait): BIGMOE_IDLE_MS=n in the ext
    source (env-gated, off by default; b26ce68) is NOT BUILT yet (the peers hook blocked the build twice while the Mac
    was loaded): `nice -n 15 cmake --build ext/build_la -j1` before arming la45 (check `strings ... | grep BIGMOE_IDLE_MS`).
    Candidate default for the next ext/build rebuild (heat only, exact): offer with the combination's adoption.
    23:0x (the orchestrator, Fable C's AUDIT): code at C 320 is BANDWIDTH-bound per Fable C (11.7 GB/s, 37.9 MB / kept
    token); stall_report.py now also splits demand SSD time per check into bytes vs a fixed per-burst cost (ca46504); the
    capture (group 1c, refrozen 945bd8cd) adds precision@96 / recall@96 (Fable C's C1-1 line: recall >= 0.85 AND
    precision@96 >= 0.80). H-1c (Leap's compact NAX hybrid, FAST only): yes for the FAST arms as fastBEn (+ R57_NAX=1) /
    fastBEh (+ H-1c) once Leap's off-by-default ref2 switch lands (proposed CFG['nax_hybrid'], toggled by R57_H1C=1;
    wired e9b9609; Leap 34f8800 = CFG["nax_hybrid"] (NAX6-H in-kernel hybrid, default off, counts()["nax_hybrid"]): matches).
    23:1x-23:3x: Leap f91a956 = CFG['nax_native'] (fragment-native pools: NAX6-N +17.3 %, with nax_hybrid NAX6-NH +23.3 %
    at S 16, bitwise == NAX6 / NAX6-H): needs pools in Leap's order (tierglu_nax6n.repack). MY PLAN (told Leap): a CPU gather
    at load in the ext (BIGMOE_NAX_NATIVE; index maps = repack() applied to an arange slab) for demand / prefetch / PF1
    staging reads; no disk copy (records3 70.4 GB, records3m 66.5 GB, 158 GB free), Wednesday; asked Leap (1) is repack a
    per-expert permutation, (2) do prefill tier calls run NAX with nax_native. W24-sp (11-bit scale / bias pack, -10.9 %
    bytes, exact) needs a ~63 GB record copy = below the 100 GB floor unless a copy goes: Kamen's call; not started.
    Added to Tuesday's chain (af2c975): cmb1t (R57_CHATTRUNC=0.4 on chat; NewIdeas' line +1.5 %), fastBEhw (fastBEh + the
    warm split with the FAST mask: Fable C's gated expert term), MB per kept token per arm in combo_report (judge cmbsc
    by it: MoonShots' M-25 says the joint optimum SHRINKS the sidecar; wire MoonShots' joint-fit size files as an arm if
    they exist at arming). la45's line now also needs MB per kept token not up > 3 % (bandwidth-bound code). Tonight's
    trace copy refrozen with a wall-clock anchor (b42f5fc6); stall_report bins per-miss service by fanwatch SSD temp.
    NATIVE POOLS, Leap's facts (23:4x): repack() is one per-shape permutation (axis 0 untouched; gate/up O 640 KG 40,
    down O 2560 KG 10): native[((t*KG + g)*32 + r)*per + w] = rowmajor[((t*32 + r)*KG + g)*per + w], per = 6 u32 (w3),
    2 u32 (l1), 1 bf16 (s3, b3, LSB b). Gather ONLY tier-pool slot reads (base MSB + LSB sidecar: demand, prefetch, the
    OOO spin); NOT read_rebuilt / R-52 group buffers / PF1 staging / non-tier or MTP pools (prefill never reads the tier
    pools). Assert (BIGMOE_NAX_NATIVE == 1) == (CFG nax_native and tier_nax_ooo) and TIER_GLU == 3c (a mismatch = wrong
    outputs, no crash). COST: the CPU gather is 176-183 us per 2.92 MB expert (16 GB/s) vs memcpy 45 us: ~+130 us per
    demand miss unless it overlaps the next pread -> compare with Leap's offered GPU repack kernel before building.
    MoonShots M-25b joint-fit sizes (copied to data/seed45/joint45_256_{0,2070}.json, md5 8b592da1 / 568f049e) = arms
    cmbj0 / cmbj2 on the default's stack in Tuesday's chain (judge by MB per kept token on code vs cmb0; +2.07 GB peak
    ~43.8 GB).
    NATIVE REPACK SPEC (Leap 23:5x, agreed): Leap writes the GPU repack (claim + in-place tile transpose) in ref2's
    _ooo_nax6 (between the spins and phase 2) and _nax6_glu, tonight + GPU after ~07:00. MY SIDE (Tue by day, CPU): (1)
    BIGMOE_NAX_NATIVE=1 in the ext: per tier pool an int32 dirty-flag array (mx.zeros((C,), int32), base + sidecar),
    registered with the ext and with ref2.native_flags(t['base'], dirty_m, t['sideP'], dirty_l) after install_sidecars;
    (2) the loader's IN-SERVICE demand loads write row-major + dirty = 1 (release) before ready; (3) every other tier load
    (prefetch incl. PF_SIDE, JOINT background, ensure() from Python) gathers native on the CPU (Leap's closed form per
    piece; (O, KG, per) from the pool shapes), flag 0; (4) the assert (env == 1) == (CFG nax_native and tier_nax_ooo) and
    TIER_GLU 3c; (5) self-check: after a cold check every resident slot == repack(row-major record) bitwise on 2-3 layers.
    Then fastBEnh. Leap's price estimate: ~2.5-3.5 ms per check vs NAX6-N's ~8 ms (PASS >= 80 % of the gain survives).
    N7-15 MEASURED (Leap 01:5x, quiet; ref2 84f669e, inert by default): the GPU repack keeps ~50 % of NAX6-N's gain at
    3 + 1 dirty slots per call (95 % at 0, 82 % at 1 + 0, 8 % at 6 + 2; break-even ~8 base slots): ~3.5 of ~7 ms per
    check at C 256. API: ref2.native_flags(t['base'], dirty_m, t['sideP'], dirty_l) (int32, own contiguous buffers, >= 2
    entries); NEVER pass the flag arrays through mx.depends (MLX copies them, the clears are lost); register dirty_l too
    (unregistered sidecar slots pass unchanged). COUNTS['nax_repack']. Decision: fastBEnh stays for Wed (my ext side Tue
    by day); hiding the repack inside the spin as slots land = the follow-up for the other half.
    EDGE CASE (Leap 02:0x): write the flag on EVERY tier-pool load, explicitly (1 = in-service demand, 0 = the native CPU
    gathers), always BEFORE the slot's ready status, never after: a slot reused after an abandoned demand load (its phase
    2 never ran) would otherwise show a stale 1 beside native bytes and be repacked twice.
    03:2x: Leap's status calls N7-15 a KILL by its line (47-50 % of the gain kept): fastBEnh DEMOTED to optional (build my
    ext side only if Tuesday has room; the repack hidden in the spin is the better route). The orchestrator touched
    EvalSuite's GO at 03:20 (my watcher stopped on it); NO-SWAP 41 GB then, my turn still blocked (needs 48).
    05:30: the DAY9 night turn (task b5mp98b33) exited 3 = 'past NOTAFTER 05:30: not queued' (never ran). Mission 20's
    turn (task b52sfw0tf, pid 41794) stays armed to 13:30 (WAITMEM 50; its AFTER gate now holds). To re-run the night
    items: re-arm turn45_n9.sh with a new window after Kamen's memory decision (the frozen scripts are ready, incl. 1b /
    1c / c45j_320).
    TUE 11:0x-15:00: Kamen OK'd the orchestrator closing apps + idle terminals; idle NO-SWAP is still only 45-47 GB, so
    mission 20 (WAITMEM 50) lapsed at 13:30. ARMED 14:56 FOR WED 00:45 (after Fit12's 00:30-00:45), all at C 224 (<= ~41
    GB peak), e5ef048: (1) mission 20 task b219pvseh (turn pid 68957, ticket 90; PW_CS='160 224', line on C 224, MG 6, window to
    03:00); (2) the combination task bx2qs1td1 (turn pid 69085, ticket 180, AFTER after_pw2.sh; CMB_C=224: measurement 2 = c45t_224 /
    c45tj_224, pr_224, chA_224 / chB_224, cmb0..cmbsc, FAST; window to 04:00); (3) the look-ahead + keepalive
    task bvocrsvsm (ticket 75, AFTER after_cmb.sh; LA_C=224; window to 05:00). Then Breakthrough's FLOOR to 15:00.
    MORNING: stall_report.py data/r57 c45t_224,c45tj_224; pr_report.py pr_224; CMB_C=224 combo_report.py; day9_report's
    chat checks: .venv/bin/python scripts/day9_report.py 224 (SUFFIX arg); pw_report via PW_CS='160 224'.
    Wed->Thu night: touch ~/EvalSuite/results/relax/GO when that night's combined run ends (EvalSuite's RELAX queues).
    WED BY DAY, the orchestrator's order (15:1x): (1) the VOLATILE EXPERT TIER (NewIdeas' RANKED 33, exact; Leap's PURGE-1
    PASS 15:05: purgeable Metal slabs are reclaimed before compression or swap, toggles 0.2-4 us; ~/Leap/HANDOVER.md,
    native/purge_balloon.swift): BIGMOE_VTIER (per base layer a shared MTLBuffer victim slab, volatile while idle; LRU
    evictions copy in (overlapping the incoming read), misses look there first and copy back (~40 us vs SSD ~250+), pin
    non-volatile during the layer's service, previous state 'Empty' = purged -> clear that layer's tier index); cap by GB;
    counters + the tier's peak bytes beside phys_footprint (volatile memory is NOT in it). Smoke after 15:00 (one big
    job): C 224 + ~10-14 GB tier vs C 224, tokens == REF2-T, MB per kept token, tok/s; if PASS it rides Wed night.
    (2) the per-row 'no LSB' mask (FAST; gated rows' ranks 0-1 at tier 3 via LP1, ~3 h + smoke).
    VOLATILE TIER BUILT TUE 15:1x-15:4x (ahead of Wed): ext 2a99aa7 (ext/build_vt), harness 744eca4 (R57_VTIER=base,side
    slots; needs BIGMOE_EXT_BUILD=build_vt), unit test scripts/test_vtier.py PASS (fake layer: every resident slot == its
    record over ~60 calls incl. a forced purge via the test-only ext.vtier_purge). SMOKE = the last two arms of tonight's
    look-ahead turn (vt0 / vt1 = + 64 / 32 slots ~7.8 GB volatile at C 224; line in la45_tue.sh: exact; PASS MB per
    kept token <= -10 % with tok/s not down; KILL MB down < 3 % or tok/s down > 2 %). Design notes: ghosts are set only
    by make_room's evictions and cleared at all 6 free-slot takers; tier slots copied this call are 'busy' (no reuse in
    the same call); the ghost copy-in runs before the job's SSD read (+~40 us per job: overlap is a later optimization).
    U3 BUILT TUE 15:2x-15:5x (3d826fc; the orchestrator's Wed #2, the per-row no-LSB mask): R57_FAST=U3 (code) / U3A
    (code + math + agent) = the map's q1u_cf09_t3: sure rows (cf >= 0.9; never the bonus row) keep ranks 0-1 at 3 bits
    (their sidecar request = an unsure row's rank-0 expert, slot -2, LP1's kernel test -> tier 3; tier._lp1_patch) and
    ranks 2-9 only where the expert is in the check's union (all ranks of unsure rows + ranks 0-1 of sure rows, as
    dm_q1u_masks.py); the union mask is built per layer in the FAST wrapper; _ooo_call_t3 = tier._ooo_call copied (md5
    d5bf5acd asserted). Null control R57_U3_THR=2 + R57_U3_FORCE=1 must equal REF2-T bitwise. Smoke = scripts/u3_smoke.sh
    (u3c / u3n / u3 at C 224 on 12 HumanEval; line inside). ARMED TONIGHT (the orchestrator 15:5x): task bsswcdft0 (turn
    wrapper pid 82997, ticket 45, AFTER after_pw2_u3.sh = mission 20 gone; U3_DEADLINE 0430); u3n must equal u3c on every
    token of all 12 prompts or U3 stops; the combination's after_pw2.sh now waits for mission 20 AND the U3 turn.
    ORDER: Fit12 00:30-00:45 -> mission 20 -> U3 smoke -> combination -> look-ahead + keepalive + tier smoke -> FLOOR.
    Morning: U3's numbers from data/r57/u3*_224_runs.json + data/u3/u3.log (MB per kept token on code u3 vs u3c).
    PREDICTIONS to read tonight's numbers against: NewIdeas (victim_tier.py on cap45, tier never purged): vt1_224 SSD MB
    per kept token 79.2 -> 52.1 (-34 %) vs C 224 (C 256 alone 62.5). MTP Head (ROUTEPRED): R-57's forecast per-row
    recall@10 0.611 (@16 0.738); a check's rows' top-10 forecasts name 50.5 % of L+1's misses at 3.49 reads per miss
    (C 256 LRU); a next-check predictor is dead (precision 0.07).
    NATIVE RECORDS ON DISK (Leap 16:0x, TABLE_350 DISK-PLAN / NATIVE-3C; ONLY IF KAMEN DECIDES, nothing converted):
    Leap has ref2 CFG native_3c (REF2-T's 3c on native records, == 3c bitwise, 1-7 % slower), nax_native / nax_hybrid,
    and scripts/convert_records_native.py (in place per layer, verify + atomic rename, index.json 'layout', ~2 min, has
    --inverse). MY SIDE then (~2.5-3 h): (1) the ext's read_rebuilt (tier.py prefill_call / _prefill_grouped -> 4-bit
    MLX rows on the CPU) needs the inverse permutation per piece; (2) pool loads need nothing (native file = native
    pools, N7-15 flags stay 0); (3) a guard on index.json's per-layer 'layout' refusing row-major readers (stock 3c,
    NAX6 without nax_native, tier_nax4, TIER_GLU 3b, read_rebuilt without the inverse); (6) ~238 lines of direct
    records3 readers (~/Leap/data/records3_readers.txt) read permuted rows unless they check 'layout'. Smoke: the
    residency check + a short REF2-T decode token for token vs the pre-conversion reference with native_3c on.
    COMBINED CONVERSION PLAN (the orchestrator 17:1x: native layout + MoonShots' M-27 11-bit scales in ONE in-place pass,
    Kamen decides once): docs/PLAN_records3_convert.md (1336043): disk plan, engine readers (~5 h), guards, exact A/B line.
  - **WED 21:5x (the orchestrator: LOO cut 08:35):** no new agent-LOO arm after 08:35 (was 09:00), so the Thu ticket
    releases and touches q42/GO by ~08:45 (runner 42's original start; runner 43's 14:00 rule). night_thu.sh caps it itself
    for a 04:00-09:59 start (ALOO 0835, also C 256 <= 08:10 and C 224 trio <= 08:30), so bpop21hkz stays armed as is
    (its env says 0900). From a 07:10 grant: old, new, -vtier, -chat, -lever1 run; -K83 / -keepalive / new2 / old2 cut.
  - **WED 21:3x (the orchestrator: C 224 moves to Thu morning):** OK to the adaptive 23:00 run. No C 224 window tonight
    (RELAX ~23:50-07:10). night_thu.sh is now 3 steps: C 256 headline (d256_wed.sh) -> C 224 FAST trio u3ct / qallt /
    qallft (NEW scripts/c224_thu.sh, MG 10, data/c224t, report tested on stand-in data) -> agent LOO (ALOO_DEADLINE 0900:
    arms cut from the tail so runner 42 starts by ~09:10). D256 / C224T deadlines default to start + 27 / + 54 min.
    ARMED (bpop21hkz, 21:3x): turn45 48 120, NOTBEFORE 07:05 / NOTAFTER 07:45, then touch ~/EvalSuite/results/q42/GO
    however it ends. The orchestrator tells EvalSuite (later runner 42) and moves Kamen's conversion heads-up. DKV Thu
    after this ticket, with a token check (agreed).
  - **WED 21:2x (the evening 45 GB slot vs memory; Leap DKV):** the EARLY ticket (20:35-21:15) never queued: NO-SWAP
    stayed 41 GB < WAITMEM 44 with Kamen's apps open (Chrome closed). Stopped by hand (nothing queued). The old 23:00 ticket
    (eve_2300.sh, C 224, PEAK 40) is STOPPED too: same gate, and PEAK 40 understated qallf (measured lifetime peaks, data/r57
    mem[1]: U3C 12 HumanEval 30.9 GB at C 160 / 39.4 at C 224 = 0.134 GB per row; all-in +0.3; forecast reads +2.6-3.3 ->
    qallf ~34.8 + 0.134 (C - 160) GB). NOW ARMED (buzc2iazf, 21:26): 23:00-23:15, PEAK 37 / WAITMEM 41 / MARGIN 4,
    scripts/eve_2300b.sh = all-in arms at the largest C whose peak + 4 fits at the grant (224 >= 47.4, 208 >= 45.2,
    192 >= 43.1, else 176), then rx0 / qallr, then l2_wed.sh at C 160. The C 224 headline needs apps closed (night_apps)
    or ~6 GB more: asked the orchestrator for a night window (C 224-only ticket u3c / qall / qallf, MEM ~44-48).
    Leap DKV (2f726fb / d080232 / 43d3ecf: copy-free drafter window cache, exact, -0.48 / -1.00 ms per propose at 2,047
    rows): ~/Leap/data/r57_dkv.diff (4 lines, R57_DKV=1 / R57_DKV_ADD=1, default OFF) dry-run-patches
    scripts/r57_screen.py cleanly; apply AFTER tonight's run (allin_wed.sh snapshots r57_screen.py at 23:00), then
    token-check both in the next exact slot.
  - **WED 19:1x (Leap's conversion blockers + the orchestrator 18:4x):** the 20:20 by-day ticket is STOPPED (TaskStop
    bv15yei9d; it had queued no lock). The 23:00 ticket (bxzoxgb73, same process) runs allin_wed.sh = u3c / qall / qallf /
    u3c2 at C 224, then rx0 (relax flag off on snap r57_screen_allinr.py, 2 prompts CAP 64, every token == REF2-T or no
    relaxed arm) and qallr (qall + RELAX 0.5, 12 HumanEval), then l2_wed.sh at C 160. qall8 deferred to the next slot.
    convert_records3.sh (8e8bdc4): the T0_DONE guard is replaced by ~/EvalSuite/results/NAX6_DONE == "D4X: PASS" +
    CHECK1_DONE "check 1 rc 0" (T0 now runs after the conversion). 19:4x: "D4X: DIFFERS (HIGHER)" is GO too (the
    orchestrator 19:2x decision (a), as runners 43 / 44 read it); Kamen may veto that before Thu 10:00: CHECK before
    converting on a DIFFERS. Overlays are quarantined before converting
    (scratch/model_mix index.json -> .rowmajor-stale; undo = mv back). ~/FableGod/decision_map/r3_overlay is flagged for
    its owner, not touched. Leap's checklist: ~/Leap/data/CONVERSION_THU_CHECKLIST.md (B2 dm_t3 LAYOUT = Breakthrough's
    map). After 23:00: report to the orchestrator + MoonShots, publish, TRIED (qallr In flight now).
  - **WED 18:1x TONIGHT / THU (the orchestrator 17:5x-18:0x):** 20:20 ticket ARMED (task bv15yei9d: NOTBEFORE 20:20 /
    NOTAFTER 20:35, WAITMEM 36 -> scripts/bd160n_wed.sh at C 160 uniform: exact lever 2 off/on, QOM all-in u3cn / qalln /
    qallfn, relaxed acceptance on scripts/r57_screen_rlx.py = MoonShots 32edb12 applied to a COPY (main screen untouched):
    rx0n flag-off check vs REF2-T, then qallrn = qall + R57_RELAX_DELTA=0.5). IF rx0n == REF2-T: add ONE arm to the 23:00
    ticket (allin_wed.sh: a second runner call with C45_SCREEN = a snap of r57_screen_rlx.py, qall + RELAX 0.5) before
    22:30. Kamen closes Chrome + Spotify at 23:00 (the 23:00 ticket will run; RELAX -> ~23:50). THU: RELAX to ~07:10, my
    ~95-min night_thu ticket ~07:10-08:45 (touch ~/EvalSuite/results/q42/GO at its end, also on failure), NAX6 Part 1 to
    ~10:35, then I CONVERT records3 (~10:45-11:00) on its PASS (Kamen approved; plan follows from the orchestrator).
    Answered: the Fri 00:30 night stays for the CONVERTED arms only (in-place conversion leaves no row-major store);
    a clean C1 (row-major NAX) only if ~10 min is added to the Thu ticket (orchestrator's call).
  - **WED 15:5x STATE (main usage 52 % at 15:51; plan ~70 % at 23:30: slow down).** QOM BUILT + by-day measured (5bb2743,
    c387c97: R57_FAST=QOM on ext/build_qom; C 160 uniform: bytes x0.734 vs U3C; QOM all-in +26.3 % vs U3C, 85.8 tok/s);
    DRAFT17 wired (723ee9b, R57_D17=1: 78/78 rows gated). C 96 / 128 by-day runs INVALID (< 160 slots per layer = sync path;
    TRIED). Lever 2 needs arm gate+t+pf + BIGMOE_PRED_LINES=4 (else no forecast posted); smoke 2 PASS (exact + lever 2:
    32/32 tokens, 2,538 reads, 1,192 used). Token files are [run][token]: compare run 0.
    - 23:00 TICKET (task bxzoxgb73, eve_2300.sh): allin_wed.sh NOW QOM-based at C 224 (u3c / qall = QOM + D17 + D7b + HC8 +
      DNR + hc_b + SMALL_NATIVE / qallf = + lever 2 / qall2 / u3c2; no REF2_OOO_1C: Leap to make it QOM-aware), then
      l2_wed.sh (C 160, all arms gate+t+pf + PRED_LINES 4). Report both to the orchestrator + the honest list toward
      ~50 ms per check (parts: check, draft, I/O, gate service, build; ck/drf/io/svc/wt/bld in checks.json).
    - QUEUE (tomorrow): lever 2 stage 2 (SAMELAYER-T on the p3 read, needs a mid-layer forecast post; weights in
      ~/TrainLab/data/samelayer_t_W.npz); Leap's ScreenedHead subclass for the chat switch (R57_CHATSH; READY Leap 5571831, NOT c1aff9c: that one set mtplx's generic hook, which qwen4_exp ignores = no effect;
      sanity check in the run: chat drafts differ from today's at a small share of depths, not zero:
      sys.path.insert(0, ~/Leap/scripts); from screened_mtp import screened_mtphead; ChatSH = screened_mtphead(MTPHead,
      model, model.language_model.lm_head); head = ChatSH(); head.add(prompt_ids); then append / draft_cut as today; build
      once per session; test: chat steady tok/s, every token == REF2-T, chat draft agreement); draft-ahead
      (24 GB only); QOM tail 4 only if tonight's s7_ref3 fails (then the 24 GB LSB split C_l 160 / C_m 115 = 40.2 MB per kept code;
      NEVER 171 / 0 with width 4: every kept LSB re-read, 164 MB per kept; NewIdeas 5dc01fd); next exact slot (DENSE-N / HC8 / hc_b / one-call OOO + R57_D8NAX (wired d119aa5, smoke exact) + R57_HEADC (wired 7094cdb,
      not smoked) + R57_GDNB (Leap 70cd998, bitwise, -0.71 ms per check; wired, not smoked)); next FAST all-in: Leap's screened VERIFIER head (f5404cc, FAST, -0.79 ms per check; needs 4 hooks:
      ref2.screened_head_install(model.language_model.lm_head) once, screened_head_reset() + screened_head_add(prompt_ids)
      per prompt, screened_head_add(committed_ids) after each commit, ref2.CFG['screened_head'] = True).
    - R57_DSUB (Leap 54c50c7, EXACT-safe, SUPERSEDES R57_HEADC): the draft head over FR-Spec 98K + session ids on
      qmm16c, -0.99 ms per code check (with D8-NAX the drafter 10.4 -> 5.8 ms). SUB = d7b_nax.DraftSubset(model.
      language_model.lm_head) once; head2s: if SUB: return d7b_nax.screened_head2s(draft, hid, SUB); per prompt
      SUB.reset(); SUB.add(prompt_ids); after each check SUB.add(committed_ids). Wire WITH the verifier head (same
      session-feed hooks), tomorrow.
    - SESSION-VOCAB DIFF READY (Leap eeb9170, ~/Leap/data/r57_session_vocab.diff, 5 hunks: R57_DSUB / R57_SVH /
      R57_SV_CHECK, all off by default): APPLY ONLY AFTER Thu's ~06:40 slot ends (tonight's 23:00 run and Thu's slot copy
      the smoke-tested screen): patch --dry-run first; then a 1-prompt smoke with all three set (svh_calls ~ checks,
      head2s == proposes, chk_out ~0, dsub_extra == svh_extra) + an exact arm with only R57_DSUB (tokens == REF2-T).
  - **WED 14:46-15:3x BUILD DAY (Kamen: "today we BUILD"; 15:1x rules: every session builds its biggest piece in parallel,
    tests = bare minimum; "300 is absolutely possible on fast mode and 200 on exact"; Chrome + Spotify open until 23:00 =
    NO-SWAP ~29-40 GB by day, one > 5 GB job at a time). KAMEN DECISION 15:0x: YES to the NAX exact reference after
    EvalSuite's decision-4 certification; after Friday's conversion R57_PRESET=45 -> NAX6-N if NATIVE-FRI passes.
    - LEVER 2 STAGE 1 BUILT e8b7b6d (ext/build_l2; BIGMOE_FC_F / FS): L+1's posted forecast read into the volatile tier
      right after L's release; CPU byte test scripts/test_fc_tier.py PASS (bare, mix, direct on/off). Slot scripts/l2_wed.sh
      (C 160, line pre-registered: KEEP stall <= -20 % + >= +3 %; KILL < +1 % or penalty > 0.05 ms).
    - ALL-IN FAST (code): screen switches R57_HC8 / R57_DNR / R57_HCB (469b061) + one-call OOO REF2_OOO_1C=1 (Leap 55968c5,
      safe on U3's sure rows; log line "build-day engagement" must show ooo_1c > 0); scripts/allin_wed.sh (C 224, u3c /
      allin / allinf / allin2 / u3c2 + dump arm). By-day bare test scripts/bd96_wed.sh: C 96 FAILED at once (a 16-row check
      needs <= 128 slots per layer: 119 > 82 with per-layer sizes); C 128 uniform (R57_LAYSZ=0, BIGMOE_TIER_CL=64) runs:
      u3cb_128 45.7 tok/s (steady 50.1), lifetime 26.6 GB, demand SSD 92 ms of a 215 ms cycle.
    - 23:00 TICKET ARMED (task bxzoxgb73): NOTBEFORE 23:00 / NOTAFTER 23:15, WAITMEM 44 -> scripts/eve_2300.sh = allin_wed.sh
      (C 224) then l2_wed.sh (C 160); RELAX moves to ~23:50 if it runs, else the Thu spare (~13:10).
    - NEXT EXACT SLOT (pre-registered): plain / DENSE-N (R57_DNR) / HC8 / HC8 / DENSE-N / plain + hc_b + one-call OOO arms
      (each: every token == REF2-T and not slower than plain by > 1 % -> exact adoption).
    - QOM + DRAFT17 = my next build (the biggest FAST piece): Breakthrough's module ~/Breakthrough/keepset (6f1ca44, read-only):
      Q.qom_keep_mx(ids [R,10], scores, conf [R] (NaN = no draft), resident [R,10]) -> keep, weights (dropped zeroed, no
      renorm), bits; thr 0, ks 2; test vectors keepset/qom_vectors.npz. The tail width of sure rows' kept ranks 2-9 is a FLAG
      (3 = MSB only, measure speed with it; 4 = LSB reads, map C's form); tonight's s7_ref3 decides. Needs residency BEFORE
      the reads: plan = an "optional" bit per posted id (sure rows' ranks 2-9) that the loader does not load when missing.
    - SAMELAYER-T weights for stage 2: ~/TrainLab/data/samelayer_t_W.npz (W_bf16 [47,512,2560] uint16, b [47,512]; X = L's
      MLP-side read of its pre-attention stream, r57_screen.py:582); stage 2 comes after QOM.
    - THU SLOT: EvalSuite asks (15:18) to touch ~/EvalSuite/results/q42/GO when my post-RELAX ticket ENDS (also on failure):
      arm night_thu.sh as `bash scripts/turn45.sh ... /bin/bash scripts/night_thu.sh; touch ~/EvalSuite/results/q42/GO`.
  - **WED 13:49-14:02 AGENT LOO BY DAY (the orchestrator's GO in Kamen's 13:4x test window): CUT by the 2 GB swap rule in
    arm 2 (the new default: swap 10.01 -> 12.13 GB; it grew ~+1.8 GB from NO-SWAP 51 GB, old +0.3).** Only old ran: 28.7
    tok/s steady, 5/5 tokens (bash18 24.1, text23 36.0, bash20 27.8, edit03 45.1, write12 17.8), 444 s per arm (not ~3 min).
    New's partial: bash20 24.6 vs 27.8. No verdict (data/aloo/aloo_report.txt now says INCOMPLETE; it printed INTERACTION
    on missing arms: fixed, with a swap-per-arm line; the RAM levers run first now: -vtier, -chat, -lever1, -K83, -keepalive).
    Reading, not proven: the new default holds ~50 GB at C 224 with the purgeable tier, and day memory (sessions 8.5 + apps
    3.6 GB) squeezes it; a memory-pressure cause for agent -9.9 % fits.
  - WED 14:1x, MTP Head's K83 lead (DRAFT17: draft_fused falls back off 16 rows, +8.6-9 ms per drafter pass) does NOT fire
    here: R57_ROWS is unset (16-row blocks; aold's 308 agent checks max 16 rows) and drafter ms per check FELL under the
    new default (agent 12.5 -> 11.4, code/math 11.6 -> 10.3; d256 C 224 checks). Agent's cost is the check's I/O: bash18
    misses 246 -> 251, SSD MB 417 -> 341-362, yet io 56 -> 63-71 ms, check 110 -> 118-124 (HE/68 alike): slower service
    per miss = the vtier / keepalive / lever-1 I/O path. NEXT 45 GB SLOT AFTER TONIGHT: Leap's REF2_DENSE_NATIVE=1 (7fe72a8,
    exact, -1.46 ms per 16-row check, +1.5 GB) as an arm vs an equal-RAM control: dense-native at C 213 vs plain C 224, 14
    prompts, ADOPT if >= +1 % geo steady and every token == REF2-T (pre-registered Wed 14:2x).
  - NEXT 45 GB SLOT ALSO: Leap's HC8 FAST arm (c805fd0; Leap 14:5x): after load ~/Leap/scripts/hc8r.py hc8r.hc8_install(model)
    (trunk GatedResidual mixers -> 8-bit g64, -0.6 GB) + REF2_HC8_FAST=1 (one-pass 8-bit HC read, -4.3 ms per check). Both
    together (the install alone falls back to MTPLX's slow eager chain). FAST: tokens differ from REF2-T (no token check;
    R57_REFTOK= in its arms); EvalSuite same-scores decides adoption (its decision 4 leaned PASS). BigMoE's HC paths
    (BIGMOE_HC_VREAD / HC_PACK / COMPILE_HC, bigmoe/fuse.py) are opt-in and OFF in R57_PRESET=45, so ref2's hook is the
    only one. WIRE AFTER night_thu.sh ENDS (it copies scripts/r57_screen.py at each step's start): an R57_HC8=1 switch in
    the screen. One slot, shared control: plain C 224 / DENSE-N C 213 / HC8 C 224 / HC8 / DENSE-N / plain (6 arms, ~32 min).
    HC8 line (pre-registered Wed 14:5x): KEEP for the FAST track if HC8 vs plain >= +2 % geo steady with no domain < -3 %
    (and EvalSuite same-scores); else KILL.
  - DENSE-N IS NOW RAM-NEUTRAL (Leap 2190e10, ~/Leap/scripts/ref2.py:254): after load and after ref2.apply(),
    n, mb = ref2.dense_native_convert(model) (head=False; no env var; inert until called: _DNR_ON is set only there).
    Converts 4-bit dense weights with N >= 1024 in place (qkv|z concat, out_proj, o_proj, q_proj, shared down) to 4-D
    native arrays (direct reads raise). BigMoE's only direct quantized read is the router gate under S10B_DIR (N 512,
    not converted). So the slot is all C 224: plain / DN / HC8 / HC8 / DN / plain; DN line unchanged (>= +1 % geo
    steady, every token == REF2-T; Leap expects ~-2.0 ms per check). Wire R57_DNR=1 + R57_HC8=1 after night_thu.sh ends.
  - BUILD #3 (native expert records, +18.7 % exact on the expert kernel; the orchestrator 14:4x): Leap builds the
    load-path side as a PATCH in its own copies (CPU gather for prefetch / JOINT / ensure, dirty flags for demand loads),
    as with W1-PICKUP; I review and integrate, nothing lands in ~/BigMoE without me. No second 45 GB copy on disk: repack
    at load, or wait for Friday's records3 conversion. Not objected (Wed 14:4x).
  - **THU EARLY SLOT, NOT ARMED (the orchestrator fixes the time in the Wed-night order ~22:00: at RELAX_DONE ~06:40 or
    after RELAX's quiet arms, before T0): scripts/night_thu.sh, one quiet ticket ~95 min, MEM ~52 GB, apps closed.**
    ACCEPTED 14:3x as sized: placement RELAX_DONE (~06:40) before T0; the orchestrator sends NOTBEFORE / NOTAFTER ~22:00
    with the full order (if the night is cut, T0 / F1 lose time, not the headline). The REF2_DENSE_NATIVE arm: next slot, OK.
    1 = the C 256 headline (d256_wed.sh D256_C=256 -> data/d256/d256_report_256.txt); 2 = agent leave-one-out at C 224
    (agent_loo.sh -> data/aloo/aloo_report.txt; line + fix pre-registered in its header, sent 10:2x). Arm it with:
    GAP0=0 GAP=0 MARGIN=4 NOTBEFORE=hh:mm NOTAFTER=hh:mm bash scripts/turn45.sh 48 100 "..." /bin/bash scripts/night_thu.sh
  - FOR THE 24 GB FAST BUILD (NewIdeas lounge 13:32, corrected 13:40, their 55e170f): in FAST (QOM cf 0 + 3-bit) the LSB
    pool sits idle on chat (0.0 MB per kept), so give its RAM to C_m: at 24 GB 11-bit, 171/0 vs 154/49 = x0.91 / 0.84 /
    0.85 bytes; keep C_l 4-8; EXACT keeps its split. 11-bit parts are x0.955 each (not x0.824).
  - **WED 09:49-10:10 THE NEW DEFAULT AT C 224 (d256_wed.sh D256_C=224, old vs new A-B-B-A, 14 prompts, all exact):
    BETWEEN.** new +7.2 % geo steady (51.0 vs 47.1 tok/s; code 74.2 / chat 38.8 / math 63.6 / agent 26.8 vs 69.0 / 34.5 /
    56.4 / 29.8), lifetime peak 42.1 vs 40.3 GB, SSD MB per kept 56.0 vs 82.9. W1B's six (11-02's footing): 64.9 vs 60.9
    steady (whole run 59.7 vs 56.0). AGENT -9.9 %: bash18 -16.6 % (9.7K-token prompt, 3.1 kept per check; new 18.7 / 22.6
    vs 24.6 / 24.9), text23 -2.6 %. Per the pre-registered rule the default STAYS; proposed to the orchestrator: per-lever
    arms on agent prompts tonight beside the C 256 headline (C 256 by day swapped, see below; tonight's slot is set ~22:00).
    MTP Head 09:48: SAMELAYER-T BETWEEN (trained recall@10 code 0.823 / chat 0.851; layers 40-47 0.854 / 0.892; no
    follow-up queued). The orchestrator 10:1x: lever 2's forecast reads get SAMELAYER-T's trained weights as a flag
    (A/B vs untrained; MoonShots 7d92f75: code forecast misses 13.7 -> 8.1 MB per kept, exact, +125 MB).
  - **WED 08:57 5b PASS (U3C len on code, FAST; C 224, on the new default):** SSD MB per kept token x0.732 vs U3, steady
    +3.7 %, kept per check x0.977. Absolute geo on 12 HumanEval: U3C 110 tok/s at 15.0 MB per kept, U3 106 at 20.5 MB,
    the exact u3n2 gate 83.1 (== REF2-T), all at a 39.4 GB lifetime peak. Dump data/u3c/dump_224 sent to Breakthrough for
    dm_u3c_replay.py: U3C MASK CHECK PASS 08:5x (1,248 records bitwise; warm per the length rule). Adoption needs EvalSuite
    same-scores on code + a request-level code switch.
    ALL WED_TESTS items are now done (0, 1, 2, 3, 3b, 4, 5, 5a, 5b); open: C 256 confirmation of the new default; the
    lever 1 per-step pruning (JOINT KILL by its own line, yet ADD in item 5). (Item 1 vs REF2-T: expected, closed.)
    LEVER 1 NEXT (MoonShots 09:0x, ~/MoonShots/data/ssdmicro2.txt, 26a2ba8): (a) WAKE-AHEAD: after 1.2 / 2.0 ms of SSD
    idle a burst pays +50 / +49 us; ONE 4 KB F_NOCACHE read issued 150 us ahead removes 87 / 94 % (250 us: 91 / 87 %),
    so wire one read at the router's launch (lead 150-250 us, jitter-tolerant) instead of the keepalive trickle.
    (b) ZERO-COPY (WALL1 D1 / M-29): -173 us per 2-record call at 45 GB; at 24 GB -30..-60 us per call at 4-15 records
    (three runs; the -158 was an outlier). At ~43 layers with a miss per check, (b) is worth ~7 ms of ~105 ms per check.
    C 256 BY DAY DOES NOT FIT (09:15-09:19): scripts/d256_wed.sh (old vs new at C 256, the orchestrator OK'd it for the
    headline) swapped 9.29 -> 11.58 GB in the first arm (old default, ~42 GB) with ~11 GB of sessions resident although
    NO-SWAP read 48 GB; the per-arm guard killed it, I stopped the run (TaskStop + checked no children + peer unlock).
    No numbers. The orchestrator asked: (a) D256_C=224 now (5b at C 224 = 39.4 GB kept swap flat) or (b) C 256 tonight
    with apps closed. The script now takes D256_C and reads the swap base at the run's start (e255b6e).
  - **WED 08:35 THE 45 GB EXACT DEFAULT IS ~+19 % FASTER: ADOPTED as R57_PRESET=45 (0365ada).** Item 5 (C 160, 14 prompts,
    A-B-C-C-B-A, all six arms 14 / 14 == REF2-T): the night's levers (chat switch, keepalive 50 us, vtier 64/32, K-83)
    +12.1 % = ADOPT; lever 1's full stack (JOINT, copy split, coherent spin, system post) on top +6.4 % = ADD. SSD MB per
    kept token -30 %, footprint +1.8 GB. R57_D45=0 = the 11-02 default (default45_wed.sh pins it); each flag off with
    its own =0 (BIGMOE_COPY_PAR=0 is popped). Orchestrator told 08:3x; peer say to all. NEXT: confirm at C 256 (the
    default's C; ~43.5 GB lifetime expected) in the first free quiet slot. ITEM 4 PASS (converted path exact end to end).
  - **WED 07:28-08:33 MORNING RAN (started on Breakthrough's "map batch done" 07:26; every arm ends by 12:55: no arm
    starts after 12:30)**. Part 1 scripts/morning_1104.sh (done 07:50), part 2 scripts/morning2_1104.sh (07:52-08:33:
    B1 item 1 -> C items 4 + 5 -> D 5b, which stopped on data/u3c/HOLD as planned; Breakthrough told "morning block done").
    - 3b BETWEEN (p3 0.789 / p6 0.792; full 0.794; tokens == pr_160; MTP Head has data/r57/pr_dump, SAMELAYER-T landed).
    - 5a PASS (u3n == u3c, 12 prompts; one 282 s heat pause inside u3n, tokens exact); item 3's 2nd check ALL EQUAL.
    - ITEM 0 LIVE 07:51 (d0030a1): the first try (07:41) tested on build_nat, which lacks set_direct_split -> rc 3,
      restored; item0_live.sh now tests on build_w1. ext/build sha 5333899cb514 (== build_w1 == build_m01), Leap
      7f43a3f. EvalSuite told (peer send); it froze snap/bigmoe-da8e7a6 and asked about MAXK 160: answered (runtime env,
      ext/build serves it; offered a build_next rebuild if they still want one).
    - BUG FIXED da8e7a6: tier.py's block (01f652c, 11-01: 9-16 rows on rank plans) crashed every TIER_COMBINE call the
      streamer puts on its sync path (24 GB stack, MAXK 80: W1B 24's 12-token warm-up died, 07:42). Such calls take the
      stock block (as before 11-01); a CPU mock routes 9 widths, the pre-fix tier.py fails exactly the 4 crash cases.
    - ITEM 1 W1B 24 GB (07:56): 33.2 tok/s mean, 383.8 SSD MB per token, lifetime footprint 23.86 GB; w24 == w24t shas.
      vs REF2-T: 3 of 6 equal (HumanEval 68 / 91, algebra 1282); prealgebra 1640, algebra 694, gsm8k 708 differ. NOT the
      fix (every prompt prefills in one >= 50-row call, which it does not touch): the 24 GB stack's own numeric path.
      Expected, not a bug: REF2-T (ref2 batch-invariant kernels + key buckets) is the 45 GB reference only; the 24 GB
      line keeps its own stock-kernel reference (exact-reference memory: "does not change the 24 GB / 12 GB lines"), and
      its own check (w24 == w24t) passed. Never call the 24 GB stack exact against REF2-T.
    - ITEM 2 lever 1 BETWEEN by its line: all 8 arms exact; steady +9.0 % (w1uf 65.7 vs w1u 60.3 tok/s geo, C 224); but
      the fixed part per check 19.2 -> 19.5 ms (line <= 10): the gain is not the mechanism it targets (stall -4.1 ms per
      check). JOINT's own step line KILL again (busy -2.4 ms, needs <= -8). Full-stack stall report:
      data/w1/stall_w1t_vs_w1tp.txt.
    - ITEM 5 extended (17ddb0c): dfc / dfc2 = dfb + lever 1's full stack, order A-B-C-C-B-A, its own pre-registered line
      (ADD / LEAVE OUT / BETWEEN); dfb's verdict unchanged. Reports leave heat-paused runs untimed (a pause inside a prompt
      put it at 0.8 tok/s).
    - 5b: the orchestrator 07:5x: when the morning block ends, SendMessage Breakthrough "morning block done"; it runs
      NewIdeas' screen 4 (~20 min, shared); on its "screen 4 done": rm data/u3c/HOLD and run 5b under turn45 (NOTAFTER
      12:00) only if it still ends by 12:55. Breakthrough OK'd 5b's line (07:3x); send it data/u3c/dump_<C>/ afterwards.
  - **WED 06:2x-06:5x MORNING BLOCK SET (the orchestrator 06:2x: GPU ours ~08:30-12:50, day tests pulled forward; Kamen
    wants them done before 13:45)**: START scripts/morning_1104.sh as a harness background task (CLAUDE_PID 77383) when
    Breakthrough messages "map batch done"; it runs a frozen copy of itself (data/r57/snap/morning_1104_run.sh).
    - Blocks: A 3b + 5a (C 160) -> item 0 (scripts/item0_live.sh: patch live + ext/build rebuilt + tests; Fit12 said YES
      06:2x: its 13:05 runs use ~/Breakthrough/v3p, not ~/BigMoE's bigmoe/ or ext/build; keep the .venv and models/bare
      unchanged to ~13:55) -> B items 1 + 2 -> C items 4 + 5 (scripts/default45_wed.sh, defined 06:5x).
    - Log: data/morning_1104.log. Latest starts: A 12:15, B 11:15, C 11:50; arms stop at 12:40.
    - Item 3 DONE on CPU: data/ab/ref_tokens.json from the night's u3c_160 + chat23 (README beside it).
    - build_m01 rebuilt 06:23 (fresh, sha 5333899cb514).
    - After item 0: commit the live patch + send EvalSuite (peer send) the commit, the ext/build sha256 prefix and Leap's
      HEAD (data/item0.log's 'ITEM 0 LIVE' line).
  - **WED 05:4x-05:5x PRE-ROUTE KILL WITHDRAWN (MTP Head's catch, ojox-4a 05:3x; confirmed in ref/qwen4_exp.py)**: pr_160's
    full / p3 / p6 scored L+1's router on L+1's ATTENTION-side HC read; the router sees the MLP-side read (own hc_norm +
    read mix per side, no layernorms). Fixed in scripts/r57_screen.py: "full" = L+1's MLP-side read at its start (PLE in),
    p3 / p6 MLP side, "fullA" = the old read (control), R57_PR_DUMP=1 saves MTP Head's SAMELAYER-T rows (X = full's input,
    Y = L+1's true MoE input, float32, ~2.5 GB). CPU logic test PASS (scripts/test_pr_capture.py: wiring, PLE, dump).
    pr_report.py marks pre-fix files. RE-RUN = WED_TESTS 3b (scripts/pr2_run.sh, ~4 min, shared slot, C 160, tokens vs
    pr_160's; with item 3 or an earlier gap the orchestrator gives). Lines unchanged; MTP Head predicts all 0.76-0.81.
  - **WED 04:1x-04:4x**: JOINT recheck for the orchestrator (cd525aa): KILL at C 160 by its line, not a build or flag
    problem (45 % of sidecar reads issued early; layer span unchanged; my per-kind burst count was the bug; stall_report
    now prints 'JOINT read'). Health review 04:42: my mission 20 C 224 arms grew swap 4.11 -> 7.50 GB under the per-arm
    guard; c45_runner now applies the 2 GB rule per run (f3b802d; chains may export C45_SWAP0 for a chain-wide base).
  - **WED 03:28 Breakthrough's records3 LAYOUT CHECK: PASS** (~/FableGod/decision_map/out_layout/LAYOUT_check.txt:
    converted store + build_nat vs today's store and ext, baseline and t3_top2_all on 3 windows, test vs ctrl and vs
    stored out/ all bitwise equal). Branch (a): the 13:40 layout patch + ext rebuild goes ahead, no flip-back.
  - **WED 03:14 NIGHT DONE (chain 00:30-03:07, lock released): docs/NIGHT_1104.md has the scoreboard row + every line.**
    W1B C 160: SSD busy 110.4 / exposed 112.0 ms, 76.5 calls, 169.4 MB/kept, 42.0 tok/s, exact. BYTES-bound (1190 MB per
    check); per-burst fixed 18.1 ms = lever 1's ceiling at C 160. JOINT no gain; keepalive ~-3 ms; vtier -30 % bytes,
    ~+3-7 % tok/s (copy costs: zero-copy vtier = next); pre-route KILL (WITHDRAWN 05:5x: wrong read, re-run 3b); chat switch +21.6 % exact; U3 crashed (fixed,
    5a); mission 20 KILL on time at C 160; cmb32 KILL; cmbsc not run (no 160 size file). data/ab/ref_tokens.json MISSING
    (WED_TESTS 3). Lounge notes sent (no wakes at night); morning: messages only if asked.
  - **WED 00:3x NIGHT (main, CLAUDE_PID 77383)**: memory gate opened 00:30:26 (NO-SWAP 35 GB). STALE-SLOT CHECK PASS
    00:34 (data/sc/sc.log): sc0/sc1 default, sc2/sc3 C_l 32, sc4/sc5 zero-copy direct, each with vs without R57_CBB:
    3 prompts x 128 tokens equal, 127 per-check logits hashes equal (distinct per check), so every 45 GB number stands;
    posted to the lounge (no wake: night = no acks). Side note: sc4/sc5 (DIRECT on today's UNALIGNED row-major slots)
    ran -15..-23 % vs sc0 (M-29's +843 us unaligned cost; single pass, not a speed number). Then the sprint started
    00:34 (sprint_s160.sh), U3 / combination / mission 20 follow with cutoffs 02:00 / 02:30 / 03:30. Watcher bgpyfvd5s
    fires on 'night chain end|lock gone|lost the lock'. Continuation bfpqv7xt9 only queues if the chain gave up (it
    did not: stop it by TaskStop after the chain ends if it is still waiting). Morning: stall_report c45t_160,c45tj_160
    FIRST, s0_report, w1_report, then ka / vt / pr / chA-chB / U3 / combo (CMB_C=160) / pw; one scoreboard row to NewIdeas.
    01:0x U3 CRASHED at start (tierglu sys.path; fixed a2584ff, re-run = WED_TESTS 5a). 01:37-01:41 a HEAT PAUSE froze
    cmb5_160 (the CHATSW + JOINT stack) 7 s after its start: check its per-prompt numbers vs cmb0 before using them.
  - **MOVED TO MAIN (Ultra) Tue ~22:2x (claudesub 77 %; Kamen 22:2x: research NOW; Wed = his research day 13:45-23:30, all
    batch tests end before he arrives, T0 moved out of his day)**. CLAUDE_PID is now 77383 (lock files key on it). The move
    stopped bmk0rx79b; RE-ARMED as bnnn44vsq (wrappers 79982 / 79984, turn45_s160.sh 25 330): data/r57/snap/night_now.sh =
    night_s160.sh with evening-safe cutoffs (sprint by 01:00, U3 02:00, combination 02:30, mission 20 03:30; inner deadlines
    2400 = none; memory wait to 01:00), AFTER after_prefix2.sh (Breakthrough's re-armed prefix bcthuogm9: its log's last
    line 'prefix done' / 'everything stays', or from 23:15 no prefix process + log quiet 10 min). LEVER 1 BUILT TONIGHT
    (5565a56; ext/build_w1, all default off): Leap's W1-PICKUP (BIGMOE_SPIN_COHERENT, BIGMOE_POST_SYS) + S0 instrumentation
    (BIGMOE_TRACE: reads carry tp0 / tp1; kind 5 = ensure(), kind 6 = the release) + the direct path (BIGMOE_RECORDS_DIRECT,
    preadv straight into the slots) now traced; scripts/test_w1.py PASS (bounce + direct: every slot == its record part);
    scripts/s0_report.py (zero-hit split + S0 stages). WEDNESDAY'S LIST = docs/WED_TESTS.md (0: the conversion patch +
    ext/build rebuild at 13:40 (decide then: build ext/build from the source before 5565a56 if EvalSuite's snapshot must
    carry only 761cb3d's reader), 1: the 24 GB baseline 13:45, 2: lever 1 at 45 GB, 4: the e2e check, 5: the combined
    default, 6: FAST, 7: Leap's F1).
  - **23:0x**: convert_records3.sh + ab_records3.sh now write native+p11+pad (Leap's tool --pad; need Leap >= 7624eb0;
    test mode PASS: output == scratch/r3p11pad, inverse md5 3/3); the A/B night gains abB2z (+ zero-copy reads).
    EvalSuite's records3 checks moved to variant ref2tf0 on snap/leap-7f43a3f. WED 13:40 DELIVERY to EvalSuite = my
    commit + ext/build .so sha256 prefix + the Leap commit matching the format (7f43a3f today). Tonight's chain holds
    the lock (granted 22:59) and waits for NO-SWAP >= 33 to 01:00; continuation ticket bfpqv7xt9 (night_now2.sh, wait
    to 01:45) queues only if it gives up; the orchestrator asked Kamen to quit Chrome.
  - **LATE TUE 22:4x-22:5x builds (all committed, default off)**: the STALE-SLOT CHECK (scripts/stale_check.sh, frozen
    *_sc.*) runs FIRST in tonight's chain (night_now.sh edited before it started): R57_CBB (a command-buffer boundary per
    MoE call) + R57_LOGHASH (every check's logits hash) at C 160 on three pairs (default / C_l 32 / direct); verdict in
    data/sc/sc.log; a FAIL goes to the orchestrator at once. R57_FAST=U3C built (0ea5b8b; R57_U3C_LEN, R57_U3C_DUMP).
    The padded conversion format 'native+p11+pad' (172eba5): r3layout_ref layout, ext set_direct_split (aligned l1
    planes straight in, b via a bounce), staged tier.py sidecars in record order; test_w1 + test_layout_engine PASS
    (TEST_EXT_BUILD=build_w1). DONE TONIGHT (22:5x): Leap's kernels + tool for native+p11+pad (7624eb0, installed live,
    ref2.self_test PASS); my padded copies scratch/r3p11pad (md5 L00 98fcba62 / L20 1f375d00 / L47 f770f6d1, test_layout
    PASS); LEAP'S CMP PASS 22:5x: its --pad output == mine byte for byte, index entries field for field; scratch/model_mix now points at them (Wed's e2e covers the conversion's real format;
    test_layout_engine PASS on build_w1). scratch/r3p11 (unpadded) stays for Breakthrough's overlay.
  - **LATE TUE (22:3x-22:4x), decisions + builds**: (1) THE A/B NIGHT is now bracketed and converts itself (the
    orchestrator 22:4x, EvalSuite's proposal): abA -> md5 + convert -> abB -> abB2 -> --inverse (md5 == originals) -> abA2,
    ends ROW-MAJOR (scripts/ab_records3.sh 899e737; needs RELAX_DONE + no T0 chunk running, not T0_DONE; AB_T0GO=1 touches
    ~/EvalSuite/results/t0/GO after abA2 if T0's leftover follows). The permanent conversion after a PASS waits for
    T0_DONE; EvalSuite's checks 1 / 2 go with it, not in the A/B night; the Fri 00:30 slot is set ~22:00 Wed.
    (2) LEVER 1: BIGMOE_COPY_PAR (37b9f8b, a lone record's copy over 3 threads, M-29: 122 -> 81 us) replaces the direct arm
    in w1_lever1.sh. M-29 (MoonShots f1a98b3): direct reads into today's UNALIGNED pieces are +843 us. Zero-copy needs
    4 KB-padded pieces (-173 us per 2-record call); proposed to Leap as the conversion format 'native+p11+pad' (MSB pieces
    padded to 36,864 = msb_sz unchanged; LSB: pad b (+16 KB per record) or l1 planes first; Leap decides; needs the p11
    kernels' stride from the pool shape). (3) Leap's S7B-PROBE (50de28c / fb999be): GPU-cached stale slot reads happen only
    within ONE command buffer; a command-buffer boundary is enough. Today's engine is safe by its schedule; tonight's
    C 160 tokens check it live. Leap builds default-off coherent slot reads Wed. (4) P1 (Breakthrough, WED_TESTS 5b):
    R57_FAST=U3C to build Wed morning. Base sets: unsure = ranks 0-3 + warm ranks 4-9, sure = 0-1. Union over ALL rows of
    the live-cut block. warm = prompt top-10 ids per layer OR ~/FableGod/fablec/masks/pop_cap45.npy >= 0.05. pmtc first,
    len (footprint alone at >= 128 prompt tokens) only on Breakthrough's word. Dump per prompt .npz: (check, layer)
    records ids [rows, 10] -1-padded, sure, keep, rows + warm [48, 512] + prompt_len, on HumanEval 68 / ifeval 1220 /
    multi de3, for dm_cold_masks.run(). Line: chat MB per kept <= 0.85x U3's AND tok/s >= U3's. (5) Scripts ready for
    Wed: w1b_24.sh (24 GB baseline; s10b S10B_KEYS), w1_lever1.sh, w1_report.py (scoreboard row), s0_report.py,
    mix_e2e.sh.
  - **TONIGHT Tue -> Wed: ONE TICKET AT C 160 (re-armed 19:23; the orchestrator 19:1x: NO-SWAP 21.9 GB at 19:1x, ~30-35 GB
    expected at 00:30; Breakthrough 19:2x: separate tickets leave gaps where a FLOOR step can start and hold memory)**.
    Background task bmk0rx79b (turn45_s160.sh 25 280, bash pid 30544): queues at 00:45 or later, ONLY after Breakthrough's
    00:30 map prefix (AFTER data/r57/snap/after_prefix.sh: night_prefix.log's last line 'prefix done' / 'everything stays
    for Wed 15:00', or past 01:20), no WAITMEM (FLOOR waits for my first ticket until 02:00, Breakthrough 8198865); the
    wrapper keeps a grant at >= 29 GB available (PEAK 25 + MARGIN 4); data/r57/snap/night_s160.sh then waits INSIDE the
    lock for NO-SWAP >= 33 GB until 01:45 (else exit 3: the night goes to FLOOR) and runs, with start cutoffs:
    sprint_s160.sh by 02:30 (c45t_160 / c45tj_160 traced JOINT A/B, ka0/ka1/ka0r/ka1r_160 on build_la, vt0/vt1_160 on
    build_vt with R57_VTIER=64/32, pr_160, chA/chB_160) -> U3 at C 160 by 03:15 -> the combination at C 160 (CMB_M2=0)
    by 03:30, no new arm after 05:00 (cmbsc fails: no laysz45_160_sc15) -> mission 20 by 04:15 (its C 224 arm self-skips).
    Log: data/s160/night.log (+ s160.log, the per-script logs). BUG FIXED before it bit: c45_runner turns arm commas into
    spaces, so R57_VTIER=64,32 would have handed '32' to env; r57_screen takes '64/32'. MORNING (tags at C 160):
    stall_report.py data/r57 c45t_160,c45tj_160 FIRST (the first wall-1 row; ALSO split the stall by layers with / without
    resident hits: Leap's W1-PICKUP found a device-scope post followed only by the spin can stay unseen for ms, so
    POST_SYS may be the bigger lever; promised to Leap), then ka / vt / pr (pr_report PR_DIR, TAG
    pr_160) / chA-chB / U3 / combo_report (CMB_C=160) / pw_report.
  - **WALL 1 SPRINT: BigMoE = LEAD (the orchestrator Tue ~18:3x; Kamen: "lets crack wall one ... which doesnt come back
    as impossible"; charter ~/FableGod/push/WALL1_SPRINT.md)**: every report = the best MEASURED number + the next step, never
    "impossible". Benchmark W1B = docs/WALL1_BENCH.md (S45's six, CAP 256, exact vs s45t_B; untraced w1_<C> + traced w1t_<C>;
    45 GB at C 224 / 256, 24 GB = the shipped s10b stack at C 128). Lever 1 plan = docs/PLAN_wall1_lever1.md (JOINT +
    keepalive measured tonight; BUILD Wed: BIGMOE_SPLIT_KB parallel >= 256 KB piece reads in ext/build_w1 + unit test; line:
    exact AND fixed cost <= 10 ms/check AND steady >= +5 % = PASS, < +1 % = KILL). EACH MORNING: one scoreboard row per line
    to NewIdeas (Night | SSD busy | Exposed | Calls/check | MB per kept token | Tok/s | Exact?) + the next step; the first
    45 GB trace row = tonight's c45t_224 / c45tj_224 (stall_report). SLOTS (the orchestrator 19:0x, option b): THU BY DAY
    right after T0_DONE (~09:30 if RELAX ends ~07:30; Kamen at school, quiet): ONE quiet lock ~30 min, still row-major:
    the 24 GB baseline (W1B) first, then lever 1's arms; send the conversion's 1 h heads-up when that lock starts;
    EvalSuite's ifx check #1 also before the conversion; then convert (scripts/convert_records3.sh) + EvalSuite check #2.
    If RELAX / T0 run late into the afternoon: fall back to Fri 00:30 next to the A/B. Thu 00:30 = only the e2e check
    (RELAX's night untouched otherwise). Build BIGMOE_SPLIT_KB Wed after the move to main. Team: Fable A designs from each night's trace,
    MoonShots SSD micro-tests by day, MTP Head (L+1 predictor if pr_224 misses), Leap on ask. Move to main Wed morning
    (the orchestrator; never while attached runs live).
  - **CONVERSION ENGINE WORK (Kamen APPROVED Tue ~17:3x via the orchestrator: "yes, do it"; state Tue 17:5x)**:
    - WHEN: the conversion waits for BOTH ~/EvalSuite RELAX_DONE and T0_DONE (orchestrator 17:2x: T0 reads records3
      row-major through v3p; T0 Wed 15:30 -> Thu 00:15 + its leftover after RELAX), plus a 1 h heads-up to all sessions and
      md5s first (Leap's tool: --md5 FILE). EvalSuite: NO writes under models/bare and NO venv changes until both DONEs.
    - DONE + committed: ext reader 761cb3d (read_rebuilt_layout / record_rowmajor / layout_max; read_expert's fmt-3 path
      turns a native / native+p11 record back into today's row-major record first; ext/build_nat; ext/build NOT rebuilt
      yet). scripts/test_layout.py PASS (all 512 records of L0 / L20 / L47 native+p11 and L20 native == records3 bytes,
      4-bit prefill pieces equal, wrong layout aborts, pools load 35,216 B pieces). scripts/r3layout_ref.py = my own
      reference converter (scratch only). Leap's native tool == it (L20, cmp); Leap's COMBINED tool
      ~/Leap/scripts/convert_records_p11.py (2b3fc63; [--inverse] [--layers] [--md5 FILE] [--yes]; ~3.5 s/layer, refuses
      < 112 GB free or lsof-open) == my scratch/r3p11 byte for byte. Its index entry keeps the original under "rowmajor"
      (--inverse needs it: never drop that key).
    - Leap's p11 format: s3 / b3 / b = 11-bit codes (sign << 10 | (exp - base) << 7 | mant7), 800 blocks x 11 words
      LSB-first, word 8800 = base, piece 8804 words = 35,216 B; record MSB 2,064,384 + LSB 720,896 = 2,785,280 B.
      Kernels (2b3fc63): 3c-N (7 kinds) + NAX6-N detect p11 by the pool's dtype (s3 uint32 [C, 8804]); bitwise on full L20 +
      L44; +1.2 % / +2.2 %. ref2 router: per layer by t["layout"] (OOO) or bigmoe.tier._LAYOUT[0] (tier_glu), 0 -> my 3c,
      1 / 2 -> 3c-N; ref2.apply() sets bigmoe.tier.LAYOUT_ROUTER = True; guards both ways. LEAP 90456ce (supersedes
      2b3fc63; EvalSuite freezes THIS one): with REF2 removed (r57_screen removes it around every draft) layouts 1 / 2 still
      take 3c-N (my catch: remove() left LAYOUT_ROUTER True, so a converted layer would have run my row-major 3c).
      My direct records3 readers (m01_convert, m03_convert, test_records3 / 3p / 3m, test_bounce_pool) refuse a converted
      store. Asked MoonShots for data/packed45_224.json (B2 arm at C 224).
    - STAGED (not live): patches/records3_layout.diff (tier.py + stream.py; staged copy scratch/stage_layout, base md5s in
      scratch/stage_layout/base_md5.txt): t["layout"] / rows3 / offs per layer from index.json, load_index(layout_ok),
      p11 pool shapes from the index sizes + contiguity check, _read_rebuilt (prefill + grouped), tier_call sets _LAYOUT[0]
      and refuses a converted layer without LAYOUT_ROUTER or with 3b, M-01 / POM / RECORDS=3 refuse converted layers.
      No-op on row-major. scripts/test_layout_engine.py [pkg dir] PASS on scratch/model_mix (a symlink model dir: L0 / 20 /
      47 native+p11, the rest records3).
    - WED AFTER BREAKTHROUGH'S DAY SLOT (its map holds ext/build 15:00-~15:15 and build_nat ~15:15-15:17; wait for "day slot
      done" in ~/Breakthrough/data/wed_day.log, by 15:27; NEVER rebuild build_nat: Breakthrough's dm_t3 + FLOOR night 2 load it;
      keep scratch/r3p11 to Fri), in order: base md5s unchanged -> `patch -p0 < patches/records3_layout.diff` in ~/BigMoE ->
      test_layout_engine.py . -> lsof ext/build -> rebuild ext/build (-j2, taskpolicy -b) -> commit -> send EvalSuite the
      commit + `shasum -a 256 ext/build/bigmoe_ext.cpython-312-darwin.so | cut -c1-12` (tools/snap_bigmoe.sh). EvalSuite runs
      ifx repro check #1 (patched engine, row-major) before the conversion and #2 after, both on one Leap snapshot (2b3fc63).
      No env change needed for check 2 (the router reads the index's layout).
    - THU 00:30 (my slot, before RELAX; tell EvalSuite before 00:00 and touch relax/GO after): the end-to-end GPU exactness
      run = the 45 GB default on scratch/model_mix at C 224 vs chat23 REF2-T tokens (every token passes 3 converted
      layers: router + p11 kernels + prefill reader together). SCRIPT READY: scripts/mix_e2e.sh (C 160, 11 prompts vs
      cmb0_224's tokens, else chat23's; then the row-major control mixc; stops unless the live engine has the patch and
      ext/build has layout_max() == 2); r57_screen's R57_MODEL_DIR (a68aa9e) points the load at scratch/model_mix. ARM
      Wed evening with frozen copies (data/r57/snap/*_e2e.*: r57_screen_e2e.py, c45_runner_e2e.sh), a ~30-min quiet
      ticket NOTBEFORE 00:20 (T0 ends 00:15), then ALWAYS touch ~/EvalSuite/results/relax/GO (and by 02:00 at the latest).
      Tell EvalSuite before 00:00 that the slot is this check. EvalSuite's own checks: variant ref2tn = ref2t on
      snap/leap-90456ce + my bigmoe snapshot, C 192, six IFEval rows (1,614 stored tokens), ~6 min each; #1 Thu after
      T0_DONE + RELAX_DONE (before the conversion), #2 after it; check 2 == check 1 is the conversion's test.
    - THU CONVERSION (by hand, never armed): CLAUDE_PID=65439 CONV_HEADSUP=<epoch of the heads-up> bash
      scripts/convert_records3.sh (refuses without ~/EvalSuite/results/RELAX_DONE + T0_DONE, a >= 60-min-old heads-up, my
      quiet lock with >= 10 min left, Leap >= 90456ce, nothing open in records3; read-only --check; md5s ->
      data/records3_md5_rowmajor.txt; convert; md5s -> data/records3_md5_p11.txt; index check). NOT under taskpolicy -b
      (19 s/layer there vs 3.5 s/layer: ~3 min + ~1.5 min md5s). TESTED 17:45 in test mode (CONV_MODEL=scratch/convtest,
      3 layers): output == r3p11; --inverse --md5: files == records3, index entries restored exactly; re-convert: md5 ==
      the first conversion. Then tell all sessions (peer say + the orchestrator) and EvalSuite (check #2).
    - THE A/B SCRIPTS READY (not armed): scripts/ab_records3.sh (arms abB, abB2, flip 1 = --inverse + md5 check, abA, flip 2
      = re-convert + md5 == data/records3_md5_p11.txt, abBr; AB_BRANCH=b stops after abA; 40 prompts = chat23's 30 + 10 more
      HumanEval; refs data/ab/ref_tokens.json, BUILD IT Wed from chat23_ref_tokens.json + tonight's u3c_224 tokens (check
      they agree on HumanEval 68 / 91)) + scripts/ab_records3_report.py (-> data/ab/ab_report.txt, both lines). Arm Thu
      evening after the conversion with frozen copies (data/r57/snap/*_ab.*: r57_screen_ab.py, c45_runner_ab.sh).
    - THE A/B (orchestrator 17:4x-17:5x), Fri 00:30, one quiet lock, the same C for every arm (C 224 if the night again
      allows only <= 41 GB peak): B (converted, M-17 sizes), B2 (MoonShots' packed sizes: data/seed45/packed45_224.json md5
      11309e04, packed45_256.json md5 bda5746e; equal pool RAM 29.677 GB at 224; held-out prediction vs M-17 at C 224: code
      MB/kept -15.0 %, IFEval -14.6 %, multi -14.2 %; B vs A shows only the smaller parts: -4.5 % MSB, -6.4 % sidecar bytes per miss), --inverse + md5 == originals, A (row-major), convert again (md5 == the first conversion),
      B again. Branch (a) because Breakthrough's FLOOR night 2 reads the layout (dm_t3 via record_rowmajor / build_nat;
      its GPU check Wed ~15:18); if that check fails, (b): leave row-major for FLOOR night 2, re-convert Fri 15:00 if PASS.
      Tokens vs stored refs (tonight's cmb0 / u3c / chA at C 224, chat23, EvalSuite's ref2t.r2). ADOPTION (orchestrator):
      PASS (tokens identical, code MB per kept token <= -10 %) -> the store STAYS converted; any token differs -> --inverse
      + md5. Report against my PLAN line and M-27b's (+ median steady >= +3 %; KILL < +1 % or MB > -5 %).
    NewIdeas ~11:4x (Kamen "Yes, queue both"): Tue 3 Nov night = Fable's FLOOR only; other night items move to Wed night.
    Queued idea (the orchestrator, Leap's D7b r85b_d7b.txt): DFlash2 with 4-bit layers + bf16 fc drafts code in 6.3 vs
    10.4 ms at identical kept (exact; math -3 %): once the chat switch ships, the type rule can send code to it (~+1.5-2.5 %).
    Disk (the orchestrator asked 13:4x): told it records3p (49 GB) can go to the Trash (only BIGMOE_POM reads it; R-44b
    never adopted; m03_convert.py rebuilds it); records3 (the default) and records3m (Breakthrough's 12 GB line) stay.
    Leap 11:1x: K-83 (the second exact stack; runner 62 at C 160 exact, draft 11.4 -> 10.2 ms, steady +0.7 %) ported as
    K83_EXACT=1 (k73_live.py block verbatim) -> tonight's c1k_256 arm; ADOPT into R57_PRESET=45 if exact and not slower
    (my call as the preset's owner; NewIdeas asleep). R57_SB1=1 = SB from 1 row (Leap's C0: 1-row checks 48 vs 44 ms; ~0.5 %
    on chat) - untested, exact. R-84 (drafter head on qmm16c, drafts not bitwise) waits.
    The orchestrator 11:2x: Tue 3 Nov night is Fable's FLOOR experiment (Breakthrough, ~10 h, Kamen OK); its run 8 (the
    3-bit sure-row arm, MoonShots M-18) needs my tiered-engine harness with Breakthrough on Tuesday.
  - **KAMEN "Yes, 1-3" (Mon ~10:1x, relayed by the orchestrator 10:1x)**: (1) WIRE MTP Head's chat switch into
    R57_PRESET=45 (exact: only the drafter changes; ~/TrainLab/INTEGRATION_CHATSWITCH.md: chat -> the 125B's MTP head with
    ~/TrainLab/ckpt/d22_b5.safetensors over it, K15, running-product cut 0.3 + early exit, history = prompt after prefill +
    each check's kept rows; code / math / agent stay on DFlash2 L1-20; type rule = scripts/type_rule.py / d23c_mtptrunc.py
    rule(); port from ~/TrainLab/sticky/d23c_mtptrunc.py arm mtp15e). Before it ships: (a) every token equal on chat
    prompts with the wired default, (b) lifetime peak at C 256 with BOTH drafters resident <= 45 GB, (c) the chat gain at
    C 256 (D-23d +24.5 % was at C 192). MTP Head sleeps to Tue 15:09 (no answers before then); its D-23e (C 224) may not run.
    (2) TONIGHT Mon -> Tue: after Kamen is idle 20 min past 01:00 the orchestrator closes Chrome + Spotify + Steam
    (~/.local/share/quiet/night_apps.sh, log ~/Library/Logs/night_apps.log); expect NO-SWAP ~51-52 GB (C 300 gate 52
    borderline, C 320 gate 55 unlikely). ARM ONE quiet ticket, done before ~07:00: NewIdeas' warm split + P on L, the wired
    chat switch at C 256 (a/b/c), C 300 / 320 NO-SWAP-gated; then touch ~/EvalSuite/results/ifx/GO (runner 38 waits for it).
    (3) MBPP downloaded for MTP Head (~/TrainLab/data/mbpp/), not mine.
  - **Mon 09:08 notes (usage-pace SLEEP to ~10:51, weekly 32 % vs line 31 %)**: EvalSuite 07:43: touch
    ~/EvalSuite/results/ifx/GO when tonight's warm split + P arm are done (its runner 38, the REF2c-T IFEval re-test, queues
    then, not before 23:00; at 02:00 without it). MTP Head 08:39: the chat switch PASSED D-23d (exact; chat +24.5 %, 19/19
    prompts, non-English +27 %; agent stays on DFlash2): wire it into the live default ONLY when Kamen says so (note
    ~/TrainLab/INTEGRATION_CHATSWITCH.md; harness ~/TrainLab/sticky/d23c_mtptrunc.py arm mtp15e; both drafters resident,
    38.2 GB at C 192). Its open C 224 confirmation (~46 GB free, separate passes) rides tonight's turn only if NewIdeas orders it.
  - **C50 DONE Mon 07:20-07:22 (data/c50/, quiet, every token == REF2-T)**: at C 256 (OOO + K-73 both arms) per-layer
    sizes (L) vs uniform (U): steady 60.6 -> 63.6 (+5.0 %), whole 54.9 -> 56.4, check 91.9 -> 84.2 ms, SSD MB per kept
    token 74.0 -> 62.4 (-15.7 %; replay -19.3 %), misses per check 219 -> 171; 5/6 prompts up; peak 41.7 GB both = PASS.
    KAMEN'S NUMBER (~42 GB, the full default): 63.6 tok/s steady at 41.7 GB, exact (vs 50.9 at C 224 on Sun = +25 %).
    C 300 / 320 skipped (49 GB free < 52 / 55): still open for a freer night. Sent to the orchestrator + NewIdeas 07:2x
    (+ a correction: runner 62's 20 lock-free minutes may have restarted), note to MoonShots. Full C45 report ran 07:2x
    (data/c45/c45_report.txt) = the 01:3x numbers. Open: C 300 / 320, warm split (Monday night), P on top of L.
    NewIdeas 07:3x, MONDAY NIGHT: (1) the warm per-row split (build R57_WARMSPLIT by day; lead file
    ~/.local/share/usage-pace/leads/2026-11-01_per_row_cost_opus.md; plus the regression on data/r57/c45*_checks.json),
    (2) P on top of L, one arm (ext/build_prior + BIGMOE_EVICT_PRIOR=30 on the C 256 default); C 300 / 320 only on a night
    with NO-SWAP >= 55 GB (NewIdeas asked Kamen, via the orchestrator, for Chrome closed). Default moved to C 256 (3e4786d).
  - **07:18 C50 ARMED**: peer wait returned 07:18 (nothing blocking); py_compile + bash -n OK; stub dry run of the arm list
    OK; preset test OK (256 -> laysz45_256 + K73, LAYSZ=0 -> uniform, 240 -> uniform, COMBINE=0 -> no K73);
    E15_SLOT_DONE already there -> chain (task bq7owhq3m, data/c50_chain.log) started turn45 07:18:58 (PEAK 42, MARGIN 4,
    WAITMEM 46, ticket 25). Results -> data/c50/; report: c45_report.py data/c50 (+ compare l vs u per C by hand).
    Mon 06:46 notes: MTP Head's same-process order effect (2nd arm +12-20 %) does not touch C45 (one process per arm,
    F_NOCACHE expert reads; A2 vs A +0.9 %). NewIdeas' Q1 note (Breakthrough's decision map): per-row k must NOT renormalise.
  - **02:3x C50 PREPARED, NOT ARMED** (usage burst over the weekly line, Kamen-number item): r57_screen preset now adopts
    the md5-pinned M-17 sizes (R57_LAYSZ=0 = uniform control) + K-73 (when R57_COMBINE=1); c45_runner has C45_ARMS
    ("tag:C[:ENV=V,..]") + C45_DEADLINE + C45_OUT; scripts/c50_chain.sh (waits for ~/TrainLab/data/E15_SLOT_DONE only, NewIdeas
    01:5x: C50 ahead of runner 62; arms l256 u256 u300 l300 l320 u320 -> data/c50/; no queueing after 11:30, no run after 11:50). NOT syntax-checked:
    the peers hook blocks every script / python run while others hold or await quiet locks (MTP Head to 05:42, Breakthrough
    #1, EvalSuite #2). `peer wait --timeout 480m` runs in the background (task b7l67804v): when it returns, FIRST
    `python3 -m py_compile scripts/r57_screen.py && bash -n scripts/c45_runner.sh scripts/c50_chain.sh`, a stub dry run of
    C45_ARMS, then start `bash scripts/c50_chain.sh` as a background task. Told NewIdeas 02:3x (it may leave a gap).
  - **NewIdeas 01:3x DECISIONS**: ADOPT L into R57_PRESET=45 (per-layer sizes from the matching data/seed45/laysz45_<C>.json,
    md5-pinned: 224 3098a505, 256 ee76e2a7, 300 cd0df64a, 320 f0a3997c; uniform when no pinned file; opt-out for A/Bs) and
    ADOPT K-73 (K73_EXACT=1 by default when R57_COMBINE=1; NewIdeas tells Leap); P not adopted (re-test on top of L later).
    C50 = c45l_256 (the likely real ~42 GB setting: Kamen's number) + c45l_300 / c45l_320 + uniform c45o_300 / c45o_320
    (never ran); chain rules stand (E15_SLOT_DONE, nothing that can't end by 12:00, split only if it starts by 10:30;
    the orchestrator's 01:0x order on top). TODO at the 02:17 wake: preset edits, C50 mode, chain; warm split if usage.
  - **C45 DONE Mon 01:18-01:26 (data/c45/, quiet, every token == REF2-T in all 8 runs; ~60 s per run)**: OOO A-B-A at
    C 224 45.2 / 45.6 -> 53.9 steady (+18.7 %, whole +15.9 %, all 6 prompts +16..+41 %); L (M-17 sizes) vs B: SSD MB per
    kept token 96.0 -> 79.5 (-17.2 %), steady 58.4 (+8.3 %) = PASS (in-sample sizes; HumanEval/91 -7.1 %); K-73 +2.4 %
    (draft not faster); P: misses/check -9.3 % but pooled misses/kept -3.5 %; sizing C 240 56.7 (39.4 GB), C 256 59.3
    (41.7 GB); C 272/300/320 skipped (46 GB free). Sent to the orchestrator + NewIdeas (01:3x), notes to Leap + MoonShots.
    c45_report.py could not run then (peers hook: others' quiet locks block programs): run it when the Mac is free.
  - **NewIdeas 20:4x: two more quiet tickets AFTER Leap's runner 62 exits (~05:45 Mon)** (Kamen 20:3x: the window runs
    through Monday, no day hold; Chrome closed 22:55 -> Mon 12:00; fans 4500 + boost 5500 to Mon 20:00):
    (1) C50 = c45o_300 / c45o_320 on the default, every token vs REF2-T, NO-SWAP >= peak + 4 (skip both if C45 already ran
    them) + c45l_300 if L PASSED at C 224 and ~/MoonShots/data/laysz45_300.json exists; (2) the per-row warm-replay split
    (leads/2026-11-01_per_row_cost_opus.md: identical check cold then warm at 1 / 4 / 8 / 16 rows; + OOO per-layer timing;
    + the SSD-wait regression from <tag>_checks.json). PLAN: after the 22:51 wake (usage permitting) build (2) in
    r57_screen (R57_WARMSPLIT) + a C50 mode in c45_runner (no A/B block); arm ONE background chain. NewIdeas 21:5x (the
    orchestrator, Kamen "Yes, tonight only"): MTP Head's E1 + E5 training (3-h quiet ticket, night8_train.sh pid 58883)
    goes first after runner 62 -> MTP Head 23:2x: pid 58883 exited 23:12 (its first ticket ran nothing); the chain waits
    for ~/TrainLab/data/E15_SLOT_DONE (E1+E5's chain writes it when its 3-h slot ends, ~08:45) AND runner_r62.sh gone;
    no new run may start that cannot end by 12:00; then C50 (must END before Mon 12:00: Chrome reopens; start by ~11:30 at the latest); then the
    warm split only if it starts by ~10:30 (else skip it to Monday night). Then tell NewIdeas.
  - **TONIGHT'S C45 TURN (NewIdeas 07:4x + 11:4x + 11:5x + 15:3x; the orchestrator 15:2x = Kamen 15:22 "Yes, try ~50
    GB")**. Launch at the 22:4x health review, as a background task (not nohup):
    cd ~/BigMoE && CLAUDE_PID=65439 MARGIN=4 GAP0=0 GAP=0 NOWAIT45=1 MAXFAILS=2 NOTBEFORE=23:00 WAITMEM=42 C45_PRIOR=1
      C45_K73=1 C45_L=1 C45_BIG="300 320" /bin/bash scripts/turn45.sh 38 50 "BigMoE C45: OOO A-B-A + K-73 + M-17 sizes +
      LRU-prior at C 224, ~50 GB C 300/320, sizing C 240-272" /bin/bash scripts/c45_runner.sh "224 272 256 240"
    Order at the first C that fits: A c45_224 (no OOO) -> L c45l_224 (default + MoonShots' M-17 LAYSZ45 per-layer pool
    sizes, BIGMOE_TIER_SIZES=data/seed45/laysz45_224.json = a copy of ~/MoonShots/data's, md5 3098a505..., same pool
    bytes) -> B c45o_224 (default) -> K c45k_224 (default + Leap's K-73 exact-safe kernel stack + R-74 shared_cat + R-76
    draft_fused (drafter), K73_EXACT=1: its every-token check, Leap cancelled its runner 61) -> A2 c45_224r (A-L-B-K-A2:
    B in the middle, L and K next to it) -> P c45p_224 (prior, on OOO) -> c45o_300 / c45o_320 (Kamen's ~50 GB arms) ->
    c45o_272 / 256 / 240. Every arm only if NO-SWAP >= peak + 4 (the orchestrator's quiet rule; peak = 38.0 + 0.1325 per C
    unit over 224: needs 42 / 44 / 46 / 48 / 52 / 55 GB at C 224 / 240 / 256 / 272 / 300 / 320). Last nights' grants saw
    NO-SWAP 42-47 GB, so C 300 / 320 (and 272) most likely skip: told the orchestrator 15:37; Kamen 15:3x "No, skip
    the arms" (via the orchestrator): no stopping his sessions, no start below +4; they run only if the gate passes on
    its own, and the report's last line lists every skip / failure / pause from c45.log. A heat PAUSE between runs is waited out (10 min max). One run ~1.5-2.8 min + SSD
    cooling: up to 11 runs, ticket 50 (released when done). Report: .venv/bin/python scripts/c45_report.py (table +
    verdicts; per C to the orchestrator: tok/s, misses per kept token, lifetime peak). Pre-registered: OOO = B vs
    mean(A, A2) steady tok/s at C 224, tokens identical (the number for Kamen); L (MoonShots' lines) PASS = SSD MB per
    kept token (ri_diskio_bytesread over the loop, pooled) -10 % or more vs B with steady tok/s +3 % or more, KILL =
    bytes above -3 %, tokens identical (replay: -20.7 %; R-27 died at 24 GB, b36 -1.5 %, where JIT + JOINT covered it:
    the 45 GB preset has no JIT, so L tests that); if L passes, laysz45_256.json (copied too) is next; prior arm PASS =
    median misses per check -7 % or more vs B (c45o_224), tokens identical, steady tok/s not
    lower than B. Per check also: demand SSD busy (io_s), gate service on misses (slow_s, the GPU's spin bound) and
    draft ms (SSD idle): NewIdeas' SSD- vs compute-bound reading per C, and R-70D's window (S45-T at C 224: SSD 33-103
    ms = 34-52 % of the check, demand loads ~9-13 GB/s, draft ~9-17 ms). MoonShots M-14b: a 13-feature learned
    eviction key, -10.5 % held out vs LRU, only ~0.7 points past LRU + prior: not building it.
  - **R-69b PASS (Leap 07:4x, shared, C 160, rough; ~/Leap/data/r69b/)**: block hook + TIER_COMBINE + OOO: 7,479 OOO
    calls, every tier_call got post + scores at widths 1-16; tokens B == A1 == A2 == s45t_B gate+t on 4 prompts. Steady
    tok/s 36.4 / 36.6 -> 41.2 (+13 %), median cycle -11 %, misses and demand SSD unchanged (OOO hides the stall). Not BIG
    (rough, < 20 %); tonight's C45 turn runs C45_OOO=1 for the quiet number at C 224. Adoption into R57_PRESET=45 =
    NewIdeas' call (then the sizing runs carry OOO and keep a no-OOO control).
  - **KAMEN HOLD Sat 11:5x ("Hold it for now")**: no research runs and no locks until he lifts it; Kamen 16:28 "Yes, at
    01:00": it lifts Sun 01:00 (the orchestrator clears HOLD, PAUSE goes unless heat), then night big tests as usual; ~/.local/share/quiet/HOLD + PAUSE kept by hold_guard.sh: never clear them. Light work (reading, planning,
    writing code) is fine. R-52 DONE 07:48 before the hold (1d85640): BETWEEN, exact; PF_REUSE=1 8K TTFT -6.5 % at +0.18
    GB, =2 -10.3 % at +0.80 GB (line +0.1); NewIdeas decides. EvalSuite's R-56b passed the gate16 arm bit-exact at full
    length: R-55 adoption (MAXK 160 + ext/build rebuilt from the R-55 source) waits only on NewIdeas' word.
  - NEXT (daytime, shared GPU unless a speed verdict): R-52 24 GB TTFT (scripts/r52_runner.sh, quiet: a TTFT verdict;
    blocked at 07:13 by EvalSuite's lock), R-60 MTPDROP (24 GB shared screen; weights from MTP Head ~/TrainLab).
  - **R-60 MTPDROP (NewIdeas 23:1x, fast integration, exact: drafts only)**: MTP Head's D-22 head (EAGLE-3-style; code K15
    7.78 -> 9.83 tokens per pass in MTPLX's runtime, token-identical) into the 24 GB production stack. Replace ONLY the MTP
    layer's dense parts (fc_hidden, fc_embedding, attn q/k/v/o, router moe.gate, shared expert; 69.1M weights) in bf16
    (~138 MB) or 8-bit g64 (stock 4-bit keeps 12-33 % of the gain); keep MTPLX's MoE kernels + BIGMOE_MTP_STREAM's
    streamed routed experts (the trained router may shift the MTP layer's misses). Weights: ~/TrainLab (b3, or step 76
    ckpt/d22_base76 if b3's runtime verdict fails). Screen at 24 GB, shared GPU (rough): b44's prompts, tokens == the
    default, kept per check + tok/s, lifetime peak <= 24 GB. PASS tokens identical AND kept/check +3 % -> one quiet
    confirmation -> default on NewIdeas' word; KILL < +1 %. 45 GB items (S45-T, CAP45) stay first when memory allows.
  - NewIdeas' FAST INTEGRATION list: ~/NewIdeas/RANKED_45GB.md (exact-safe stack = gate + truncation + bigger C (+
    prefetch, switch); non-exact batch = REF2-T). Then the 24 GB TTFT screen (scripts/r52_runner.sh, committed).
  - R-52 24 GB screen CODED, untested, default off: tier.py BIGMOE_PF_REUSE=1 keeps _prefill_grouped's double buffers
    across layer calls (=2 also skips the per-call clear_cache); dropped at prefill_done / before a single-call scratch.
    Waits behind 45 GB work (TTFT-only lever, ~4-8 %).
  - Leap 20:2x lead (R-50 screen, ~/Leap/data/r50_screen.txt): _sync_call's fresh per-call scratch (9 x mx.take +
    concatenate, then clear_cache) costs ~8 ms per layer call on the 45 GB REF checks (~385 ms per 16-row check);
    a preallocated scratch reused across calls (same gather, same order) should stay exact. At 24 GB the checks run
    tier_call on pool slots (verify rows <= 8 x top-10 <= MAXK 80), so only PREFILL has the pattern (tier.prefill_call
    / _prefill_grouped: mx.zeros scratch per call or group + clear_cache). Parked as a prefill / TTFT lever (exact).
  - PF1 BUG FIX 7ac3192 (Leap R-40 3y): a lone call's unconsumed look-ahead stayed pending on a staging buffer that the
    next forward restaged for layer 0, so layer 2 ran on layer 0's experts (PF1 on + commit keep >= 5; shipped PF1 off).
    Leap screens it ('R-40 STEP 3y-fix' in ~/Leap/TABLE_350.md) after its R-21 + 3z; result comes to BigMoE.
    PASSED Thu 20:52 (Leap, on HEAD b8bd33c, C 128; ~/Leap/data/r40s3y_screen_fix.txt): after a commit keep 5 the next
    prefill is bit-equal to the reference (all 242 per-layer records + last logits; 228 differed before), no-commit /
    gated cases equal, safety-net restages 0 (the kick-time drop does the job).
  ON RESUME (only when the orchestrator relays Kamen's start): (1) re-create the 3-hourly health-review cron (fires :11
  every 3 h, i.e. 01:11 / 04:11 / ... / 22:11; prompt = the orchestrator's 'standing duty 2026-10-25' text, it starts
  "3-hourly laptop + research health review"); (2) usage-pace check; (3) R-44 (a) M-01 per the lines above, then (b)
  POM at R2 4; keep M-01's SSD / CPU out of Leap's REF2 + SB A/B quiet locks (Leap step 3x diagnostic, its runner 16).
  Also check (NewIdeas 01:4x, Fit12 R-45): mtplx frspec_draft._full_vocab_head defines a class per call, so each request
  leaves its pruned head (~0.095 GB) in a GC cycle until a gen-2 collection; if the 24 GB engine builds that head per
  request (BIGMOE_FRSPEC=1), multi-prompt lifetime footprints creep; gc.collect() between requests bounds it (exact).
  QUEUED LATER (NewIdeas ~22:35, pricing only, after b39 / R-38 / the R-16 overlap screen): what would v3 at a 45 GB
  budget with Leap's DFlash2 drafter + 16-row checks take, and could Leap's exact-16 hand-off (~/Leap/HANDOFF_EXACT16.md:
  S4 HC read + D2 split-K + SB, bitwise, -26.5 / -30.9 ms per 48-layer check) + DFL2E's variable-row rule (R-35) live
  there? Rough hours and risks. (For v3 at 24 GB the hand-off is LOW: SSD-capped, and AdaptiveWidth verifies 2-7 rows.)

## 10-23 14:50 KAMEN: ONLY TWO FOCUSES — the 350 tok/s breakthrough and the <12 GB model. 24 GB-only work STOPS.
- Wait idle for NewIdeas' hand-off (B12/B8 run on this v3 engine; the 350 line needs wide verify passes + kernels).
- Fast mode (FM1, b16 + JIT, scripts/fast24.py pinned 36c9cc5): Eval suite run 1 = 5/5 vs v3 natural; its run 2 runs
  only when the two focuses leave the GPU free. Uncommitted here (LEDGER FM1 rows, scripts/b24_runner.sh, this note):
  commit once the Eval suite no longer needs HEAD = 36c9cc5 (or when a focus task needs a commit).
- MoonShots reports B12L diverging under GPU load and is bitwise-testing tier_glu (3c): if 3c is load-dependent, that is
  an engine bug here too (check its result).

## 10-21 evening state
- H50 (LEDGER): full stack at 0.50 fits ~41-42 GB whole process; v3+GDN code 65 / edit 86 / prose 40 tok/s (96 tok).
  Exact GDN adopted: BIGMOE_GDN_EXACT=1 (bitwise, +1-4 %), add it to both stacks. CL1: sidecar size flat, keep default.
- KAMEN 21:50: THE MAIN TRACK IS THE 24 GB SETTING (0.25). 0.50 runs were tests only: no more GPU time on 0.50.
- b13 queued (overnight lock ticket from the session, then `HAVE_LOCK=1 CLAUDE_PID=$CLAUDE_PID nohup bash
  scripts/b13_runner.sh &`): 0.25 at 256 tokens, exact RECORDS=3 vs exact via plane pools (±OoO) vs v3 (±OoO).
- Next levers: exact mode's RECORDS=3 cost (GPU rebuild into pools / exact via plane pools at equal slots), OoO at
  S=1, AW1 policy defaults, PF_CORR_FUSE, records4 / 2-bit tiers with MoonShots, tier-mode lmp4pd long prefill.

## 3-BIT TIER BUILD — DONE 10-21 16:05 (V3 validated; DESIGN_3bit.md, LEDGER B3a..V3, OOO1)
- Engine: bigmoe/tier.py (MSB-3 base + LSB-1 sidecar pools, rank-sorted block, compact-scratch exact prefill, 3b/3c,
  fused combine, OoO); ext: records3 parts + CPU rebuild (rec_fmt 3, serial per job on wide miss lists), read_rebuilt,
  post_ids partial-hit row. Tests: scripts/test_records3.py, test_tier.py; SpecDecode scripts/guard_sim.py.
- Runners b3..b10 (data/b*/). GSM harness scripts/gsm_v3.py (data/v3/gsm_v3b_4433333333.json).
- Open: exact mode's −10–13 % on RECORDS=3 (CPU rebuild): try a GPU rebuild into the pools or make exact-via-plane-pools
  (4444444444) the default once it is faster at equal bytes; tier-mode lmp4pd (long-prompt layer-major prefill) not
  wired (chunk-major used); C_l sweep 32/48/64; records4 / 2-bit tiers (MoonShots); exact GDN conv+norm (~1.5 %);
  AW1 + PF_CORR_FUSE integration.

## Running now / open (2026-10-20 ~14:15)
- DETACHED: scripts/segtest_runner.sh (pid via `pgrep -fl BigMoE/scripts/segtest_runner`), queued for the quiet lock
  since 13:35 behind the Eval suite. It re-tests BIGMOE_PF_SEG=64 (now gated to calls where the reference itself takes
  gather_qmm_rhs: ids.size >= 16 and >= 4·uniq) on prose / code / edit at 0.25/96 + a 24 GB-mode memory probe.
  Output: data/night2/segtest.txt (the LAST 3 prose/code/edit blocks after "13:35:08 segtest start" in segtest.log).
  PASS = prose efab73b6f6, code 8c56402b7f, edit cd4289b64d. If PASS: add BIGMOE_PF_SEG=64 to the exact 24 GB mode
  (HANDOVER stack + LEDGER row M24f), and re-measure its prefill peak (should be ~1.9 GB under the 23.5 GB now).
  If prose still differs: PF_SEG stays v2; note it in M24f.
- Pending merges (fork patches, exact, from MoEPrefetch): split-phase MoE (BIGMOE_SPLIT, +3–5 % at 50 %) and learned
  look-ahead correction (BIGMOE_PF_CORR, +2.9 % ar at C=128) — ~/MoEPrefetch/fork/apply_split.py, apply_corr.py.
- Last RESULT sent to the orchestrator 10:50 (STK4/LC1v/M24d/AW1); next RESULT after PF_SEG settles.
- Usage: 5 h window resets ~17:10; weekly ~64 % (research stops at 85 %). Always pass --weekly to usage-pace.

## Next: exact expert-subset prefill ("segment calls", PrefillKernels design 2026-10-20) — replaces PF_GROUP
In _sync_call (sync prefill path), per chunk and layer:
1. Reference sort once: fl = inds.flatten(); order = argsort(fl); sid = fl[order]; xs = x_flat[order // k];
   cut sid into expert segments (contiguous since sorted).
2. Groups of consecutive experts with scratch <= ~0.3 GB: slice [a, b) of xs/sid, remap ids to 0..G-1 (order-preserving),
   call mx.gather_qmm(xs[a:b], W_scratch, ..., rhs_indices=..., transpose=True, sorted_indices=True) DIRECTLY
   (not SwitchGLU: its indices.size >= 64 do_sort threshold sends small groups to the unsorted gather_qmv path —
   the likely cause of PF_GROUP's prose miss).
3. Pad each call's rows (x = 0, id = the group's LAST expert id, appended at the end so rows stay sorted under sorted_indices=True) to a multiple of 64 AND to >= max(16, 4G) rows, so the call
   stays on gather_qmm_rhs (needs B >= 16, B/G >= 4) and avoids BUG1 (unaligned bm 64).
4. gate, up, swiglu, down per group the same way; write rows into one full y_sorted [k*T, D] at a..b; drop pad; then the
   reference tail y = y_sorted[inv_order] (SwitchGLU returns per-(row, slot) outputs; the model does the combine).
First a one-layer bitwise test (y_sorted vs SwitchGLU's) before a model run; then prose/code/edit shas at 0.25/96
(efab73b6f6 / 8c56402b7f / cd4289b64d).

## Next (day plan)
1. Read the batch results; one combined RESULT.
2. Spec policy: SpecDecode adaptive width (AW1) beats plain on all kinds at C=128; use it in the integrated stack.
3. MTP depth per prompt kind (MoonShots: 3–4 best; prose loses at 4).
4. Prefix checkpoints, expert-ordered prefill, gate commit change (orchestrator's day plan).
5. vm_stat decompression check during decode; deeper read queue with MoEPrefetch (B=8 best so far;
   MoEPrefetch's BIGMOE_PF_CORR look-ahead correction: io −20 %, identical).
6. Kernel-probe self-test (exactness band is M5-specific).
