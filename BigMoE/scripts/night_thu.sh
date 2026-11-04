#!/bin/bash
# Thu early, one quiet ticket of ~95 min (the orchestrator Wed 10:1x fixes the slot in the Wed-night order ~22:00: at
# RELAX_DONE ~06:40 or after RELAX's quiet arms, before T0; apps closed: C 256 swapped +2.3 GB by day, Wed 09:15):
#   1. the adopted default's headline at C 256, 11-02's footing (scripts/d256_wed.sh, old vs new A-B-B-A, 14 prompts; ~25 min)
#   2. which lever costs agent at C 224 (scripts/agent_loo.sh, leave-one-out on 5 agent prompts, 9 arms; ~67 min: 7.4 min
#      per arm, measured Wed 13:49; the day try stopped on the swap rule in its 2nd arm at 14:02, only old ran)
# Both lines are pre-registered in their headers. Swap: the 2 GB rule per run (each script reads its own base). The new
# default holds its footprint + the 7.8 GB purgeable volatile tier (~50 GB at C 224, ~54 at C 256; the day try grew swap
# +1.8 GB in the new arm from NO-SWAP 51 GB, old +0.3), so MG is raised: an arm below 52.7 GB (C 256) / 50.5 GB (C 224)
# NO-SWAP at its start is skipped, not swapped.
# usage (a harness background task): GAP0=0 GAP=0 MARGIN=4 NOTBEFORE=hh:mm NOTAFTER=hh:mm D256_DEADLINE=hhmm \
#   ALOO_DEADLINE=hhmm bash scripts/turn45.sh 48 100 "BigMoE: C 256 headline + agent LOO, MEM ~52 GB" /bin/bash scripts/night_thu.sh
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$HOME/BigMoE" || exit 1
LOG="$HOME/BigMoE/data/night_thu.log"
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
export D256_MG=${D256_MG:-10} ALOO_MG=${ALOO_MG:-12}
say "night_thu start (pid $$, MG $D256_MG / $ALOO_MG)"
say "builds: BigMoE $(git rev-parse --short HEAD), Leap $(git -C "$HOME/Leap" rev-parse --short HEAD 2>/dev/null) (Leap's _rows16 change moves the -K83 arm only if it lands first)"
D256_C=256 bash scripts/d256_wed.sh; say "1 C 256 headline rc=$? ($(grep Verdict data/d256/d256_report_256.txt 2>/dev/null | cut -c1-110))"
bash scripts/agent_loo.sh; say "2 agent LOO rc=$? ($(grep Verdict data/aloo/aloo_report.txt 2>/dev/null | cut -c1-140))"
say "night_thu end"
