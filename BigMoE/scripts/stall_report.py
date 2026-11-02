"""Measurement 2 of cloud task 12 (the orchestrator 11-02 21:0x): the per-layer stall timeline at C 320 with OOO on, from
r57_screen's R57_STALL dump ({TAG}_stall.json; the night's c45t_320 and, with BIGMOE_JOINT=1, c45tj_320). The question:
is the exposed SSD time latency (a fixed cost per stalled layer: the look-ahead fixes it) or bytes (only residency does)?
Per check pass (the seq with >= 40 base layers served in the check's window), per layer L (ext ids from the dump's laymap):
- demand misses: reads (tag 0 demand, 2 joint) issued inside the loader's service of (L, seq), base and sidecar apart
- service: routing seen -> release (base + sidecar; the loader serves one call at a time, so they are serial)
- issue delay: routing seen -> the first read starts; read time: start -> bytes in place (one pread + the piece copies)
- cadence: L's routing seen -> L+1's (the GPU's time from L's router to L+1's, OOO's resident work included)
Fits over (pass, layer) samples: cadence = the layer's own no-miss time + beta x rows + a x [any miss] + b x MB read (a =
the fixed cost per stalled layer, b = ms per MB); the stall at (pass, L) = cadence - the layer's own time - beta x rows; read time = d + MB / BW over reads that start alone (d = issue -> first byte + ramp, the closest proxy: the
first byte itself is not observable, one pread per expert). Then per check: sum of stalls vs the check's wall time, split
first layers 0-7 / middle 8-39 / tail 40-47. Without vs with JOINT side by side.
usage: .venv/bin/python scripts/stall_report.py [DIR=data/r57] [TAGS=c45t_320,c45tj_320] -> DIR/stall_report.txt"""
import json, os, sys
import numpy as np

D = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/BigMoE/data/r57")   # r57_screen writes its JSON there
TAGS = (sys.argv[2] if len(sys.argv) > 2 else "c45t_320,c45tj_320").split(",")
MB = {"base": 2.162688, "side": 0.770048}                # record bytes (data/seed45/laysz45_*.json slot_bytes)
L_ = []
def say(s=""):
    print(s); L_.append(s)


def union_len(iv):
    tot, cur = 0.0, None
    for a, b in sorted(iv):
        if cur is None or a > cur[1]:
            if cur:
                tot += cur[1] - cur[0]
            cur = [a, b]
        else:
            cur[1] = max(cur[1], b)
    return tot + (cur[1] - cur[0] if cur else 0.0)


def passes(run, laymap):
    """-> list of passes: dict(rows, k, wall, lay = per layer dict(seen, svc_b, svc_s, mb, ms, delay, rd))"""
    base = {b: i for i, (b, s) in enumerate(laymap)}; side = {s: i for i, (b, s) in enumerate(laymap) if s is not None}
    tr = np.array(run["tr"]) if run["tr"] else np.zeros((0, 5)); rd = np.array(run["rd"]) if run["rd"] else np.zeros((0, 5))
    k1 = tr[tr[:, 2] == 1] if len(tr) else tr
    chk = run["chk"]; out = []
    for i, (c0, c1, cb, ce, c2, rows, k) in enumerate(chk):
        t_end = chk[i + 1][0] if i + 1 < len(chk) else ce + 1.0
        w = k1[(k1[:, 3] >= c1) & (k1[:, 3] < t_end)]
        if not len(w):
            continue
        seqs, cnt = np.unique(w[:, 1], return_counts=True)
        sq = seqs[np.argmax(cnt)]                         # the check pass (a commit replay, if it reaches the gates, is apart)
        e = w[w[:, 1] == sq]
        lay, b_t0 = {}, {}
        for L_ext, _, _, t0, t1 in e:                     # base rows first: JOINT issues a sidecar's reads (tag 2) inside
            if int(L_ext) in base:                        # its base row's service, so a sidecar's window opens there
                b_t0[base[int(L_ext)]] = min(b_t0.get(base[int(L_ext)], np.inf), t0)
        for L_ext, _, _, t0, t1 in e:
            L_ext = int(L_ext)
            kind = "b" if L_ext in base else "s" if L_ext in side else None
            if kind is None:
                continue
            li = base[L_ext] if kind == "b" else side[L_ext]
            w0 = t0 if kind == "b" else min(t0, b_t0.get(li, t0))
            r = rd[(rd[:, 0] == L_ext) & (rd[:, 3] >= w0 - 1e-6) & (rd[:, 3] <= t1 + 1e-6) & (rd[:, 2] != 1)] if len(rd) else rd
            d = lay.setdefault(li, dict(seen=np.inf, svc_b=0.0, svc_s=0.0, mb=0, ms=0, delay=[], rd=[]))
            if kind == "b":
                d["seen"] = min(d["seen"], t0); d["svc_b"] += t1 - t0; d["mb"] += len(r)
            else:
                d["svc_s"] += t1 - t0; d["ms"] += len(r)
            if len(r):
                d["delay"].append(r[:, 3].min() - t0)
                d["rd"] += [(x[3], x[4], MB["base" if kind == "b" else "side"]) for x in r]
        if len([l for l in lay if np.isfinite(lay[l]["seen"])]) < 40:
            continue
        out.append(dict(rows=rows, k=k, wall=ce - c1, lay=lay))
    return out


def analyse(tag):
    f = os.path.join(D, f"{tag}_stall.json")
    if not os.path.exists(f):
        say(f"\n{tag}: no {f}"); return None
    S = json.load(open(f)); laymap = S["laymap"]; NL = len(laymap)
    P = []
    for run in S["runs"]:
        if run.get("paused"):
            continue
        for p in passes(run, laymap):
            p["key"] = run["key"]; P.append(p)
    if not P:
        say(f"\n{tag}: no traced check passes"); return None
    for p in P:                                           # cadence: L's routing seen -> L+1's
        for L in range(NL - 1):
            a, b = p["lay"].get(L), p["lay"].get(L + 1)
            if a and b and np.isfinite(a["seen"]) and np.isfinite(b["seen"]):
                a["cad"] = b["seen"] - a["seen"]
    smp = []                                              # (pass, L): rows, misses, MB, cadence
    for pi, p in enumerate(P):
        for L, d in p["lay"].items():
            if "cad" in d:
                smp.append((pi, L, p["rows"], d["mb"] + d["ms"], d["mb"] * MB["base"] + d["ms"] * MB["side"], d["cad"]))
    A = np.array(smp)
    # cadence = alpha_L (this layer's no-miss time) + beta x rows + a x [any miss] + b x MB: one least-squares fit with a
    # per-layer intercept; stall at (pass, L) = cadence - alpha_L - beta x rows (data), a x [miss] + b x MB (model)
    Ls = sorted({int(x) for x in A[:, 1]}); li = {L: j for j, L in enumerate(Ls)}
    X = np.zeros((len(A), len(Ls) + 3))
    X[np.arange(len(A)), [li[int(x)] for x in A[:, 1]]] = 1.0
    X[:, -3], X[:, -2], X[:, -1] = A[:, 2], (A[:, 3] > 0).astype(float), A[:, 4]
    coef = np.linalg.lstsq(X, A[:, 5], rcond=None)[0]
    al, be, ca, cb_ = coef[:len(Ls)], coef[-3], coef[-2], coef[-1]
    st = A[:, 5] - al[[li[int(x)] for x in A[:, 1]]] - be * A[:, 2]      # the data's stall (noise included)
    ok = np.ones(len(A), bool)
    nz = (A[:, 3] == 0).mean()
    say(f"\n== {tag}: {len(P)} traced check passes on {len({p['key'] for p in P})} prompts "
        f"(rows {np.mean([p['rows'] for p in P]):.1f}, accepted {np.mean([p['k'] for p in P]):.1f}, check wall "
        f"{1e3 * np.mean([p['wall'] for p in P]):.1f} ms)")
    say("| layer | base misses | sidecar misses | MB | service base + side ms | issue delay ms | stall ms (cadence excess) | "
        "share of passes with a miss |")
    say("|---|---|---|---|---|---|---|---|")
    for L in range(NL):
        dl = [p["lay"][L] for p in P if L in p["lay"]]
        if not dl:
            continue
        sl = st[ok & (A[:, 1] == L)] if ok.any() else []
        dly = [x for d in dl for x in d["delay"]]
        say(f"| {L} | {np.mean([d['mb'] for d in dl]):.2f} | {np.mean([d['ms'] for d in dl]):.2f} | "
            f"{np.mean([d['mb'] * MB['base'] + d['ms'] * MB['side'] for d in dl]):.1f} | "
            f"{1e3 * np.mean([d['svc_b'] for d in dl]):.2f} + {1e3 * np.mean([d['svc_s'] for d in dl]):.2f} | "
            f"{1e3 * np.median(dly) if dly else float('nan'):.3f} | {1e3 * np.mean(sl) if len(sl) else float('nan'):.2f} | "
            f"{100 * np.mean([(d['mb'] + d['ms']) > 0 for d in dl]):.0f} % |")
    rds = [r for p in P for d in p["lay"].values() for r in d["rd"]]
    R = np.array(rds) if rds else np.zeros((0, 3))
    fit = ""
    if len(R) > 10:                                       # reads that start alone: nothing else in flight at their start
        R = R[np.argsort(R[:, 0])]
        alone = np.array([not np.any((R[:, 0] < r0) & (R[:, 1] > r0)) for r0 in R[:, 0]])
        for nm, sel in (("alone", alone), ("all", np.ones(len(R), bool))):
            if sel.sum() > 5 and len(np.unique(R[sel, 2])) > 1:
                d_, b_ = np.linalg.lstsq(np.c_[np.ones(sel.sum()), R[sel, 2]], R[sel, 1] - R[sel, 0], rcond=None)[0]
                fit += (f"; reads {nm} (n {sel.sum()}): time = {1e3 * d_:.3f} ms + {1e3 * b_:.3f} ms per MB "
                        f"({1 / b_ / 1e3 if b_ > 0 else float('nan'):.1f} GB/s per read)")
    per = {}
    for pi, p in enumerate(P):                            # per check: stall sum by region vs the wall
        s_ = {"0-7": 0.0, "8-39": 0.0, "40-47": 0.0}
        for j in np.where(ok & (A[:, 0] == pi))[0]:
            L = int(A[j, 1]); s_["0-7" if L < 8 else "8-39" if L < 40 else "40-47"] += st[j]
        per[pi] = s_
    tot = np.mean([sum(v.values()) for v in per.values()])
    reg = {k: np.mean([v[k] for v in per.values()]) for k in ("0-7", "8-39", "40-47")}
    svc = np.mean([sum(d["svc_b"] + d["svc_s"] for d in p["lay"].values()) for p in P])
    svcu = np.mean([union_len([(r[0], r[1]) for d in p["lay"].values() for r in d["rd"]]) for p in P])
    nst = np.mean([sum((d["mb"] + d["ms"]) > 0 for d in p["lay"].values()) for p in P])
    say(f"per check: stall (cadence excess) {1e3 * tot:.1f} ms of {1e3 * np.mean([p['wall'] for p in P]):.1f} ms wall "
        f"(layers 0-7 {1e3 * reg['0-7']:.1f}, 8-39 {1e3 * reg['8-39']:.1f}, 40-47 {1e3 * reg['40-47']:.1f}); loader "
        f"service {1e3 * svc:.1f} ms, SSD busy {1e3 * svcu:.1f} ms; {nst:.1f} layers with a miss; misses "
        f"{np.mean([sum(d['mb'] for d in p['lay'].values()) for p in P]):.1f} base + "
        f"{np.mean([sum(d['ms'] for d in p['lay'].values()) for p in P]):.1f} sidecar")
    say(f"fit cadence = layer's own + {1e3 * be:.3f} ms per row + {1e3 * ca:.3f} ms per stalled layer + {1e3 * cb_:.3f} ms "
        f"per MB ({100 * nz:.0f} % of layer samples without a miss identify the no-miss times){fit}")
    lat = ca * np.mean([sum((d["mb"] + d["ms"]) > 0 for L, d in p["lay"].items() if "cad" in d) for p in P])
    byt = cb_ * np.mean([sum(d["mb"] * MB["base"] + d["ms"] * MB["side"] for L, d in p["lay"].items() if "cad" in d) for p in P])
    say(f"split of the per-check stall by the fit: latency {1e3 * lat:.1f} ms (x {nst:.1f} stalled layers) vs bytes "
        f"{1e3 * byt:.1f} ms -> {'LATENCY-bound (the look-ahead / JOINT road)' if lat > 1.5 * byt else 'BYTES-bound (residency)' if byt > 1.5 * lat else 'MIXED (both)'} (latency share {100 * lat / max(lat + byt, 1e-9):.0f} %)")
    return dict(tot=tot, svc=svc, lat=lat, byt=byt, nst=nst)


say("Measurement 2 (cloud task 12): per-layer stall timeline at C 320, OOO on (from r57_screen R57_STALL)")
res = {t: analyse(t) for t in TAGS}
if all(res.values()) and len(TAGS) == 2:
    a, b = res[TAGS[0]], res[TAGS[1]]
    say(f"\n{TAGS[1]} vs {TAGS[0]}: stall per check {1e3 * a['tot']:.1f} -> {1e3 * b['tot']:.1f} ms, loader service "
        f"{1e3 * a['svc']:.1f} -> {1e3 * b['svc']:.1f} ms (tok/s and tokens: c45_runner's {TAGS[0]}.txt / {TAGS[1]}.txt)")
open(os.path.join(D, "stall_report.txt"), "w").write("\n".join(L_) + "\n")
