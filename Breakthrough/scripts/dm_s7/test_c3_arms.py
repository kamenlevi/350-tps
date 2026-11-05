"""Install test of Cloud Fable 3's mask arms (install_c3.sh; Breakthrough, Thu 2026-11-05). Runs against the dm_ablations.py
first on PYTHONPATH (the scratch copy). CPU. Per arm: ABLATIONS[arm] sets exactly PERT {rmask: <snapshot dir>, renorm: False};
the harness's loader (os.path.join(OUT, rmask, nm)) resolves to the snapshot; the snapshot holds 36 windows whose files equal
cloud3's source byte for byte and whose keep arrays have the map's routing shapes.
Usage (BigMoE venv): PYTHONPATH=<dir with dm_ablations.py>:~/FableGod/decision_map python test_c3_arms.py <arm> ..."""
import filecmp, os, sys
import numpy as np
import dm_ablations as A
import dm_common as C
SRC = os.path.expanduser("~/FableGod/cloud3/live/cloud3/masks")
SNAP = os.path.expanduser("~/FableGod/decision_map/out/c3")
ROUT = os.path.expanduser("~/FableGod/decision_map/out/routing")
bad = []
def ok(c, m):
    print(("  ok   " if c else "  FAIL ") + m, flush=True)
    if not c: bad.append(m)
print(f"[t] dm_ablations from {A.__file__}", flush=True)
for arm in sys.argv[1:]:
    d = os.path.join(SNAP, arm)
    C.clear(); A.ABLATIONS[arm](); p = dict(C.PERT); C.clear()
    ok(p == {"rmask": d, "renorm": False}, f"{arm}: PERT == {{rmask: snapshot, renorm: False}}")
    ok(os.path.join(C.OUT, p["rmask"], "x") == os.path.join(d, "x"), f"{arm}: the loader resolves to the snapshot")
    names = sorted(f for f in os.listdir(d) if f.endswith(".npz"))
    same = sum(filecmp.cmp(os.path.join(d, n), os.path.join(SRC, arm, n), shallow=False) for n in names)
    shp = sum(np.load(os.path.join(d, n))["keep"].shape == np.load(os.path.join(ROUT, n))["ids"].shape for n in names)
    ok(len(names) == 36 and same == 36 and shp == 36, f"{arm}: 36 windows, {same}/36 byte-equal to cloud3's source, {shp}/36 routing shapes")
print("ALL OK" if not bad else f"FAILED: {len(bad)}", flush=True)
sys.exit(1 if bad else 0)
