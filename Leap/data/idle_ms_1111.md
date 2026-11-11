# BIGMOE_IDLE_MS=50: the idle engine stops burning a core (Wed 11 Nov 01:49-01:57)

**Why:** the 1.1.0 serve.py idles at 100 % of one core at 24 and 32 GB (data/agent_cc_1111.md, 01:27-01:30): bigmoe_ext's
loader thread spins (`__builtin_arm_yield()`, bigmoe_ext.cpp:1804). The ext already has the lever (Breakthrough 11-02,
bigmoe_ext.cpp:1521-1526): BIGMOE_IDLE_MS=n makes the loader nap 200 us per pass after n ms without a served call; calls
within a request come far less than 50 ms apart; timing only, so exact. The orchestrator (01:3x): yes to 50 if the A/B
shows idle CPU down and decode the same within noise (separate passes, so the order cannot favour one arm).

**Setup:** the v110 clean clone (the 1.1.0 candidate, unchanged; the variable set in the process environment, which the
ext reads when it loads). ab_idle.sh; data in idle_ms_1111/.

**Idle CPU (serve.py, one 16-token request, 10 s rest, CPU time over 60 s):**

| setting | without (01:27-01:30) | BIGMOE_IDLE_MS=50 |
|---|---|---|
| 24 GB | 100 % of one core | **1.6 %** |
| 32 GB | 100 % | **1.5 %** |

A second request after 70 s idle was served normally (first token 1.57 / 1.56 s vs 1.62 / 1.63 s for the first).

**Decode (run.py --config chat --kind code, HumanEval/68, /16, /91 x 256 tokens; A = unset, B = 50; order A B B A per
setting, each run its own process):**

| setting | A (unset) | B (50) | B / A | first token A / B | tokens |
|---|---|---|---|---|---|
| 24 GB | 129.2, 128.7 (128.9) | 129.0, 129.5 (129.2) | 1.002 | 3.46 / 3.46 s | equal in all 4 |
| 32 GB | 130.0, 131.9 (130.9) | 128.6, 129.7 (129.1) | 0.986 | 4.39 / 4.34 s | equal in all 4 |

Lifetime peaks unchanged (23.69-23.70 GB at 24; 31.76-31.77 GB at 32).

**Verdict: PASS within noise.** Idle CPU 100 % -> 1.5-1.6 %; decode the same at 24 GB; at 32 GB the B mean is 1.4 % lower,
inside the run-to-run spread (the two A runs alone differ by 1.5 %: 130.0 vs 131.9); first token and tokens identical.
Mechanism check: inside a decode the loader serves a call every few ms, so the 50-ms nap never engages; the only
in-decode difference is one clock read per idle spin pass (tens of ns). Confirmation: 8 more 32 GB runs (B A A B B A A B)
in the clean-clone slot after the cold agent test. Adopted per the orchestrator: BIGMOE_IDLE_MS=50 as an env default in
release/src chat.py + serve.py (1.1.0 candidate rebuild + clean-clone check, held for the orchestrator's review) and in
release/next serve.py; BIGMOE_IDLE_MS=0 in the shell restores the spin.
