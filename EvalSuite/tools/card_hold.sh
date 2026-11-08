#!/bin/bash
# Hold runner 61's card reference (PREREG_card_gates amendment 5; the orchestrator 16:4x): once the running runner's current
# chunk ends, stop it (by pid, its children too, then peer unlock), start no chunk until HOLD_FILE exists or HOLD_MIN
# minutes have passed (whichever comes first), then re-arm the reference stage (the same command, exec'd here, so it stays
# attached to this background task). If the runner exits by itself, nothing is re-armed. Runner pid 0: no runner runs
# (already stopped); hold from now.
#   card_hold.sh <runner pid> <hold file> <minutes> <cutoff "YYYY-mm-dd HH:MM">
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$HOME/EvalSuite" || exit 1
R=$1; F=$2; MIN=$3; CUT=$4
L=results/day61_ref_runner.log; n0=$(grep -n "run: decode ref2tnaxn" "$L" | tail -1 | cut -d: -f1)   # the current chunk's start line
log() { echo "$(date '+%H:%M:%S') $*" | tee -a "$L"; }
desc() { local p c; for p in "$@"; do c=$(ps -A -o pid=,ppid= | awk -v p="$p" '$2 == p {print $1}'); [ -n "$c" ] && { echo "$c"; desc $c; }; done; }
if [ "$R" != 0 ]; then
  log "hold armed (pid $$): runner $R stops after its current chunk; then no chunk until $F or $MIN min"
  until tail -n +$((n0 + 1)) "$L" | grep -q "reference: chunk rc=" || ! kill -0 "$R" 2>/dev/null; do sleep 2; done
  kill -0 "$R" 2>/dev/null || { log "hold: runner $R exited by itself: nothing re-armed"; exit 1; }
  kill -STOP "$R"; D=$(desc "$R" | tr '\n' ' ')
  kill -TERM $D "$R" 2>/dev/null; kill -CONT "$R" 2>/dev/null; sleep 3
  for p in $D $R; do kill -0 "$p" 2>/dev/null && log "hold: pid $p still alive"; done
  peer unlock > /dev/null 2>&1
fi
t0=$(date +%s)
log "hold (pid $$): the runner is stopped (pid $R, children: ${D:-none}); $(grep -c . results/ref2tnaxn.r6/decode.jsonl) rows; no chunk until $F or $(date -r $((t0 + MIN * 60)) +%H:%M)"
until [ -e "$F" ] || [ $(( $(date +%s) - t0 )) -ge $((MIN * 60)) ]; do sleep 30; done
log "hold ends: $([ -e "$F" ] && echo "$F exists" || echo "$MIN min passed"); re-arming the reference stage"
exec env CARD_STAGE=ref CARD_TAG=ref CARD_WAIT_STRATA=1 CARD_CUTOFF="$CUT" tools/day_runner61.sh
