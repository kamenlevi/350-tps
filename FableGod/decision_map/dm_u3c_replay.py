"""Replay BigMoE's U3C routing dump through the COLD rule (Breakthrough, Tue 2026-11-03 22:5x; WED_PLAN.md P1; BigMoE's
R57_FAST=U3C, Wed; spec agreed by SendMessage Tue 22:4x). Dump: one .npz per prompt. Per record (check, layer):
ids [n, R, 10] int16 padded -1, sure [n, R] bool, keep [n, R, 10] bool, rows [n]; plus warm [48, 512] bool and prompt_len.
Per record: base set = ranks 0-1 on sure rows, ranks 0-3 + warm ranks 4-9 on unsure rows; union = the base sets of all the
block's rows; keep = base set | union member (sure rows' ranks 0-1 count as kept: they run at 3 bits). Compared bitwise
with the engine's keep. Also checks that warm holds every cap45-popular expert (pop_cap45 >= 0.05), as pmtc requires (len
with a prompt of >= 128 tokens uses the footprint alone, so that check is skipped there).
Usage (BigMoE venv): python dm_u3c_replay.py <dump.npz> [...]"""
import os, sys
import numpy as np
POP = np.load(os.path.expanduser("~/FableGod/fablec/masks/pop_cap45.npy"))

def replay(path):
    Z = np.load(path); need = ("layer", "ids", "sure", "keep", "rows", "warm")
    miss = [k for k in need if k not in Z.files]
    if miss: return f"{os.path.basename(path)}: missing arrays {miss} (has {Z.files})"
    warm, plen = Z["warm"].astype(bool), int(Z["prompt_len"]) if "prompt_len" in Z.files else -1
    bad, n = [], len(Z["rows"])
    for j in range(n):
        R, l = int(Z["rows"][j]), int(Z["layer"][j])
        E = Z["ids"][j, :R].astype(np.int64); sure = Z["sure"][j, :R].astype(bool)
        b = np.zeros(E.shape, bool); b[sure, :2] = True; b[~sure, :4] = True
        b[~sure] |= warm[l][E[~sure]]
        kp = b | np.isin(E, np.unique(E[b]))
        if not np.array_equal(kp, Z["keep"][j, :R].astype(bool)): bad.append(j)
    tbl = "skipped (len, long prompt)" if plen >= 128 and not (warm >= (POP >= 0.05)).all() else \
          ("holds every cap45-popular expert" if (warm >= (POP >= 0.05)).all() else "MISSING cap45-popular experts")
    first = "; first mismatches: " + ", ".join(f"record {j} (check {int(Z['check'][j]) if 'check' in Z.files else '?'}, layer "
                                               f"{int(Z['layer'][j])})" for j in bad[:3]) if bad else ""
    return (f"{os.path.basename(path)}: {n} records, prompt {plen} tokens: keep {'ALL EQUAL' if not bad else f'{len(bad)} DIFFER'}"
            f"; warm {tbl}{first}")

if __name__ == "__main__":
    out = [replay(p) for p in sys.argv[1:]]
    print("\n".join(out))
    print("U3C MASK CHECK: " + ("PASS" if out and all("ALL EQUAL" in o and "MISSING" not in o for o in out) else "FAIL / INCOMPLETE"))
