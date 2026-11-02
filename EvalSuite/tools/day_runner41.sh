#!/bin/bash
# EvalSuite runner 41 (DRAFT until the wiring lands; detached, from a live evalsuite session): T0 same scores
# (docs/PREREG_t0_2026-11-03.md). Arms b12llff4t0c (theta 0.8: math + HumanEval+ in ~15-min chunks, then the 29 agent
# rows in ONE process: the creep test) and b12llff4t0h (theta 0.95: IFEval + math in chunks), Fit12's top-2 two-pass
# decode on the pinned live bt_b12 (8db71cc537), MTP off. Shared GPU ("MEM 14 GB" in the lock reason: the day rule's one
# memory-heavy job), cli --need 14 (B12_GB). Every process first runs T0's VOID gate (Fit12's lsha). Window: from START
# once results/t0/GO exists (NewIdeas assigns the slot), until END (no chunk starts in its last 20 min). Then
# tools/t0_report.py -> results/t0.txt and results/T0_DONE. Code pin: bt_b12.py, Fit12's t0 scripts, evalsuite/, MLX /
# mtplx; a change stops it (exit 7). Stop it by pid only, and its cli child too.
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$HOME/EvalSuite" || exit 1
LOG=results/day41_runner.log
GO=results/t0/GO
START=${T0_START:-"2026-11-03 15:00"}
END=${T0_END:-"2026-11-04 00:00"}
EARLIEST=$(date -j -f "%Y-%m-%d %H:%M" "$START" +%s)
DEADLINE=$(date -j -f "%Y-%m-%d %H:%M" "$END" +%s)
export PEER_QUEUE_TIMEOUT=21600
unset EVALSUITE_BIGMOE_CODE EVALSUITE_STAGE_ENV B12_ENGINE B12_FOLD B12_PFR_GRID B12_CM B12_CL B12_FOLD_CM B12_FOLD_AW \
  B12_W B12_PMIN F12_R53A B12_FRS_NOCYCLE B12_PFR_MIN
PY=.venv/bin/python
A=b12llff4t0c; H=b12llff4t0h
say() { echo "$(date +%H:%M:%S) $*" >> "$LOG"; }
nset() { if [ -f "results/$1/decode.jsonl" ]; then grep -c "\"set\": \"$2\"" "results/$1/decode.jsonl"; else echo 0; fi; }
nall() { echo $(( $(nset $A math) + $(nset $A humaneval) + $(nset $A agent) + $(nset $H ifeval) + $(nset $H math) )); }
lid_shut() {
  ioreg -r -k AppleClamshellState -d 4 2>/dev/null | grep -m1 '"AppleClamshellState"' | grep -q Yes || return 1
  (( $(system_profiler SPDisplaysDataType -detailLevel mini 2>/dev/null | grep -c "Resolution:") > 1 )) && return 1
  return 0
}
calm() {
  while pgrep -f '^/bin/zsh [^ ]*soft_end\.sh' >/dev/null || [ -e "$HOME/.local/share/quiet/PAUSE" ] || lid_shut; do sleep 30; done
}
pin() {
  { shasum "$HOME/Breakthrough/scripts/bt_b12.py" "$HOME/Fit12/scripts/t0_hook.py" "$HOME/Fit12/scripts/t0_twopass.py"
    find evalsuite -name '*.py' ! -path '*__pycache__*' | sort | xargs shasum
    ls "$HOME/BigMoE/.venv/lib/python3.12/site-packages" | grep -E '^(mlx|mlx_lm|mlx_metal|mtplx)-.*dist-info$'; } 2>&1 \
    | shasum | cut -c1-12
}
PIN0=$(pin)
say "runner 41 start (pid $$); code pin $PIN0; from $START once $GO exists, until $END"
grep -q b12llff4t0c evalsuite/model.py || { say "T0 not wired (pending/t0_wire.py): runner stops"; exit 2; }
while [ "$(date +%s)" -lt "$EARLIEST" ] || [ ! -e "$GO" ]; do sleep 60; done
SWAPTRIPS=0; NOPROG=0
next_job() {   # the next chunk: arms alternate on their core sets; the agent process last
  if [ "$(nset $A math)" -lt 50 ] || [ "$(nset $A humaneval)" -lt 60 ]; then
    if [ $(( $(nset $H ifeval) + $(nset $H math) )) -lt 150 ] && [ "$1" = A ]; then echo "$H ifeval,math"; else echo "$A math,humaneval"; fi
  elif [ $(( $(nset $H ifeval) + $(nset $H math) )) -lt 150 ]; then echo "$H ifeval,math"
  elif [ "$(nset $A agent)" -lt 29 ]; then echo "$A agent"
  fi
}
last=H
while :; do
  job=$(next_job $last); [ -n "$job" ] || break
  set -- $job; v=$1; sets=$2
  calm
  [ "$(pin)" = "$PIN0" ] || { say "code changed: pin $PIN0 -> $(pin): runner stops"; exit 7; }
  left=$(( DEADLINE - $(date +%s) ))
  [ "$left" -gt 1200 ] || { say "deadline near: runner stops at $(nall)/289 rows"; exit 6; }
  b=$(nall)
  if [ "$sets" = agent ]; then mins=$(( left / 60 - 5 )); ck=0; else mins=25; ck=15; fi
  EVALSUITE_DEADLINE=$DEADLINE ./bin/evalsuite gpu decode "$v" --sets "$sets" --chunk-minutes $ck --minutes $mins --share \
    >> "$LOG" 2>&1; rc=$?
  n=$(nall)
  say "$v ($sets): chunk rc=$rc; rows $n/289"
  [ "$v" = $A ] && last=A || last=H
  [ $rc = 5 ] && { say "VOID: T0's gate does not reproduce Fit12's lsha: runner stops"; exit 5; }
  if tail -4 "$LOG" | grep -q "can't tell which Claude session\|left the queue"; then
    say "the session that owns this runner's locks is gone: runner stops (relaunch it from a live session)"; exit 3
  fi
  if tail -4 "$LOG" | grep -q "swap guard"; then
    SWAPTRIPS=$((SWAPTRIPS + 1)); [ "$SWAPTRIPS" -ge 6 ] && { say "swap guard: 6 trips: runner stops"; exit 3; }
    say "swap guard trip $SWAPTRIPS: waiting 2 min"; sleep 120; continue
  fi
  if [ "$rc" != 0 ] && [ "$n" -le "$b" ] && tail -40 results/gpu_stage.log | grep -q "Traceback"; then
    say "the stage failed (results/gpu_stage.log): runner stops"; exit 4
  fi
  if [ "$sets" = agent ] && [ "$(nset $A agent)" -lt 29 ]; then
    say "$A: agent process ended at $(nset $A agent)/29 rows: not one process any more (the creep test is weaker)"
  fi
  if [ "$n" -le "$b" ]; then
    NOPROG=$((NOPROG + 1)); [ "$NOPROG" -ge 4 ] && { say "four chunks without a new row: runner stops"; exit 3; }
    sleep 120
  else
    NOPROG=0
  fi
done
$PY tools/t0_report.py > results/t0_run.txt 2>&1
say "$(tail -1 results/t0.txt)"
touch results/T0_DONE
say "runner 41 end"
