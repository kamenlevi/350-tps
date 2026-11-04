#!/bin/bash
# MTP Head, Wed 11-04 18:1x: P-OFF extraction (REPORT 'P-OFF'). Leap's ~/Leap/scripts/dfl2c_extract.py, used read-only
# and unchanged, on ext/poff/poff_windows.jsonl -> ext/poff/x/<key>.npz (resumable: done windows are skipped). Share
# lock MEM 20 GB; a 3-window smoke first (stops if its footprint > 19 GB); swap guard +2 GB. Started on the
# orchestrator's slot. Logs: data/poff_x_smoke.log, data/poff_x.log.
cd ~/TrainLab || exit 1
log() { echo "[$(date +%H:%M:%S)] $*"; }
swap_mb() { sysctl -n vm.swapusage | awk '{print $6}' | tr -d M; }
PY=~/BigMoE/.venv/bin/python3
export DFL2C_IN=$HOME/TrainLab/ext/poff/poff_windows.jsonl DFL2C_OUT=$HOME/TrainLab/ext/poff/x
ok=0
for t in 1 2 3; do
  out=$(peer lock share 60m --cpu 300 --gpu 90 "MEM 20 GB: MTP Head P-OFF extraction (the 125B's prefill of 892K tokens of public code, ~40 min)" 2>&1)
  log "lock try $t: $(printf '%s' "$out" | head -1)"
  printf '%s' "$out" | grep -q "reserved" && { ok=1; break; }
  sleep 60
done
[ $ok -eq 1 ] || { log "NO LOCK"; exit 4; }
log "smoke (3 windows)"
DFL2C_LIMIT=3 /usr/bin/time -l $PY ~/Leap/scripts/dfl2c_extract.py > data/poff_x_smoke.log 2>&1
fp=$(grep "peak memory footprint" data/poff_x_smoke.log | awk '{printf "%.1f", $1/2^30}')
log "smoke rc=$? footprint ${fp} GB; $(grep -c '\[dfl2c-x\] [0-9]' data/poff_x_smoke.log) windows"
if [ -z "$fp" ] || awk -v f="$fp" 'BEGIN{exit !(f > 19)}'; then
  log "footprint over 19 GB (or no footprint line): stop, re-declare MEM"; peer unlock 2>&1 | tail -1; exit 5
fi
s0=$(swap_mb); log "full run (swap $s0 MB)"
/usr/bin/time -l $PY ~/Leap/scripts/dfl2c_extract.py > data/poff_x.log 2>&1 &
pid=$!
while kill -0 $pid 2>/dev/null; do
  sleep 20
  s=$(swap_mb)
  if awk -v a="$s" -v b="$s0" 'BEGIN{exit !(a-b>2048)}'; then
    log "swap $s MB = +2 GB over the start: stopping (resumable)"; pkill -TERM -f "dfl2c_extrac[t].py"; break
  fi
done
wait $pid; log "rc=$? (swap $(swap_mb) MB); $(grep -c '\[dfl2c-x\] [0-9]' data/poff_x.log) windows this run; $(ls ext/poff/x | wc -l | tr -d ' ') files"
peer unlock 2>&1 | tail -1
log "DONE"
