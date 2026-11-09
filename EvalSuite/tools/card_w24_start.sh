#!/bin/bash
# PREREG_card_gates amendment 12: start the w24 card arm in the queue owner's slot (NewIdeas 18:59: Tue ~01:30 if the env is
# ready, else the Tue-night slot). Waits until START, then for BigMoE's data/stack/card_w24_env.txt to be committed (tracked,
# equal to HEAD) and written after amendment 12; starts runner 61 only if that happens by LATEST, so the arm has its
# ~10-12 h before the 15:00 cutoff. Otherwise it starts nothing and says so.
# Test: W24S_START=<now> W24S_LATEST=<now + 2 min> W24S_ENV=<path> W24S_DRY=1 tools/card_w24_start.sh
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$HOME/EvalSuite" || exit 1
START=${W24S_START:-2026-11-10 01:25}
LATEST=${W24S_LATEST:-2026-11-10 05:00}
CUT=${W24S_CUTOFF:-2026-11-10 15:00}
ENVF=${W24S_ENV:-$HOME/BigMoE/data/stack/card_w24_env.txt}
L=${W24S_LOG:-results/card_w24_start.log}
log() { echo "$(date '+%m-%d %H:%M:%S') w24 start: $*" | tee -a "$L"; }
t_start=$(date -j -f "%Y-%m-%d %H:%M" "$START" +%s) || exit 2
t_late=$(date -j -f "%Y-%m-%d %H:%M" "$LATEST" +%s) || exit 2
t_reg=$(git log -1 --format=%ct d5429d4) || { log "amendment 12's commit d5429d4 is not in this repo"; exit 2; }
log "armed (pid $$): start after $START, env $ENVF committed in BigMoE and newer than amendment 12, latest $LATEST, cutoff $CUT"
while [ "$(date +%s)" -lt "$t_start" ]; do sleep 60; done
ready() {
  [ -s "$ENVF" ] || return 1
  [ "$(stat -f %m "$ENVF")" -gt "$t_reg" ] || return 1
  [ -n "${W24S_DRY:-}" ] && return 0
  git -C "$HOME/BigMoE" ls-files --error-unmatch "${ENVF#$HOME/BigMoE/}" > /dev/null 2>&1 || return 1
  git -C "$HOME/BigMoE" diff --quiet HEAD -- "${ENVF#$HOME/BigMoE/}"
}
until ready; do
  [ "$(date +%s)" -lt "$t_late" ] || { log "no committed env file by $LATEST: nothing started (the Tue-night slot)"; exit 3; }
  sleep 60
done
log "env ready: $(grep '^#' "$ENVF" | head -1 | cut -c1-160)"
if [ -n "${W24S_DRY:-}" ]; then log "DRY: would run CARD_TAG=w24 CARD_FENV=$ENVF CARD_CUTOFF=$CUT tools/day_runner61.sh"; exit 0; fi
CARD_TAG=w24 CARD_FENV="$ENVF" CARD_CUTOFF="$CUT" tools/day_runner61.sh
rc=$?
log "runner 61 (w24) ended rc=$rc"
exit "$rc"
