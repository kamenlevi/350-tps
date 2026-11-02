# Decision map night 1 vs ~/TRIED/TRIED.md (Breakthrough, Mon 2026-11-02 01:4x)

Which ablations already have numbers (so Fable does not re-buy them), by TRIED.md line. None of the earlier tests
measured what the map measures: argmax flips split by the 125B's own confidence class (sure / tie / mid). So every run
below still adds information, but some only re-measure a known effect in a new unit.

| ablation | already known (TRIED.md line) | what the map adds |
|---|---|---|
| topk2 / topk2r (Q1) | top-2 on ALL tokens with substitution or drop: KILL on quality (#9 wait-top-2, l.45; D1 frugal, l.106: Eval suite IFEval -6.0 at 24 GB); static top-5 KILL (35B, l.645); top-4 / top-6 KILL (9.70x / 2.98x MSB-3's error, l.116) | NEW: flips on code-SURE vs code-mid rows, the unit Q1 needs (kill line > 5 % on code-sure) |
| topk5 | static top-5 KLD 0.179 on the 35B (l.645); top-6 KILL (l.116) | the 125B in the flip unit |
| topk8 | top-8 renorm PASS at 24 GB (L1-17a, l.29) and 12 GB (TK1, l.612); S9 per verify row KILL on strict KLD (l.174); no-renorm M-09c / M-09d (l.222, l.634) | not in night 1; covered |
| shared_zero | none (only cost work: R-74, Scout SC2, l.354, l.328) | NEW |
| att / gdn / moe reuse_prev (P-frame) | none (cache reuse and predictors are other objects, l.101-190) | NEW |
| hc_static / hc_mean_raw | none for the read; HC mixer WEIGHT precision: HC8 ADOPTED (KLD +0.0000, l.656), HC4 KILL (top-1 0.980 -> 0.939, l.707) | NEW |
| hc_q4 | HC4 is a WEIGHT test (l.707); the map's hc_q4 is 4-bit OUTPUT activations per row: a different, harsher object | partly known; read it as an activation-precision probe |
| gdn_q4 / att_q4 | weight precision: GDN is the largest single Q4 KLD class on the 35B (0.057, Breakthrough SCOREBOARD.md:191); MSB-3 dense linears +12.5 % ppl (l.295) | output-activation precision: new unit |
| ctx2048 / ctx512 | none | WEAK on these windows: every answer starts within 442 tokens of the window start (prompts 23-441 tokens), so the cut removes nothing; expect ~0 flips |
| gdn_state_bf16 | none | not wired (needs the GDN cache patch); not in night 1 |
