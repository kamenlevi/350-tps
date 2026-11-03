#!/bin/bash
# The records3 conversion's token checks for BigMoE (PLAN_records3_convert section 5 step 3; HANDOVER Tue 3 Nov 17:3x).
# REF2-T re-decodes six IFEval rows and their tokens are compared with reference runs' rows: the two IFX reproduction
# rows (ifeval/3409, ifeval/2439) and four 308-525-token IFX rows (results/r3check_keys.txt; 1,614 tokens stored).
# Check 1 = before the conversion (row-major store), check 2 = after it (converted store). Both use variant ref2tn =
# ref2t on snap/leap-90456ce (Leap's per-layer layout router + tierglu_3cn with the p11 dequant; its only default that
# faff8e5 lacks is gdn_exact, bitwise by Leap), on a snapshot of BigMoE's layout-patched engine. Only the store differs
# between them, so check 2 == check 1 is the conversion's test; check 1 == ref2t.r2 (the stored IFX rows,
# snap/bigmoe-6c64148 + snap/leap-faff8e5) is information on the newer code. Everything else is runner 38's ref2t.r2
# recipe (TIERENV, C 192). Shared GPU, attached, in the orchestrator's slot.
#   tools/r3check.sh <bigmoe snap dir> <ref2tn.rN> <rowmajor|converted> <ref run[,ref run]> ["extra stage env k=v,k=v"]
#   check 1: tools/r3check.sh snap/bigmoe-<sha7> ref2tn.r1 rowmajor ref2t.r2
#   check 2: tools/r3check.sh snap/bigmoe-<sha7> ref2tn.r2 converted ref2tn.r1,ref2t.r2
# Exit: 0 = token-identical to the FIRST ref run on all six rows, 5 = different, 2 = refused (no snapshot or variant,
# the store not as expected, the run exists), else the stage's rc. Log: results/r3check.log.
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$HOME/EvalSuite" || exit 1
SNAP=$1; RUN=$2; WANT=$3; REFS=$4; EXTRA=$5
LOG=results/r3check.log
R3IDX=$HOME/BigMoE/models/bare/records3/index.json
TIERENV="BIGMOE_TIER=4433333333,BIGMOE_TIER_GLU=3c,BIGMOE_TIER_CL=112"   # runner 38's, for ref2t.r2
say() { echo "$(date +%H:%M:%S) $*" | tee -a "$LOG"; }
store() { if grep -q '"layout"' "$R3IDX"; then echo converted; else echo rowmajor; fi; }
[ -f "$SNAP/SOURCE" ] && [ -d "$SNAP/bigmoe" ] || { say "no snapshot at $SNAP (SOURCE + bigmoe/)"; exit 2; }
grep -q '"ref2tn"' evalsuite/model.py || { say "variant ref2tn is not in evalsuite/model.py yet (add it once runners 40 / 41 end)"; exit 2; }
case "$RUN" in ref2tn.r[1-9]) ;; *) say "run name must be ref2tn.r1 .. ref2tn.r9, not $RUN"; exit 2 ;; esac
[ -e "results/$RUN" ] && { say "results/$RUN exists: take the next run name"; exit 2; }
[ -n "$REFS" ] || { say "no reference run given"; exit 2; }
[ "$(store)" = "$WANT" ] || { say "records3 is $(store), this check wants $WANT: not running"; exit 2; }
while [ -e "$HOME/.local/share/quiet/PAUSE" ] || [ -e "$HOME/.local/share/quiet/HOLD" ]; do sleep 30; done
export EVALSUITE_BIGMOE_CODE="$SNAP"
say "r3check $RUN: records3 $(store); snapshot $SNAP ($(head -c 140 "$SNAP/SOURCE")); refs $REFS; extra env: ${EXTRA:-none}"
EVALSUITE_STAGE_ENV="$TIERENV${EXTRA:+,$EXTRA}" ./bin/evalsuite gpu decode "$RUN" --sets ifeval,ifevalx \
  --keys results/r3check_keys.txt --chunk-minutes 30 --C 192 --share >> "$LOG" 2>&1; rc=$?
say "decode $RUN rc=$rc"
[ "$rc" = 0 ] || exit "$rc"
.venv/bin/python - "$RUN" "$REFS" <<'EOF' 2>&1 | tee -a "$LOG"; r=${PIPESTATUS[0]}
import json, os, sys
run, refs = sys.argv[1], sys.argv[2].split(",")
keys = [l.strip() for l in open("results/r3check_keys.txt") if l.strip()]
def rows(v):
    p = os.path.join("results", v, "decode.jsonl")
    return {r["key"]: r for r in (json.loads(l) for l in open(p)) if "key" in r} if os.path.exists(p) else {}
got = rows(run)
if not all(k in got for k in keys):
    print(f"{run}: rows missing: {[k for k in keys if k not in got]}"); sys.exit(3)
first = None
for ref in refs:
    want = rows(ref)
    bad = [k for k in keys if k not in want or want[k]["completion_ids"] != got[k]["completion_ids"]]
    print(f"{run} vs {ref}: " + (f"DIFFERENT on {bad}" if bad else f"token-identical on {', '.join(keys)}")
          + f" ({sum(len(got[k]['completion_ids']) for k in keys)} tokens)")
    first = bad if first is None else first
sys.exit(5 if first else 0)
EOF
say "r3check $RUN end (rc $r)"
exit "$r"
