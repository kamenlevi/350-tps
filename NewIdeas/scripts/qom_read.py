"""Read-out of the Q1-ON-MISS map arms (NewIdeas, Tue 3 Nov 2026 17:2x; pre-registered in ~/NewIdeas/QUEUE.md before any
GPU run). Arms (masks ~/NewIdeas/data/dm_masks/<arm>, scripts/dm_oea_masks.py): qom_0.9_live, qom_0.5_live, qom_0_live =
on live-cut checks, rows whose drafter cf >= theta keep ranks 0-1, the check's union members and every rank 2-9 expert
resident in the base pool (CPU LRU replay at laysz45_256's C_m); Q1's SSD reads at that theta. Lines (the union arms'):
per domain all-row flips <= Q1 at 0.99's level (gate_top2_cf099) = PASS, <= 1.5x = BETWEEN, above = KILL. Paired (McNemar)
vs gate_top2_cf099 and vs q1u_0.9_live. Reads ~/FableGod/decision_map/out (read-only); writes ~/NewIdeas/data/QOM_read.txt.
Usage (BigMoE venv): python qom_read.py [arm ...]"""
import json, math, os, sys
import numpy as np
OUT = os.path.expanduser("~/FableGod/decision_map/out"); DST = os.path.expanduser("~/NewIdeas/data/QOM_read.txt")
base = json.load(open(os.path.join(OUT, "baseline.json"))); DOMS = ("code", "ifeval", "multi")
ARMS = sys.argv[1:] or ["qom_0.9_live", "qom_0.5_live", "qom_0_live"]
lines = []
def say(s=""): print(s, flush=True); lines.append(s)


def flips(name):
    p = os.path.join(OUT, name + ".json")
    if not os.path.exists(p): return None
    R = json.load(open(p)); v = {}
    for nm, b in base.items():
        m = min(len(b["tk"]), len(R[nm]["tk"]))
        f = np.r_[np.array(R[nm]["tk"][:m])[:, 0] != np.array(b["tk"][:m])[:, 0], np.zeros(len(b["tk"]) - m, bool)]
        v.setdefault(b["dom"], []).append(f)
    return {d: np.concatenate(x) for d, x in v.items()}


F = {a: flips(a) for a in ["gate_top2_cf099", "gate_top2_cf09", "q1u_0.9_live"] + ARMS}
lvl = {d: 100 * F["gate_top2_cf099"][d].mean() for d in DOMS}
say(f"Q1-ON-MISS arms: all-row flips per domain vs Q1 at 0.99's level (code {lvl['code']:.2f} / IFEval {lvl['ifeval']:.2f} / "
    f"multi {lvl['multi']:.2f} %); PASS <= 1x, BETWEEN <= 1.5x, KILL above")
say("| arm | code | IFEval | multi | verdict per domain |")
say("|---|---|---|---|---|")
for a in ["gate_top2_cf09", "q1u_0.9_live"] + ARMS:
    X = F[a]
    if X is None: say(f"| {a} | not run | | | |"); continue
    v = []
    for d in DOMS:
        r = 100 * X[d].mean() / lvl[d]; v.append("PASS" if r <= 1 else "BETWEEN" if r <= 1.5 else "KILL")
    say(f"| {a} | " + " | ".join(f"{100 * X[d].mean():.2f} % ({int(X[d].sum())})" for d in DOMS) + f" | {' / '.join(v)} |")
say("\nPaired (McNemar: only-A, only-B, z):")
for a in ARMS:
    for b in ("gate_top2_cf099", "q1u_0.9_live"):
        if F[a] is None or F[b] is None: continue
        for d in DOMS:
            x, y = F[a][d], F[b][d]; oa, ob = int((x & ~y).sum()), int((~x & y).sum())
            say(f"  {a} vs {b} {d}: {oa} / {ob}, z {(oa - ob) / math.sqrt(max(oa + ob, 1)):+.2f}")
open(DST, "w").write("\n".join(lines) + "\n")
