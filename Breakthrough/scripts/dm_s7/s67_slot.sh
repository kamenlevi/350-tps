#!/bin/bash
# Map screens 6 + 7 + Fable C's 1(b) / 1(c) in one share-lock batch (Breakthrough, Wed 2026-11-04 15:5x; the orchestrator
# 14:3x + 15:3x; NewIdeas 14:5x for s7_ref3). Pre-registered in SCOREBOARD "MAP SCREENS 6 + 7" (614e16c) and its 15:5x
# addendum. Run ATTACHED (Bash run_in_background), so each share lock sees this session's processes.
#   Order (the orchestrator 15:0x): qom_0_live_ball_c147_t3 (6), s7_ref, s7_ref3, s7_cal, s7_cal_all, q1u_0.9_live_bonus9g
#   (1b), qom_0.5_live_bonus5g (1c), then s7_trl. Start 20:00 (after BigMoE's quiet lever 2 arms, ~19:00-19:35, if they
#   slip). One map process per arm (the model loads in ~1 s), so the clock rules hold per arm:
#   - an arm starts only if the clock is before LASTGO (23:10) and its expected minutes (est, from the 14:48 smoke and
#     earlier full runs, with margin) end by DEADLINE (23:30); the first arm in order that fits goes next;
#   - DEADLINE is a hard stop (RELAX's quiet arms, MEM 34-42 GB, take the GPU at 23:30); arms that don't fit are left for
#     Thu morning beside T0 (the orchestrator's night order).
#   s7_trl goes only when Fit12's TRL store is whole (dm_t3.trl_gate); until then the next arm that fits goes, and s7_trl
#   is re-checked each time (every 2 min once it is the only arm left that fits).
#   Last, optional (NewIdeas 16:5x, the orchestrator's OK; Wed 17:0x): qom_0_live_ball_c147_t3+dense3 = screen 6 + Leap's
#   DENSE-3 (install_dense3.sh; smoke 17:00), est 10 min; it runs after 1(c) if s7_trl's store is not whole yet.
# Clear = no map process, no other session's quiet window held or waited for, no other session's shared run over 5 GB (by
# day one > 5 GB job at a time), lid open, no PAUSE, NO-SWAP >= 25 GB: 3 clear
# checks 10 s apart before the first arm and after any stop, 1 between arms. Share lock per arm, MEM 18 GB. Guards every
# 15 s: swap +2 GB, others' quiet window (3 strikes), lid closed (3 strikes), PAUSE over 5 min, DEADLINE: each stops the
# arm (a stopped arm writes nothing; it is retried from its start if it still fits). At most 14 runs.
# Read-outs: NewIdeas' map_kl.py (read-only use; prints) for screens 6 + 7 vs C; dm_screen_read.py for 6 vs C, and --null
# (+0.1 points vs the ungated twin, BYTES10.md:255-260) for 1(b) vs q1u_0.9_live and 1(c) vs qom_0.5_live.
# Override the clock at arming: S67_START / S67_LASTGO / S67_DEADLINE = "YYYY-mm-dd HH:MM:SS".
DM=~/FableGod/decision_map; PY=~/BigMoE/.venv/bin/python; LOG=~/Breakthrough/data/s67_slot.log; Q=$HOME/.local/share/quiet
ARMS="qom_0_live_ball_c147_t3 s7_ref s7_ref3 s7_cal s7_cal_all q1u_0.9_live_bonus9g qom_0.5_live_bonus5g s7_trl qom_0_live_ball_c147_t3+dense3"
D3=qom_0_live_ball_c147_t3+dense3; D3SHA=ec71be4478bc606f   # Leap's dense3.py as smoked (17:00)
est() { case $1 in s7_cal_all) echo 35;; s7_ref3|$D3) echo 10;; s7_trl|s7_cal) echo 7;; q1u_0.9_live_bonus9g|qom_0.5_live_bonus5g) echo 5;; *) echo 6;; esac; }
ts() { date -j -f "%Y-%m-%d %H:%M:%S" "$1" +%s; }
START=$(ts "${S67_START:-2026-11-04 20:00:00}"); LASTGO=$(ts "${S67_LASTGO:-2026-11-04 23:10:00}")
DEADLINE=$(ts "${S67_DEADLINE:-2026-11-04 23:30:00}")
say() { echo "[s67] $* $(date '+%a %H:%M:%S')" >> $LOG; }
swap_mb() { sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
noswap() { vm_stat | awk '/page size of/ {ps=$8} /^Pages (free|speculative|purgeable):/ || /^File-backed pages:/ {v=$NF; sub("[.]","",v); s+=v} END {printf "%d", s*ps/1e9}'; }
quiet_others() { peer ls 2>/dev/null | grep -v "^You:" | grep -qE "quiet lock until|benchmarking: quiet lock|waiting for a quiet window"; }
big_others() { peer ls 2>/dev/null | grep -v "^You:" | grep "shared run" | grep -oE "MEM [0-9]+ GB" | awk '$2 > 5 {f = 1} END {exit !f}'; }
lid_closed() { ioreg -r -k AppleClamshellState -d 1 | grep -q '"AppleClamshellState" = Yes'; }
kill_tree() { local p=$1 c; for c in $(pgrep -P $p); do kill_tree $c; done; kill -TERM $p 2>/dev/null; }
why_not() {
  if pgrep -f "run_ma[p].py" > /dev/null; then echo "a map process is running"
  elif quiet_others; then echo "a quiet window (others)"; elif big_others; then echo "another session's shared run > 5 GB"
  elif lid_closed; then echo "lid closed"
  elif [ -e "$Q/PAUSE" ]; then echo "PAUSE"; elif [ "$(noswap)" -lt 25 ]; then echo "NO-SWAP < 25 GB"; fi
}
trl_whole() { (cd $DM && DM_TRL_FALLBACK= $PY -c "import dm_t3; dm_t3.trl_gate([7, 18, 30, 41], 'mix')" > /dev/null 2>&1); }
nwin() { [ -f $DM/out/$1.json ] && $PY -c "import json; d = json.load(open('$DM/out/$1.json')); print(sum(1 for v in d.values() if isinstance(v, dict) and 'tk' in v))" 2>/dev/null || echo 0; }
todo() { local a; for a in $ARMS; do [ "$(nwin $a)" = 36 ] || echo -n "$a "; done; }
pick_next() {   # the first arm in order that is not done, fits the clock, and (s7_trl) whose store is whole; sets PICK, TRLWAIT
  local a now=$(date +%s); PICK=; TRLWAIT=0
  for a in $(todo); do
    [ $((now + $(est $a) * 60)) -le $DEADLINE ] || continue
    if [ $a = s7_trl ] && ! trl_whole; then TRLWAIT=1; continue; fi
    PICK=$a; return
  done
}
for n in s7_trl s7_ref3 q1u_0.9_live_bonus9g qom_0.5_live_bonus5g qom_0_live_ball_c147_t3 dense3; do
  grep -qF "\"$n\"" $DM/dm_ablations.py || { say "$n is not in dm_ablations.py (scripts/dm_s7/install_s7.sh, install_late.sh, install_dense3.sh); not run"; exit 1; }
done
say "armed (the orchestrator 14:3x / 15:3x, NewIdeas 14:5x / 16:5x): $ARMS; start >= $(date -r $START '+%a %H:%M'), no new arm after $(date -r $LASTGO '+%a %H:%M'), hard stop $(date -r $DEADLINE '+%a %H:%M')"
while [ $(date +%s) -lt $START ]; do sleep 30; done
cd $DM || exit 1
need=3; runs=0; last=
while :; do
  [ -z "$(todo)" ] && break
  [ $(date +%s) -ge $LASTGO ] && { say "23:10 (LASTGO): no new arm; left: $(todo)"; break; }
  pick_next
  if [ -z "$PICK" ]; then
    [ $TRLWAIT = 1 ] || { say "nothing left fits by the hard stop; left: $(todo)"; break; }
    [ "$last" = trl ] || say "waiting: s7_trl is the only arm that fits, and Fit12's TRL store is not whole yet"
    last=trl; sleep 120; continue
  fi
  w=$(why_not)
  if [ -n "$w" ]; then need=3; [ "$w" != "$last" ] && say "waiting: $w"; last=$w; sleep 10; continue; fi
  need=$((need - 1)); [ $need -gt 0 ] && { sleep 10; continue; }
  last=; runs=$((runs + 1)); [ $runs -gt 14 ] && { say "14 runs used; left: $(todo)"; break; }
  peer lock share $(( $(est $PICK) + 10 ))m --cpu 200 --gpu 100 "Breakthrough map screens 6 + 7 + 1(b)/(c) (the orchestrator 14:3x / 15:3x): MEM 18 GB (flips / KL, no timing): $PICK" >> $LOG 2>&1 \
    || { say "share lock not granted"; need=3; sleep 30; continue; }
  S0=$(swap_mb); say "go $PICK (est $(est $PICK) min; NO-SWAP $(noswap) GB, swap $S0 MB)"
  [ "$PICK" = "$D3" ] && say "Leap's dense3.py sha256 $(shasum -a 256 ~/Leap/scripts/dense3.py | cut -c1-16) (smoked: $D3SHA)"
  $PY run_map.py $PICK --max 12 --skip-done >> $LOG 2>&1 & P=$!
  bad=0; pz=0; stopped=
  while kill -0 $P 2>/dev/null; do
    sleep 15; w=
    [ $(date +%s) -ge $DEADLINE ] && { stopped="the 23:30 hard stop"; kill_tree $P; break; }
    [ $(( $(swap_mb) - S0 )) -gt 2048 ] && { stopped="swap grew > 2 GB"; kill_tree $P; break; }
    if [ -e "$Q/PAUSE" ]; then pz=$((pz + 1)); else pz=0; fi
    if quiet_others; then w="a quiet window (others)"; elif lid_closed; then w="lid closed"; elif [ $pz -ge 20 ]; then w="PAUSE over 5 min"; fi
    if [ -n "$w" ]; then bad=$((bad + 1)); else bad=0; fi
    [ $bad -ge 3 ] && { stopped="$w"; kill_tree $P; break; }
  done
  wait $P 2>/dev/null; rc=$?; peer unlock >> $LOG 2>&1
  if [ -n "$stopped" ]; then need=3; say "stopped $PICK for: $stopped"; else need=1; fi
  say "$PICK ended (rc $rc, $([ "$(nwin $PICK)" = 36 ] && echo 'done, 36 windows' || echo 'NOT done')); left: $(todo); unlocked"
  [ $(date +%s) -ge $DEADLINE ] && break
done
say "batch over; left: $(todo)"
echo "[s67] map_kl.py (NewIdeas, read-only use): C, screen 6, screen 7" >> $LOG
KL=$($PY ~/NewIdeas/scripts/map_kl.py qom_0_live_bq_c147_t3 qom_0_live_ball_c147_t3 s7_ref s7_ref3 s7_trl s7_cal s7_cal_all $D3 2>&1); echo "$KL" >> $LOG
if [ "$(nwin $D3)" = 36 ] && [ "$(nwin qom_0_live_ball_c147_t3)" = 36 ]; then   # NewIdeas QUEUE 16:5x: INVALID rule, then code flips
  D3C=$($PY ~/Breakthrough/scripts/dm_s7/dense3_check.py $D3 qom_0_live_ball_c147_t3 2>&1); echo "$D3C" >> $LOG
  say "read-out DENSE-3: $(echo "$D3C" | grep '^VERDICT' || echo 'INVALID check failed'); $(echo "$KL" | grep -F "| $D3 |" | awk -F'|' '{split($3, a, "/"); if (a[1] !~ /[0-9]/) {print "no map_kl number"; exit} f = a[1] + 0; print (f <= 1.34 ? "PASS" : f <= 2.01 ? "BETWEEN" : "FAIL") " on code flips " f " % (PASS <= 1.34, BETWEEN <= 2.01)"}')"
fi
rd() { [ "$(nwin $1)" = 36 ] || return; $PY $DM/dm_screen_read.py "$@" >> $LOG 2>&1; say "read-out: $(grep '^VERDICT' $DM/out/SCREEN_read_$1.txt 2>/dev/null || echo "$1 none")"; }
rd qom_0_live_ball_c147_t3 qom_0_live_bq_c147_t3
rd q1u_0.9_live_bonus9g q1u_0.9_live 0.1 --null
rd qom_0.5_live_bonus5g qom_0.5_live 0.1 --null
say "done"
