"""CPU unit test of dm_common._reuse (night 2's lag-k / chained MoE reuse) against a plain reference, with the window
split into uneven chunk calls; plus the chain mask's coverage on the real baseline. Tiny arrays, no model.
Usage (BigMoE venv): python test_reuse.py  -> last line "ALL OK" or "<n> MISMATCHES"."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mlx.core as mx
mx.set_default_device(mx.cpu)
import dm_common as C
from dm_ablations import ablation
rng = np.random.default_rng(0)

def run(chunks, D=3, li=12, skip=None):
    C.PREV.clear(); C.CUR["pos"] = {}; C.CUR["skip"] = skip
    Z = rng.standard_normal((sum(chunks), D)).astype(np.float32); out = []; p = 0
    for n in chunks:
        out.append(np.array(C._reuse(li, mx.array(Z[p:p + n])))); p += n
    return Z, np.concatenate(out)

bad = 0
for k in (0, 1, 2, 4):
    for chunks in ([16], [5, 3, 1, 7], [1, 1, 1, 13], [2, 30, 3]):
        C.PERT.clear(); C.PERT.update(reuse={12}, lag=k, chain=False)
        Z, O = run(chunks)
        ref = np.array([Z[t - k] if t >= k else Z[t] for t in range(len(Z))])
        ok = np.array_equal(O, ref); bad += not ok
        print(f"lag {k} chunks {chunks}: {'ok' if ok else 'MISMATCH'}")
for chunks in ([16], [5, 3, 1, 7], [3, 13], [1, 15]):
    T = sum(chunks); skip = np.zeros(T, bool); skip[[1, 2, 5, 6, 7, 8, 12, 15]] = True
    C.PERT.clear(); C.PERT.update(reuse={12}, chain=True)
    Z, O = run(chunks, skip=skip)
    last, ref = 0, []
    for t in range(T):
        if not skip[t]: last = t
        ref.append(Z[last])
    ok = np.array_equal(O, np.array(ref)); bad += not ok
    print(f"chain chunks {chunks}: {'ok' if ok else 'MISMATCH'}")
for nm in ("moe_reuse_prev_L12_35", "moe_reuse_lag4_L12_35", "moe_reuse_chain_L12_35", "moe_reuse_prev_L08_11",
           "moe_reuse_prev_L36_39"):
    C.PERT.clear(); ablation(nm)()
    r = C.PERT["reuse"]; print(f"{nm}: layers {min(r)}-{max(r)} ({len(r)}), lag {C.PERT['lag']}, chain {C.PERT['chain']}")
C.PERT.clear()
base = C.json.load(open(os.path.join(C.OUT, "baseline.json")))
tot, runs = {}, {}
for nm, w in base.items():
    a = w["a"]; n = a + len(w["lp"]) + 1
    s = C._chain_skip(nm, a, n)
    assert not s[:a].any() and not s[-1], nm
    d = tot.setdefault(w["dom"], [0, 0]); d[0] += int(s.sum()); d[1] += len(w["lp"])
    r = np.diff(np.flatnonzero(np.diff(np.r_[0, s[a:].astype(np.int8), 0])))[::2]
    runs.setdefault(w["dom"], []).extend(r.tolist())
for dom, (k, n) in tot.items():
    r = np.array(runs[dom])
    print(f"chain mask {dom}: skips {k}/{n} = {100 * k / n:.1f} % of answer rows; {len(r)} runs, mean {r.mean():.1f}, "
          f"median {np.median(r):.0f}, max {r.max()}")
sk = np.array([0, 1, 1, 1, 1, 1, 0, 1, 1], bool)
for S, want in ((0, sk), (1, np.array([0, 1, 0, 1, 0, 1, 0, 1, 0], bool)), (2, np.array([0, 1, 1, 0, 1, 1, 0, 1, 1], bool))):
    ok = np.array_equal(C.bound_runs(sk.copy(), S), want); bad += not ok
    print(f"bound_runs S={S}: {'ok' if ok else 'MISMATCH'}")
for nm in ("moe_reuse_chain1_L08_35", "moe_reuse_chain2_L08_35_topk2"):
    C.PERT.clear(); ablation(nm)()
    r = C.PERT["reuse"]; print(f"{nm}: layers {min(r)}-{max(r)}, chain {C.PERT['chain']}, max {C.PERT['chain_max']}, topk {C.PERT.get('topk')}")
C.PERT.clear()
# DAY9 Q1 / Q2: per-row k across uneven chunk calls (CUR['k'] in window order) vs a plain per-row reference
for chunks in ([16], [5, 3, 1, 7], [1, 15], [2, 30, 3]):
    T = sum(chunks); kr = rng.choice([2, 4, 8, 10], T).astype(np.int32)
    C.clear(); C.PERT.update(gate=("top", 0.99, 2), renorm=False); C.CUR["k"] = kr; C.CUR["kpos"] = {}; C.CUR["L"] = 7
    S = rng.random((T, 10)).astype(np.float32); out = []; p = 0
    for n in chunks:
        out.append(np.array(C._pert_scores(mx.array(S[p:p + n])))); p += n
    O = np.concatenate(out); rank = np.argsort(np.argsort(-S, axis=1), axis=1)
    ok = np.array_equal(O, np.where(rank < kr[:, None], S, 0)) and C.CUR["kpos"][7] == T; bad += not ok
    print(f"per-row k chunks {chunks}: {'ok' if ok else 'MISMATCH'}")
C.clear()
for nm, want in (("gate_top2_cf099", ("top", 0.99, 2)), ("gate_top2_cf0999", ("top", 0.999, 2)), ("gate_bands", ("bands",))):
    C.PERT.clear(); ablation(nm)(); ok = C.PERT.get("gate") == want and C.PERT.get("renorm") is False; bad += not ok
    print(f"{nm}: gate {C.PERT.get('gate')} {'ok' if ok else 'MISMATCH'}")
for nm, want in (("gate_top2t3_cf099", (("t3", 0.99), 3)), ("gate_top2t4_cf099", (("t3", 0.99), 4)), ("gate_top2t3_cf0999", (("t3", 0.999), 3))):
    C.PERT.clear(); ablation(nm)(); ok = (C.PERT.get("gate"), C.PERT.get("t3")) == want; bad += not ok
    print(f"{nm}: gate {C.PERT.get('gate')} bits {C.PERT.get('t3')} {'ok' if ok else 'MISMATCH'}")
for nm, want in (("cert_top2_p099", ("cert", "topk2", 0.99, 2)), ("cert_top5_p09", ("cert", "topk5", 0.9, 5))):
    C.PERT.clear(); ablation(nm)(); ok = C.PERT.get("gate") == want and C.PERT.get("renorm") is False; bad += not ok
    print(f"{nm}: gate {C.PERT.get('gate')} {'ok' if ok else 'MISMATCH'}")
C.PERT.clear(); ablation("acert_top2_p07_p09_cf099")(); ok = C.PERT.get("gate") == ("acert", "topk2", 0.7, 0.9, 0.99, 2)
bad += not ok; print(f"acert_top2_p07_p09_cf099: gate {C.PERT.get('gate')} {'ok' if ok else 'MISMATCH'}")
C.PERT.clear(); ablation("moe_reuse_chain1_L08_35_dcf099")(); ok = C.PERT.get("chain_gate") == 0.99 and C.PERT["chain_max"] == 1
bad += not ok; print(f"moe_reuse_chain1_L08_35_dcf099: chain_gate {C.PERT.get('chain_gate')} {'ok' if ok else 'MISMATCH'}")
import dm_gate
G = dm_gate.load(); cnt = {}
for spec in (("top", 0.99, 2), ("bands",), ("t3", 0.99)):
    C.PERT.clear(); C.PERT.update(gate=spec)
    for nm, w in base.items():
        a = w["a"]; n = a + len(w["lp"]) + 1; k = C._gate_k(nm, n); g = np.nan_to_num(G[nm], nan=-1)
        assert (k[:a][g[:a] < 0] == 10).all() and k[-1] == 10, nm
        if spec[0] == "top": ok = np.array_equal(k[:n - 1] == 2, g >= 0.99); bad += not ok
        if spec[0] == "t3": ok = np.array_equal(k[:n - 1] == 0, g >= 0.99) and (k[:n - 1][g < 0.99] == 10).all(); bad += not ok
        d = cnt.setdefault((spec[0], w["dom"]), {}); kk = k[a:n - 1]
        for v in (0, 2, 4, 8, 10): d[v] = d.get(v, 0) + int((kk == v).sum())
for spec in (("cert", "topk2", 0.99, 2), ("cert", "topk5", 0.9, 5)):   # the two-pass check (mission 20)
    C.PERT.clear(); C.PERT.update(gate=spec); src = C.json.load(open(os.path.join(C.OUT, spec[1] + ".json")))
    for nm, w in base.items():
        a = w["a"]; n = a + len(w["lp"]) + 1; k = C._gate_k(nm, n); p1 = np.exp(np.array(src[nm]["lp"])[:, 0])
        ok = (k[:a] == 10).all() and k[-1] == 10 and np.array_equal(k[a:n - 1] == spec[3], p1 >= spec[2]) \
            and (k[a:n - 1][p1 < spec[2]] == 10).all()
        bad += not ok
        d = cnt.setdefault((f"cert{spec[3]}", w["dom"]), {}); kk = k[a:n - 1]
        for v in (2, 5, 10): d[v] = d.get(v, 0) + int((kk == v).sum())
C.PERT.clear(); C.PERT.update(gate=("acert", "topk2", 0.7, 0.9, 0.99, 2)); src = C.json.load(open(os.path.join(C.OUT, "topk2.json")))
for dom, wf in dm_gate.WALK.items():                  # the adaptive certificate against a plain walk over the checks
    Z = np.load(os.path.join(dm_gate.TD, wf))
    for i, nm in enumerate(str(x) for x in Z["names"]):
        if nm not in base: continue
        w = base[nm]; a = w["a"]; n = a + len(w["lp"]) + 1; k = C._gate_k(nm, n)
        p1 = np.exp(np.array(src[nm]["lp"])[:, 0]); a1 = np.array(src[nm]["tk"])[:, 0]; want = np.zeros(n, bool)
        want[a:n - 1] = p1 >= 0.9
        for (kk, m, A), dt, dc in zip(Z[f"{i}_checks"], Z[f"{i}_dtok"], Z[f"{i}_dcf"]):
            for j in range(min(kk + 1, m)):
                r = A + j
                if a <= r < n - 1 and p1[r - a] >= 0.7 and dc[j] >= 0.99 and dt[j] == a1[r - a]: want[r] = True
        ok = np.array_equal(k == 2, want) and ((k == 2) | (k == 10)).all(); bad += not ok
        d = cnt.setdefault(("acert", w["dom"]), {}); kk_ = k[a:n - 1]
        for v in (2, 10): d[v] = d.get(v, 0) + int((kk_ == v).sum())
for key, d in cnt.items():
    print(f"gate k {key}: " + " ".join(f"k{v} {100 * c / sum(d.values()):.1f} %" for v, c in d.items()))
C.clear(); C.PERT.update(chain=True, chain_gate=0.99, chain_max=0)
nm = next(iter(base)); w = base[nm]; a = w["a"]; n = a + len(w["lp"]) + 1
s_ = C._chain_skip(nm, a, n); ok = np.array_equal(s_[a:n - 1], np.nan_to_num(G[nm], nan=-1)[a:] >= 0.99) and not s_[:a].any()
bad += not ok; print(f"chain skip by the drafter gate on {nm}: {'ok' if ok else 'MISMATCH'}")
C.clear()
print("ALL OK" if not bad else f"{bad} MISMATCHES")
