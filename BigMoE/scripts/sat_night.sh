#!/bin/bash
> (a quote from the project owner, kept private)
# 300"): the stacked FAST headline. Arms on scripts/r57_screen_fast.py (the merged FAST screen; qall = its flags off), C 224 by
# NO-SWAP, 12 HumanEval + 4 chat (ifeval 1220 / 1561, multi de3 / zh15), a palindrome with three qall passes:
#   qall / stack / qallm / stackb / qallb      (the stack's pair mean is centred on qallm; the noise floor from the qall passes)
# stack = qall + SN_STACK (default FAST-NAX + DN-KS + GDN lazy + D7BNAX_32 + FAST-tax; CD16 dropped Fri 16:0x after its MBPP12 quality KILL; the arming line drops what failed the Fri
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
STACK=${SN_STACK-R57_NAX=1,REF2_NAX_1CQ=1,REF2_DN_KS=1,REF2_GDN_LAZY=1,D7BNAX_32=1,R57_FASTTAX=1}   # Fri 16:0x: CD16 DROPPED (NewIdeas; MBPP12 quality KILL, c966c0d)
# stackr (the orchestrator Fri 08:4x: the shipping CODE config carries a relax gate): the stack with MoonShots' relax v2 (DELTA
# 0.5 + SPAN) IN PLACE OF CD16 (INERT asserts against both relaxed rules), = the pre-flight's clean f2k mix; 12 HumanEval only.
# Line (pre-registered Fri 08:4x, before arming): PASS = stackr >= stack x 1.03 on code (pair-mean geo steady), KILL = stackr <
# stack x 0.97, else BETWEEN; stackr vs qall, kept per check and tokens per task beside. Its env goes to data/stack/stackr_env.txt.
STACKR=${SN_STACKR-R57_NAX=1,REF2_NAX_1CQ=1,REF2_DN_KS=1,REF2_GDN_LAZY=1,D7BNAX_32=1,R57_FASTTAX=1,R57_RELAX_DELTA=0.5,R57_RELAX_SPAN=1}
# d7x (Leap Fri 08:4x, d7b_nax dd9066d3): qall + D7BNAX_32=1 (17-row D7b drafts as two qmm16c halves), 12 HumanEval only (D7b
# drafts code). Line (pre-registered Fri 08:5x): KEPT CLAUSE OK = kept per check within 1 % of qall's on code; tok/s beside
# (expected ~+2 %, under the noise floor: no speed verdict). D7BNAX_32=1 also rides in stack and stackr.
avail_gb() { vm_stat | awk '/page size of/ {ps=$8} /^Pages (free|speculative|purgeable):/ || /^File-backed pages:/ {v=$NF; sub("[.]","",v); s+=v} END {printf "%.1f", s*ps/1e9}'; }
A=${SN_AVAIL:-$(avail_gb)}
fits() { awk -v a="$A" -v n="$1" 'BEGIN {exit !(n <= a)}'; }
CC=; for c in 224:45.2 208:43.1 192:41.0 176:38.9 160:36.7; do fits ${c#*:} && { CC=${c%%:*}; break; }; done
[ -z "$CC" ] && { say "NO-SWAP $A GB < 36.7: nothing fits, nothing runs"; exit 0; }
cp scripts/r57_screen_fast.py data/r57/snap/r57_screen_sat.py && cp scripts/relax_delta.py scripts/relax_span.py scripts/inert_span.py \
  data/r57/snap/ && cp scripts/c45_runner.sh data/r57/snap/c45_runner_sat.sh || exit 2
# Fri 09:4x (EvalSuite's warning: the screen loads LIVE outside code, and Leap changed ref2.py / d7b_nax.py between processes
# this morning): freeze it for every arm of tonight's run. Copies of Leap's scripts + third_party, TrainLab's sticky and
# Breakthrough's keepset; the snapshot screen points at the copies (EvalSuite's own package and data paths stay live).
FZ="$PWD/data/r57/snap/frozen_sat"; rm -rf "$FZ"; mkdir -p "$FZ"
cp -R "$HOME/Leap/scripts" "$FZ/Leap_scripts" && cp -R "$HOME/Leap/third_party" "$FZ/Leap_third_party" \
  && cp -R "$HOME/TrainLab/sticky" "$FZ/TrainLab_sticky" && cp -R "$HOME/Breakthrough/keepset" "$FZ/Breakthrough_keepset" || exit 2
find "$FZ" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
sed -i '' -e "s#\"~/Leap/scripts\"#\"$FZ/Leap_scripts\"#g" -e "s#\"~/Leap/third_party\"#\"$FZ/Leap_third_party\"#g" \
  -e "s#\"~/TrainLab/sticky\"#\"$FZ/TrainLab_sticky\"#g" -e "s#\"/Users/kamen/Breakthrough/keepset\"#\"$FZ/Breakthrough_keepset\"#g" \
  data/r57/snap/r57_screen_sat.py
LIVE0=$(md5 -q "$HOME/Leap/scripts/ref2.py" "$HOME/Leap/scripts/d7b_nax.py" "$HOME/Breakthrough/keepset/qom_keep.py" | tr '\n' ' ')
say "frozen outside code in $FZ ($(grep -c frozen_sat data/r57/snap/r57_screen_sat.py) screen paths): ref2 / d7b_nax / qom_keep md5 $LIVE0"
RUN="/bin/bash data/r57/snap/c45_runner_sat.sh"
export C45_OUT="$PWD/data/sat" C45_SWAP0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print $6 / 1024}') C45_ALARM=1200 \
  MG=${SN_MG:-4} C45_DEADLINE=${SN_DEADLINE:-$(date -v+60M +%H%M)} C45_SCREEN=data/r57/snap/r57_screen_sat.py C45_REFTOK=
K="humaneval/HumanEval/68,humaneval/HumanEval/16,humaneval/HumanEval/91,humaneval/HumanEval/6,humaneval/HumanEval/79"
K="$K,humaneval/HumanEval/19,humaneval/HumanEval/161,humaneval/HumanEval/17,humaneval/HumanEval/56,humaneval/HumanEval/141"
K="$K,humaneval/HumanEval/101,humaneval/HumanEval/63,ifeval/1220,ifeval/1561,multi/de3,multi/zh15"
QA="BIGMOE_EXT_BUILD=build_qom,R57_REFTOK=,R57_FAST=QOM,R57_D17=1,R57_D7B=code,R57_HC8=1,REF2_HC8_FAST=1,R57_DNR=1,R57_HCB=1"
QA="$QA,REF2_SMALL_NATIVE=1,R57_D7BNAX=1,REF2_OOO_1C=1"
printf '%s\n' "# Sat 7 Nov stacked FAST (BigMoE sat_night.sh, $(git rev-parse --short HEAD)): screen scripts/r57_screen_fast.py; env (comma list):" \
  "$QA,$STACK,R57_QOM_SETS=humaneval,mbpp" > data/stack/stack_env.txt   # QOM on the code sets only (NewIdeas 70a4951, Fri 11:3x: the agent check FAILED, so no first-time QOM on math / chat)
printf '%s\n' "# Sat 7 Nov stacked FAST + relax v2 for CODE (BigMoE sat_night.sh, $(git rev-parse --short HEAD)): screen scripts/r57_screen_fast.py;" \
  "# env (comma list; R57_RELAX_LOG optional):" "$QA,$STACKR,R57_QOM_SETS=humaneval,mbpp" > data/stack/stackr_env.txt
KC=$(echo "$K" | tr ',' '\n' | grep '^humaneval/' | paste -sd, -)   # stackr runs the 12 HumanEval only (chat has no relax gate)
rm -f data/r57/st*_${CC}_*
say "stacked FAST start (pid $$, NO-SWAP $A GB -> C $CC, deadline $C45_DEADLINE, stack '$STACK')"
# SPLIT-NAX (NewIdeas Fri 10:0x, QUEUE item 2 ad24dd3): ssp = the stack + R57_QOM_SPLIT=0.99 on the 12 HumanEval, two passes placed
# symmetrically, SPEED ONLY (it stays out of the env files EvalSuite reads). Line (pre-registered Fri 10:1x, NewIdeas'): net
# pair-mean geo steady tok/s vs the stack on code: PASS >= +8 %, KILL < +3 %, else BETWEEN; kept recorded beside (no clause).
# Every arm carries R57_QCNT1C=1 (Leap's one-call counters: groups computed per check, for the bytes premise; the same small
# cost in every arm), so QAC = QA + the counter; the env files keep QA.
QAC="$QA,R57_QCNT1C=1"
RR="$QAC,$STACKR,R57_RELAX_LOG=$PWD/data/sat/stackr_relax.jsonl"
# NEVER-WAIT A/B (NewIdeas Fri 13:5x, QUEUE item 4 d3e845f; the map PASSed on code, Breakthrough 1d46c51): snv = the stack +
# R57_NEVERWAIT=1 + REF2_NEVERWAIT=1 (Leap's ref2 never-wait; bit check 4 CLEAN, c2e6a53) on the 12 HumanEval, two passes placed
# symmetrically like SPLIT-NAX, SPEED ONLY (it stays out of the env files EvalSuite reads). Line (pre-registered Fri 13:5x,
# NewIdeas', before arming): net pair-mean geo steady tok/s vs the stack on code: PASS >= +8 %, KILL < +3 %, else BETWEEN; kept
# recorded beside (no clause). Logged beside, per check (code, checks >= 2, medians): check ms, gate service, misses, stalled
# layer calls and eval wait for the stack and snv, and snv's never-wait counters (late groups / uses / mass, last-layer late
# uses, stalls), so the read can split "waits removed" from "late work added".
NWE="R57_NEVERWAIT=1,REF2_NEVERWAIT=1"
for t in stq sts str s7x ssp snv stqm snvb sspb s7xb strb stsb stqb snw; do rm -f data/r57/${t}_${CC}_*; done   # every tag tonight
# Fri 15:5x: SPLIT-NAX and NEVER-WAIT ran by day instead (scripts/fri_day.sh, data/fday, b3b1e68: both KILL vs the stack at
# C 224, -1.3 % / -2.8 %), so they leave tonight's palindrome (NewIdeas 15:2x); the report points there.
for a in "stq:$QAC" "sts:$QAC,$STACK" "str:$RR" "s7x:$QAC,D7BNAX_32=1" "stqm:$QAC" "s7xb:$QAC,D7BNAX_32=1" "strb:$RR" \
         "stsb:$QAC,$STACK" "stqb:$QAC"; do
  KK=$K; case "${a%%:*}" in str|strb|s7x|s7xb|ssp|sspb|snv|snvb) KK=$KC ;; esac
  R57_KEYS=$KK C45_ARMS="${a%%:*}_$CC:$CC:${a#*:}" $RUN
  say "${a%%:*} rc=$?"
done
# never-wait's speed ceiling (the orchestrator Fri 09:0x; ~/FableGod/far/NEVERWAIT_TEST.md section 3, Method B, no new code):
# the STACK with R57_WARMSPLIT=4 on the 12 HumanEval, one pass after the palindrome: every 4th check from the 3rd runs its own
# full 16-row input cold, then warm with all its experts resident, both rolled back, before the real check commits.
# Line (pre-registered Fri 09:0x, before arming), with S = this arm's median gate service per live check:
#   PASS = median (cold16 - warm16) >= 0.6 x S; BETWEEN = 0.3-0.6 x S; KILL = < 0.3 x S (the wait is not where the logs say).
#   Caveat (section 3): a sample is a full 16-row check, heavier than the live ones (Wed: 602 vs 138 misses); the samples'
#   median misses are printed beside the live checks'. The ceiling ignores the late groups' own compute.
R57_KEYS=$KC C45_ARMS="snw_$CC:$CC:$QAC,$STACK,R57_WARMSPLIT=4" $RUN
say "snw rc=$?"
LIVE1=$(md5 -q "$HOME/Leap/scripts/ref2.py" "$HOME/Leap/scripts/d7b_nax.py" "$HOME/Breakthrough/keepset/qom_keep.py" | tr '\n' ' ')
[ "$LIVE1" = "$LIVE0" ] && say "live outside code unchanged during the run" \
  || say "NOTE: live outside code CHANGED during the run ($LIVE0 -> $LIVE1); every arm used the frozen copies"
"${SN_PY:-$HOME/BigMoE/.venv/bin/python}" -I - "$CC" "$(date +%F)" "${SN_FANLOG:-$HOME/Library/Logs/fanwatch.log}" >> "$LOG" 2>&1 <<'EOF'
import datetime as D, json, math, re, statistics as S, sys
C, day, fanlog = sys.argv[1], sys.argv[2], sys.argv[3]
g = lambda xs: (lambda ys: math.exp(sum(map(math.log, ys)) / len(ys)) if ys else float("nan"))([x for x in xs if x and x > 0])
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
P = {"qall": ("stq", "stqm", "stqb"), "stack": ("sts", "stsb"), "stackr": ("str", "strb"), "d7x": ("s7x", "s7xb"),
     "ssp": ("ssp", "sspb"), "snv": ("snv", "snvb")}
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
rr, nr = ratio(pm(P["stackr"], lambda r: r["tpsw"], "code"), pm(P["stack"], lambda r: r["tpsw"], "code"))
rq, _ = ratio(pm(P["stackr"], lambda r: r["tpsw"], "code"), pm(P["qall"], lambda r: r["tpsw"], "code"))
vr = "MISSING" if nr == 0 else ("PASS" if rr >= 1.03 else "KILL" if rr < 0.97 else "BETWEEN")
L.append(f"Verdict stackr (pre-registered Fri 08:4x){' INDICATIVE at C < 224' if int(C) < 224 else ''}: {vr}: code vs stack "
         f"{100 * (rr - 1):+.1f} % over {nr}, vs qall {100 * (rq - 1):+.1f} % (PASS >= +3 % vs stack; KILL < -3 %)")
rs_, ns_ = ratio(pm(P["ssp"], lambda r: r["tpsw"], "code"), pm(P["stack"], lambda r: r["tpsw"], "code"))
ks_, _ = ratio(pm(P["ssp"], kept, "code"), pm(P["stack"], kept, "code"))
vs_ = "MISSING" if ns_ == 0 else ("PASS" if rs_ >= 1.08 else "KILL" if rs_ < 1.03 else "BETWEEN")
def q1c(ts, i):   # per-check mean of Leap's one-call counter i over the clean passes (first check excluded), code prompts
    xs = []
    for t in ts:
        if f"{t}_{C}" in hit:
            continue
        try:
            xs += [c[i] for e in json.load(open(f"data/r57/{t}_{C}_checks.json")) if dom(e.get("key", "")) == "code"
                   and not e.get("paused") for c in e.get("q1c", [])[1:]]
        except OSError:
            pass
    return S.mean(xs) if xs else float("nan")
gs, gp = q1c(P["stack"], 2), q1c(P["ssp"], 2)
if ns_:
    L.append(f"Verdict SPLIT-NAX (pre-registered Fri 10:1x, NewIdeas){' INDICATIVE at C < 224' if int(C) < 224 else ''}: {vs_}: "
             f"tok/s {100 * (rs_ - 1):+.1f} % vs the stack on code over {ns_}, kept {100 * (ks_ - 1):+.1f} % (PASS >= +8 %, KILL < +3 %); "
             f"groups computed per check: stack {gs:.0f}, ssp {gp:.0f} ({gp / gs:.3f}x), split drops per check {q1c(P['ssp'], 3):.0f}")
else:
    L.append("SPLIT-NAX: not run tonight; run by day Fri 15:40 (data/fday, b3b1e68): KILL, -1.3 % vs the stack at C 224")
def pcm(ts, f, d="code"):   # median of a per-check field over the clean passes' checks >= 2 (steady, as tpsw), one domain
    xs = []
    for t in ts:
        if f"{t}_{C}" in hit:
            continue
        try:
            for e in json.load(open(f"data/r57/{t}_{C}_checks.json")):
                if dom(e.get("key", "")) == d and not e.get("paused"):
                    xs += [x for x in f(e)[2:] if x is not None]
        except (OSError, ValueError):
            pass
    return S.median(xs) if xs else float("nan")
rn_, nn_ = ratio(pm(P["snv"], lambda r: r["tpsw"], "code"), pm(P["stack"], lambda r: r["tpsw"], "code"))
kn_, _ = ratio(pm(P["snv"], kept, "code"), pm(P["stack"], kept, "code"))
vn_ = "MISSING" if nn_ == 0 else ("PASS" if rn_ >= 1.08 else "KILL" if rn_ < 1.03 else "BETWEEN")
if nn_:
    L.append(f"Verdict NEVER-WAIT (pre-registered Fri 13:5x, NewIdeas){' INDICATIVE at C < 224' if int(C) < 224 else ''}: {vn_}: "
             f"tok/s {100 * (rn_ - 1):+.1f} % vs the stack on code over {nn_}, kept {100 * (kn_ - 1):+.1f} % (PASS >= +8 %, KILL < +3 %)")
    L.append("  snv never-wait counters per check (medians): " + ", ".join(
        f"{n} {pcm(P['snv'], lambda e, i=i: [x[i] for x in e.get('nw', [])]):.1f}"
        for i, n in enumerate(("late groups", "late uses", "late mass", "last-layer late uses (dropped or waited)", "stalls"))))
else:
    L.append("NEVER-WAIT: not run tonight; run by day Fri 15:40 (data/fday, b3b1e68): KILL, -2.8 % vs the stack at C 224")
for b in ("stack",) + (("snv",) if nn_ else ()):
    L.append(f"  per check (code, checks >= 2, medians) {b:5s}: check {pcm(P[b], lambda e: e.get('ck', [])):.1f} ms, gate service "
             f"{pcm(P[b], lambda e: e.get('svc', [])):.1f} ms, misses {pcm(P[b], lambda e: e.get('miss', [])):.0f}, stalled layer "
             f"calls {pcm(P[b], lambda e: e.get('stl', [])):.1f}, eval wait {pcm(P[b], lambda e: e.get('wt', [])):.1f} ms")
r7, n7 = ratio(pm(P["d7x"], lambda r: r["tpsw"], "code"), pm(P["qall"], lambda r: r["tpsw"], "code"))
k7, _ = ratio(pm(P["d7x"], kept, "code"), pm(P["qall"], kept, "code"))
L.append(f"d7x kept clause (pre-registered Fri 08:5x): {'MISSING' if n7 == 0 else 'OK' if abs(k7 - 1) <= 0.01 else 'NOT OK'}: "
         f"kept {100 * (k7 - 1):+.2f} % vs qall on code over {n7} (within 1 %); tok/s {100 * (r7 - 1):+.1f} % (no speed verdict)")
try:                                                     # never-wait's speed ceiling (R57_WARMSPLIT samples of arm snw)
    ws = [s for e in json.load(open(f"data/r57/snw_{C}_warmsplit.json")) for s in e.get("samples", [])]
    ck = json.load(open(f"data/r57/snw_{C}_checks.json"))
    live = [(c, x) for e in ck if not e.get("paused") for c, x in zip(e.get("svc", []), e.get("miss", []))]
    S_ = S.median([c for c, _ in live]) if live else float("nan")
    d_ = [s["cold"][1] - w[1] for s in ws if s.get("cold") for w in s.get("warm", []) if w[0] == s["cold"][0]]
    mc = S.median([s["cold"][2] for s in ws if s.get("cold")]) if ws else float("nan")
    ml = S.median([x for _, x in live]) if live else float("nan")
    cd = S.median(d_) if d_ else float("nan")
    vn = "MISSING" if not d_ else ("PASS" if cd >= 0.6 * S_ else "KILL" if cd < 0.3 * S_ else "BETWEEN")
    L.append(f"Verdict never-wait ceiling (pre-registered Fri 09:0x){' INDICATIVE at C < 224' if int(C) < 224 else ''}: {vn}: "
             f"median cold16 - warm16 {cd:.1f} ms over {len(d_)} samples vs S {S_:.1f} ms (PASS >= 0.6 S, KILL < 0.3 S); "
             f"sample misses {mc:.0f} vs live {ml:.0f} per check")
except (OSError, ValueError, KeyError, TypeError) as e_:
    L.append(f"never-wait ceiling: MISSING ({type(e_).__name__})")
rl = [r.get("rlx") for t in P["stackr"] for r in runs[t].values() if r.get("rlx")]
sp = [r.get("spn") for t in P["stackr"] for r in runs[t].values() if r.get("spn")]
if rl or sp:
    L.append(f"stackr relaxed accepts {sum(x.get('relaxed', 0) for x in rl)}; span: rows {sum(x.get('rows', 0) for x in sp)}, span rows "
             f"{sum(x.get('span_rows', 0) for x in sp)}, relaxed {sum(x.get('relaxed', 0) for x in sp)}")
try:                                                     # EvalSuite's same-scores runner reads ONE code file (Fri 09:2x rule):
    envl = lambda f: [x for x in open(f).read().splitlines() if x and not x.startswith("#")][-1]   # stackr if its line PASSed,
    pick = "stackr" if vr == "PASS" else "stack"                                                   # else the stack (no CD16 since Fri 16:0x)
    open("data/stack/code_env.txt", "w").write(
        f"# CODE profile for EvalSuite's same-scores run (sat_night.sh, Sat {C}): {pick} (stackr verdict {vr}; rule: stackr if "
        f"PASS, else stack). Screen scripts/r57_screen_fast.py. One comma-separated env line:\n"
        + envl(f"data/stack/{pick}_env.txt") + "\n")
    L.append(f"code_env.txt = {pick} (stackr verdict {vr})")
except (OSError, IndexError) as e_:
    L.append(f"code_env.txt NOT written ({type(e_).__name__})")
open("data/sat/sat_report.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))
EOF
say "report rc=$? (data/sat/sat_report.txt)"
say "stacked FAST end"
