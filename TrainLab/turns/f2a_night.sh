#!/bin/bash
# F2a night v2 (MTP Head; NewIdeas' quiet whole-Mac window Sun 11-08 23:00 -> Mon 07:00, QUEUE c16f510; the orchestrator 01:0x;
# corpus under Kamen's standing download OK, ext/chatcorpus). Pre-registered: REPORT 'F2A night: pre-registration' + amendments 1-2.
# Stage 1 (the pre-registered verdict):
#   1. capture: 24 on-policy IFEval eval windows, then ring 1 (data/f2a/ring) until the ring budget, free disk < 28 GB
#      (amendment 2: 54 GB free on Sun 08:14, and v1 would have TERMed train + eval at the 25 GB guard) or 02:00
#   2. train: b5 -> ckpt/d22_f2a, 2 epochs, until 03:00     3. eval: f2a vs b5 -> data/f2a/f2a_eval.txt; commit
# Stage 2 (amendment 2; only if stage 1 is done by 03:30): delete ring 1; capture ring 2 (the next corpus sequences) to 05:10;
#   train f2a -> ckpt/d22_f2a2, 2 epochs, to 06:05; eval f2a2 vs b5 and f2a -> data/f2a/f2a2_eval.txt to 06:30; commit.
# The lock is released by 06:50. A ring under 200 windows is not trained on (NO DATA).
# Guards per phase: swap +2 GB -> SIGTERM (the phase saves), free disk < 25 GB -> SIGTERM, 10 min past its deadline -> SIGTERM;
# PAUSE -> the scripts wait. Memory (smoke Sun 01:17): peak ~21 GB + 0.118 GB per pool slot -> C 256 at NO-SWAP >= 54, C 192
# >= 46, C 128 >= 38, C 64 >= 31, else C 16.
# DRY=1 ROOT=<dir> PY=<stub>: control-flow test (times from now, no lock, no git).
# Usage (attached, run_in_background): cd ~/TrainLab && ./turns/f2a_night.sh > data/f2a/night.log 2>&1
cd "${ROOT:-$HOME/TrainLab}" || exit 1
mkdir -p data/f2a
log() { echo "[$(date '+%a %H:%M:%S')] $*"; }
at() { date -j -f "%Y-%m-%d %H:%M" "$1" +%s; }
NB=$(at "2026-11-08 23:00"); CAP1=$(at "2026-11-09 02:00"); TR1=$(at "2026-11-09 03:00"); EV1=$(at "2026-11-09 03:15")
S2=$(at "2026-11-09 03:30"); CAP2=$(at "2026-11-09 05:10"); TR2=$(at "2026-11-09 06:05"); EV2=$(at "2026-11-09 06:30")
END=$(at "2026-11-09 06:50")
PY=${PY:-$HOME/BigMoE/.venv/bin/python3}
if [ -n "$DRY" ]; then
  n=$(date +%s); NB=$n; CAP1=$((n + 600)); TR1=$CAP1; EV1=$CAP1; S2=$CAP1; CAP2=$CAP1; TR2=$CAP1; EV2=$CAP1; END=$((n + 900))
  peer() { echo "lock held (dry: peer $1)"; }; git() { echo "(dry) git $1 $2"; }
fi
swap_mb() { sysctl -n vm.swapusage | awk '{print $6}' | tr -d M; }
noswap_gb() { vm_stat | awk '/page size of/ {ps = $8} /^Pages (free|speculative|purgeable):/ || /^File-backed pages:/ {v = $NF; sub("[.]", "", v); s += v} END {printf "%d", s * ps / 2^30}'; }
disk_gb() { df -g / | awk 'NR == 2 {print $4}'; }
nwin() { find data/f2a/ring -name 'w_*.npz' 2>/dev/null | wc -l | tr -d ' '; }
frac() { local A; A=$(noswap_gb); FR=0.03   # gate: measured peak + 4
  [ "$A" -ge 31 ] && FR=0.125; [ "$A" -ge 38 ] && FR=0.25; [ "$A" -ge 46 ] && FR=0.375; [ "$A" -ge 54 ] && FR=0.5
  log "NO-SWAP $A GB -> capture frac $FR"; }
commit() {
  git add data/f2a/*.txt data/f2a/*.log ckpt/d22_f2a*.json 2>/dev/null
  git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && log "committed: $1"
}
log "F2a night v2 armed: not before $(date -r "$NB" '+%a %H:%M'); stage 1 capture to 02:00, train to 03:00, eval to 03:15; stage 2 if done by 03:30 (capture to 05:10, train to 06:05, eval to 06:30); end 06:50; disk $(disk_gb) GB free"
while [ "$(date +%s)" -lt "$NB" ]; do sleep 30; done
[ "$(date +%s)" -ge "$END" ] && { log "past the end: nothing runs"; exit 5; }
mins=$(( (END - $(date +%s)) / 60 ))
out=$(peer lock quiet --queue ${mins}m "MEM 44 GB: MTP Head F2a chat-head capture + training (NewIdeas' quiet window to 07:00)" 2>&1)
log "lock: $(printf '%s' "$out" | tail -1)"
printf '%s' "$out" | grep -qi "lock held\|reserved" || { log "NO LOCK"; exit 4; }
phase() {   # $1 name, $2 deadline (epoch), rest: the command
  local nm=$1 dl=$2; shift 2
  local s0; s0=$(swap_mb)
  log "phase $nm start (swap $s0 MB, NO-SWAP $(noswap_gb) GB, disk $(disk_gb) GB, ring $(nwin) windows): $*"
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
# ---- stage 1 (pre-registered)
frac
phase capture "$CAP1" env F2A_RING_GB=50 F2A_DISK_MIN=28 $PY -I sticky/f2a_capture.py --frac $FR --eval 24
n1=$(nwin)
if [ "$n1" -ge 200 ]; then
  phase train "$TR1" env F2A_EPOCHS=2 $PY -I sticky/f2a_train.py
  phase eval "$EV1" $PY -I sticky/f2a_eval.py f2a
  tail -1 data/f2a/f2a_eval.txt 2>/dev/null
  commit "F2a night stage 1: ring 1 = $n1 windows, f2a vs b5 (verdict in data/f2a/f2a_eval.txt)"
else
  log "NO DATA: ring 1 has $n1 windows (< 200): no training"
fi
# ---- stage 2 (amendment 2: data scaling)
if [ "$(date +%s)" -lt "$S2" ] && [ -f ckpt/d22_f2a.safetensors ] && [ "$n1" -ge 200 ]; then
  log "stage 2: deleting ring 1 ($n1 windows); ring 2 continues from cursor.json"
  find data/f2a/ring -name 'w_*.npz' -delete
  frac
  phase capture2 "$CAP2" env F2A_RING_GB=50 F2A_DISK_MIN=28 $PY -I sticky/f2a_capture.py --frac $FR --eval 0
  n2=$(nwin)
  if [ "$n2" -ge 200 ]; then
    phase train2 "$TR2" env F2A_EPOCHS=2 F2A_INIT=f2a $PY -I sticky/f2a_train.py --run f2a2
    phase eval2 "$EV2" $PY -I sticky/f2a_eval.py f2a2
    tail -2 data/f2a/f2a2_eval.txt 2>/dev/null
    commit "F2a night stage 2: ring 2 = $n2 windows, f2a2 vs b5 and f2a (data/f2a/f2a2_eval.txt)"
  else
    log "NO DATA: ring 2 has $n2 windows (< 200): no stage-2 training"
  fi
else
  log "stage 2 skipped (time $(date '+%H:%M'), f2a checkpoint $([ -f ckpt/d22_f2a.safetensors ] && echo present || echo missing))"
fi
commit "F2a night: logs (data/f2a)"
peer unlock 2>&1 | tail -1
log "F2a night DONE"
