#!/bin/bash
# nw3 FIRST (Breakthrough, Fri 2026-11-06 23:4x; NewIdeas 7e74d6c, after Kamen opened the window at 23:30): NEVER-WAIT v3 (b)'s
# three code arms (data/nw3_code_extra.txt; pre-registered in SCOREBOARD 'Fri 21:3x: PRE-REGISTRATION, NW3'), the first map
# work after EvalSuite's runner 49. NewIdeas' order tonight: BigMoE's quiet ticket -> Leap's 5-min run -> Fit12's clean 12 GB
# run -> runner 49 (~4 h, the 45 GB engine) -> these arms -> EvalSuite's CERT reference decodes (runner 53) -> the rest of the
# map (nw3's 36-window arms, step 0, T1; armed separately once the verdict is out).
# - Beside runner 49 only if memory allows (the map's peak + 8 GB free). It does not: runner 49 declares MEM 46 GB and the map
#   18 GB, 64 GB in all. So the arms wait for runner 49's END: its pid read at arming, and q49.pid's (EvalSuite deletes it at
#   the end).
# - Runner 53 also waits for that end. It polls every 60 s, then skips while another session's shared run declares MEM > 5 GB.
#   This driver polls every 5 s and claims the GPU at the first clear moment with a 3-min share lock whose reason starts
#   "MEM 18 GB". The s67 runner's own lock replaces it within ~30 s; with S67_KEEPLOCK=1 that lock is kept from arm to arm.
# - Never beside a quiet run. The claim and every arm wait while another session holds or waits for a quiet window. They also
#   wait for another session's shared run over 5 GB (MEM read with or without "~") or at >= 50 % GPU, PAUSE / HOLD, a closed lid.
# - Not named *sat_night*: EvalSuite's runner 49 waits while `pgrep -f 'sat_night\.sh'` matches. That is meant for BigMoE's
#   ticket, but it matched the old Breakthrough driver too, which is why that one was stopped.
# Then the runner's read-out lands in data/s67_slot.log (code_read.py: VERDICT / VERDICT2 and the twin lines). s67_extra.txt is
# put back and the driver exits, so the verdict can go out at once (BigMoE runs the S1 engine A/B at the next chunk boundary of
# EvalSuite's runs). Run ATTACHED (Bash run_in_background), cwd ~/Breakthrough. Log: data/nw3_first.log.
# NW3_LASTGO / NW3_DEADLINE ("YYYY-mm-dd HH:MM:SS"): no start after / hard stop (default Sat 14:00 / 15:00).
export BIGMOE_EXT_BUILD=build_nat
H=~/Breakthrough; PY=~/BigMoE/.venv/bin/python; LOG=$H/data/nw3_first.log; X=$H/data/s67_extra.txt; L=$H/data/nw3_code_extra.txt
DM=~/FableGod/decision_map; KEEP=$H/data/s67_extra_before_nw3.txt; Q=$HOME/.local/share/quiet; ES=$HOME/EvalSuite/results
LG="${NW3_LASTGO:-2026-11-07 14:00:00}"; DL="${NW3_DEADLINE:-2026-11-07 15:00:00}"
LASTGO=$(date -j -f "%Y-%m-%d %H:%M:%S" "$LG" +%s)
P49=$(cat $ES/q49.pid 2>/dev/null)
say() { echo "[nw3_first] $* $(date '+%a %H:%M:%S')" >> $LOG; }
kids() { local p=$1 c; for c in $(pgrep -P $p); do kids $c; echo $c; done; }
SAVED=
stopall() {   # once: stop my runs (TERM, then KILL if frozen; never SIGCONT), put s67_extra.txt back, unlock
  [ -n "$DONE_STOP" ] && return; DONE_STOP=1; trap - EXIT INT TERM HUP
  for c in $(kids $$); do kill -TERM $c 2>/dev/null; done; sleep 5
  for c in $(kids $$); do ps -o stat= -p $c 2>/dev/null | grep -q T && kill -KILL $c 2>/dev/null; done
  [ -n "$SAVED" ] && cp $KEEP $X && say "s67_extra.txt put back"
  peer unlock >> $LOG 2>&1; say "ended ($1)"
}
trap 'stopall "exit"' EXIT; trap 'stopall "stopped"; exit 1' INT TERM HUP
grep -q "NEVER-WAIT v3 (b)" $DM/dm_common.py && grep -q "nw3_mask" $DM/dm_ablations.py || { say "nw3 is not installed in the map: nothing run"; exit 1; }
[ -n "$P49" ] || { say "no runner 49 pid in $ES/q49.pid at arming: nothing run (re-arm by hand)"; exit 1; }
alive49() { kill -0 $P49 2>/dev/null || { [ -f $ES/q49.pid ] && kill -0 "$(cat $ES/q49.pid 2>/dev/null)" 2>/dev/null; }; }
lid_closed() { ioreg -r -k AppleClamshellState -d 1 | grep -q '"AppleClamshellState" = Yes'; }
why_not() {   # empty = clear
  local pl; pl=$(peer ls 2>/dev/null | grep -v "^You:")
  if echo "$pl" | grep -qE "quiet lock until|benchmarking: quiet lock|waiting for a quiet window"; then echo "a quiet window (others)"
  elif echo "$pl" | grep "shared run" | grep -oE "MEM ~?[0-9]+" | tr -d "~" | awk '$2 > 5 {f = 1} END {exit !f}'; then echo "another session's shared run > 5 GB"
  elif echo "$pl" | sed -n 's/.*shared run[^:]*: about [0-9]*% CPU, \([0-9]*\)% GPU.*/\1/p' | awk '$1 >= 50 {f = 1} END {exit !f}'; then echo "another session's shared run >= 50 % GPU"
  elif [ -e $Q/PAUSE ] || [ -e $Q/HOLD ]; then echo "PAUSE / HOLD"
  elif lid_closed; then echo "lid closed"; fi
}
say "armed: runner 49 = pid $P49 (q49.pid); then $(grep -v '^#' $L | awk '{print $1}' | tr '\n' ' '); last start $(date -r $LASTGO '+%a %H:%M'), hard stop $DL"

# 1. runner 49's end
while alive49; do
  [ $(date +%s) -ge $LASTGO ] && { say "runner 49 is still up at the last start: nothing run"; exit 1; }
  sleep 5
done
say "runner 49 ended (pid $P49 gone; q49.pid $([ -f $ES/q49.pid ] && echo "holds $(cat $ES/q49.pid)" || echo gone))"

# 2. the claim, at the first clear moment
w0=
while :; do
  [ $(date +%s) -ge $LASTGO ] && { say "no clear moment by the last start: nothing run"; exit 1; }
  w=$(why_not); [ -z "$w" ] && break
  [ "$w" != "$w0" ] && say "waiting: $w"; w0=$w; sleep 5
done
if peer lock share 3m --cpu 200 --gpu 100 "MEM 18 GB: Breakthrough nw3 code arms, first after runner 49 (NewIdeas 7e74d6c); flips/KL, no timing" >> $LOG 2>&1
then say "claimed the GPU (share lock 3 min, MEM 18 GB); the runner's own lock follows"
else say "claim lock not granted: the runner waits its turn"; fi

# 3. the runner (S67_KEEPLOCK: one lock from arm to arm)
cp $X $KEEP && SAVED=1
{ grep -v '^#' $L; echo "ALONE 0 00:00"; } > $X
now="$(date '+%Y-%m-%d %H:%M:%S')"
S67_KEEPLOCK=1 S67_START="$now" S67_LASTGO="$LG" S67_DEADLINE="$DL" S67_XALONE="$now" bash $H/scripts/dm_s7/s67_slot.sh & wait $!
say "runner ended (rc $?)"
cp $KEEP $X && SAVED= && say "s67_extra.txt put back"
say "read-out: $(grep -E "^(\[s67\] read-out: )?VERDICT2? qom_0_live_ball(_c208)?_nw3c?\+code" $H/data/s67_slot.log | tail -6 | cut -c1-170 | tr '\n' ' ')"
touch $H/data/nw3_first.DONE
exit 0
