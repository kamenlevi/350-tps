"""Q1-UNION keep masks (Breakthrough, Mon 2026-11-02 23:2x; Fable C's AUDIT_350.md section 4, the orchestrator 23:2x;
pre-registered SCOREBOARD a6dd04e). On drafter-sure rows (the realizable gate dm_gate: cf >= theta) keep ranks 0-1 and every
rank 2-9 expert already in the CHECK's union at that layer: all ranks of the block's unsure rows, ranks 0-1 of its sure
rows. Blocks = the HPD-0 walks' 16-row checks (rows A .. A + m); the rows after a check's first miss enter the union with
the wrong-draft stand-in (row p + 97's routing) and their own drafts' cf (dcf). Unsure rows, prompt rows and rows outside
the walk keep all 10. Out: out/q1u_cf<thr>/<window>.npz keep [n - 1, 48, 10] bool, rank-sorted as DAY9's routing capture;
with --resident also ORs in the LRU-C-256-resident experts (Q1-on-miss variant: not written unless asked).
Usage (BigMoE venv): python dm_q1u_masks.py 0.99 0.9"""
import json, os, sys
import numpy as np
import dm_gate
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
base = json.load(open(os.path.join(OUT, "baseline.json"))); G = dm_gate.load()

def masks(thr):
    tag = "q1u_cf0" + str(thr)[2:]; os.makedirs(os.path.join(OUT, tag), exist_ok=True)
    st = {}
    for dom, wf in dm_gate.WALK.items():
        Z = np.load(os.path.join(dm_gate.TD, wf))
        for i, nm in enumerate(str(x) for x in Z["names"]):
            if nm not in base: continue
            ids = np.load(os.path.join(OUT, "routing", nm))["ids"]; N = len(ids); g = np.nan_to_num(G[nm], nan=-1.0)
            keep = np.ones((N, 48, 10), bool); kept = drop = 0
            for (k, m, A), dc in zip(Z[f"{i}_checks"].tolist(), Z[f"{i}_dcf"].tolist()):
                last, fm = min(A + m, N - 1), min(A + k, N - 1)
                blk = []                                          # (routing row, sure)
                for p in range(A, last + 1):
                    if p <= fm: blk.append((p, g[p] >= thr))
                    else: blk.append(((p + 97) % N, (dc[p - A] if p - A < m else -1.0) >= thr))
                for l in range(48):
                    u = set()
                    for p, s in blk: u.update(ids[p, l, :(2 if s else 10)].tolist())
                    for p in range(A, fm + 1):
                        if g[p] < thr: continue
                        inu = np.array([e in u for e in ids[p, l, 2:].tolist()])
                        keep[p, l, 2:] = inu; kept += int(inu.sum()); drop += int((~inu).sum())
            np.savez(os.path.join(OUT, tag, nm), keep=keep)
            d = st.setdefault(dom, [0, 0]); d[0] += kept; d[1] += drop
    for dom, (kp, dr) in st.items():
        print(f"{tag} {dom}: of Q1's dropped rank 2-9 pairs on sure rows, {100 * kp / max(kp + dr, 1):.1f} % are union members "
              f"(kept), {kp + dr} pairs", flush=True)

if __name__ == "__main__":
    for t in sys.argv[1:] or ["0.99", "0.9"]: masks(float(t))
