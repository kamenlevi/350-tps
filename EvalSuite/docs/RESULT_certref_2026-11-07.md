# RESULT: CERT's missing NAX6-N reference rows (Sat 2026-11-07 08:15)

Pre-registered in docs/PREREG_cert_2026-11-08.md ("the new reference decodes", 154 rows). Runner 53 (tools/day_runner53.sh):
NAX6-N's exact AR (the decode stage on the converted store, TIERENV 4433333333 / 3c / 112) on dec_humanevalx (104) and
dec_mathx (50) -> results/ref2tnaxn.r3, 154/154 rows. Chunks at C 192: 5 rows Fri-Sat 03:5x, the rest 06:5x-08:15. The
runner yielded twice for S4.

| set | rows | NAX6-N pass | cap hits |
|---|---|---|---|
| humanevalx (HumanEval+ base + plus, the 104 not in the core 60) | 104 | 93.3 % | 3 |
| mathx (math500 / gsm8k, cert_build.py, sha256 4fffdcb2d283) | 50 | 84.0 % | 8 |

These are in line with NAX6's core sets (HumanEval+ 91.7 %, math 88.0 %). They are CERT's reference rows with
ref2tnax (the core 60 + 50) and ref2tnaxn.r2 (MBPP 100).
