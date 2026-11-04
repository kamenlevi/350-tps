#!/bin/bash
# MTP Head, Thu 11-05 (the orchestrator 21:5x): PORT steps 1-5 at L1-20's full recipe on the CPU (fp32 weights + Adam
# + grads ~9 GB, ~11-12 GB in all) vs L1-20's logged losses (port/compare_l120.py; PASS = every step within 2e-3 rel).
# Rules: a share lock MEM 12 GB, once runner 42 (NAX6 Part 1) runs, only if NO-SWAP stays >= 20 GB beside it: start
# needs >= 32 GB available (12 + 20) for 3 clear minutes and no other session's quiet lock / queued quiet ticket.
# Gives up at $GIVE_UP (default 11:15; the conversion window ~11:20 is the fallback, ask the orchestrator).
# Swap guard +2 GB (SIGTERM). Logs: data/port/steps_thu.log, data/port/steps_thu.json.
cd ~/TrainLab || exit 1
GIVE_UP=${GIVE_UP:-1115}
log() { echo "[$(date +%H:%M:%S)] $*"; }
swap_mb() { sysctl -n vm.swapusage | awk '{print $6}' | tr -d M; }
avail_gb() { vm_stat | awk '/page size of/ {ps=$8} /Pages free/ {f=$3} /Pages inactive/ {i=$3} /Pages speculative/ {s=$3} /Pages purgeable/ {p=$3} END {printf "%d", (f+i+s+p)*ps/2^30}'; }
others() { peer ls 2>/dev/null | grep "^- "; }
locks() { grep -oE "· (shared run \(others may work\)|benchmarking|waiting for a quiet window)[^·]*"; }
nquiet() { others | locks | grep -cE "^· (benchmarking|waiting for a quiet window)"; }
clear=0
log "waiting: no other quiet lock / ticket, >= 32 GB available, 3 clear minutes (gives up $GIVE_UP)"
while :; do
  q=$(nquiet); a=$(avail_gb)
  if [ "$q" -eq 0 ] && [ "$a" -ge 32 ]; then clear=$((clear + 1)); else clear=0; fi
  [ "$clear" -ge 6 ] && { log "clear: ${a} GB available"; break; }
  [ "$(date +%H%M)" -ge "$GIVE_UP" ] && { log "GIVE UP at $GIVE_UP: quiet=$q avail=${a} GB"; exit 3; }
  sleep 30
done
out=$(peer lock share 40m --cpu 600 --gpu 0 "MEM 12 GB: MTP Head PORT steps 1-5 vs L1-20 (CPU only, ~10 min; the orchestrator 21:5x)" 2>&1)
log "lock: $(printf '%s' "$out" | head -1)"
printf '%s' "$out" | grep -q "reserved" || { log "NO LOCK"; exit 4; }
s0=$(swap_mb); log "start (swap $s0 MB)"
/usr/bin/time -l ~/TrainLab/.venv-torch/bin/python -I port/train_port.py --data ~/Leap/data/l120 --epochs 2 --lr 2e-5 \
  --S 4 --A 64 --micro 1 --bs 32 --pmask 0.5 --no-val --max-steps 5 --ckpt-layers --attn-chunk 8 --rows 128 --threads 6 \
  --log-json data/port/steps_thu.json > data/port/steps_thu.log 2>&1 &
pid=$!
while kill -0 $pid 2>/dev/null; do
  sleep 15
  s=$(swap_mb); a=$(avail_gb)
  if awk -v x="$s" -v y="$s0" 'BEGIN{exit !(x-y>2048)}' || [ "$a" -lt 20 ]; then
    log "swap $s MB / avail ${a} GB: NO-SWAP margin gone, stopping"; pkill -TERM -f "port/train_por[t].py"; break
  fi
done
wait $pid; log "rc=$? footprint $(grep 'peak memory footprint' data/port/steps_thu.log | awk '{printf "%.1f GB", $1/2^30}')"
peer unlock 2>&1 | tail -1
[ -f data/port/steps_thu.json ] && ~/TrainLab/.venv-torch/bin/python -I port/compare_l120.py data/port/steps_thu.json
log "DONE"
