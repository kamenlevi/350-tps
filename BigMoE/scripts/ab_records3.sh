#!/bin/bash
# THE records3 CONVERSION A/B (docs/PLAN_records3_convert.md section 4, pre-registered with the plan 1336043; M-27b's line in
# ~/NewIdeas/QUEUE.md; the orchestrator 11-03 17:4x-17:5x), the night after the conversion: one quiet ticket, the same C for
# every arm (AB_C, default 224), 40 prompts (chat23's 30, which hold S45's six, + 10 more HumanEval), CAP 256:
#   abB   converted (native+p11), M-17 sizes (laysz45_C)          abB2  converted, MoonShots' packed sizes (packed45_C)
#   flip  --inverse --md5 data/records3_md5_rowmajor.txt (match)  abA   row-major, M-17 sizes
#   flip  convert again (md5 == data/records3_md5_p11.txt)        abBr  converted, M-17 sizes (abA sits between two B's)
# AB_BRANCH=b (FLOOR night 2 cannot read the layout): stop after abA; the store stays row-major (re-convert Fri 15:00 if PASS).
# Every arm's tokens vs data/ab/ref_tokens.json (chat23's REF2-T tokens + u3c_224's HumanEval tokens, built at arming time).
# Lines (scripts/ab_report.py -> data/ab/ab_report.txt): mine = PASS if every token equals the references in every arm AND
# abB2's code SSD MB per kept token <= -10 % vs abA AND abB2's steady tok/s not below abA's; KILL if any token differs (->
# --inverse + md5: the store goes back to row-major) or code MB per kept token > -3 %; else BETWEEN. M-27b = PASS if tokens
# are bitwise AND code MB/kept <= -10 % AND median steady >= +3 %; KILL if any token differs, > -5 % or < +1 %.
# usage: inside turn45 (HAVE_LOCK=1 KEEP_LOCK=1), with frozen copies (data/r57/snap/*_ab.*); CLAUDE_PID set
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$HOME/BigMoE" || exit 1
mkdir -p data/ab
LOG="$HOME/BigMoE/data/ab/ab.log"
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
RUN="/bin/bash data/r57/snap/c45_runner_ab.sh"
export C45_SCREEN=data/r57/snap/r57_screen_ab.py C45_DEADLINE=${AB_DEADLINE:-0300} C45_OUT="$HOME/BigMoE/data/ab"
CC=${AB_C:-224}
R3=models/bare/records3
PY="$HOME/BigMoE/.venv/bin/python"
TOOL="$HOME/Leap/scripts/convert_records_p11.py"
LOCKF="$HOME/.claude-peers/locks/${CLAUDE_PID}.json"
keepalive() { "$PY" -I -S -c '
import json, os, sys, time
p = sys.argv[1]
d = json.load(open(p))
if d.get("mode") != "quiet" or d.get("until", 0) <= time.time(): sys.exit(1)
d["active_at"] = time.time(); t = "%s.tmp%d" % (p, os.getpid()); json.dump(d, open(t, "w")); os.replace(t, p)' "$LOCKF"; }
layout() { "$PY" -I -c "
import json; ls = {r.get('layout', 'row-major') for r in json.load(open('$R3/index.json'))['layers'].values()}
print(ls.pop() if len(ls) == 1 else 'mixed')"; }
K="ifeval/1220,ifeval/1561,ifeval/3280,multi/ar21,multi/ar22,multi/bg0,multi/bg2,multi/de3,multi/de4,multi/es10,multi/es11"
K="$K,multi/fr7,multi/fr8,multi/ja18,multi/ja19,multi/ru12,multi/ru13,multi/zh15,multi/zh16,agent/bash17,agent/edit00"
K="$K,agent/text23,agent/write11,agent/bash18,humaneval/HumanEval/68,humaneval/HumanEval/91,math500/test/prealgebra/1640.json"
K="$K,math500/test/algebra/694.json,math500/test/algebra/1282.json,gsm8k/708,humaneval/HumanEval/16,humaneval/HumanEval/6"
K="$K,humaneval/HumanEval/79,humaneval/HumanEval/19,humaneval/HumanEval/161,humaneval/HumanEval/17,humaneval/HumanEval/56"
K="$K,humaneval/HumanEval/141,humaneval/HumanEval/101,humaneval/HumanEval/63"
REF="$HOME/BigMoE/data/ab/ref_tokens.json"
PK="$HOME/BigMoE/data/seed45/packed45_$CC.json"
arm() {  # arm TAG [ENV...]: one arm on the store as it is
  local tag=$1; shift
  R57_KEYS=$K MG=${AB_MG:-6} C45_ALARM=900 C45_REFTOK="$REF:gate+t" C45_ARMS="${tag}_$CC:$CC${1:+:$1}" $RUN
  say "$tag rc=$? (store $(layout))"
}
say "A/B start (pid $$, C $CC, branch ${AB_BRANCH:-a}, store $(layout))"
[ "$(layout)" = native+p11 ] || { say "the store is not native+p11: STOP"; exit 2; }
[ -s "$REF" ] && [ -s "$PK" ] || { say "missing $REF or $PK: STOP"; exit 2; }
[ -s data/records3_md5_rowmajor.txt ] && [ -s data/records3_md5_p11.txt ] || { say "missing the conversion's md5 lists: STOP"; exit 2; }
arm abB
arm abB2 "BIGMOE_TIER_SIZES=$PK"
keepalive || { say "lock gone before the flip: STOP (store stays native+p11)"; exit 3; }
say "flip 1: --inverse (md5 must match the originals)"
"$PY" "$TOOL" "$R3" --inverse --md5 data/records3_md5_rowmajor.txt --yes >> "$LOG" 2>&1 || { say "inverse FAILED rc=$?: STOP (look before anything else)"; exit 4; }
grep -q "md5 after --inverse: 48 of 48 files match" "$LOG" || { say "the md5s after --inverse do not all match: STOP"; exit 4; }
keepalive
arm abA
if [ "${AB_BRANCH:-a}" = a ]; then
  keepalive || { say "lock gone before flip 2: the store stays row-major (re-convert by hand)"; exit 3; }
  say "flip 2: convert again"
  "$PY" "$TOOL" "$R3" --yes >> "$LOG" 2>&1 || { say "re-conversion FAILED rc=$?: STOP"; exit 4; }
  (cd "$R3" && md5 -r L*.bin) | diff -q - data/records3_md5_p11.txt > /dev/null || { say "re-converted md5s differ from the first conversion: STOP"; exit 4; }
  say "re-conversion md5 == the first conversion"
  keepalive
  arm abBr
fi
"$PY" scripts/ab_records3_report.py "$CC" >> "$LOG" 2>&1; say "report rc=$? (data/ab/ab_report.txt)"
say "A/B end (store $(layout))"
