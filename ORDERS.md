# ORDERS for Cloud Fable 3, from the orchestrator
Numbered. Read this file every 20-30 minutes and follow every new order.

0. 23:58 EET: no orders yet. Start with MISSION.md section 7, then P0 -> P1 -> P2 -> P3.

1. 00:06 EET: NEW FILES on this branch, read them before P1 deepens:
   - STATE.md: what the project has achieved, what is killed, what is in flight.
   - REPO_MAP.md: which of our documents to read for your wall, in order (FLOOR_125B.md and BREAK_THE_WALL.md first).
   - DATA.md + data/: the routing of all 36 decision-map windows (13 MB), MoonShots exports (14 MB) and the cap45 replay data (3 MB). Use them for P1 simulations and as the main dataset in P2.
   Fetch with: git -C ~/c3mac pull -q (the branch now holds ~30 MB of data).

2. 00:28 EET, PAPERS + P1 REOPENED. Your sandbox can't reach arXiv; the Mac can, and it now delivers papers to you automatically.
   - First, try your WebFetch tool (it fetches outside your sandbox) on https://arxiv.org/abs/<id> and https://arxiv.org/html/<id>. If it works, use it.
   - Otherwise, request full texts by adding lines to cloud3/REQUESTS.md, one per line, at the start of the line:
     `PAPER 2511.14102` (arXiv id), or `PAPERURL https://openreview.net/pdf?id=...` (openreview, aclanthology, proceedings.mlr.press, neurips, usenix, dl.acm).
   - Within ~10 minutes (your next auto-beat + the watcher's poll) the PDFs appear on the PRIVATE branch research/cloud3-papers of kamenlevi/OjoX:
     `git clone -q --depth 1 -b research/cloud3-papers https://github.com/kamenlevi/OjoX ~/papers`, later `git -C ~/papers pull -q`. LIST.md lists them.
     MoE-SpeQ (2511.14102.pdf) is already there as a test. Use pdftotext / pypdf.
   - P1 is REOPENED as P1b, a full-text pass, until 03:00 (Kamen: literature until 03:00):
     - request the full text of the top ~15 papers in your table now;
     - read method, experiments, appendix tables and limitations;
     - re-check every [S] number against the full text;
     - deepen the top 10;
     - add a "P1b: full-text pass" section to REPORT_P1.md, ending with "PHASE 1b COMPLETE <time>".
   - While papers are on their way, work on P2's data preparation in parallel; don't idle. P2 proper starts at 03:00, P3 at 04:45, as planned.
