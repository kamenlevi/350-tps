# Tue 10 Nov afternoon tests: 36 GB Mac simulation, PF-A at 24 GB, PF-B length bisect (13:46-14:02)

> (a quote from the project owner, kept private)
after BigMoE's W24g, one at a time, under one share lock, with a +2 GB swap guard. Evidence and scripts are in
data/tue_afternoon_1110/.

## 1. A 36 GB Mac simulated for the 24 GB package (`--mem 24`, w13b)

How it was set up:
- **Ballast:** anonymous memory locked with mlock() (ballast.py; wired, never paged out; no sudo, inside
  vm.user_wire_limit).
- **GPU working set:** capped at 27 GB inside the process by sitecustomize.py: `mx.device_info()` reports 27 GB, which the
  engine passes to `mx.set_wired_limit`, and the MLX memory limit is 1.5x that. No system setting was touched. All 6 runs
  logged "R57_WIRED: mx.set_wired_limit(27.00 GB)".
- **Ballast size:** this Mac's other processes (the sessions, the desktop app) hold about 17 GB, not a bare macOS's 6-8.
  So the plain 28 GB ballast would have tested a 36 GB Mac with a browser open. Two sizes were run:
  - Case A: a ballast leaving the engine about 25 GB (NO-SWAP 47 -> 25 GB), a 36 GB Mac with ~11 GB for macOS and apps,
    as INSTALL.md says.
  - Case B: the literal 28 GB. Other memory had been freed by then, so it left 27 GB (NO-SWAP 55 -> 27): in practice a
    second run of case A, not the browser-open stress case.

| run | case A (25 GB room) | case B (27 GB room) | free memory (this morning) |
|---|---|---|---|
| 12 HumanEval (BigMoE's keys, CAP 256) | **138.1 tok/s**, first token 3.61 s, peak 23.77 GB, tokens 12/12 identical | 137.3 tok/s, 3.66 s, 23.78 GB, 12/12 | 135.9 tok/s, 3.63 s, 23.78 GB |
| one 3,003-token prompt (paper text) | 26.9 tok/s decode, first token 17.98 s, peak 25.03 GB | 26.5 tok/s, 19.36 s, 25.04 GB | - |
| 3-turn chat.py --mem 24 | turns: 92 / 256 / 43 tokens at 29.7 / 43.0 / 27.5 tok/s; first token 2.28 / 3.28 / 4.68 s; peak 23.67 / 23.88 / 23.96 GB | ran (38 s) | - |
| swap | flat (6,659 MB) | +403 MB during the 3K prompt | - |

- With 25-27 GB of room and a 27 GB GPU working set, the 24 GB package ran at full speed. Its tokens were identical, its
  peaks unchanged and swap flat or nearly so.
- **What this does not prove:** a 36 GB M5 Max has a different GPU (more cores; MLX picks some kernel tiles by GPU type,
  so tokens may differ slightly) and a different SSD and thermals. None of that can be simulated here. The ballast also
  does not reproduce macOS's own memory policy on a 36 GB machine (compressor sizing, the real default working set).
- No browser-open (~17 GB of other use) case was run.

## 2. PF-A at 24 GB (chat.py --mem 24, R57_PFLM=1 vs 0; chat.py's 24 GB default unchanged)

| prompt | answers | first token: PF-A / default | lifetime peak: PF-A / default | decode |
|---|---|---|---|---|
| short (24 tokens, one chunk) | identical, 77 / 77 tokens | 1.98 / 2.03 s | 23.62 / 23.61 GB | 27.3 / 27.5 tok/s |
| long (6,980 tokens) | identical, 256 / 256 tokens | **17.70 / 42.06 s (2.38x)** | **25.98 / 25.67 GB** | 24.9 / 25.0 tok/s |

- PF-A works at 24 GB with identical answers and a 2.4x faster first token on a 7K prompt, for +0.3 GB.
- **The label is wrong past ~3K tokens:** at 6,980 tokens the 24 GB line peaks at 25.67 GB with the default prefill and
  25.98 GB with PF-A, both above "up to 25.1 GB on longer ones". The gate's longest prompt was 2,801 tokens, and the 3K
  prompt above peaked at 25.03 GB. The peak grows with prompt length; 10K and 30K at 24 GB were not measured.

## 3. PF-B length bisect (exact-32, R57_LOGHASH=1, 64 tokens, PF-B at TOK 8192 vs PF-A)

| prompt | PF-B MoE calls | tokens | verify-logits hashes | first token PF-A / PF-B | peaks PF-A / PF-B |
|---|---|---|---|---|---|
| 9,988 | 96 (2 groups per layer) | equal | **25 / 25** | 21.4 / 18.1 s | 34.26 / 35.50 GB |
| 15,002 | 96 (2 groups) | equal | **28 / 28** | 30.2 / 25.8 s | 35.43 / 36.77 GB |
| 20,003 | 144 (3 groups) | equal | **25 / 25** | 40.1 / 33.7 s | 36.57 / 38.06 GB |
| 25,003 | 192 (4 groups) | equal | **24 / 24** | 50.1 / 41.2 s | 37.31 / 39.01 GB |
| 29,988 (last night) | 192 (4 groups) | differ from the 40th | **0 / 25** | 62.6 / 51.7 s | 38.16 / 40.42 GB |

- PF-B is bitwise exact up to 25K tokens and breaks between 25K and 30K.
- The group count is not the cause: 4 groups pass at 25K here, and at 7.9K in the published TOK 2048 check.
- Group shapes at TOK 8192: 25K = 8 + 8 + 8 chunks plus a single 427-token chunk; 30K = 8 + 8 + 8 + 6 chunks, so its last
  call groups 5,412 tokens. The passing runs had multi-chunk last groups of 1,796, 6,810 and 3,619 tokens.
- Leading hypothesis, not tested: a matmul in the grouped MoE call (the router's N = 512, or the shared expert) whose
  bits depend on M for some shapes, as the shared expert's gate did before the per-chunk fix.
- The next step is a kernel-level check: the 30K run's group M (5,412; and 4,096 / 1,316 at TOK 4096) against the
  per-chunk calls, bit for bit. It needs a few minutes of GPU and no model run. No fix is built; the orchestrator is asked
  first.
