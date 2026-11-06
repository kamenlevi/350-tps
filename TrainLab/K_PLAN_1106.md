# K plan for the weekend (MTP Head, Fri 2026-11-06 09:5x; the orchestrator 09:4x)

**Bottom line.** K is 10.36 per 16-row check on the 12 HumanEval with the shipping drafter, but HumanEval flatters it.
On MBPP (held-out code) the same drafter keeps **5.94**. The two levers measured tonight (CD16, relax v2) mostly help
on HumanEval-style text. No drafter retrain we have measured moves code K beyond retrain noise. **K 14 on average code
has no priced route from the drafter side.**

## 1. Today's K (measured)
- **Engine** (BigMoE's FAST-NAX A/B, Fri 08:xx, C 224, 12 HumanEval, DRAFT17 + D7B = L1-20 with 4-bit layers): **10.36**
  kept per check (qall control 10.55). Per prompt it runs from 5.7 to 14.2: HE/68 14.2, /16 13.5, /56 13.1, /141 11.8,
  /63 11.3, /6 11.3, /161 10.1, /17 9.5, /19 8.9, /101 8.6, /79 8.2, /91 5.7.
- **Exact walk** (L1-20, 16 rows, the 125B's own answers): HumanEval+ (24) **9.57**, MBPP (100) **5.94**, GSM8K
  (60) 7.00, agent (12) 3.01.
- **Where the misses sit** (HumanEval+ walk, 666 checks; 0.924 right per token; per depth 0.86-0.96):
  - The first miss lands at depth 1-5 in 29 % of checks, 6-10 in 21 % and 11-15 in 22 %. 28 % of checks get all 15
    right.
  - The weakest depths are 2-3 (0.92 / 0.91) and 13-15 (0.89 / 0.89 / 0.86).
  - At the first miss, the 125B's token is the drafter's 2nd choice 55 % of the time and its 3rd choice 15 %. It is
    4th-16th 20 % of the time and missing from the candidates 11 %.
- **K 14 means ~0.975 right per token at every depth**, i.e. a third of today's errors.

## 2. What each lever adds ([K] measured, [P] predicted; workload named)
- **CD16 copy drafting** (Fable GOAL, INERT): HumanEval+ 10.44 -> 12.91 (x1.24) [P, lexer replay]; tok/s x1.15 on the
  12 HE [P]. Copying from the docstring is flattering, since copied rows are 61-68 % of HE answer tokens. On MBPP expect
  ~x1.0: MATCH, a copy override, measured x0.98 there. Runs tonight.
- **Relax v2** (MoonShots M-44, lossy, host-light): kept x1.10-1.23 on code [P, replay]. v1 measured +9.9-10.4 % kept
  [K], but host work ate the tok/s. Sat 00:30 ticket. CD16 and relax v2 both gain in comments and docstrings: don't
  multiply them, measure the stacked arm.
- **Already in the 10.36 base**: D17 (the 17th draft, right on 79.8 % of full blocks) and D7B (4-bit layers, code
  x1.00). BP-9's DSUB is a speed lever (-1 ms), not a K lever.
- **Built, BETWEEN**: the MATCH session override, HE+ x1.038 at 16 rows and x1.204 at 32 rows (12.35) [K, walk].
- **32-row checks**: HE+ 9.57 -> 10.26 [K, walk]; 12.35 with MATCH. This only pays once a row costs <= ~0.9 ms (today
  ~2-3 ms per added row): it is a cycle-side gate.
- **Drafter retrains, all measured on the code walk:**
  - On-policy data: +0.13 per doubling (PASS, but K 13 needs ~23 doublings).
  - 2x capacity (P-CAP): +0.18. Off-policy prefill data (P-OFF): +0.11. 2-step refine (D-21): +0.04.
  - One reseed alone moves code by 0.16 (SEED), so none of these is above noise except the data slope.
- **Ceilings** [K, walk]: a perfect pick among the drafter's top 3 gives 11.57 (x1.21), among all 16 12.37 (x1.29). Trees
  are a KILL at equal cost. The MTP chain keeps 10.98 vs 10.44, but costs ~20 ms of sequential steps.

## 3. The next D98 bet
- **DFlare's recipe** (arXiv 2606.02091, published): a larger block-diffusion drafter, +14.7-15.5 % average acceptance
  over DFlash on Qwen3-4B / 8B. Our P-CAP (2x layers at L1-20's data) gave +1.9 %, inside the noise, so their gain must
  come from something we lack (data, training length or layout).
- Predicted: +0.2..+1.0 K at 16 rows, unless the read finds that missing ingredient.
- Cost:
  - A desk read, ~15 min, no GPU.
  - Then, only if it names an ingredient we lack: one local night, ~1 h of GPU at MEM ~37 GB (P-CAP-sized), and the
    code + math walk, read on math too (code's retrain noise is 0.16, math's 0.01).
  - No download (we train on our own 125B data) and no paid GPU. A full bigger-drafter build is 1-2 weeks: decode nights
    for data plus training.
- Second option, also published and local: an acceptance-targeted loss (LK losses, arXiv 2602.23881; NewIdeas #17), one
  retrain night on L1-20's data. Its gain is unknown and it has the same noise caveat.

## 4. Prior art on HumanEval-type code (tokens per verify round, bonus included)
| drafter | target | setting | acceptance | tag |
|---|---|---|---|---|
| DFlash2 L1-20 (D7B + D17) | our 125B, FAST, C 224 | 16-row block, 12 HE | 10.36 | ours [K] |
| DFlash2 L1-20, exact walk | our 125B | 16 rows; HE+ / MBPP | 9.57 / 5.94 | ours [K] |
| DFlash (z-lab) | Qwen3-Coder-Next | block 16, <= 4096 new tokens | 7.25 | published (model card) |
| EAGLE-3 | LLaMA-3.1-8B | chain / tree, setups vary | 4.4-5.6; "up to 7.5" best | published |
| PARD-2 | Llama3.1-8B / Qwen3 | parallel draft | 6.95 / 5.97 (average incl. GSM8K, MATH, MT-Bench) | published |
| DFlare | Qwen3-4B / 8B | larger block-diffusion drafter | +15 % over DFlash (average) | published |

The targets, prompts and lengths differ, so these aren't 1:1. Our high HumanEval K says more about our 125B restating
HumanEval prompts than about the drafter.

## 5. My pick for the weekend
1. **Tonight:** read CD16 and relax v2 in the engine (others run them), plus a stacked arm. If both hold, HE K is ~12-13
   [P].
2. **Sat, CPU, ~15 min (mine):** put MBPP and a docstring-free HumanEval into the K scoreboard, so "average code" is
   measured, not assumed. At MBPP's 5.94, 300 tok/s needs a ~20 ms cycle.
3. **Sat, desk, ~15 min:** read DFlare. On Sun night, only if it names an ingredient we lack, run one ~1 h local probe
   (quiet lock), judged on code + math with the SEED noise lines.
4. **Not this weekend:** bigger drafters on free cloud (P-CAP doesn't support it) and 32-row checks (they need <= 0.9 ms
   per row first).

Sources: BigMoE data/fnx/fnx_report.txt + nxn_224.txt; TrainLab REPORT (D-02b, MATCH, RERANK-0, P-CAP, P-OFF, SEED),
TRIED D-21; NewIdeas QUEUE (300 line, items 6-9), KEPT_LEDGER; MoonShots HANDOVER (M-44); DFlash model card
huggingface.co/z-lab/Qwen3-Coder-Next-DFlash; EAGLE-3 arXiv 2503.01840 (+ 2602.23881, 2605.09992, 2602.01469); PARD-2
arXiv 2605.08632; DFlare arXiv 2606.02091.
