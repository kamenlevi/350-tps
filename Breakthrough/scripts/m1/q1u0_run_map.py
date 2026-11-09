#!/usr/bin/env python3
"""Map arm q1u_0_live (= Fit12's S1u) without editing the decision map's files (Breakthrough, Mon 9 Nov 2026 21:4x).
Registers the arm in memory, dm_ablations.q1_union on the masks NewIdeas' builder wrote to
~/Breakthrough/data/dm_masks/q1u_0_live (an absolute rmask dir resolves as the harness documents), then runs run_map.py's
own code as: run_map.py q1u_0_live --max 12 --skip-done. The result lands where every map arm's does:
~/FableGod/decision_map/out/q1u_0_live.json. This file's name holds 'run_map.py', so other runners' `pgrep -f run_map.py`
gates see this process as a map process. Start it with cwd ~/Breakthrough (never inside ~/FableGod): the thermostat and
fanwatch's heat freeze recognise research jobs by working folder or command line.
Usage (BigMoE venv): cd ~/Breakthrough && python -I -B scripts/m1/q1u0_run_map.py
"""
import os, sys
sys.dont_write_bytecode = True
DM = os.path.expanduser("~/FableGod/decision_map")
MASKS = os.path.expanduser("~/Breakthrough/data/dm_masks/q1u_0_live")
ARM = "q1u_0_live"
sys.path.insert(0, DM)
import dm_ablations as A  # noqa: E402

n = len([f for f in os.listdir(MASKS) if f.endswith(".npz")])
assert n == 36, f"{n} mask files in {MASKS}"
if ARM in A.ABLATIONS:
    print(f"[q1u0] {ARM} is already registered in dm_ablations.py; using that entry", flush=True)
else:
    A.ABLATIONS[ARM] = A.q1_union(MASKS)
src = os.path.join(DM, "run_map.py")
sys.argv = [src, ARM, "--max", "12", "--skip-done"]
print(f"[q1u0] running {src} {' '.join(sys.argv[1:])} (masks {MASKS})", flush=True)
exec(compile(open(src).read(), src, "exec"), {"__name__": "__main__", "__file__": src})
