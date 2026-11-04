#!/bin/bash
# MTP Head, Wed 11-04 18:2x: P-OFF on the orchestrator's 18:1x slots. Waits for 21:00, P-CAP's runner gone, no other
# session's quiet lock (BigMoE's 20:20-20:58 ticket) and no other share lock declaring MEM >= 5 GB (gives up 21:20).
# Then turns/poff_x.sh (extraction). If the on-path rate is >= 0.75 (REPORT 'P-OFF amendment') and it is <= 21:55, it
# runs turns/poff_t.sh (training + code walk, ~65 min, before BigMoE's 23:00 run). Log: data/poff_night.log.
cd ~/TrainLab || exit 1
log() { echo "[$(date +%H:%M:%S)] $*"; }
clear=0
while :; do
  now=$(date +%H%M)
  if [ "$now" -ge 2100 ]; then
    q=$(peer ls 2>/dev/null | grep -v "MTP Head" | grep -c "quiet lock")
    big=$(peer ls 2>/dev/null | grep -v "MTP Head" | grep -E "shared run|quiet lock" | sed "s/.*·//" | grep -oE "MEM [0-9]+ GB" | awk '$2 >= 5' | wc -l | tr -d " ")
    pc=$(pgrep -f "pcap_ru[n].sh" | wc -l | tr -d " ")
    if [ "$q" -eq 0 ] && [ "$big" -eq 0 ] && [ "$pc" -eq 0 ]; then clear=$((clear + 1)); else clear=0; fi
    [ "$clear" -ge 6 ] && { log "slot free for 6 polls (3 min)"; break; }   # not a gap between another job's arms
    [ "$now" -ge 2120 ] && { log "GIVE UP at 21:20: quiet=$q big=$big pcap=$pc"; exit 3; }
  fi
  sleep 30
done
./turns/poff_x.sh > data/poff_x_run.log 2>&1
log "extraction runner rc=$?: $(tail -2 data/poff_x_run.log | tr '\n' ' ')"
rate=$(grep -oE "on-path rate \(assistant\) [0-9.]+" data/poff_x.log | awk '{print $NF}')
log "on-path rate (assistant): ${rate:-none}"
if [ -z "$rate" ]; then log "no rate line: extraction incomplete, no training"; exit 4; fi
if awk -v r="$rate" 'BEGIN{exit !(r < 0.75)}'; then log "on-path rate < 0.75: KILL by the pre-registered diagnostic, no training"; exit 0; fi
[ "$(date +%H%M)" -le 2155 ] || { log "too late for the 21:50-22:55 slot: training moves to Thursday"; exit 0; }
./turns/poff_t.sh > data/poff_t.log 2>&1
log "training runner rc=$?: $(tail -2 data/poff_t.log | tr '\n' ' ')"
log "DONE"
