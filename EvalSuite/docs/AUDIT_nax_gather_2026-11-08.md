# AUDIT: which EvalSuite results can hit MLX 0.32.2's NAX sorted-gather bug (Sun 2026-11-08 08:3x)

**The bug (Leap, 08:2x; ~/Leap/TABLE_350.md "MLX NAX SORTED-GATHER BUG", a521e91):**
- MLX 0.32.2's sorted NAX expert gather leaves output rows unwritten when two things hold for one call:
  - it has more than 32,768 sorted rows (> 3,276 tokens at top-10);
  - the row count is not a multiple of 64 (T % 32 != 0 tokens).
- Decode steps (<= 16 rows) never reach it. Only prefill calls on long prompts can.

**Method:** tools/nax_gather_audit.py.
- Prompt lengths come from each row's n_prompt (exact).
- For every run with rows on long items, it counts the rows that would have such a call under three rules: MoE once per
  1,024 tokens, once per 4,096 tokens, or once per prompt.
- Then I read the prefill chunking in the code each run used.

**Bottom line:** every EvalSuite gate and reference is unaffected. Only the b12 family's agent rows can be exposed (3 rows
per run). fast24's prefill chunking was not checked.

## Which prompts are long
- Only three sets have long prompts:
  - agent: 27 of 29 items over 3,000 tokens, max 11,952;
  - agentlong: 15 of 17;
  - ruler: 24 of 24, max 16,307.
- Every other set's longest prompt is <= 520 tokens: HumanEval+ 367, humanevalx 441, MBPP 323, math500 520, IFEval 149,
  multi 50.

## Safe
- **Gates on short sets:** CERT, S4 v1 / v1', C30, STACK, the 12 GB gates (t80 / t90 / t95ck1u) and the chat gate
  (m1b, running). No call can pass 3,276 tokens.
- **The exact references' long rows.** ref2.generate prefills in 1,024-token calls (snap/leap-52cf2c9/ref2.py:1186), so
  each call has <= 10,240 rows. This covers:
  - ref2tnaxn (NAX6-N agent + ruler) and ref2tnfhn;
  - the PF-E agent refs ref2tnaxn.r4. Their agent/write11 (7,932 tokens) is Leap's 79,320-row example; it was prefilled
    in 1,024-token calls, so BigMoE's prefill comparisons against these rows stand.
- **tfwin, replay, relax.py (relax_A / B / control) and live16 / 16b:** 1,024-token prefill calls (tfwin.py:77,
  replay.py:66, relax.py:304).
- **r57 rows (agentfast_*, bisect_*; 11-06):** the frozen screen snap/r57frz-af1 prefills with chunk=1024
  (r57_screen_fast.py:888, called at :926). R57_PFCHUNK has defaulted to 1024 since 90d5534.
- **MTPLX generate_ar (ref, floor, plan4433333333; 10-20..22):** MTPLX's 'auto' prefill chunk is 2,048 (today's
  mtplx/generation.py:1056), so <= 20,480 rows per call. The October mtplx was not checked.

## Exposed, if the path's MoE uses the sorted NAX gather (Leap says b12_prefill does)
- **The b12 family through EvalSuite's _gen_mtp:** decode.py calls bt_b12.b12_prefill_state(model, ids, 512, 4096), so
  the MoE runs once per 4,096 tokens. MLX 0.32.2 is recorded.
- That exposes 3 of 29 agent rows per run, through each prompt's last call:

  | Row | Prompt tokens | Last call |
  |---|---|---|
  | agent/edit02 | 11,952 | 3,760 |
  | agent/write11 | 7,932 | 3,836 |
  | agent/write12 | 7,638 | 3,542 |

- Affected runs (10-22..11-05): b12, b12g, b12l, b12ll, b12llff, b12llff2, b12llff3, b12llff4, b12llff4p, b12llff4t0c,
  b12llfoff, b12llfon, b12llfx, b12llfx2, b8, b8fast. The single-row .r9 runs have none.
- **fast24 (f24b16, f24nat; 10-23):** prefilled by BigMoE's fast24.generate_fast24, whose chunking I did not check.
  - Per-4,096 calls would expose the same 3 rows.
  - One call per prompt would expose 27 of 29.
- Any agent score from these runs (the 12 GB line's October agent results) should be re-run with Leap's fix
  (~/Leap/scripts/pfb_fix.py switch_glu_padded), or read with these rows left out.
