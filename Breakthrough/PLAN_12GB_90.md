# 12 GB LOSSY: 57 -> 90-130 tok/s on code (Breakthrough + Fit12, Thu 5 Nov 2026 19:38)

- **Goal** (Kamen 19:4x, via the orchestrator): 12 GB lossy at 90-130 tok/s on code, as soon as possible, then publish.
- **The bar**: EvalSuite same-scores on code.
- **Fit12's section** has the measured budget and its levers: `~/Fit12/PLAN_12GB_90_fit12.md`. It is linked here, not
  copied, because Fit12 does not write in this repo.

**The budget in brief** [K]. t80ck1u (T3R2) spends ~261 ms per check for ~15 kept tokens: 57.3 tok/s on the shared text,
44.2 on full outputs.

| part | ms per check |
|---|---|
| draft | 13 |
| pass 1 (P1-K1): wait 53, compute 71 | 130 |
| exact passes (46 % of checks) | 105 |
| commit | 12 |

The exposed SSD wait is ~128 ms, 49 % of the check. It reads 1.23 GB per check at ~9.6 GB/s, 70-80 % of the SSD's
12-14 GB/s.

## Update Thu 19:5x (Fit12's replay: `~/Fit12/PLAN_12GB_90_fit12.md`, "Lever 1 RESULT")

- **The certificate is token-exact.** It shows 0-1 divergences from the exact model in ~3,400 tokens, at every θ and cf.
  So all of the map's damage comes from pass 1's KV, and lever 2 as first framed (a sharper certificate) is **KILLED**.
- **Calibrated speeds** come from Fit12's replay (full outputs, 16 HumanEval prompts, cf gate 0.9), within 2-4 % of
  T3R2's measured runs. Without the cf gate, every point is ~8 % slower.

  | pass 1 | θ 0.8 | θ 0.9 | θ 0.95 | θ 0.98 |
  |---|---|---|---|---|
  | P1-K1 | 45.8 | 41.0 | 37.9 | 35.3 |
  | top-2 | 40.2 | 37.6 | 35.9 | 33.4 |

- **The code-valid points so far are slower than the exact mode.** Top-2 at θ 0.95 (1.22 %, PASS) runs ~36 tok/s; the
  exact mode, t80ck2, runs 40.8 on full outputs and 49.9 on the shared text. Until a FAST form passes code and is
  priced, the base for the factors is the exact mode. From 49.9, 90-130 needs x1.8-2.6.
- **Lever 2 is now a wider pass 1.** It means a better KV for the certified rows. On the map, top-5 at θ 0.9 passes
  (0.92 %).
  - Step 0b on Saturday finds the cheapest passing width: top-3 / top-4 / top-5 at θ 0.8 / 0.9 (topk3 / topk4
    registered by install_topk34.sh).
  - Fit12 builds the engine form (ranks 0-4 in pass 1) and prices it from one calibration run.
- **Levers 1 and 3 apply to the exact base unchanged.** They come first now.

## Step 0: the 57 is not yet a code-valid base

T3R2 certifies at θ 0.8 behind a P1-K1 pass 1: only the block's rank-0 union, at most 4 experts per row. The map's
certificate sweep (`~/FableGod/decision_map/out/CERT_read.txt`) [K] uses 4-bit experts and the 12 code windows; the code
line is 1.34 %.

| pass 1, certificate | code flips | rows certified | blocks needing pass 2 |
|---|---|---|---|
| top-2, θ 0.99 | 1.16 % | 73.4 % | 77 % |
| top-2, θ 0.95 | 1.22 % | 82.3 % | 63 % |
| top-2, θ 0.9 | 1.49 % | 85.4 % | 60 % |
| top-2, θ 0.8 | **1.63 %** | 88.4 % | 55 % |
| top-2 at 3 bits, θ 0.8 | 1.75 % | 88.2 % | 57 % |
| **top-5, θ 0.9** | **0.92 %** | **89.8 %** | 51 % |

- **EvalSuite T0 = KILL.** T0 is the top-2 two-pass at 12 GB, run on HumanEval+ at θ 0.8: 80.0 vs 91.7, McNemar 7 / 0.
  The map's matching arm, top-2 at θ 0.8, is over the line, so the map predicted the KILL. T0's IFEval ran at θ 0.95 and
  failed too (-6.0). The map's IFEval for that arm is 6.48 %, against the chat route's 4.30 % PASS.
- **The damage comes through the context.** At θ >= 0.8, certified rows flip only 0.0-0.3 %. The uncertain rows computed
  exactly after them flip 4-12 % (17 % at θ 0.7). So a cheaper pass 1 means a worse context.
- **What follows:**
  - P1-K1 at θ 0.8 is probably over the line too.
  - A better pass 1 beats a lower θ. Top-5 at θ 0.9 passes with more rows certified than top-2 at θ 0.8.
- **Step 0** [Breakthrough]: map screens of t80ck1u's own certificate form (P1-K1, θ 0.8, cf gate 0.9) and of the
  code-valid candidates (θ 0.95; a top-4/5 pass 1). The arms are built as rank masks with the keepset replay's blocks,
  run on the code windows, and queued for the next night slot.
- **The base** for the factors below is the fastest form that passes code. It may be under 57.

## The top 3 at 12 GB

Factors are on the per-check time, with quality held.

### 1. Kept per check on code: x1.2-1.4 [P, halved]

- **Levers**: the copy draft, INERT and the drafter.
- **Why it ranks first**: it is quality-neutral, because the verify decides every token. Every part of the 12 GB check is
  paid per check, so kept per check passes through almost 1:1 (Fit12: +20 % kept is x1.15-1.2 after the extra rows'
  misses).
- **Evidence**:
  - HumanEval answers re-emit the signature and docstring: copy rows are 61-68 % of tokens. Fable FULL's replay gives
    x1.4-1.6 [P].
  - INERT: x1.15 on the 12 HumanEval keys [G].
  - The drafter ceiling (D98): kept 12-12.5 vs 10.5 [G].
- **First test**: a CPU replay over T3R2's 16 HumanEval prompts gives the copy spans and today's kept per check on them.
  Then a T-A1-style timing probe of a wide copy pass at 12 GB in Fit12's harness.
- **Owners**:
  - Breakthrough: the replay;
  - Fable FULL / GOAL: their builds;
  - MTP Head: P-OFF / D98 on the T3R2 prompts.

### 2. Exact-pass diet at a code-valid certificate: x1.15-1.3 [G]

- **The idea** (Fit12's lever 1): the exact passes are 105 of 261 ms. Two routes: a certificate calibrated on code, and a
  mid pass for moderately unsure rows before REF2-T.
- **The constraint**: after step 0 the gain must come from a better pass 1 or the mid pass, not from a lower θ.
- **First test** [Fit12, CPU]: from T3R2's logged checks, why rows go exact and what each threshold or pass-1 width would
  save. Then the map screen of each candidate, then a T3R2-style A/B.

### 3. Bytes and compute per check (exact): x1.1-1.25

- **Why it helps**: the wait is exposed at ~9.6 GB/s, so every byte cut comes off the wait.
- **Levers**:
  - the 3-bit pass 1: t80ck1um3 is x1.105 on the shared text [K]; its quality is unscreened (3-bit top-2 at θ 0.8 is
    1.75 % on the map);
  - rank-0 residency: a CPU replay of pass 1's 341 misses through an LRU of the 12 GB slots (Breakthrough's keepset
    replay);
  - Leap's kernels on pass 1's 71 ms of compute.
- **First test**: the residency replay [Breakthrough, CPU]; Leap's FAST-NAX arms on the T3R2 harness.

### The stack

x1.5-2.3 [G] on the code-valid base. That is 75-130 tok/s if the base is 50-57.

130 needs the SSD wait hidden by overlap: reads issued before routing is final, or late terms. The SSD already runs at
70-80 % of its ceiling during the waits, so cutting bytes alone cannot get there.

## Not in the top 3

- **The split** (QOM-KEEP's resident keep off on sure rows): ~x1.0 at 12 GB. P1-K1 already posts the union only, with no
  resident keep, so it is the split's extreme form.
- **Never-wait** (FAR): 12 GB's dose is ~50 misses per kept token, against 6.6 at C 208 (~7.5x). Saturday's tier 1 at
  the 45 GB pools gives the dose-response first.
- **Prefetch**: the frugal form is KILL (recall 0.61-0.73, x0.90).
- **BYTES10 beyond the 3-bit pass 1**: <= x1.2 priced at 12 GB [G].

## Who does what (started Thu 19:4x)

- **Fit12**: lever 2: the CPU test on T3R2's logged checks, then the A/B.
- **Breakthrough**:
  - this plan;
  - step 0's code screens: t80ck1u's form first;
  - lever 1's replay;
  - the rank-0 residency replay.
- **Leap**: pass-1 kernels at 12 GB.
- **MTP Head**: kept per check with P-OFF / D98 on the T3R2 prompts.
