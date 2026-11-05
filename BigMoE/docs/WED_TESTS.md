# Wednesday 4 Nov: BigMoE's test list for Kamen's research day (13:45-23:30)

BigMoE, lead of the WALL 1 SPRINT, Tue 3 Nov ~22:3x. Everything below is built and unit-tested tonight; none of it needs
code written during the day. Exact = every token equal to the stored REF2-T tokens. Times include model loads.

## Already running tonight (results ready by ~05:00, read in the morning)

One quiet ticket at C 160 (data/s160/night.log):
- the wall-1 sprint:
  - JOINT on / off, traced (the first scoreboard row: SSD busy, exposed SSD, calls per check);
  - keepalive A-B-A-B;
  - the volatile expert cache smoke;
  - the pre-route capture (lever 2's recall; INVALID, it read the attention side: re-run = 3b);
  - the chat-switch checks;
- U3: CRASHED at start 01:02 (u3n rc 1: the LP1 patch imported tierglu before the TIER_GLU loader put MoonShots'
  planes_engine on sys.path; u3c, the control, ran). Fixed in scripts/r57_screen.py (U3C had the same bug); re-run = 5a;
- the combination's exact levers at C 160 (each lever's own delta, tokens checked);
- the prefill-warm mission.

Morning reports:
- stall_report.py and s0_report.py on c45t_160 / c45tj_160 (S0's zero-hit split: is the late routing post real?);
- pr_report, combo_report, the U3 and vtier lines.
- DONE Wed 03:14: docs/NIGHT_1104.md (scoreboard row, every line, next steps).
- JOINT (S1) rechecked Wed 04:1x (orchestrator): KILL at C 160 by its line, not a build or flag problem. JOINT issued
  45 % of sidecar reads early. Overlap-merged bursts went 76.5 -> 68.1 per check, the layer read span was unchanged
  (2.486 -> 2.489 ms), and without JOINT the sidecar already starts 17 us after the base. stall_report.py now prints a
  'JOINT read' line; in item 2 keep JOINT in the stack only if w1tj / w1tp move the layer span (POST_SYS may raise the
  pairing).

## Wednesday morning, before 13:40 (CPU / builds, no GPU)

- The stale-slot check ran FIRST in tonight's chain: PASS 00:34 (data/sc/sc.log; all three pairs, tokens + 127 logits
  hashes equal with vs without the command-buffer boundary). No item 0b.
- The conversion format becomes "native+p11+pad" (agreed with Leap 22:4x on MoonShots' M-29):
  - MSB s3 / b3 padded to 36,864 B; LSB l1 planes first, b packed; msb_sz / lsb_sz / recsz unchanged.
  - Leap: kernel stride from the pool shape + the tool's layout.
  - BigMoE:
    - r3layout_ref.py "native+p11+pad" + regenerate the scratch copies for Leap's cmp;
    - tier.py builds the sidecar pool pieces in record order;
    - the direct path for aligned pieces with the b tail copied;
    - test_layout / test_layout_engine on the new copies.
- U3C is built (0ea5b8b). Its first run also writes the mask dump for Breakthrough (R57_U3C_DUMP, 3 prompts).
- **5b NARROWED (Breakthrough Wed 07:26, FLOOR's 42 held-out windows, SCOREBOARD 45fb226): the per-request table is
  CODE+, not GENERAL.** pmtc (the form built in 0ea5b8b) vs the u8+t3 live control: multi 6.70 vs 5.66 % (z +2.78, a
  cost); IFEval z +0.92 and code z -1.88 show none. len (warm = the prompt's footprint alone, only when the prompt has
  >= 128 tokens) holds on code: 0.81 vs 1.11 %, at cached bytes x0.196 vs x0.272 (-28 %) [P, 45 GB plain-LRU replay].
  So 5b = U3C in len's form on code requests only; chat keeps plain U3. No engine change is needed for the test:
  R57_FAST=U3C + R57_U3C_LEN=1 exist (0ea5b8b) and 5b runs code prompts only (scripts/u3c_wed.sh, e947f23; Breakthrough
  07:3x: "the line is fine as written"). Breakthrough's mask check (dm_u3c_replay.py) now also checks warm against the
  length rule: prompts >= 128 tokens must hold the footprint alone, < 128 the footprint + cap45 table; the dump's
  prompt_len is len(ids), the same count the rule uses in run(). DEPLOYMENT CAVEAT (Breakthrough 07:3x): code-only
  needs a request-level switch in the engine (the screen knows the domain from the prompt key, a server would not);
  until one exists, U3C is an opt-in mode for code requests, which is what 5b measures.

## The day's tests, in order (GPU: one quiet lock per block)

**PULLED FORWARD TO THE MORNING (the orchestrator Wed 06:2x: the GPU is BigMoE's from ~08:30, after FLOOR and
Breakthrough's map batch, to 12:50; Kamen wants the tests done and prepared before 13:45).** scripts/morning_1104.sh,
started on Breakthrough's "map batch done" (log data/morning_1104.log):
- A (quiet, C 160): 3b scripts/pr2_run.sh, then 5a scripts/u3_smoke.sh. 5a's fresh u3c re-checks item 3's 10 HumanEval at
  full length.
- 0 (~09:00, CPU): scripts/item0_live.sh. Fit12 06:2x: YES, its 13:05 runs load neither ~/BigMoE/bigmoe nor
  ~/BigMoE/ext/build; they need the .venv and models/bare unchanged until ~13:55, and nothing here touches either.
- B (quiet): 1 scripts/w1b_24.sh (build_m01 rebuilt 06:23 from the current source), then 2 scripts/w1_lever1.sh (C 224 if
  NO-SWAP >= 44).
- C (quiet, needs 0): 4 scripts/mix_e2e.sh, then 5 scripts/default45_wed.sh.
- Every runner stops starting arms at 12:30 (the orchestrator 07:2x: every arm must END by ~12:55; Fit12's T3R2 goes quiet
  at 13:05, hard stop 13:40, no slack).
- STARTED 07:28 (Breakthrough's "map batch done" 07:26; FLOOR night 1 ended 07:06), so item 0 runs at ~07:4x, after A.
- **3b DONE 07:31 (151 s, lifetime peak 29.4 GB): BETWEEN.** Per-row recall@10: p3 0.789, p6 0.792; full 0.794, R-57
  0.634, fullA 0.565 (== pr_160's full, as required). All 18 prompts' tokens == pr_160's. The partial reads lose almost
  nothing against the full read at L+1's start; the gap to 1 is L+1's own attention write. MTP Head's SAMELAYER-T rows:
  data/r57/pr_dump/pr2_160_00..17.npz (2.4 GB; X = L+1's MLP-side read at its start, Y = its true MoE input; sent 07:3x).
  Report: data/r57/pr2_160_preroute.txt.
- **5a PASS (07:40):** u3n == u3c on all 12 prompts (the copied OOO path is exact); u3 ran (93 s). One 282 s heat pause
  inside u3n (fanwatch at the 6000 cap) put one prompt at 0.8 tok/s: the item 5 / 5b reports now leave paused runs untimed.
  Item 3's second check (fresh u3c_160 vs data/ab/ref_tokens.json, 12 keys, full length): ALL EQUAL.
- **Item 0 LIVE 07:51 (d0030a1):** the 07:41 try tested on build_nat, which lacks set_direct_split (the patched tier.py's
  native+p11+pad path needs it) -> rc 3, files restored; item0_live.sh now tests on build_w1. ext/build sha256
  5333899cb514 (byte-identical to build_w1 and build_m01), Leap 7f43a3f; EvalSuite told.
- **Item 1 (07:56): W1B 24 GB = 33.2 tok/s mean, 383.8 SSD MB per token, lifetime footprint 23.86 GB; w24 == w24t.** The
  07:42 try crashed at the 12-token warm-up: tier.py's block (01f652c, 11-01) took 9-16-row calls that the 24 GB stack's
  MAXK 80 sends to the sync prefill path (per-expert output under TIER_COMBINE). Fixed in da8e7a6 (such calls take the
  stock block, as before 11-01; nothing that worked changes). vs REF2-T: 3 of 6 equal (HumanEval 68 / 91, algebra 1282);
  prealgebra 1640, algebra 694, gsm8k 708 differ, not because of the fix (their prefills are single >= 50-row calls):
  expected: REF2-T is the 45 GB reference only; the 24 GB line keeps its own stock-kernel reference (w24 == w24t PASS).
- **Item 2 (07:50): lever 1 BETWEEN by its line.** All 8 arms exact (6 / 6 == REF2-T each); steady tok/s (geo) w1u 60.3 ->
  w1uf 65.7 (+9.0 %, C 224); but the fixed part per check 19.2 -> 19.5 ms (line <= 10; data/w1/stall_w1t_vs_w1tp.txt):
  the stall falls 4.1 ms per check, not the issue / first-byte / wake cost the lever targets. JOINT's step line: KILL
  (busy -2.4 ms, needs <= -8). Traced steps (cumulative, single pass): JOINT +1.6 %, keepalive +2.7 %, copy split
  +0.5 %, coherent spin +1.9 %, system post -0.6 %.
- **Item 4 (08:05): PASS.** mix (layers 0 / 20 / 47 converted, native+p11+pad) == mixc (the live package on the new
  ext/build) on all 11 prompts, and both == REF2-T on every token (vs ref14, data/ab/ref_tokens.json and 5a's u3c_160).
  The script printed "every token equal False" only because its reference fell back to chat23, which has no
  HumanEval/16 or /6 ("REFTOK 0 / 1"); mix_e2e.sh now uses ref14. So the converted path is exact end to end, and the
  rebuilt ext/build + the layout patch + the tier fix keep the 45 GB route exact.
- **Item 5 (08:05-08:32, C 160: NO-SWAP 48 < 52): ADOPT + lever 1 ADD -> ADOPTED as R57_PRESET=45 (0365ada, 08:35).**
  A-B-C-C-B-A, all six arms 14 / 14 == REF2-T, no heat pauses (data/d45/d45_report.txt). dfb vs dfa (the night's levers:
  chat switch, keepalive 50 us, volatile tier 64/32, K-83): steady +12.1 % geo (chat +17.3, code +12.4, math +12.8,
  agent +0.5; worst prompt agent/bash18 -4.5 %, best multi/zh15 +29.4 %); SSD MB per kept token 172.5 -> 120.2;
  lifetime footprint 31.8 -> 33.6 GB. dfc vs dfb (lever 1's full stack: JOINT, copy split, coherent spin, system post):
  +6.4 % (code +11.7, math +5.4, chat +3.8, agent +3.2). Geo tok/s per arm: dfa 35.7 / dfa2 36.1, dfb 39.5 / dfb2 40.9,
  dfc 42.9 / dfc2 42.7: ~+19 % together. R57_D45=0 = the 11-02 default. NOT yet measured at C 256 (the 45 GB default's
  C, 41.7 GB lifetime on 11-02; +1.8 GB here at C 160 -> ~43.5 GB expected): first free quiet slot.
- **5b PASS (08:48-08:57, C 224, after Breakthrough's screen 4; on the new R57_PRESET=45):** U3C len vs U3 on 12 HumanEval,
  A-B-A-B: SSD MB per kept token x0.732 (geo; per prompt x0.56-0.91), steady tok/s +3.7 % (per prompt -5.5..+15.5 %),
  kept per check x0.977; no heat pauses. Absolute geo steady: U3 106.4 / 105.7 tok/s at 20.5 MB per kept; U3C 110.1 /
  110.0 at 15.0 MB; lifetime peak 39.4 GB. The u3n2 gate (U3's null control on the rebuilt ext/build + the new default)
  == 5a's u3c_160 (REF2-T) on all 12: 83.1 tok/s, an EXACT number for the new default on code at C 224 (the old default
  at C 160 this morning: 49.8). Dump for Breakthrough's mask check: data/u3c/dump_224/ (HumanEval 16 / 68 / 91; sent).
  U3C MASK CHECK PASS (Breakthrough 08:5x, dm_u3c_replay.py on dump_224: 1,248 records bitwise == the rule; warm follows
  the length rule: 16 = the < 128 fallback with the cap45 table, 68 / 91 footprint only) -> cleared for EvalSuite same-
  scores on code. FAST: those decide adoption; code-only needs a request-level switch before it ships.
- **The new default at C 224 (09:49-10:10, after the 09:15 C 256 try swapped +2.3 GB by day): BETWEEN.** All 4 arms
  14 / 14 == REF2-T. new vs old +7.2 % geo steady (51.0 vs 47.1 tok/s; lifetime 42.1 vs 40.3 GB); code +7.4, chat +12.6,
  math +11.1, agent -9.9 % (bash18 -16.6 %, 9.7K-token prompt). W1B's six: 64.9 vs 60.9. The default stays (pre-registered
  rule); per-lever agent arms + the C 256 headline go to tonight (data/d256/d256_report.txt).
- **Agent leave-one-out by day (13:49-14:02, C 224, in a test window): CUT by the 2 GB swap rule in arm 2, no verdict.**
  old (aold): 5 / 5 agent prompts, 28.7 tok/s geo steady (bash18 24.1, text23 36.0, bash20 27.8, edit03 45.1, write12
  17.8), 444 s per arm (not ~3 min), lifetime peak 40.4 GB, swap +0.32 GB. new (anew) finished bash18, text23 and bash20
  (bash20 24.6 vs 27.8 steady), then swap passed +2 GB from the run's start (10.01 -> 12.13 GB; NO-SWAP 51 GB at its
  start; lifetime peak 42.2 GB plus the 7.8 GB purgeable volatile tier): SWAP GUARD. The report now says INCOMPLETE when
  arms are missing (it printed INTERACTION) and prints swap per arm; the RAM levers run first (-vtier, -chat, -lever1,
  -K83, -keepalive). The full run goes to Thu ~06:40 with apps closed (scripts/night_thu.sh, ~95 min). data/aloo/.
- **K-83's drafter row fallback as the agent cause (MTP Head's DRAFT17 lead): does not fire here.** R57_ROWS is unset, so
  every block is 16 rows (aold's 308 agent checks max 16 rows; Leap's 05fafe7 changes nothing at 16). Drafter ms per
  check FELL under the new default (agent 12.5 -> 11.4, code / math 11.6 -> 10.3; data/r57/d256*_224_checks.json). The
  agent cost sits in the check's SSD service: bash18 per check misses 246 -> 251, SSD MB 417 -> 341-362, I/O 56 -> 63-71
  ms, check 110 -> 118-124 ms (HumanEval/68 the same shape: I/O 127 -> 134-142 ms). Fewer bytes, slower service per miss:
  the volatile tier / keepalive / lever 1's I/O path, which the Thu leave-one-out tests first.
- **Next 45 GB slot after Thu's (pre-registered Wed 14:2x-15:1x, ~32 min quiet, MEM ~44 GB, all at C 224, 14 prompts):**
  plain / DENSE-N / HC8 / HC8 / DENSE-N / plain. DENSE-N = Leap's ref2.dense_native_convert(model) (2190e10: 4-bit dense
  weights with N >= 1024 replaced in place by the native layout, one copy, exact by construction): ADOPT into the exact
  default if >= +1 % geo steady AND every token == REF2-T. HC8 = Leap's hc8r.hc8_install(model) + REF2_HC8_FAST=1
  (c805fd0: 8-bit trunk hyper-connection mixers read in one pass, -0.6 GB; FAST, tokens differ): KEEP for the FAST track
  if >= +2 % geo steady with no domain < -3 %, then EvalSuite same-scores decides; else KILL.
- **Lever 2, stage 1 BUILT (Wed 14:5x-15:0x, e8b7b6d; BUILD_DAY #2): forecast reads into the volatile tier.** Today's
  default posts L+1's forecast (PF_B 96, ranked list <= 61) but issued no reads (no spare or victim slots; R-57's victim
  prefetch was KILLED: wrong guesses evicted needed experts). Now, right after L's release, the loader reads the first
  F = 4 ids of that list that are neither resident nor tiered (FS = 2 for the sidecar) as whole records INTO THE PURGEABLE
  VOLATILE TIER (one GCD block each, trace tag 3): the GPU never reads the tier, so a wrong guess evicts nothing; a demand
  miss found there is copied back (waiting for a read in flight). CPU test scripts/test_fc_tier.py PASS on records3 and on
  the converted layer, direct reads on and off (32 loads, every piece == plain demand loads; in-flight, pressure, skip and
  purge cases); test_layout_engine.py PASS on ext/build_l2. Slot (scripts/l2_wed.sh, C 160 by day, ~25-30 min): smoke,
  then l2c / l2f / l2f2 / l2c2 (14 prompts) + traced l2ct / l2ft (W1B's six). Line (pre-registered ~15:0x, before any run):
  KEEP if every token == REF2-T AND stall per check <= -20 % AND >= +3 % geo steady; KILL if < +1 % or the next-demand
  penalty > 0.05 ms per burst; else BETWEEN. Stage 2 = SAMELAYER-T's trained forecast (weights asked of MTP Head).
> (a quote from the project owner, kept private)
  r57_screen switches R57_HC8 (Leap's hc8r.hc8_install + ref2 hc8_fast, v4), R57_DNR (ref2.dense_native_convert) and
  R57_HCB (ref2 hc_b), each off unless set. scripts/allin_wed.sh at C 224 on the 12 HumanEval, all arms on ext/build_l2:
  u3c (U3C len) / allin (+ D7b code drafter + HC8 + DENSE-N-RAM + hc_b) / allinf (allin + lever 2) / allin2 / u3c2, then a
  dump arm for one map screen. No pass line: the combined FAST number today's builds reach, and the cycle's parts per check
  (check, draft, SSD I/O, gate service, build) for the list toward ~50 ms per check. QOM at 45 GB is not in (not cheap to
  wire). Runs behind lever 2's slot when memory allows (Chrome holds 13 GB by day), else Thu ~13:10.
- **QOM IN THE ENGINE (FAST, Wed 15:0x-15:5x; 5bb2743 + c387c97, ext/build_qom; R57_FAST=QOM):** Breakthrough's keep-set
  rule (~/Breakthrough/keepset 6f1ca44, read-only) on U3 at thr 0: a sure row's rank 2-9 expert outside the check's loads
  is posted with bit 21 (optional); the loader never reads it on a miss (slot -2), qom_keep_mx keeps the resident ones after
  the spin, a dropped use reads the row's rank-0 slot at weight 0. CPU test scripts/test_qom_ext.py PASS. DRAFT17
  (R57_D17=1, 723ee9b, MTP Head's draft17.py): a 17-position draft gates the last row too (smoke: 78 / 78 rows gated).
- **By-day FAST numbers (shared GPU, apps open, single pass: a lead, not a verdict).** C 96 / C 128 runs were INVALID: a
  16-row check (160 ids) takes the sync-free FAST path only when it fits the pool (C >= 160 per layer), so at C 128 every
  check ran ref2's host-synced _tier_slots (no OOO, no 3-bit sure rows, no QOM). At C 160 uniform pools (R57_LAYSZ=0,
  C_l 64; data/bdq/bdq_report.txt), 12 HumanEval: U3C 66.9 tok/s (33.8 SSD MB per kept, check 116.5 ms); QOM 67.3
  (24.8 MB per kept = x0.734; 747K optional uses, 153K misses never read; its drafter ms rose 11.9 -> 15.7: GPU
  contention); QOM ALL-IN (+ D7b code + HC8 v4 + DENSE-N-RAM + hc_b) 85.8 tok/s = +26.3 % vs U3C, check 100.2 ms.
  Lever 2 read nothing in the earlier FAST arm: only arm gate+t+pf posts L+1's forecast (and needs BIGMOE_PRED_LINES=4).
  Smoke 2 (data/smk): the exact default with lever 2 on, 2 prompts: every token == REF2-T (32 / 32 each), 2,538
  forecast reads, 1,192 used; the QOM all-in + lever 2 runs. Tonight 23:00 (if the apps close): QOM-based all-in at C 224
  (u3c / qall / qallf / qall2 / u3c2) then lever 2 at C 160.
- **5b after the morning block, if it ends before 12:00:** scripts/u3c_wed.sh (U3C len on code vs U3, A-B-A-B, plus the
  u3n2 gate on today's ext/build and the mask-check dump; line in its header).
- **Item 3 is DONE on CPU (06:22):** data/ab/ref_tokens.json = chat23's 30 + the night's u3c_160 (CAP 256, REF2-T) for the
  10 HumanEval; chat23 == u3c_160 on /68 and /91, and u3c_160 == pr_160 on the first 128 of all 10
  (data/ab/ref_tokens.README.txt).
- **Item 5 defined (06:5x):** see the row below.

| # | When | Test | Why | Time | Memory | Line |
|---|---|---|---|---|---|---|
| 0 | 13:40 (Breakthrough's layout check PASSED Wed 03:28: go), after Fit12's T3R2 and before 1 (nothing may import bigmoe/ while it changes) | **conversion: bigmoe/ patch live + ext/build rebuilt; ext/build_m01 rebuilt too** (CPU, 10 min; build_m01 for item 1:
b48's stale-ext guard refuses a .so older than the source), commit + .so sha to EvalSuite | Thursday's conversion; EvalSuite's ifx checks need the snapshot | 10 min | - | test_layout_engine.py on the live package PASS |
| 1 | 13:45 | **W1B 24 GB baseline** (scripts/w1b_24.sh): today's shipped exact 24 GB stack (s10b, C 128, M-01, JOINT) on W1B's six prompts (S10B_KEYS), untraced + traced | the sprint's 24 GB row; the 1.5x target needs it | ~15 min | <= 24 GB | measurement |
| 2 | right after 1 | **Lever 1 at 45 GB** (scripts/w1_lever1.sh; frozen copies r57_screen_w1.py / c45_runner_w1.sh made at arming) (C 224 if NO-SWAP >= 44, else C 160), traced, then the winner untraced: default / + JOINT / + JOINT + keepalive / + direct reads into the slots (BIGMOE_RECORDS_DIRECT, no bounce copy) / + coherent one-row spin (BIGMOE_SPIN_COHERENT) / + system-scope routing post (BIGMOE_POST_SYS), on ext/build_w1 | wall 1's per-call overhead (~20 ms of a 97 ms check) | ~50 min | C 224: ~44 GB / C 160: ~33 GB | exact AND fixed part <= 10 ms per check AND steady >= +5 % = PASS; < +1 % = KILL. Per step: JOINT busy <= -8 ms; keepalive d -0.04 ms; pickup: cadence a - burst a falls >= 0.03 ms |
| 3 | any shared slot before the A/B night (exactness only) | **the A/B night's reference**: REF2-T tokens of the 10 extra HumanEval (16, 6, 79, 19, 161, 17, 56, 141, 101, 63) at CAP 256, merged with chat23's 30 into data/ab/ref_tokens.json (found missing Wed 03:1x; ab_records3.sh STOPs without it) | the A/B night's every-token check | ~12 min | ~33 GB (C 160) | the 10 runs agree with tonight's pr_160 / u3c_160 tokens on their first 128 |
| 3b | with 3 (same shared slot), or any earlier gap the orchestrator gives (no map process running) | **the pre-route re-run with the fixed read** (scripts/pr2_run.sh; added Wed 05:5x): pr_160's 18 prompts, CAP 128, C 160, R57_PREROUTE=1 + R57_PR_DUMP=1. The night's KILL is withdrawn: its full / p3 / p6 were L+1's attention-side read (MTP Head's catch); "fullA" keeps that read as the control | lever 2's real recall; MTP Head's SAMELAYER-T rows (~2.5 GB in data/r57/pr_dump) with no separate capture | ~4 min | ~30 GB (C 160) | unchanged: PASS p3 >= 0.85 AND p6 >= 0.90 per row; KILL p3 < 0.75; else BETWEEN. Every token == pr_160's, and fullA within 0.01 of pr_160's full (0.565), else look first. MTP Head predicts all 0.76-0.81 (BETWEEN) |
| 4 | after 2 | **conversion end-to-end on scratch/model_mix** (layers 0 / 20 / 47 native+p11, the rest row-major; scripts/mix_e2e.sh at C 160) | the converted path (Leap's router + p11 kernels + my prefill reader) exact end to end, before any byte of records3 changes | ~20 min | ~33 GB | every token == stored REF2-T on 11 prompts = PASS; any difference = no conversion until found |
| 5 | after 4 | **the combined exact default** (scripts/default45_wed.sh, defined Wed 06:5x): A-B-A-B dfa / dfb / dfa2 / dfb2 on W1B + the combination's prompts (14), CAP 256, C 224 if NO-SWAP >= 52 else 160; dfb = the default + the chat switch + keepalive 50 us + vtier 64/32 + K-83 (+ lever 1's winner via D45_W1). Left out by the night: chat 8 rows, t 0.4, A6, COPYGATE, D7b, JOINT, 32 rows. ADOPT if every token == REF2-T AND geo-mean steady >= +3 % AND no domain < -3 %; KEEP the default if a token differs or < +1 %; the preset is edited by hand | the integrator's Thu 15:00 deliverable, one exact 45 GB default | ~25 min | as 2 | exact; the new default's steady tok/s vs 63.6 (C 256) or tonight's C 160 baseline |
| 5a | after 5, before 5b | **U3 smoke re-run** (scripts/u3_smoke.sh at C 160, fresh frozen copies; tonight's run crashed at start on the tierglu sys.path bug, fixed Wed 01:4x) | U3 and U3C (5b) need the copied OOO path exact first | ~6 min | as 2 | u3n == u3c token for token = PASS (then u3's FAST numbers count); any difference = U3 / U3C stop until found |
| 5b | after 5 | **Breakthrough's P1: the per-request COLD table on top of U3** (FAST; spec ~/Breakthrough/WED_PLAN.md P1, b800a4b): on drafter-unsure rows keep ranks 0-3 plus ranks 4-9 that are warm for this request (its prefill routed to them, or prior45 share >= 0.05) or in the check's union; sure rows = U3. BigMoE builds it as R57_FAST=U3C in r57_screen (Wed morning); Breakthrough checks the kept masks against its map (36 windows) from a routing dump | replay: -27 / -36 / -38 % SSD bytes vs U3 on code / IFEval / multi (halved -14..-25 %); quality = u8+t3's, so EvalSuite's task results decide | ~25 min (U3 vs U3C, R57 prompts) | as 2 | pre-registered (orchestrator / Breakthrough): chat SSD MB per kept token <= 0.85x U3's AND tok/s >= U3's = PASS; then EvalSuite same-scores |
| 6 | evening | **FAST preset** on the combined stack: EvalSuite's RELAX arms B + E / C + E, + NAX6 (+ hybrid) | the second track (quality judged by EvalSuite's same-scores tests) | ~30 min | as 2 | tok/s and kept per check; quality by EvalSuite after Thu's RELAX |
| 7 | when Leap asks | Leap's F1 (ref2 fatt_verify, 0002e2e): verify-call attention on fs4 | an exact-at-layer-level attention lever; EvalSuite certifies after RELAX | ~10 min | as 2 | Leap's line |

Notes:
- Order rule: 0 goes first, because 1-2 import bigmoe/ live and an A/B must not span two code versions. 1-2 then
  run on the patched engine, which is a no-op on today's store; their token checks confirm that. 1-2 need the GPU
  quiet. 4-6 need 0.
- If memory allows only C 160 by day (Kamen's apps open), every relative line still holds; the absolute 45 GB numbers
  wait for a night at C 224 / 256.
- Schedule (the orchestrator, Tue 22:3x): every batch test ends before Kamen arrives (FLOOR deadline 13:00, Fit12's T3R2
  13:05-13:40), and T0 moves out of his day. So the GPU is ours from 13:45: 0 (CPU, 13:40) -> 1 -> 2 -> 4 -> 5 -> 6, ~3 h of GPU in
  all (0 is CPU), leaving the rest of the day for what the results open up (lever 2's forecast reads, the next build).

## Thursday after RELAX_DONE + T0_DONE (unchanged)

EvalSuite's ifx check #1 (row-major, patched engine) -> heads-up -> scripts/convert_records3.sh -> EvalSuite's check #2.
Then Fri 00:30, the A/B (scripts/ab_records3.sh: B, B2, inverse, A, re-convert, B).

## Build queue after the day's tests (Kamen's decision 2 = YES, Tue 23:1x: a FAST mode may depend on the cache state)

QOM's engine path. Spec: NewIdeas QUEUE.md Tue 17:01. Sure rows (cf >= theta) keep ranks 0-1, union members, and rank
2-9 experts that are resident after the check's loads; would-be misses are dropped (weight 0). It needs:
- the loader: "optional" ids served only from committed residency, never loaded or taken from in-flight prefetches;
- the kernels: a drop sentinel = weight 0 (ask Leap);
- the harness: R57_FAST=QOM, default off, and a suite-format decode entry with per-row counters.
EvalSuite's four requirements (Tue 23:22) are met by that design. It certifies under >= 2 prompt orders at C 256 +
laysz45_256. The off path is checked first against REF2-T's stored rows (ifeval/3409, ifeval/2439, HumanEval/27).
Determinism (EvalSuite 23:3x, agreed):
- promotion only inside ensure(), never on read completion;
- look-ahead prefetch OFF in QOM mode;
- within a call: the non-optional loads in id order, then the optional ids judged against that state, the served ones
  touched in id order;
- self-test: the same key list twice in fresh processes, quiet vs beside a GPU + SSD load; the per-check served-optional
  set hashes (logged by the loader) and the tokens must be equal. The
theta per domain comes from the map verdict (scripts/qom_read.py -> data/QOM_read.txt).


## Wed 21:2x: the evening 45 GB slot vs memory (the early ticket did not run)

- The EARLY ticket (20:35-21:15, eve_early.sh) never queued: NO-SWAP (free + speculative + purgeable + file-backed)
  stayed at 41 GB, below its WAITMEM 44, from P-CAP's end to 21:15, with Kamen's apps open and Chrome closed.
  Stopped by hand; it had queued nothing (data/turn45.log).
- Lifetime peaks measured on earlier runs (data/r57/*_runs.json, mem[1]):
  - U3C on the 12 HumanEval: 30.9 GB at C 160, 39.4 at C 224. That is 0.134 GB per row, i.e. recsz x 48 layers.
  - The QOM all-in adds +0.3 (qalq 31.2).
  - Lever 2's forecast reads (FC_F 4) add +2.6 to +3.3 (qaf / qfx 33.5-33.6 against qs / qo1 30.2-30.9, on 2 prompts).
  - The biggest all-in arm (qallf) therefore peaks at about 34.8 + 0.134 (C - 160) GB, with 0.5 GB spare.
  - Under RULES (NO-SWAP >= peak + 4 under a quiet lock), C 224 needs 47.4 GB. The old 23:00 ticket's PEAK 40
    understated that.
- The 23:00-23:15 ticket now runs scripts/eve_2300b.sh. Every all-in arm runs at one C: the largest that fits at the grant
  (224 if NO-SWAP >= 47.4, 208 if >= 45.2, 192 if >= 43.1, else 176). The ratios (all-in vs U3C, relaxed, + lever 2)
  stay clean; the absolute tok/s at C < 224 is a lower bound for the 45 GB route. Lever 2 stays at C 160.
- The C 224 headline needs Kamen's apps closed (the night) or ~6 GB more free.
- Thu (the orchestrator 21:3x): the C 224 trio (u3ct / qallt / qallft, scripts/c224_thu.sh) is step 2 of the morning
  ticket (night_thu.sh: C 256 headline -> C 224 trio -> agent LOO cut at 09:00 so runner 42 starts by ~09:10).
- Thu (the orchestrator 21:5x): no new agent-LOO arm after 08:35, so the ticket touches q42/GO by ~08:45 (runner 42's
  original start); night_thu.sh also caps steps 1-2 at 08:10 / 08:30 for a late grant.
- Thu (the orchestrator 22:1x): Leap's DKV is installed in scripts/r57_screen.py behind R57_DKV=1 (+ R57_DKV_ADD=1), default
  off, loading a pinned copy (scripts/dkv.py = Leap 23919fb) by path; CPU smoke: hooks in, uninstall restores. Its token
  check (scripts/dkv_thu.sh: 14 ref14 prompts at C 224 vs REF2-T, plus the copy-free path count) is step 3 of the morning
  ticket, before the agent LOO (cut 08:35). Line (pre-registered): PASS = every token == REF2-T AND fast > 0 -> R57_PRESET=45
  after a same-run speed A/B; FAIL -> bisect DKV vs + ADD; VOID -> re-run.
- Wed 22:5x: the 23:00 ticket was cancelled before it queued: NO-SWAP 36 GB at 22:51 with no big job running (the many
  sessions' anonymous memory), below the 41 GB its smallest rung needed. The relaxed 0.5 arm and lever 2's exact stage 1 move
  to the Fri 00:30 night (with FAR-G1 and Rule C); the C 224 trio runs in the Thu 07:05 ticket.

## Thu 5 Nov morning ticket (07:38-08:15, memory-adaptive night_thu.sh): results

The ticket got its quiet lock at 07:38, after RELAX. NO-SWAP was 47.3 GB at the start. The runner 42 GO was touched at
08:14:53, ~30 min before the planned ~08:45.

1. **C 256 headline: SKIPPED.** Its arms need NO-SWAP >= 52.7 GB; there was 47.3.
2. **FAST trio at C 208:** the largest C where qallft fit. 12 HumanEval, order u3ct / qallt / qallft (data/c224t/c224t_report.txt).

   | arm | geo steady tok/s | kept per check | SSD MB per kept | lifetime peak | ck ms per check |
   |---|---|---|---|---|---|
   | u3ct (U3C len) | 102.9 | 10.54 | 20.4 | 37.3 GB | 86.4 |
   | qallt (QOM all-in) | 97.6 | 10.33 | 8.1 | 37.6 GB | 91.2 |
   | qallft (+ lever 2) | 93.4 | 10.33 | 51.5 | 43.4 GB | 96.4 |

   - Ratios: qallt vs u3ct -5.1 %; qallft vs qallt -4.3 % (lever 2's forecast reads: 76,957 issued, 9,010 used).
   - **Confounded, no verdict.** The arms ran in a fixed order with no control arm (the order control was in the cancelled
     Wed 23:00 run). The die warmed 60 -> 84 C under the 5,500 rpm quiet fan cap, and ck rose 86 -> 91 -> 96 ms in arm
     order, although the all-in's levers should lower ck. The byte figures stand: the all-in reads 0.40x U3C's SSD bytes
     per kept token.
   - The by-day C 160 result (all-in +26.3 % vs U3C) is not contradicted until an A-B-A run says so. The Fri relaxed-copy
     run gets u3c at both ends.
   - Memory: qallft peaked at 43.4 GB at C 208, above the ladder's 41.2 estimate. Forecast reads add ~5.8 GB over qall at
     C 208, not 2.6-3.3. The Fri ladder uses the measured value.
3. **DKV token check at C 224: PASS** (pre-registered). Tokens == REF2-T on 14 / 14 prompts; the copy-free path was taken
   1,345 times (slow 180, adopt 125). Next: a same-run speed A/B (on / off), then R57_PRESET=45.
4. **Agent LOO: INCOMPLETE** (2 of 9 arms).
   - aold ran 444 s, lifetime peak 40.3 GB.
   - anew ran 718 s, lifetime peak 42.1 GB, and included a 182 s heat freeze at 08:06.
   - The SWAP GUARD stopped -vtier at 08:14:50: swap grew 8.39 -> 10.51 GB since the LOO started.

## Thu 5 Nov 10:20-10:28: the records3 in-place conversion (done)
- Ran by hand after runner 42's GO: NAX6_DONE 'D4X: PASS', CHECK1_DONE 'check 1 rc 0 (10:20)', RELAX_DONE written 08:55,
  heads-up 08:54:24 (86 min before), BigMoE's quiet lock, nothing open in records3.
- The read-only check passed; md5 of the 48 row-major files (data/records3_md5_rowmajor.txt); converted in 370 s;
  md5 of the converted files (data/records3_md5_p11.txt); index check: 48 layers native+p11+pad with their rowmajor
  entries kept, and load_index refuses row-major readers. Log: data/conversion.log.
- Overlays: scratch/model_mix's index renamed .rowmajor-stale; the decision map's overlay (already renamed .STALE-... by its
  owner) still has its own index and must be re-indexed or deleted. Back: convert_records_p11.py --inverse with the
  row-major md5s.

## Fri 6 Nov 00:52-01:23: the palindrome run (data/fri/fri_report.txt)

The quiet lock came at 00:52 with 41 GB available, which gave the C 192 rung. The frx0 gate passed: the relaxed copy with
its flags off == REF2-T (2 prompts, 128 tokens). Every arm ran both passes on all 12 HumanEval. A heat freeze hit the
first half at 01:00-01:02 (162 s; it was not flagged PAUSED).

| arm | pair-mean geo steady tok/s | first / second pass | kept per check |
|---|---|---|---|
| u3c | 82.5 | 89.8 / 75.1 | 10.61 |
| qall | 86.8 | 88.3 / 85.3 | 10.05 |
| s99 | 81.3 | 71.9 / 90.7 | 10.10 |
| s90 | 89.1 | 85.8 / 92.2 | 10.14 |
| qallr | 87.9 | 98.5 / 75.0 | 11.04 |
| span | 78.5 | 88.9 / 67.8 | 11.10 |

### Verdicts

**Split (s99 / s90): VOID, not NOT PASS.** The all-in arms set REF2_OOO_1C. On that one-call path, Leap's ref2 applies
QOM's drop inside the kernel (ooo1c.a3c_one_call_qom; t["qom"] is popped) and never calls qom_keep_mx. The split plumbing
(R57_QOM_SPLIT) and the new group counters live in r57's two-phase _ooo_call_t3, which these arms do not use:
- the counters are 0 on every check;
- the strict rows (7.1 / 8.9 per check) are counted on the host only.

So s99 / s90 ran qall. Their -6.3 % / +2.7 % against qall measure tonight's noise floor between identical configs: about
+-6 %.

**Rule C: KILL** (pre-registered).
- s per task 1.167x; tokens per task 1.000x.
- Kept per check is +10.4 %, but tok/s is -9.5 %: the per-check host work (token decodes for the tagger and a sync per
  check) costs more than the extra kept tokens.

**Relaxed 0.5:** tok/s +1.3 % (inside the noise) at kept +9.9 %: the same per-check cost eats the gain.

**C3-R8: unresolved.** On this path 'uses' is the loader's posted count, before the drop: qall 2,812 vs exact 3,708 per
check (0.759x). Groups really computed need the counter inside the one-call path.

### Next
- Test the split on the two-phase path, where it works: qall / s99 / s90 with REF2_OOO_1C off. No new code is needed.
- Or have Leap move the split into the one-call kernel's keep flags.
