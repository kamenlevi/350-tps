"""PF-D unit test (Sun 8 Nov 17:xx, no model load): random experts of three layers, their records3 bytes split into the MSB-3 /
LSB-1 parts a pool slot holds verbatim, rebuilt by pflm.rebuild_parts on the GPU, against the ext's own rebuild
(read_rebuilt_layout, the code tier.prefill_call runs today). Prints mismatching words per piece; exit 0 only if all equal.
usage: ~/BigMoE/.venv/bin/python scripts/pfd_unit.py [n_experts_per_layer]"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser(f"~/BigMoE/ext/{os.environ.get('BIGMOE_EXT_BUILD', 'build_qom')}"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mlx.core as mx  # noqa: E402
import bigmoe_ext as ext  # noqa: E402
import pflm  # noqa: E402

D = os.path.expanduser("~/BigMoE/models/bare/records3")
cfg = json.load(open(os.path.expanduser("~/BigMoE/models/bare/config.json")))
tc = cfg.get("text_config", cfg)
H, I = int(tc["hidden_size"]), int(tc["moe_intermediate_size"])
ix = json.load(open(os.path.join(D, "index.json")))
rows3, ins = [I, I, H], [H, H, I]
shapes4 = []
for O, K in zip(rows3, ins):
    shapes4 += [((O, K // 8), mx.uint32), ((O, K // 64), mx.bfloat16), ((O, K // 64), mx.bfloat16)]
pers4 = [int(np.prod(sh)) * (4 if dt == mx.uint32 else 2) for sh, dt in shapes4]
n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
rng = np.random.default_rng(1108)
bad = 0
for L in (0, 23, 47):
    r = ix["layers"][str(L)]
    assert r.get("layout") == "native+p11+pad", r.get("layout")
    t = dict(r=r, rows3=rows3, shapes4=shapes4, offs=list(r["msb_piece_off"]) + list(r["lsb_piece_off"]),
             msb_sz=r["msb_sz"], recsz=r["recsz"], path=os.path.join(D, r["file"]), layout=2)
    ids = np.sort(rng.choice(int(r["E"]), n, replace=False))
    buf = pflm.read_parts(t, ids, 0, int(r["recsz"]))
    w3s, s3s = pflm.msb_pieces(t, buf[:, :r["msb_sz"]])
    l1s, bs = pflm.lsb_pieces(t, buf[:, r["msb_sz"]:])
    reb = pflm.rebuild_parts(t, w3s, s3s, l1s, bs)
    ref = [mx.zeros((n, *sh), dt) for sh, dt in shapes4]
    mx.eval(*ref)
    ext.read_rebuilt_layout(t["path"], int(r["recsz"]), int(r["msb_sz"]), pers4, ids.astype(np.int32).tolist(),
                            list(range(n)), ref, 2, rows3, t["offs"])
    for i, (g, rr) in enumerate(zip(reb, ref)):
        gv = np.array(g.view(mx.uint16) if g.dtype == mx.bfloat16 else g)
        rv = np.array(rr.view(mx.uint16) if rr.dtype == mx.bfloat16 else rr)
        assert gv.shape == rv.shape, (L, i, gv.shape, rv.shape)
        nb = int((gv != rv).sum())
        bad += nb
        print(f"layer {L:2d} piece {i} {str(gv.shape):18s} {'==' if nb == 0 else f'{nb} words differ'}"
              f"{'' if rv.any() else '  (reference all zero!)'}")
print(f"PFD UNIT ({'kernel' if os.environ.get('R57_PFD_KERNEL', '1') != '0' else 'ops'}): {'PASS' if bad == 0 else 'FAIL'} "
      f"({bad} differing words; {3 * n} experts, 9 pieces each)")
if os.environ.get("PFD_UNIT_TIME", "1") == "1" and bad == 0:   # speed: 96 experts of layer 23, kernel vs ops (same bytes)
    import time
    r = ix["layers"]["23"]
    t = dict(r=r, rows3=rows3, shapes4=shapes4, offs=list(r["msb_piece_off"]) + list(r["lsb_piece_off"]),
             msb_sz=r["msb_sz"], recsz=r["recsz"], path=os.path.join(D, r["file"]), layout=2)
    ids = np.sort(rng.choice(int(r["E"]), 96, replace=False))
    buf = pflm.read_parts(t, ids, 0, int(r["recsz"]))
    w3s, s3s = pflm.msb_pieces(t, buf[:, :r["msb_sz"]])
    l1s, bs = pflm.lsb_pieces(t, buf[:, r["msb_sz"]:])
    mx.eval(*w3s, *s3s, *l1s, *bs)
    res = {}
    for name, fn in (("kernel", pflm.rebuild_parts), ("ops", pflm.rebuild_parts_ops)):
        os.environ["R57_PFD_KERNEL"] = "1" if name == "kernel" else "0"
        best = 1e9
        for _ in range(3):
            t0 = time.perf_counter()
            o = fn(t, w3s, s3s, l1s, bs)
            mx.eval(*o)
            best = min(best, time.perf_counter() - t0)
        res[name] = o
        print(f"  {name}: {best * 1e3:.1f} ms for 96 experts = {best * 1e3 / 96:.3f} ms per expert")
    same = all(np.array_equal(np.array(a.view(mx.uint16) if a.dtype == mx.bfloat16 else a),
                              np.array(b.view(mx.uint16) if b.dtype == mx.bfloat16 else b)) for a, b in zip(res["kernel"], res["ops"]))
    print(f"  kernel == ops on the 96: {same}")
    bad += 0 if same else 1
sys.exit(0 if bad == 0 else 1)
