# Related-work check for the paper set (MoonShots; due Tue 10 Nov 12:00). Pass 1: Sun 8 Nov 17:00-17:1x EET

Every source below was re-opened today with `research/relwork/check.py` (all arXiv ids in one API query, every URL
fetched read-only) and `ctx.py` (the lines about our model). Raw extracts: `check_1108_1700.txt`. All competitor numbers
are SELF-REPORTED unless we reproduced them (only Strata, findings/2026-11-08_1630). Third-party text was read as data.

## 1. Citations (arXiv): 68 ids in MAIN.md + RESULTS_FIRST + EXTERNAL_* files
- 68 / 68 exist; titles and first authors are in `check_1108_1700.txt`.
- **Wrong name (fix):** 2511.14102 is "Specter: Fast MoE Inference via Quantization-Enabled Multi-Step Speculative
  Offloading". MAIN cited it as "MoE-SpeQ"; no arXiv paper of that name exists (arXiv search, 0 hits).
- **Name is the method, not the title (fine; cite with title):** 2605.00342 = EVICT ("Making Every Verified Token
  Count"); 2607.12696 = EcoSpec ("Less Experts, Faster Decoding"); 2609.02897 = AdaptiveSpec ("Margins, Not Windows").
- **Wording to check:** 2512.17073 ("Bandwidth-Efficient Adaptive MoE via Low-Rank Compensation") is cited as "token-level
  precision restoration". The abstract fits loosely; cite it by title.
- **Ambiguous label:** RESULTS_FIRST's "2606.10493 / KTransformers" row. 2606.10493 is "Achieving Cloud-Grade SLOs for
  Local MoE Inference through CPU-GPU Hybrid Design", a separate paper. KTransformers' Expert Deferral is the SOSP '25
  paper. Keep them apart.
- Still to open by hand: KTransformers (SOSP '25), Thinking Machines Lab "Defeating Nondeterminism" (Sep 2025),
  Leviathan et al. 2023, Pre-gated MoE (2023), QuaRot / SpinQuant, GPUDirect Storage / BaM, the patent and HotOS '15 items,
  and the benchmark papers (HumanEval / EvalPlus, MBPP, IFEval, GSM8K, MATH-500): no arXiv ids in the draft yet.

## 2. Competitors on OUR model (Qwen3.8-Flash-Next), re-opened
| who | what the source says today | our record (4 / 7 Nov) | status |
|---|---|---|---|
| Splash (github.com/incoai/splash, README "Performance" + release 1.4.0 notes) | Q2_0 (ISTA-DASLab GSQ-RCO, 2.4 bpw) on an **M5 Pro, 20-core GPU, 64 GB**: decode 95 tok/s on short prompts (1.3x Strata serving the same GGUF on that Mac), prefill 1,312 tok/s at 32K, cached TTFT 171 ms on a 32K replay, 171 tok/s aggregate with 4 concurrent requests; SPEED-Bench coding prompts, 1,024-token outputs; all replayed prompts hit its SSD cache. Releases now at 1.6.0 | 1.4.0: 28.8 on a 24 GB Air; 1.5.0: 56.5 (measured by Kapitsa) | **NEW and material**: same machine class, self-reported |
| Strata (github.com/Niko1221/Strata; issue #2844) | MIT. README lists Qwen3.8-Flash-Next packs (ISTA-DAS, Unsloth UD-IQ4_XS ... Q8_0, Gyro). Issue #2844: M1 Max 64 GB, Q2_0, decode 26.7 tok/s; cites an M5 Max 128 GB table at 119.5 / 108.2; engine RSS 40.3 GB | same | confirmed; our own run (IQ3_XXS, 44-47 tok/s) is the measured comparison; Splash puts Strata at ~73 on Q2_0 short prompts [P: 95 / 1.3] |
| Kapitsa (github.com/nace-ai/kapitsa) | "A 180B model on a 48 GB Mac, at 61 tok/s (M5 Pro)", experts streamed from the SSD (Q2_0); bench file 2026-10-28 (M5 Pro 48 GB, four engines); NEW 2026/11: "Qwen3.8-Flash-Next 180B writes 6% faster on an M5 Max, with the same tokens: greedy decode 107.3 -> 113.9 tok/s" | 61.3 (README) | confirmed; 113.9 on an M5 Max is new (memory setting to read) |
| SlotStream (github.com/carloslfu/slotstream) | original MLX 4-bit, exact; "Our 48 GB M5 Pro measured 20.91-23.69 tok/s ... at a 33 GB memory budget" (5 Oct 2026); latest release v0.2.30; issue #5 (Mac mini M2 16 GB, 10.2 GB target), issue #41 (M4 Pro 24 GB, 15.9 GB budget) | 23.69 / 15.86 / 5.41 / 1.48 | confirmed (README); issue figures to re-read for the exact tok/s lines |
| Evolving Agent Teams (arXiv 2610.36848) | "30.3 tokens/s decode for Qwen3.8-Flash-Next in MLX 4-bit on a 48 GB M4 Pro" (a Metal port of FreeToken streaming experts from SSD) | 30.3 | confirmed |
| Palm-Infra (github.com/TencentYoutuResearch/Palm-Infra) | NEW row: "Qwen3.8-Flash-Next NVFP4, 20 GiB: 16.2 t/s / 21.8 t/s (dagger: best observed real-prompt run, eight CPU threads, 20 GiB expert cache)"; CPU NVFP4 expert SSD offload, experimental CUDA | only the 122B row | new; CPU-side engine, different class |

## 3. Other >= 80B MoE rows, re-opened
| who | source says | status |
|---|---|---|
| Memory-Sovereign Inference (arXiv 2608.23805) | Qwen3-Next-80B-A3B in Q4_K_M; "a 512+64 mechanism diagnostic decodes at 5.037 tokens/s without reuse and 11.636 tokens/s with LRU64"; bit-identical logits and exact tokens for its held-consumer case | confirmed, but 11.6 is a mechanism diagnostic, "not a policy study": cite it as that |
| PagedMoE (arXiv 2611.03173) | Qwen3.5-397B-A17B, 24 GiB expert cache, 8.89 tokens/s (1.33x independent precision); PC with RTX 5090 32 GiB + 64 GB DDR5 | confirmed |
| flash-moe, Anemll fork, anemll-flash-mlx, mlx-flash, colibri | READMEs reachable (status 200) | lines to re-read if the papers cite them |

## 4. Not readable this way
- Reddit threads (1xezdgs "flash next q2 on a 24gb m5 macbook air 49 t/s", 1w53inj, 1wp7zyb, 1ibbloy, 1idseqb): the page is
  JS-rendered. The titles match the records; the bodies need a browser read or must be cited as "a user post".
- "Sushi" (named by the orchestrator): in no project file; asked for its link (Sun 17:1x).

## 5. Consequences for the papers (as of pass 1)
- [MAIN] section 8: replace the v1.1 rows with section 2 above; add Splash's M5 Pro 64 GB row; mark all self-reported.
- [MAIN] abstract, where we lose: a 2.4-bit engine reports 95 tok/s decode and a far faster prefill on this machine
  class (self-reported); our Strata run used Strata's 3-bit file.
- [MAIN] section 12: "MoE-SpeQ (2511.14102)" -> "Specter (2511.14102)".
- No "fastest" claim on chat, on exact decode, on prefill or on first token. A decode claim on code would need Splash run
  on our prompts (decision asked, Sun 17:2x).
- Pass 2 (Mon-Tue): the companion papers' reference lists, the hand-opened items in section 1, the issue figures.
