# DENSE_REBUILD v2: the dense part of the 45 GB FAST check after Leap's part B (Fable B, Fri 6 Nov 2026 08:06 EET)

Marks: [K] measured by its owner, [P] derived from measured numbers, [G] my estimate (halved in sums). Nothing here ran
on a GPU. v1 is kept as `DENSE_REBUILD_v1.md`. Source for every [K]: `~/Leap/TABLE_350.md` 'STEP 0 PART B RESULT'.

## 0. Verdict

- **v1's reading was wrong, and part B says why.** One wide dependent wait costs ~1.6 us [K], not 12-20. So the dispatch
  count is not the lever, and v1's one-dispatch kernels W and D are PARKED. Their two real gains survive as shape fixes.
- **The dense time sits in calls that leave the GPU empty.** A code-MMA simdgroup takes ~1.15 us per quant group [P], and
  the GPU keeps ~208-235 simdgroups in flight [P]. A call with fewer simdgroups than that costs its K chain, whatever
  its bytes.
- **Price after this round, at 16 rows: ~21 ms [P], range 20-22, against 33.9 today [K part A].** At 2 rows ~23.5 against
  35.8. This sits just above Leap's 16-20.
- **12-15 ms is not reachable by kernels alone.** The byte floor is 10.7 ms at 250 GB/s. After this round the remaining
  gap is the HC read's in-loop excess, the up mix at 140 GB/s and ~25 small launches per attention layer (section 5).
- **New in v2:** a ks plan per shape (section 2), a row-parallel GDN step that makes the 16-row step cost what the 2-row
  one does (section 3), a gate kernel without its serial chains, the expert id glue as one kernel, a pad-free row frame.

## 1. The fill model [P from part B]

`t = 1.6 us + 1.15 us x max(KG / ks, tiles x KG / C)`, with KG = K / 64, C = simdgroups in flight.

| evidence [K] | number |
|---|---|
| out_proj, 96 groups, 80 tiles, 112 us | 1.17 us per group |
| a\|b 40 groups 45 us; k / v 48 us; shared gate\|up 47 us | 1.13-1.20 us per group |
| in_proj, 512 tiles x 40 groups, 113 us | C = 208 |
| attention q, 384 tiles x 40 groups, 75 us | C = 235 |

- A call is byte-bound only when it has at least ~240-320 simdgroups for its whole run. Below that it is chain-bound.
- Two ways to fill a narrow call: split K (ks), or let its rows ride as extra tiles of a wide call that reads the same x.

## 2. The ks and tile plan per shape (`kernels/ksplan.py`, `ksplan.out`)

| shape | tiles x KG | today us [K] | plan | simdgroups | plan us [P] | floor us at 250 | ms per check |
|---|---|---|---|---|---|---|---|
| out_proj / o_proj | 80 x 96 | 112 | **ks 4** | 320 | 39-44 | 35 | -3.3 |
| GDN a\|b | 3 x 40 | 45.5 | **fold into in_proj** (515 tiles) | - | +0.7 | 0.9 | -1.6 |
| attention k\|v | 2 x 16 x 40 | 2 x 48 | **fold into q** (416 tiles) | - | +6 | 6.4 | -1.1 |
| shared gate\|up + gate | 41 x 40 | 47 | **ks 8** | 328 | 10-11 | 8 | -1.7 |
| shared down | 80 x 10 | 13.7 | **ks 5** | 400 | 6 | 4 | -0.4 |
| router, 8-bit | 16 x 40 | 18.6 | qmm16c8 at ks 10, **only after a flip check** | 160 | 6-7 | 5.8 | -0.6 |
| attention 8-bit 640 x 2,560 | 20 x 40 | 21.9 | qmm16c8 at ks 10 | 200 | 7 | 7.2 | -0.2 |

- **Sum: -8.1 ms without the router, -8.9 with it.** Leap's own table says -8.7.
- **Measured after v2 [K Leap, 08:0x]:** out_proj runs 41.4 us at ks 6 against 47.1 at ks 4, so the fill point is past
  the model's 4 for this shape; Leap keeps ks 6. DN-KS's chained bench: PASS, -7.74 ms per 2-row check.
- **The model's pick for out_proj was ks 4 (superseded by the line above).** It is fill-bound from ks 4 on (7,680 group steps over C). ks 8 only adds threadgroup
  memory. If a fold is not wanted, a|b alone wants ks 10 (6 us) and k|v merged wants ks 8 (9 us).
- **The folds need no new kernel and no K split.** a|b become tiles 512-514 of the in_proj stream (16,384 + 96 = 16,480
  columns = 515 tiles exactly). k|v become tiles 384-415 of q's stream. Each tile's arithmetic is unchanged, so a fold is
  bitwise against any arm that already runs these rows on qmm16n / qmm16c at ks 1. That makes the two folds candidates
  for the exact arm too (-2.7 ms), unlike the K splits.
- **Threadgroup memory:** a split's partials take (ks - 1) x 2 KB. Stay at or under 20 KB, where residency holds [K
  NAX-OCC]. That allows ks <= 11.
- **The router is the risky row.** Its logits pick the experts, so a new K order can flip routes on near-ties. Gate it on
  route flips, not on logit error. It is the smallest gain here; skipping it costs 0.6 ms.
- **SDPA: no new kernel is needed.** The single-call forms exist: att_single (MLX's own fused SDPA, 61 -> 5 kernels per
  call, -2.4 ms [K R-62], my FASTTAX patch turns it on) and fs4 (F1, fatt_verify with F1-R8). fs4 is N-invariant, so it
  also drops the key-bucket pads and the class re-runs. Leap's chain bench can pick: one run of each at the check's real
  key count.

## 3. What the K split does not cover

### 3a. gated_delta_step at 16 rows: `kernels/gdn_chunk.py` (compiles; algebra checked on CPU)
- [K] 25-27 us at 2 rows (6.2 MB at 239-250 GB/s), 57.5 us at 16 rows. The extra 30 us is not bytes. Each check row
  rewrites the whole state before the next row may start.
- The recurrence unrolls exactly. With P(i, t) = g_{i+1}..g_t and G_t = g_0..g_t:
  - d_t = beta_t (v_t - G_t S0 k_t - sum_{i<t} P(i, t)(k_i . k_t) d_i)
  - o_t = G_t S0 q_t + sum_{i<=t} P(i, t)(k_i . q_t) d_i
  - S_n = G_{n-1} S0 + sum_{i<n} P(i, n-1) d_i k_i^T
- So the state is touched twice only: S0 times the 32 vectors [k_t, q_t] (independent of the recursion), and one rank-n
  update. The recursion becomes a 16-step forward substitution on scalars per (head, state row).
- This is the chunk-wise form of the delta rule, known from training; here it serves the check.
- CPU check (`gdn_chunk_check.out`, 200 random heads, 1-16 rows): outputs differ from the fp32 loop by 5.9e-7, the state
  by 2.9e-7; 0.10 % of outputs round to a different 16-bit float. So it is FAST, not bitwise.
- Expected [G]: 28-40 us at 16 rows instead of 57.5, i.e. -0.6..-1.1 ms per 16-row check. I count -0.5.
- **Line for Leap (chained, layer 4, 16 rows): PASS <= 40 us per call, KILL > 50.** Outputs within 1e-5 of the loop.
- Side gain for the commit: the state after any kept prefix m is the same last step with n = m. A replay then needs only
  d_i, k_i and g, with no loop. That fits the lazy commit's pack.

### 3b. HC k2b: `kernels/hc_k2c.py` (compiles; drop-in for hc8r's kernel 7)
- k2b costs 9.4-10.5 us for 0.45 MB [K]. Bytes are not the cost. Two serial chains are: one thread adds 64 threadgroup
  values in a row for xsum, and one adds 16 partials in a row for c.
- k2c sums per stream first (4 short chains, 4 multiplies) and lets one simdgroup add each quant group for xsum.
- Expected [G]: 4-5 us, i.e. -0.5 ms per check over 96 reads. I count -0.25. Line: PASS <= 6 us, KILL > 8.
- Folding the gate into the up mix is not worth it: 80 threadgroups would each re-read the partials (29 MB per read).

### 3c. The 2 -> 16-row pads: `kernels/pad_carry.py` (sketch, no kernel)
- ~300 Full + Concatenate launches per 2-row check, ~0.6 ms [K]. They exist only below 16 rows.
- A ref2 call that slices its 16-row result remembers the 16-row parent. The next call takes the parent instead of
  padding. Real rows keep their bits by the row-independence INVs (R-62b, R-71, R-71b).
- It is worth 0 at 16 rows, so it is the last item to build.

### 3d. The expert id and mask glue: `kernels/eprep.py` (compiles; logic checked, 4,000 cases, 0 differ)
- One dispatch for ids_p, ids_k, ids_s and the zeroed weights that `_ooo_1c_call` builds from 4-12 tiny ops.
- Integer and select logic only, so bitwise. The two posts stay. The -2 select on pre_l belongs in kernel A's prologue.
- Worth [P]: 8-10 launches x 1.6 us x 48 layers = -0.6..-0.8 ms of the ~1.5 ms Leap counts under the experts.

## 4. The price

| step, 16-row check | ms |
|---|---|
| dense part today [K part A, 16 rows] | 33.9 |
| ks plan and folds, without the router (section 2) [P] | -8.1 |
| att_single or fs4 [K R-62] | -2.4 |
| row-parallel GDN step [G, halved] | -0.5 |
| gate kernel k2c [G, halved] | -0.25 |
| router on qmm16c8, if the flip check passes [P] | -0.6 |
| **after this round** | **~21 (20-22)** |

- At 2 rows: 35.8 - 8.1 - 2.4 - 0.25 - 0.5 (pads) - 0.6 = ~24.
- The expert glue kernel is -0.6..-0.8 ms more, outside the dense part.
- Leap's 16-20 needs every kernel at 220 GB/s. This round does not get there: see section 5.

## 5. What is left after this round, in order of size [P]

1. HC reads in the loop: 8.6 ms in situ against 5.95 ms as a chain. ~2.6 ms has no owner yet. It is not in k1c / k2b /
   k3c themselves. A chained replay of a whole read inside a layer would find it.
2. k3c, the up mix: 3.8 MB at 137-143 GB/s. At 220 it is -0.9 ms. It is a 5-group chain over 320 simdgroups, so it is
   fill-bound with a heavy tail; the tail (16 loads of h per lane) is the suspect.
3. in_proj at 210 GB/s against attention q's 245 with the same kernel: -0.5 ms if it reaches 240. 512 tiles is 2.4x C;
   try nt 2 so fewer threadgroups are in flight.
4. Attention's other ~25 launches per layer after att_single: -0.5 ms.
5. Then the count: ~3,000 launches x 1.6 us is ~4.8 ms per check. That is where a fused layer kernel would pay, but
   only after the items above. W and D stay parked until then.

## 6. Order for Leap

1. DN-KS with the plan of section 2 (already pre-registered) and the two folds.
2. att_single or fs4 in the FAST arm.
3. `gdn_chunk` on the chained bench, then in the GDN body.
4. `hc_k2c`, then `eprep`, then the pad frame.

## 7. Files (`kernels/`)

| file | what | check |
|---|---|---|
| `ksplan.py`, `ksplan.out` | the fill model and the plan per shape | runs on CPU |
| `gdn_chunk.py`, `gdn_chunk_check.out` | row-parallel GDN step, Metal draft + numpy forms | compiles (3 instances); algebra PASS |
| `hc_k2c.py` | gate kernel, drop-in for kernel 7 | compiles |
| `eprep.py`, `eprep_check.out` | expert id glue kernel | compiles; logic PASS |
| `pad_carry.py` | pad-free row frame, sketch | parses |
| `gdn_w.py`, `hc_d.py`, `pack_check.py` | v1's W and D, PARKED | compile; packing PASS |
| `metal_check.py`, `metal_check.out` | offline Metal compile of all drafts | PASS, 10 instances |
| `price.py`, `price.out` | v1's pricing, superseded by section 4 | - |
