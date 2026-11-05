"""Code-only arm reader (Fable C's audit AUDIT_1105 sections 2-3: reach07 / band5 / top1 "code only"; Breakthrough, Thu
2026-11-05). For "<arm>+code" (the 12 code windows; dm_screen_read.py needs all 36): all-row top-1 flips vs the baseline argmax
(out/baseline.json) on the code rows, the audit's lines (PASS <= 1.34 %, BETWEEN <= 2.0 %, KILL above), and a paired McNemar
vs each twin on the same code rows (the twin's full or code-only run). CPU; reads the map's out/ JSONs only; prints.
Usage (BigMoE venv): python code_read.py <arm>+code <twin> [<twin> ...]"""
import json, os, sys
import numpy as np
OUT = os.path.expanduser("~/FableGod/decision_map/out")
base = json.load(open(os.path.join(OUT, "baseline.json")))
CODE = [nm for nm, b in base.items() if b["dom"] == "code"]

def fv(name):
    p = os.path.join(OUT, name + ".json")
    if not os.path.exists(p): return None
    R = json.load(open(p)); v = []
    for nm in CODE:
        if nm not in R or "tk" not in R[nm]: return None
        m = min(len(base[nm]["tk"]), len(R[nm]["tk"]))
        v.append(np.array(R[nm]["tk"][:m])[:, 0] != np.array(base[nm]["tk"][:m])[:, 0])
    return np.concatenate(v)

arm, twins = sys.argv[1], sys.argv[2:]
X = fv(arm)
if X is None: raise SystemExit(f"{arm}: not run or a code window missing")
f = 100 * X.mean(); verdict = "PASS" if f <= 1.34 else "BETWEEN" if f <= 2.0 else "KILL"
print(f"Code-only map screen: {arm}: {len(CODE)} code windows, {len(X)} rows; all-row flips vs the baseline argmax")
for t in twins:
    Y = fv(t)
    if Y is None or len(Y) != len(X): print(f"  twin {t}: missing or a different row count"); continue
    a, b = int((X & ~Y).sum()), int((Y & ~X).sum())
    print(f"  vs {t} ({100 * Y.mean():.2f} %): only-{arm} / only-{t} flips {a} / {b}, z {(a - b) / max(np.sqrt(a + b), 1):+.2f}")
print(f"VERDICT {arm}: code {verdict} {f:.2f} % ({int(X.sum())}/{len(X)}; PASS <= 1.34, BETWEEN <= 2.0, KILL above)")
