# IDEAS (NewIdeas, account-1; ranked by impact x evidence; each with its kill test and result)

Scale used everywhere: 125B = 48 layers x 512 experts, top-10, expert 2560x640 SwiGLU (4.92M weights, 2.77 MB at 4 bits).
Quality yardstick: Breakthrough's law KLD_excess ~ 0.0051 x (E / 0.0032)^1.5, E = missed gate energy sum w_r^2 per layer
(top-10 renormalised); ar4 = 0.0096 means E <= ~0.0049, i.e. ~96 % of the routed output energy must be computed.

---------------------------------------------------------------------------------------------------------------------
## I1. Deferred experts: a late expert joins the token d layers later instead of stalling it (status: WEAK, alive only
## as a partial trade; 125B check handed to Breakthrough)
**Result (35B, 4-bit experts, teacher-forced 3 x 1365 tokens, LRU per layer, data/defer35/results.txt, 90 s of GPU):**
| arm (C = cache slots of 256, W = ranks always waited) | KLD | top-1 | missing slots / mass |
|---|---|---|---|
| floor (every MoE output x 1.0078) | 0.0103 | 0.968 | 0 |
| drop, C26 (10 %) W2 = frugal | 0.1632 | 0.855 | 0.40 / 0.31 |
| defer 1 layer, C26 W2 | **0.0554** | 0.918 | 0.33 / 0.26 |
| defer 2, C26 W2 | 0.0792 | 0.900 | |
| defer 4, C26 W2 | 0.1053 | 0.883 | |
| add at the last layer, C26 W2 | 0.1364 | 0.861 | |
| defer 1 / 2, C26 W0 (ranks 0-1 late too) | 0.1412 / 0.2260 | | 0.41 / 0.37 |
| drop / defer 2 / end, C13 (5 %) W2 | 0.1933 / 0.1122 / 0.1923 | | 0.50 / 0.39 |
Share of drop's excess over the floor that remains: d=1 29 %, d=2 45 %, d=4 62 %, at the end 82 %.
**Finding (new physics):** a routed expert's contribution is consumed by the next 1-2 layers (routing, attention/GDN
inputs and the K/V the token leaves behind); arriving later it is worth little, and in the final residual almost
nothing (18 % of the damage undone). Ranks 0-1 must be on time (W0 arms are worse than dropping at d >= 2).
**Verdict:** the kill rule (d=2 keeps > 50 % of the excess) is passed narrowly (45 %), the "strong" bar (d=2 within 2x of
the floor) is missed by far (7.7x). Deferral is not free coverage: a late expert costs the full read and returns
55-70 % of its value. Useful only as a d = 1 trade for low ranks, to turn residual stalls into a small quality cost
(e.g. wait ranks 0-3, defer 4-9 by one layer). Predicted on the 125B by scaling: d1_w2 ~0.03 (noren 0.100), d1_w4
~0.016 (w4 0.045). Breakthrough measures it (tf_defer125.py) with its speed.
**Prior art:** Layer Parallelism (2502.02790), ScMoE (2404.05019), Pipeline-Native Transformers (2608.23841, trained
expert_delay); training-free deferral of cache misses not found.

---------------------------------------------------------------------------------------------------------------------
## I1-half. Half a layer late: the late expert joins after layer L+1's attention, before its router (status: ALIVE, best
## latency-hiding variant; 125B check on Breakthrough's queue as dh_w2)
35B (batch 2, 14:40): half_C26_W2 KLD **0.0385** (top-1 0.932) vs d=1 0.0554, drop 0.1632, floor 0.0103: 19 % of drop's
damage left (d=1: 29 %). 5 % residency (C13): 0.0476 vs drop 0.1933 (20 %). Ranks 0-1 half-late: 0.100 (keep them on time).
Why it works (with I5 below): what hurts is the next layer's ROUTING and the K/V/state the token leaves; half-late misses
only layer L+1's attention input. Slack = layer L's resident experts + L+1's attention (~0.4-0.6 ms): about one cold read
(0.34 ms + 0.19 ms per 2.77 MB), so it hides most single misses per layer but not bursts of 3-4 (10 % residency eager
needs ~3.2 per layer): combine with prediction for the rest. Costs the full reads (like exact streaming).

## I6. Near-tie re-routing toward resident experts (status: DEAD as a bytes lever: equals the mass rule on the 35B (batch 4); Breakthrough's untested idea, measured
## here because this harness has all 256 router scores)
+delta on the router logits of experts in the layer's LRU, select top-8 of the biased logits, weight by the ORIGINAL
probabilities. 35B C26 (10 %), every chosen expert read: delta 0.25 -> reads 131.8 -> 95.0 (-28 %) at KLD 0.031 (+0.019 over
exact 0.0117); 0.5 -> 68.8 (-48 %) at 0.059; 1.0 -> 37.6 (-71 %) at 0.103. With frugal (waits ranks 0-1 only) it does
nothing (0.160-0.185). The floor arm explains why it is cheap at small delta: this MoE already flips near-ties under any
perturbation (0.8 % on every MoE output = KLD 0.010, top-1 0.968), so swapping a near-tied expert costs little more.
Prior art: cache-conditional experts (2412.00099), Cache-Prior; not tested before on a 256-512-expert top-8/10 model
here. **125B traces (CPU, open loop, expA *_800_g, 2,926 decode tokens, C=51 = 10 %):** every selected expert read:
reads/token 155.7 (delta 0) -> 109.9 (0.25, -29 %) -> 87.9 (0.5, -44 %) -> 70.5 (1.0, -55 %), while the TRUE top-10 mass
swapped out per layer is only 0.7 % / 1.9 % / 4.2 % [WRONG, see correction]. KLD on the 125B: Breakthrough's turn
(tf_defer125.py d1_w10_b25, dh_w2_b25). CORRECTION 16:05 (Breakthrough caught it): the '0.7 % / 1.9 % / 4.2 % swapped mass' figures were the NET change in kept router weight; a swap costs the displaced AND the added expert (orthogonal outputs). Displaced true top-10 mass per layer is 6.7 % (delta 0.25) / 10.8 % (0.5) at C=51, 6.0 % at C=97; swap gate energy 0.0081 / 0.0126 / 0.0073 -> the energy law predicts KLD ~0.02 at delta 0.25 (Breakthrough's per-text fit: hard 0.019, easy 0.0055: gsm FAILS, code borderline), ~2.2x the energy per saved read of the mass rule. Re-routing is probably dominated by wait-by-mass under the gate; the 125B probe d1_w10_b25 (first in Breakthrough's queue) and the 35B frontier decide. Next on the 35B: frontier vs
wait-by-mass at equal reads (batch 3, pol35.py).

## I5. Lazy exactness: decode frugal, repair the past exactly in the background (status: DEAD, dominated; see DEAD.md)

## I1-half at K=4 (dh_w4): the gate candidate (status: PREDICTED PASS, 125B rows queued at Breakthrough, 16:15)
Breakthrough's per-text energy-law fit with the 35B's half-late factor (f ~0.2 of drop's excess) predicts: dh_w2 fails
(ifeval ~0.028, gsm ~0.006), dh_w3 marginal, **dh_w4 (ranks 0-3 on time, cold ranks 4-9 half a layer late) passes every
part** (ifeval ~0.014 vs 0.0204, gsm ~0.0025 vs 0.0045, code ~0.001 vs 0.0025) with only 41-50 waited reads/token at 10 %,
where every drop policy fails (m50 easy 0.0114). Speed if the late reads hide: ~45 ms/token = ~22 tok/s eager (m85 14.2),
~28-30 with MTP on code; SSD traffic stays at exact's 360-475 MB/token (25-33 ms at 14.6 GB/s, inside the 45 ms).
If it holds it is the first policy here that beats wait-by-mass at the formal gate (1.55x), and it slots into the
stall-free loader with look-ahead prefetch for ranks 0-3. 35B analogue C26_w4_lhalf + a 35B yardstick in batch 3.

## Batch 4 frontier (35B, C26 = 10 % unless noted, frozen segments, 17:43; data/defer35/results.txt 'pol' lines)
| arm | reads/token | waited cold | KLD (prose/gsm/code) |
|---|---|---|---|
| frugal C26_w2_ldrop | 21.8 | 21.8 | 0.163 (0.112/0.268/0.108) |
| **frugal + cold rank 1 half-late (C26_w1_lhalf_r2)** | 21.8 | **9.5** | **0.168** |
| wait-by-mass m50 / m70 / m85 | 39.6 / 66.8 / 97.9 | same | 0.108 / 0.057 / 0.028 |
| exact (w8) | 128.7 | 128.7 | 0.011 (floor) |
| near-tie b25 + exact | 92.7 | 92.7 | 0.030 (= m85 at -5 % reads: no gain) |
| half-late cold ranks >= 2 / >= 4 (w2 / w4) | 129 | 23.7 / 52.2 | 0.039 / **0.022** |
| 5 %: frugal / w3 / w4 / half-late x50 / x70 | 31.8 / 51.3 / 73.2 / 57.2 / 96.1 | 31.8 / 51.3 / 73.2 / 31.8 / 32.4 | 0.202 / 0.125 / 0.085 / 0.138 / 0.090 |
Findings: (1) cold rank 1 half a layer late in frugal is nearly free (+0.005 KLD, +3 %) and halves waited reads (at 5 %:
+0.005, 31.8 -> 14.2); dropping it instead costs +0.127. (2) Near-tie re-routing equals the mass rule (Breakthrough's
energy-law prediction holds): dead as a bytes lever. (3) Under fidelity, half-late ranks >= 4 beats wait-by-mass on waits
(0.022 at 52 waited vs 0.028 at 98) at full bytes. (4) At 5 %, waiting for ranks 0-2 (w3) or half-late within 50 % mass
already beats frugal 10 %'s KLD on this model at 51-57 reads/token. (5) Dead: top-16 weight normalisation (k5_n16 0.179 vs
k5 0.084; frugal_n16 0.257 vs 0.163) and static top-5/top-4 (0.084 / 0.229). (6) The routed-MoE-one-layer-late dataflow
by layer band: 0-10 0.166, 10-20 0.127, 20-30 0.095, 30-40 0.180 (middle layers tolerate most; total 0.409).
The 35B yardstick (LM Studio's all-4-bit build: 0.101/0.139/0.096) is dominated by its 4-bit dense layers, so it is NOT a
usable analogue of the 125B's ar4 gate.

## I7. Pre-routed frugal (TrainLab's composition; status: DEAD on the 125B with the current predictor (+11-26 % KLD,
## top-2 precision 62 %); revival needs a trained top-2 estimator)
35B zero-shot: C26 0.141 vs frugal 0.168 at 16.4 vs 18.6 cold reads/token; C13 0.174 vs 0.202; every waited read has a
layer of slack. Window matters (B8-40; all layers 0.237); true router weights matter (2x). Prior art: Pre-gated MoE / Edge0
(trained), Speculating Experts (training-free, ALL ranks predicted: GSM8K collapse). New here: only the waited top-2 are
pre-routed, the rest stay the true router's resident choices, and the pre-picks warm the LRU (fewer reads overall).

## I8. Demand-first staging prefetch for frugal's waited ranks (status: FALSIFIED on the eager engine 03:53, see DEAD.md; model +16-19 % in the fast engine with MTP;
## hardware A/B handed to Breakthrough 01:30; design note to MoonShots' loader ring)
Why prefetch lost on hardware (Breakthrough 18:10: eager code 22.7 vs 26.2, MTP 37.6 vs 39.2): NVMe has no priority, so
prefetch reads issued together with the layer's demand reads share the SSD's bandwidth and slow the waited reads; and
the 4 spare slots per layer came out of C. Mechanism: (1) issue the d=1 prefetches for layer l+1 only AFTER layer l's
demand reads have landed (the window is then layer l's MoE half + layer l+1's attention half); (2) read them into a small
GLOBAL staging ring (8-16 slots, ~40 MB), never into the per-layer cache; a staged expert routed at ranks 0-1 is promoted
by a 2.8 MB copy into the LRU victim slot, one routed at ranks 2-9 is computed for free if it has landed; (3) use the
corrected d=1 forecast (MoEPrefetch step 29, BIGMOE_PF_CORR, 35 MiB: top-10 agreement 0.62 -> 0.75), k = 2 per row.
Evidence (scripts/stage_sim.py, stage_time.py; data/stage/): 125B traces (MoEPrefetch *_400_pf d=1 forecasts + Breakthrough
expA probabilities, 4 prompts x 400 tokens); SSD = 0.191 ms floor + 2.77 MB at 13.1 GB/s shared (fits MoonShots' QD
1/4/6/10 latencies). d=1 recall of the true ranks 0-1: top-2 0.56, top-4 0.76, top-8 0.87 (TrainLab's ridge: top-2 0.68,
top-4 0.85). Fast engine, 4-row MTP passes (0.63 ms/layer + 3 ms/pass, 3 tokens/pass):
| C | no prefetch | k=2 with demand ('now') | k=2 after, plain d=1 | k=2 after, recall 0.69 | recall 0.78 | oracle top-2 |
|---|---|---|---|---|---|---|
| 51 (10 %) | 57.8 tok/s (61 waited/pass) | 54.4 (-6 %) | 63.6 (+10 %) | 67.8 (+17 %) | 71.0 (+23 %) | 81.7 (+41 %) |
| 26 (5 %) | 50.7 (90 waited/pass) | 45.8 (-10 %) | 55.9 (+10 %) | 60.3 (+19 %) | 63.8 (+26 %) | 75.5 (+49 %) |
'now' reproduces the MTP loss Breakthrough measured; the eager loss (-13 %) is larger than the model's 'now' (+4 %), so
part of it was the spare slots and the implementation. Waits are ~30 % of a fast-engine MTP pass (oracle bound 1.41-1.49x):
after the engine itself, the biggest speed factor of the small-RAM line. Staged experts used at ranks 2-9 also lower the
missed gate energy (M=1, C=51, k=3: 0.0246 -> 0.0231 per layer). Kill: the hardware A/B ('now' vs 'after', spares from C vs
a global ring) shows < +5 % on MTP code at C=51. PRE-REGISTERED (01:47) for Breakthrough's v3 MTP engine (model
calibrated to ~81 ms/pass, 37.2 tok/s baseline): arm 1 (C=47 + 4 spares, corrected k=2, 'after') 42.3 tok/s (+14 %, waited
61 -> 25 per pass); 'now' 38.0 (+2 %); plain d=1 'after' 40.7 (+9 %); global ring at C=51 42.6 (+15 %).
AMENDED 01:53 (SSD model v2: 0.06 ms floor + min(8.1 GB/s per read, 14.0 shared), which fits the QD1/2/4 bandwidths that
v1 overstated; the truth is between): arm 1 +11 % (v1 +14 %), 'now' +2 %, plain 'after' +8 %, ring +12 %; fast engine
MTP C=51: 'after' corrected +16 % (v1 +17 %), + same-layer 0.8 +24 %, oracle +39 %; exact C=128: same-layer 0.8 +19 %,
+ d=1 +25 % (both models). Pre-registered range for arm 1: +11-14 % (data/stage/stage_time_v2.txt). Next if alive: a same-layer pre-attention forecast (layer l's router on
its own input, issued at the layer's start, lead = the attention half 0.30 ms) needs a 125B capture (recall unknown).
Model bound (01:37, data/stage/stage_time_same.txt, no false positives assumed): alone at recall 0.8 68.2 tok/s (+18 %,
= the corrected d=1), on top of the corrected d=1 71.6 (+24 %; recall 1.0: 72.3): worth ~+6 % after I8, so the capture
waits for the A/B. EXACT track too (01:52, stage_time.py exactsame; C=128, 4-row passes, eager-v3-like): no prefetch 28.5
tok/s; d=1 top-4 'after' 30.9; same-layer forecast of all cold top-10 at recall 0.8 34.0 (+19 %), 1.0 34.5; both 35.5
(+25 %): at 25 % residency the exact pass is ~half SSD time, and the attention half is the useful lead. So the capture
(tf_samelayer125.py, recall of the same-layer vs the d=1 forecast; exact forward, routing logged) was queued at 01:52
(run_samelayer.sh, ~15 min). RESULT (03:01, data/samelayer/results.txt; exact forward, KLD vs reference 0.0007-0.0028 =
numerics floor; 3,012 decode calls). Recall inside the forecast's top-k, hard (ifeval+multi) / easy (gsm+code):
| forecast | ranks 0-1 @2 | @4 | top-10 @10 | @16 |
|---|---|---|---|---|
| same-layer, pre-attention (training-free) | 0.77 / 0.71 | 0.93 / 0.87 | 0.82 / 0.73 | 0.93 / 0.85 |
| d=1 tap (BigMoE) | 0.57 / 0.52 | 0.76 / 0.70 | 0.66 / 0.58 | 0.79 / 0.70 |
| d=1 + MoEPrefetch correction | 0.65 / 0.65 | 0.84 / 0.83 | 0.73 / 0.69 | 0.85 / 0.82 |
The same-layer forecast is the most accurate at equal k. But timed with the REAL forecasts, false positives included
(stage_real.py, both SSD models): FRUGAL fast engine C=51: corrected d=1 k=2 'after' +15-16 % (the synthetic estimate
holds); same-layer k=1 +6 %, k>=3 loses (waste reads contend with demand reads); same-layer on top of d=1 adds nothing
(+14-15 %). EXACT C=128 (eager-v3-like): unthrottled d=1 k=12 LOSES (-9-10 %: the SSD is nearly saturated, so every
wasted read costs), d=1 k=4 'after' +12 %, same-layer CONFIRMED (in both S[:8] and the d=1 top-8, issued at the layer
start) +10 %, d=1 k=2 + confirmed@10 +14 %. So the same-layer forecast is dead as a separate prefetcher for B and is a
precision filter for A: prefetch few, precise, demand-first. The oracle-style '+19-25 %' above was optimistic.
Arm-1 prediction re-checked with the REAL corrected forecast (03:01): Breakthrough's engine 37.9 -> 42.2 tok/s (+11 %, SSD v2)
/ 36.4 -> 41.5 (+14 %, v1), waited 67 -> 30 per pass: the pre-registered +11-14 % stands.
Prefill companion (B5): v3's exact prefill reads every expert a chunk uses; keep chunks large and
stream the chunk scratch in expert sub-batches (Breakthrough's IDEAS prefill item).

## I9. Rank-aware LFU eviction for frugal (status: small, +~7 % on SSD-bound hardware; for the Mac mini line)
Frugal's cache only matters for ranks 0-1 (lower ranks are skipped when cold). On the 125B expA traces (2,926 decode
tokens, C=51): LRU 19.8 waited reads/token; LRU refreshed only by rank 0-1 uses 20.1 (worse); LFU with decay 0.99 per
token counting rank 0-1 uses only 18.5 (-7 %; decay 0.97: 19.0-19.4; counting lower ranks hurts at slow decay); Belady
OPT 12.3 (-38 %). Missed lower-rank energy unchanged within +-5 %. Worth it where reads bind (Mac mini: ~+7 % tok/s);
in the latency-bound M5 Pro engine ~+2-3 %. One eviction rule in the loader (data/stage/belady_frugal.txt).

## I1b. Deferred experts computed by the CPU as they land (status: idea, depends on I1)
With a d-layer window nothing on the GPU waits for a deferred expert, so it need not run on the GPU at all: the loader
thread preads it, the CPU (SME/NEON, ~50-100 us per 4-bit expert) computes it on the saved x_L while it is cache-hot,
writes 5 KB into a shared buffer, and the GPU adds it at layer L + d behind a shared-event wait that is normally already
signalled. MoonShots killed CPU/ANE expert compute because of the ~150 us mid-token GPU<->CPU sync (MS r1/r5/r10);
deferral removes the sync from the critical path. Also lets the GPU slots hold only resident experts.

## I1c. Parareal instead of deferral (status: idea, the fallback if I1's quality is short)
Numerical analysis' parallel-in-time scheme: sweep 1 runs every layer with resident experts only (coarse propagator G),
which fixes every layer's routing and issues ALL misses of all 48 layers at once (max queue depth); sweep 2 re-runs the
stack adding F(x_L^0) - G(x_L^0) (the missing experts on the sweep-1 input) at the RIGHT layer. Error is second order
in the sweep-to-sweep change instead of first order in d layers' Jacobians; costs a second dense sweep (~2x compute).

## I4. (DEAD, see DEAD.md: all routed experts one layer late costs KLD 0.40)
