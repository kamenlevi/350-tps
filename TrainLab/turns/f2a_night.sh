#!/bin/bash
# F2a night (MTP Head; NewIdeas' quiet whole-Mac window Sun 11-08 23:00 -> Mon 07:00, QUEUE c16f510; the orchestrator 01:0x;
# corpus under Kamen's standing download OK, ext/chatcorpus). Pre-registered: REPORT 'F2A night: pre-registration'.
#   1. capture: 24 on-policy IFEval eval windows, then the corpus ring (data/f2a/ring) until F2A_RING_GB or CAP_END
#   2. train:   b5 -> ckpt/d22_f2a (D-22 trainer, depth 6) until TRAIN_END (checkpoint kept on any stop)
#   3. eval:    f2a vs b5 on held-out + on-policy chat, the pre-registered line -> data/f2a/f2a_eval.txt
#   4. commit the small outputs; release the lock by 06:50
# Guards per phase: swap +2 GB -> SIGTERM (the phase saves), free disk < 25 GB -> SIGTERM, PAUSE -> the scripts wait.
# Memory: capture at frac 0.5 (C 256, ~42 GB) when NO-SWAP >= 46 GB, else 0.375 (C 192) at >= 40, else 0.25 (C 128).
# Usage (attached, run_in_background): cd ~/TrainLab && ./turns/f2a_night.sh > data/f2a/night.log 2>&1
cd ~/TrainLab || exit 1
mkdir -p data/f2a
log() { echo "[$(date '+%a %H:%M:%S')] $*"; }
at() { date -j -f "%Y-%m-%d %H:%M" "$1" +%s; }
NB=$(at "${NOTBEFORE:-2026-11-08 23:00}")
CAP_END=$(at "${CAPEND:-2026-11-09 03:45}"); TRAIN_END=$(at "${TRAINEND:-2026-11-09 06:10}"); END=$(at "2026-11-09 06:50")
PY=~/BigMoE/.venv/bin/python3
swap_mb() { sysctl -n vm.swapusage | awk '{print $6}' | tr -d M; }
noswap_gb() { vm_stat | awk '/page size of/ {ps = $8} /^Pages (free|speculative|purgeable):/ || /^File-backed pages:/ {v = $NF; sub("[.]", "", v); s += v} END {printf "%d", s * ps / 2^30}'; }
disk_gb() { df -g / | awk 'NR == 2 {print $4}'; }
log "F2a night armed: not before ${NOTBEFORE:-2026-11-08 23:00}; capture to ${CAPEND:-03:45}, train to ${TRAINEND:-06:10}, end 06:50"
while [ "$(date +%s)" -lt "$NB" ]; do sleep 30; done
[ "$(date +%s)" -ge "$END" ] && { log "past 06:50: nothing runs"; exit 5; }
mins=$(( (END - $(date +%s)) / 60 ))
out=$(peer lock quiet --queue ${mins}m "MEM 44 GB: MTP Head F2a chat-head capture + training (NewIdeas' quiet window to 07:00)" 2>&1)
log "lock: $(printf '%s' "$out" | tail -1)"
printf '%s' "$out" | grep -qi "lock held\|reserved" || { log "NO LOCK"; exit 4; }
phase() {   # $1 name, $2 deadline (epoch), rest: the command
  local nm=$1 dl=$2; shift 2
  local s0; s0=$(swap_mb)
  log "phase $nm start (swap $s0 MB, NO-SWAP $(noswap_gb) GB, disk $(disk_gb) GB): $*"
  env F2A_UNTIL=$dl "$@" > data/f2a/$nm.log 2>&1 &
  local pid=$!
  while kill -0 $pid 2>/dev/null; do
    sleep 15
    if awk -v x="$(swap_mb)" -v y="$s0" 'BEGIN{exit !(x-y>2048)}'; then log "$nm: swap +2 GB -> SIGTERM"; kill -TERM $pid; fi
    if [ "$(disk_gb)" -lt 25 ]; then log "$nm: disk under 25 GB -> SIGTERM"; kill -TERM $pid; fi
    if [ "$(date +%s)" -ge $((dl + 600)) ]; then log "$nm: 10 min past its deadline -> SIGTERM"; kill -TERM $pid; fi
  done
  wait $pid; local rc=$?
  log "phase $nm rc=$rc: $(tail -1 data/f2a/$nm.log | cut -c1-200)"
  return $rc
}
A=$(noswap_gb); FR=0.25
[ "$A" -ge 40 ] && FR=0.375
[ "$A" -ge 46 ] && FR=0.5
log "NO-SWAP $A GB -> capture frac $FR"
phase capture "$CAP_END" env F2A_RING_GB=${RINGGB:-34} $PY -I sticky/f2a_capture.py --frac $FR --eval 24
phase train "$TRAIN_END" $PY -I sticky/f2a_train.py
phase eval "$END" $PY -I sticky/f2a_eval.py f2a
cat data/f2a/f2a_eval.txt 2>/dev/null | tail -8
git add data/f2a/*.txt data/f2a/*.log ckpt/d22_f2a.json 2>/dev/null
git commit -q -m "F2a night: chat-head capture + training + eval (data/f2a; verdict in f2a_eval.txt)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "committed $(git log --oneline -1 | cut -c1-60)"
peer unlock 2>&1 | tail -1
log "F2a night DONE"
