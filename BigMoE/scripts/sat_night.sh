#!/bin/bash
> (a quote from the project owner, kept private)
# 300"): the stacked FAST headline. Arms on scripts/r57_screen_fast.py (the merged FAST screen; qall = its flags off), C 224 by
# NO-SWAP, 12 HumanEval + 4 chat (ifeval 1220 / 1561, multi de3 / zh15), a palindrome with three qall passes:
#   qall / stack / qallm / stackb / qallb      (the stack's pair mean is centred on qallm; the noise floor from the qall passes)
# stack = qall + SN_STACK (default FAST-NAX + DN-KS + GDN lazy + CD16 + FAST-tax; the arming line drops what failed the Fri
# pre-flight). Passes overlapping a fanwatch freeze are dropped and listed. The stack's env is written to
# data/stack/stack_env.txt for EvalSuite's same-scores run on exactly that stack.
# Lines (pre-registered Fri 08:3x, before arming; per domain, pair-mean geo steady tok/s, stack vs qall):
#   PASS    = code (12 HumanEval) >= +20 % AND chat (4) >= -3 %
#   KILL    = code < +10 %
#   BETWEEN = otherwise
#   Kept per check and tokens per task are reported beside (CD16 keeps comment rows; FAST-NAX moves the exact base), and the
#   adoption gate stays EvalSuite's same-scores. Below C 224 the verdict is INDICATIVE.
# usage: SN_STACK=... NOTBEFORE=hh:mm NOTAFTER=hh:mm NOWAIT45=1 GAP0=0 GAP=0 MARGIN=4 bash scripts/turn45.sh 33 40 "..." \
#   /bin/bash scripts/sat_night.sh   -> data/sat/sat.log, data/sat/sat_report.txt
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "${SN_ROOT:-$HOME/BigMoE}" || exit 1
mkdir -p data/sat data/stack data/r57/snap
LOG="$PWD/data/sat/sat.log"
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
STACK=${SN_STACK-R57_NAX=1,REF2_NAX_1CQ=1,REF2_DN_KS=1,REF2_GDN_LAZY=1,R57_INERT=CD16,R57_FASTTAX=1}
avail_gb() { vm_stat | awk '/page size of/ {ps=$8} /^Pages (free|speculative|purgeable):/ || /^File-backed pages:/ {v=$NF; sub("[.]","",v); s+=v} END {printf "%.1f", s*ps/1e9}'; }
A=${SN_AVAIL:-$(avail_gb)}
fits() { awk -v a="$A" -v n="$1" 'BEGIN {exit !(n <= a)}'; }
CC=; for c in 224:45.2 208:43.1 192:41.0 176:38.9 160:36.7; do fits ${c#*:} && { CC=${c%%:*}; break; }; done
[ -z "$CC" ] && { say "NO-SWAP $A GB < 36.7: nothing fits, nothing runs"; exit 0; }
cp scripts/r57_screen_fast.py data/r57/snap/r57_screen_sat.py && cp scripts/relax_delta.py scripts/relax_span.py scripts/inert_span.py \
  data/r57/snap/ && cp scripts/c45_runner.sh data/r57/snap/c45_runner_sat.sh || exit 2
RUN="/bin/bash data/r57/snap/c45_runner_sat.sh"
export C45_OUT="$PWD/data/sat" C45_SWAP0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print $6 / 1024}') C45_ALARM=1200 \
  MG=${SN_MG:-4} C45_DEADLINE=${SN_DEADLINE:-$(date -v+40M +%H%M)} C45_SCREEN=data/r57/snap/r57_screen_sat.py C45_REFTOK=
K="humaneval/HumanEval/68,humaneval/HumanEval/16,humaneval/HumanEval/91,humaneval/HumanEval/6,humaneval/HumanEval/79"
K="$K,humaneval/HumanEval/19,humaneval/HumanEval/161,humaneval/HumanEval/17,humaneval/HumanEval/56,humaneval/HumanEval/141"
K="$K,humaneval/HumanEval/101,humaneval/HumanEval/63,ifeval/1220,ifeval/1561,multi/de3,multi/zh15"
QA="BIGMOE_EXT_BUILD=build_qom,R57_REFTOK=,R57_FAST=QOM,R57_D17=1,R57_D7B=code,R57_HC8=1,REF2_HC8_FAST=1,R57_DNR=1,R57_HCB=1"
QA="$QA,REF2_SMALL_NATIVE=1,R57_D7BNAX=1,REF2_OOO_1C=1"
printf '%s\n' "# Sat 7 Nov stacked FAST (BigMoE sat_night.sh, $(git rev-parse --short HEAD)): screen scripts/r57_screen_fast.py; env (comma list):" \
  "$QA,$STACK" > data/stack/stack_env.txt
rm -f data/r57/st*_${CC}_*
say "stacked FAST start (pid $$, NO-SWAP $A GB -> C $CC, deadline $C45_DEADLINE, stack '$STACK')"
for a in "stq:$QA" "sts:$QA,$STACK" "stqm:$QA" "stsb:$QA,$STACK" "stqb:$QA"; do
  R57_KEYS=$K C45_ARMS="${a%%:*}_$CC:$CC:${a#*:}" $RUN
  say "${a%%:*} rc=$?"
done
"${SN_PY:-$HOME/BigMoE/.venv/bin/python}" -I - "$CC" "$(date +%F)" "${SN_FANLOG:-$HOME/Library/Logs/fanwatch.log}" >> "$LOG" 2>&1 <<'EOF'
import datetime as D, json, math, re, statistics as S, sys
C, day, fanlog = sys.argv[1], sys.argv[2], sys.argv[3]
g = lambda xs: math.exp(sum(map(math.log, xs)) / len(xs)) if xs else float("nan")
win, t0 = [], None
try:
    for ln in open(fanlog):
        m = re.match(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (froze|cool)", ln)
        if m and m.group(1).startswith(day):
            t = D.datetime.fromisoformat(m.group(1))
            if m.group(2) == "froze":
                t0 = t
            elif t0 is not None:
                win.append((t0, t)); t0 = None
except OSError:
    pass
arm_t = {}
for ln in open("data/sat/c45.log"):
    m = re.match(r"(\d\d:\d\d:\d\d) (run|done) (\S+)", ln)
    if m:
        arm_t.setdefault(m.group(3), {})[m.group(2)] = D.datetime.fromisoformat(f"{day} {m.group(1)}")
hit = {t for t, v in arm_t.items() if "run" in v and "done" in v and any(a < v["done"] and b > v["run"] for a, b in win)}
P = {"qall": ("stq", "stqm", "stqb"), "stack": ("sts", "stsb")}
runs = {}
for t in sum(P.values(), ()):
    try:
        runs[t] = {r["key"]: r for r in json.load(open(f"data/r57/{t}_{C}_runs.json"))}
    except OSError:
        runs[t] = {}
ok = lambda t, k: k in runs[t] and "PAUSED" not in runs[t][k].get("bad", "") and f"{t}_{C}" not in hit
kept = lambda r: r["kept"] if isinstance(r["kept"], (int, float)) else S.mean(r["kept"])
dom = lambda k: "code" if k.startswith("humaneval") else "chat"
def pm(ps, f, d=None):
    out = {}
    for k in set().union(*[runs[t] for t in ps]):
        if d and dom(k) != d:
            continue
        v = [f(runs[t][k]) for t in ps if ok(t, k)]
        if v:
            out[k] = sum(v) / len(v)
    return out
def ratio(a, b):
    ks = [k for k in a if k in b]
    return (g([a[k] / b[k] for k in ks]), len(ks)) if ks else (float("nan"), 0)
L = [f"STACKED FAST, C {C}, 12 HumanEval + 4 chat (data/sat): qall / stack / qallm / stackb / qallb; stack env in "
     f"data/stack/stack_env.txt; freeze windows {[(a.strftime('%H:%M:%S'), b.strftime('%H:%M:%S')) for a, b in win]}; passes "
     f"dropped for a freeze: {sorted(hit) or 'none'}"]
for d in ("code", "chat"):
    for b, ps in P.items():
        tp = pm(ps, lambda r: r["tpsw"], d)
        L.append(f"{d:4s} {b:5s} geo steady {g(list(tp.values())):6.1f} tok/s over {len(tp)}; passes " +
                 ", ".join(f"{t} {g([r['tpsw'] for k, r in runs[t].items() if ok(t, k) and dom(k) == d]):.1f}" for t in ps) +
                 f"; kept per check {g(list(pm(ps, kept, d).values())):.2f}; tokens per task "
                 f"{S.median(pm(ps, lambda r: r['n'], d).values()) if pm(ps, lambda r: r['n'], d) else float('nan'):.0f}")
rc, nc = ratio(pm(P["stack"], lambda r: r["tpsw"], "code"), pm(P["qall"], lambda r: r["tpsw"], "code"))
rh, nh = ratio(pm(P["stack"], lambda r: r["tpsw"], "chat"), pm(P["qall"], lambda r: r["tpsw"], "chat"))
qm, qe = pm(("stqm",), lambda r: r["tpsw"]), pm(("stq", "stqb"), lambda r: r["tpsw"])
nf, nn = ratio(qm, qe)
L.append(f"noise floor: qall middle pass vs its end passes {100 * (nf - 1):+.1f} % over {nn}")
v = ("MISSING" if nc == 0 else "PASS" if rc >= 1.20 and (nh == 0 or rh >= 0.97) else "KILL" if rc < 1.10 else "BETWEEN")
L.append(f"Verdict stacked FAST (pre-registered Fri 08:3x){' INDICATIVE at C < 224' if int(C) < 224 else ''}: {v}: code "
         f"{100 * (rc - 1):+.1f} % over {nc}, chat {100 * (rh - 1):+.1f} % over {nh} (PASS code >= +20 % AND chat >= -3 %; "
         f"KILL code < +10 %)")
open("data/sat/sat_report.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))
EOF
say "report rc=$? (data/sat/sat_report.txt)"
say "stacked FAST end"
