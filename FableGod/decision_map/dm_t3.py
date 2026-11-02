"""DAY9 / M-18 arm on the decision map (Breakthrough, Mon 2026-11-02; orchestrator 11:0x, MoonShots' lead): the gated rows'
top-2 experts served from REF2-T's 3-bit part (records3's MSB-3 record: m = q >> 1, scale 2s, bias b + s*mean(q & 1);
BigMoE's tier.py, DESIGN_3bit.md), the rest of the window exact 4-bit.
How: the block is row-independent, so a gated row gets k = 0 in the stock combine (no routed experts) and this module adds
its own routed output: sum over ranks 0-1 of the block's own normalised gate weight x the expert computed from records3
(gather_qmm bits=3 on the MSB part, as tier._proj does for a 3-bit rank). bits=4 is the CONTROL: the same path with the
4-bit expert rebuilt bit-exactly from MSB + LSB (tier.rebuild4, s = s3 / 2, b from the LSB part), so its flips separate the
path's own numerics from the 3-bit effect (compare with gate_top2_cf099, the stock top-2).
Reads: per layer, the unique experts of the call's gated rows (pread of each record's MSB part, + LSB for bits=4), with
F_NOCACHE so the page cache is left alone. The ids need the routing, so each such call syncs once (as BigMoE's prefill)."""
import fcntl, json, os, sys
sys.path.insert(1, os.path.expanduser("~/BigMoE"))   # bigmoe.tier (read-only import)
import numpy as np
import mlx.core as mx

MD = os.path.expanduser("~/BigMoE/models/bare")
_IX, _FD = {}, {}
STATS = {"calls": 0, "rows": 0, "experts": 0, "bytes": 0}
# MSB pieces (tier._MSB order): gate w3 s3 b3, up w3 s3 b3, down w3 s3 b3; LSB (tier._LSB): gate l1 b, up l1 b, down l1 b
_SHP = {"gate_proj": (640, 2560), "up_proj": (640, 2560), "down_proj": (2560, 640)}

def _index():
    if not _IX:
        _IX.update(json.load(open(os.path.join(MD, "records3", "index.json")))["layers"])
    return _IX

def _fd(L):
    if L not in _FD:
        r = _index()[str(L)]
        fd = os.open(os.path.join(MD, "records3", r["file"]), os.O_RDONLY)
        fcntl.fcntl(fd, 48, 1)                               # F_NOCACHE: don't fill the page cache with records
        _FD[L] = fd
    return _FD[L]

def read(L, ids, lsb=False):
    """Records of experts ids (unique np.int) of layer L -> {proj: {w3, s3, b3[, l1, b]}} as mx arrays with a leading [U]."""
    r = _index()[str(L)]; fd = _fd(L); U = len(ids)
    end = r["msb_sz"] + (r["lsb_sz"] if lsb else 0)
    buf = np.empty((U, end), np.uint8)
    for i, e in enumerate(ids):
        n = os.preadv(fd, [memoryview(buf[i])], int(e) * r["recsz"])
        assert n == end, (L, e, n, end)
    STATS["experts"] += U; STATS["bytes"] += U * end
    out = {}
    for p, proj in enumerate(("gate_proj", "up_proj", "down_proj")):
        o, k = _SHP[proj]; d = {}
        for j, (f, shp, dt) in enumerate((("w3", (o, k * 3 // 32), np.uint32), ("s3", (o, k // 64), np.uint16),
                                           ("b3", (o, k // 64), np.uint16))):
            off, sz = r["msb_piece_off"][3 * p + j], r["msb_piece_size"][3 * p + j]
            a = buf[:, off:off + sz].copy().view(dt).reshape(U, *shp)
            d[f] = mx.array(a) if dt == np.uint32 else mx.array(a).view(mx.bfloat16)
        if lsb:
            for j, (f, shp, dt) in enumerate((("l1", (o, k // 32), np.uint32), ("b", (o, k // 64), np.uint16))):
                off, sz = r["lsb_piece_off"][2 * p + j], r["lsb_piece_size"][2 * p + j]
                a = buf[:, off:off + sz].copy().view(dt).reshape(U, *shp)
                d[f] = mx.array(a) if dt == np.uint32 else mx.array(a).view(mx.bfloat16)
        out[proj] = d
    return out

def _proj(h, W, idx, bits):
    if bits == 3:
        return mx.gather_qmm(h, W["w3"], W["s3"], W["b3"], rhs_indices=idx, transpose=True, group_size=64, bits=3)
    from bigmoe import tier                                   # read-only import: BigMoE's bit-exact 4-bit rebuild
    w = tier.rebuild4(W["w3"], W["l1"]); s = W["s3"] * mx.array(0.5, dtype=W["s3"].dtype)
    return mx.gather_qmm(h, w, s, W["b"], rhs_indices=idx, transpose=True, group_size=64, bits=4)

def routed_top2(block, L, xg, bits=3):
    """xg [G, D]: the gated rows' MoE input -> [G, D] = sum over ranks 0-1 of the block's normalised top-10 weight x the
    expert at `bits` (3: records3's MSB part; 4: the control, rebuilt 4-bit)."""
    gates = mx.softmax(block.gate(xg), axis=-1, precise=True)            # the block's own ops (qwen4_exp._prefill_call)
    k = block.top_k
    inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
    sc = mx.take_along_axis(gates, inds, axis=-1)
    if block.norm_topk_prob: sc = sc / sc.sum(axis=-1, keepdims=True)
    o = mx.argsort(-sc.astype(mx.float32), axis=-1)[:, :2]
    top_ids, top_sc = mx.take_along_axis(inds, o, axis=-1), mx.take_along_axis(sc, o, axis=-1)
    ids_np = np.array(top_ids).astype(np.int64)                           # sync: the records to read depend on routing
    uniq, inv = np.unique(ids_np.reshape(-1), return_inverse=True)
    W = read(L, uniq, lsb=(bits == 4))
    idx = mx.array(inv.astype(np.uint32))                                 # [2G] pair -> its expert in W
    h = mx.repeat(xg, 2, axis=0)[:, None, :]                              # [2G, 1, D]: row g's pairs are 2g, 2g + 1
    up, gt = _proj(h, W["up_proj"], idx, bits), _proj(h, W["gate_proj"], idx, bits)
    y = _proj(block.switch_mlp.activation(up, gt), W["down_proj"], idx, bits)[:, 0, :]   # [2G, D]
    STATS["calls"] += 1; STATS["rows"] += int(xg.shape[0])
    return (y.reshape(-1, 2, y.shape[-1]) * top_sc[..., None].astype(y.dtype)).sum(axis=1)
