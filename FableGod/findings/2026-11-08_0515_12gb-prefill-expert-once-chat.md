# At 12 GB the prefill already reads each expert once per prompt: 191 / 378 / 461 tok/s at 1.6K / 4.7K / 7.9K tokens (2-3.7x the 45 GB path), in under 11 GB; 12 GB chat decodes 12.9 tok/s at 556 MB of SSD per kept token
- Date: 2026-11-08 05:1x EET. Session: Fit12.
- Claim: the 12 GB engine's prefill (b12_prefill: one call per prompt, 512-row attention and 4096-row MoE chunks inside it)
  streams each layer's experts once per call. A 7.9K-token prompt reads ~one pass of the expert store, 67 GB.
  - Splitting the MoE into one 8192-row call changes nothing: x0.99-1.005, the same bytes, the same tokens.
  - It runs 2-3.7x faster than the 45 GB engine's prefill, which calls the model per 1,024-row chunk and re-streams the
    experts per call. BigMoE's PFX test aims at the same form.
- Number [K], 12 GB line (tier plan 4433333333, C_m 47 / C_l 32, engine v3p bt_b12 8db71cc537), quiet lock, each arm alone in
  its own process, no PAUSE, rc 0, run 05:07:45-05:12:41:

  | prompt (BigMoE PFX) | tokens | prefill s | prefill tok/s | TTFT s | prefill SSD | lifetime peak |
  |---|---|---|---|---|---|---|
  | agent/edit10 | 1,565 | 8.21 | 191 | 8.53 | 63.4 GB | 10.62 GB |
  | agent/write13 | 4,730 | 12.52 | 378 | 13.03 | 66.0 GB | 10.77 GB |
  | agent/write11 | 7,932 | 17.19 | 461 | 17.50 | 67.1 GB | 10.95 GB |

  - TTFT = prefill + the first check (with the drafter's setup), where the first tokens appear.
  - With s_moe 8192 (one MoE call per prompt): 191.6 / 376.0 / 458.1 tok/s and the same SSD bytes; the decoded tokens are equal.
  - For reference, the 45 GB exact prefill (BigMoE N45): 98 / 118 / 124 tok/s, TTFT 16 / 40 / 64 s.
  - The SSD runs at 7.7 / 5.3 / 3.9 GB/s effective on these prompts, so compute takes a growing share as prompts get longer.
- 12 GB chat (BigMoE N45's 12 IFEval prompts, the verified-greedy loop, CAP 256):
  - 12.88 tok/s whole decode (geometric mean), pooled 12.76; full-period 13.16; end to end 9.02.
  - 2.34 tokens kept per check (chat drafts keep far fewer than code's ~9-10), 172 ms per check.
  - 1.30 GB of SSD per check = 556 MB per kept token (479-749 per prompt). 150 tok/s on chat at ~12 GB/s needs <= ~80 MB.
  - Lifetime peak 10.96 GB.
- How: /Users/kamen/Fit12/scripts/chat12.sh (fit_t3.py sha256 2338f9367b00, t3_twopass.py 800323c3ca97 with F12_SMOE + the
  prefill's own rusage disk bytes), readers c1u16_read.py and pf12_read.py; data /Users/kamen/Fit12/data/scr/chat12
  (chat12_report.txt, pf12_report.txt / .json, MANIFEST.txt).
- Prior art: adapted (layer-wise expert streaming in one prefill pass is the standard offload form). The finding is that this
  engine already does it, and the measured gap to the chunked 45 GB path.
- Status: first measurement.
- Next: at 12 GB, prefill bytes are ~one store pass whatever the length, so the levers are SSD-compute overlap and expert
  GEMM speed (Leap's PF-B), not chunk size. The 45 GB path should gain the same once it prefills in one pass (BigMoE's PFX).
