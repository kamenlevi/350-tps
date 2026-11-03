#!/bin/zsh
# WHOLE-CHIP-2 night runner (Leap, Tue 2026-11-03 17:5x; TABLE_350 'WHOLE-CHIP-2'): waits for the night window
# (00:30-14:00, Kamen's rule: quiet runs at night, never while he is on the Mac), for no PAUSE / HOLD, and for a quiet
# lock in the FIFO; then H (native/wc_handoff, ~1-2 min) and S (scripts/wc_screen.py sustained, ~7 min); then unlocks.
# Stops on swap growth > 2 GB. Run ATTACHED (run_in_background) so the lock stays with this session.
cd ~/Leap
Q=~/.local/share/quiet
LOG=data/wc2_night.log
say() { echo "$(date '+%a %H:%M:%S') $*" | tee -a $LOG; }
swap_mb() { sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
say "runner up (pid $$); waiting for 00:30"
while true; do
  hm=$((10#$(date +%H%M)))
  if [ $hm -ge 30 ] && [ $hm -lt 1400 ]; then break; fi
  sleep 60
done
while [ -e $Q/PAUSE ] || [ -e $Q/HOLD ]; do sleep 60; done
say "queueing a quiet lock"
PEER_QUEUE_TIMEOUT=43200 peer lock quiet --queue 15m "Leap WHOLE-CHIP-2: Neural Engine handoff (~2 min) + sustained re-run (~7 min), MEM 4 GB" >> $LOG 2>&1
say "lock: $(peer ls 2>/dev/null | grep -c 'quiet run') quiet runs listed"
if [ -e $Q/PAUSE ] || [ -e $Q/HOLD ]; then say "PAUSE / HOLD set after the grant: stopping"; peer unlock >> $LOG 2>&1; exit 0; fi
s0=$(swap_mb)
W=data/wc
say "H: wc_handoff (K 4 / 8 / 12 / 16, 20 checks, 0.70 ms layers, 200 GB/s share)"
native/wc_handoff $W/ane_e4_a4_s1.mlpackage,$W/ane_e8_a4_s1.mlpackage,$W/ane_e12_a4_s1.mlpackage,$W/ane_e16_a4_s1.mlpackage 20 0.70 62 0.71 200 > data/wc2_handoff.txt 2>&1
say "H exit $?; swap +$(( $(swap_mb) - s0 )) MB"
if [ $(( $(swap_mb) - s0 )) -gt 2048 ]; then say "swap guard: stopping"; peer unlock >> $LOG 2>&1; exit 1; fi
say "S: sustained re-run"
WC_COND="quiet lock, night; WHOLE-CHIP-2 S" WC_PH=15 WC_WARM=60 WC_ALONE=0 \
  WC_UNITS=a4x4,q4,a4x4+q4,a4x4,q4,a4x4+q4,a4x4,q4,a4x4+q4 \
  ~/BigMoE/.venv/bin/python scripts/wc_screen.py > data/wc2_sustained.log 2>&1
say "S exit $?; swap +$(( $(swap_mb) - s0 )) MB"
peer unlock >> $LOG 2>&1
say "done, unlocked"
