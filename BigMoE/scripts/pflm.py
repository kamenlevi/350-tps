"""R57_PFLM=1|2 (Sun 8 Nov; Kamen's MUST prefill >= 500 tok/s; NewIdeas' PF-A, Leap's advice, MoonShots'
patches/layer_major_prefill/DESIGN.md): layer-major prefill with the screen's chunk boundaries, plus a per-layer expert scratch
so each layer's experts are read from records3 ONCE per prompt instead of once per 1,024-row chunk.

- Today (45 GB r57, R57_TIER=1): every prefill MoE call goes stream._sync_call -> tier.prefill_call, which builds a scratch of
  exactly the call's unique experts, fills it from records3 with the ext's CPU rebuild (an SSD read of every one of them) and
  frees it. A 1,024-row chunk routes to ~all 512 experts, so each chunk re-reads ~1.5 GB per layer (~75 GB per chunk): a 7.9K
  prompt reads ~600 GB (N45: TTFT 64 s, 124 tok/s).
- Order: `for layer: for chunk:` instead of `for chunk: for layer:`. Each (layer, chunk) step gets exactly today's inputs (its own
  hyper stream, the layer's KV / GDN cache after chunks 0..k-1), the same chunk sizes and the same kernels (MoonShots DESIGN.md:
  bit-identical when the per-call computation is unchanged; Leap: a one-call prefill is NOT bitwise, 0 / 9 hashes).
- Reads: install() wraps tier.prefill_call. While LMC["on"], a layer's first call allocates nothing new beyond one full-E scratch
  (E rows x every 4-bit piece, rows = expert ids, ~1.57 GB: about today's per-call scratch, which is freed meanwhile) and reads
  the call's experts into their rows; later chunks of the same layer read only experts not yet there. The scratch is reused
  across layers (a new layer only resets which rows are valid) and dropped after the prefill (the decode peak is unchanged).
  - R57_PFLM=1: the call runs on the full-E scratch with the ORIGINAL ids (no copy). The kernel sees E = 512 weight rows instead
    of len(unique): tier.prefill_call's docstring warns that this changed MLX's gather kernel choice on SHORT prompts (B7 prose
    sha); layer-major only runs prompts > 1 chunk. Exactness is an empirical question: R57_LOGHASH vs the chunk-major arm.
  - R57_PFLM=2: bitwise by construction: each call gathers its unique rows into a compact copy (mx.take, sorted ids) and runs on
    compact ids, exactly today's call shape. Costs one extra ~1.5 GB copy per call (the 45.0 GB line decides).
- Logits: only the last chunk goes through the mixer + head, its last 256 rows (as R57_PFNOLOG).
- R57_PFLM=3 (PF-B, Sun 08:4x, Leap's plan; mode 1's scratch on original ids): each layer is split at its MoE. Every chunk's
  attention part (PLE, attention hyper read, attention / GDN, MLP hyper read) runs in chunk order and goes to the GPU with
  mx.async_eval; meanwhile the CPU reads ALL the layer's experts into the scratch (R57_PFLM_AHEAD=1, the default: PFX routed
  93-99 % of them, so ~1-7 % more bytes; the ext holds the GIL, so the overlap is CPU read || GPU attention). Then ONE MoE
  call per group of chunks (<= R57_PFLM_TOK tokens, default 4096) on Leap's padded SwitchGLU (MLX 0.32.2's sorted gather
  leaves rows unwritten past 32,767 sorted rows unless M % 64 == 0), then each chunk's residual write. The router and the
  shared expert run once per group (per-token, batch-independent per Leap; R57_LOGHASH vs mode 1 decides). The screen passes
  on_layer (its TAP for the drafter, which layer(...) did in modes 1 / 2). R57_PFLM_CC=1: mx.clear_cache() after each layer.
"""
import os
import numpy as np
import mlx.core as mx
import mlx.nn as nn

LMC = {"on": False, "mode": 1, "t": None, "have": set(), "sc": None, "reads": 0, "hits": 0, "calls": 0, "tier": None}


class _SegPerChunk(nn.Module):
    """PF-B's exactness fix (Leap 16:5x, 6553fcb; PrefillKernels FINDINGS N3): the MoE block's shared_expert_gate is a q4
    matmul with N = 1, which MLX 0.32.2 runs through qmm_splitk with split_k = 512 / ceil(M / 32): its bits depend on M. Over a
    group of chunks it runs once per chunk slice (PF-A's M), concatenated on the token axis; everything else stays batched."""

    def __init__(self, f, sizes):
        super().__init__()
        self.f = f
        self.sizes = list(sizes)

    def __call__(self, x):
        outs, o = [], 0
        for n_ in self.sizes:
            outs.append(self.f(x[:, o:o + n_]))
            o += n_
        return mx.concatenate(outs, axis=1)


def switch_glu_padded(m, x, indices, align=64):
    """Leap's ~/Leap/scripts/pfb_fix.py (Sun 08:3x): SwitchGLU's forward (sort, up / gate / down sorted gather, SwiGLU,
    unsort) with the sorted rows padded to a multiple of 64 (copies of the last row, same expert), so MLX 0.32.2's
    affine_gather_qmm_rhs_nax takes its aligned path. Bitwise == the 1,024-token calls (Leap, 1.6K / 4.7K / 7.9K)."""
    from mlx_lm.models.switch_layers import _gather_sort, _scatter_unsort
    xe = mx.expand_dims(x, (-2, -3))
    xs, idx, inv = _gather_sort(xe, indices)
    R = idx.shape[0]
    pad = (-R) % align
    if pad:
        xs = mx.concatenate([xs, mx.repeat(xs[-1:], pad, axis=0)], axis=0)
        idx = mx.concatenate([idx, mx.repeat(idx[-1:], pad, axis=0)], axis=0)
    h = m.activation(m.up_proj(xs, idx, sorted_indices=True), m.gate_proj(xs, idx, sorted_indices=True))
    y = m.down_proj(h, idx, sorted_indices=True)
    if pad:
        y = y[:R]
    return _scatter_unsort(y, inv, indices.shape).squeeze(-2)


def _scratch(t):
    """The full-E scratch for layer t's piece shapes (reallocated only when the shapes change) and, on a new layer, no valid
    rows yet. Returns E."""
    E = int(t["E"])
    shp = [((E,) + tuple(sh), dt) for sh, dt in t["shapes4"]]
    if LMC["sc"] is None or [(tuple(s.shape), s.dtype) for s in LMC["sc"]] != shp:
        LMC["sc"] = None
        mx.clear_cache()
        LMC["sc"] = [mx.zeros(sh, dt) for sh, dt in shp]
        mx.eval(*LMC["sc"])
        LMC["t"] = None
    if LMC["t"] is not t:                                # a new layer: no row of the scratch is valid for it yet
        LMC["t"], LMC["have"] = t, set()
    return E


def _read_all(t):
    """PF-B: every expert of layer t not yet in the scratch, read now (CPU) while the GPU runs the queued attention parts."""
    E = _scratch(t)
    need = [e for e in range(E) if e not in LMC["have"]]
    if need:
        LMC["tier"]._read_rebuilt(t, need, need, LMC["sc"])
        LMC["have"].update(need)
        LMC["reads"] += len(need)


def install(tier, mode=1):
    """Wrap bigmoe.tier.prefill_call (stream._sync_call looks it up at call time). Inactive unless LMC['on']."""
    LMC["mode"] = int(mode)
    LMC["tier"] = tier
    if getattr(tier, "_pflm_installed", False):
        return
    orig = tier.prefill_call
    from bigmoe.stream import PIECES

    def prefill_call(cls, self, x, indices, bm, *a, **kw):
        if not LMC["on"]:
            return orig(cls, self, x, indices, bm, *a, **kw)
        t = bm["tier"]
        tier.STATS["prefill_calls"] += 1
        ids = np.array(indices)
        uniq = np.unique(ids)
        _scratch(t)
        need = [int(e) for e in uniq if int(e) not in LMC["have"]]
        if need:                                         # the same ext rebuild as today, into those experts' own rows
            tier._read_rebuilt(t, need, need, LMC["sc"])
            LMC["have"].update(need)
            LMC["reads"] += len(need)
        LMC["hits"] += len(uniq) - len(need)
        LMC["calls"] += 1
        if LMC["mode"] == 2:                             # today's call shape: a compact sorted scratch + order-preserving ids
            gi = mx.array(uniq.astype(np.int32))
            scr = [mx.take(s, gi, axis=0) for s in LMC["sc"]]
            mx.eval(*scr)
            idx = mx.array(np.searchsorted(uniq, ids).astype(np.int32)).astype(indices.dtype)
        else:
            scr, idx = LMC["sc"], indices
        saved = [getattr(getattr(self, proj), field) for proj, field in PIECES]
        for (proj, field), arr in zip(PIECES, scr):
            setattr(getattr(self, proj), field, arr)
        try:
            y = switch_glu_padded(self, x, idx) if LMC["mode"] == 3 else cls.__call__(self, x, idx, *a, **kw)
            mx.eval(y)
        finally:
            for (proj, field), arr in zip(PIECES, saved):
                setattr(getattr(self, proj), field, arr)
        if LMC["mode"] == 2:
            del scr
        return y

    tier.prefill_call = prefill_call
    tier._pflm_installed = True


def _split_layers(tm, xs, hs, cache, states, stage, on_layer):
    """R57_PFLM=3 (PF-B): each layer split at its MoE (qwen4_exp DecoderLayer.__call__'s steps verbatim; REF2's patched
    hyper read / attention / write are looked up at call time as there; its _dec_call only acts on 5-16-row passes)."""
    import mtplx.models.qwen4_exp as Q
    tok = int(os.environ.get("R57_PFLM_TOK", "4096") or 4096)
    ahead = os.environ.get("R57_PFLM_AHEAD", "1") != "0"
    cc = os.environ.get("R57_PFLM_CC") == "1"
    seg = os.environ.get("R57_PFLM_SEG", "1") != "0"     # =0: the batched gate (pb3 / pb38 at d44ec7a: not bitwise)
    assert not seg or all(hasattr(l_.mlp, "shared_expert_gate") for l_ in tm.layers), "R57_PFLM_SEG: no shared_expert_gate"
    groups, cur, n = [], [], 0                           # contiguous chunk groups of <= tok tokens (at least one chunk)
    for k, x in enumerate(xs):
        if cur and n + x.shape[1] > tok:
            groups.append(cur)
            cur, n = [], 0
        cur.append(k)
        n += x.shape[1]
    groups.append(cur)
    for layer in tm.layers:                              # a fully resident layer would run the unpadded stock call
        bm_ = layer.mlp.switch_mlp._bm
        assert "tier" in bm_ and not bm_["full"], "R57_PFLM=3: every layer must take the tier path (none fully resident)"
    for L, (layer, c) in enumerate(zip(tm.layers, cache)):
        t = layer.mlp.switch_mlp._bm["tier"]
        pend = []
        for k, x in enumerate(xs):
            if L == 0:                                   # as _forward: the ssm mask of a B=1 unpadded chunk is None
                assert Q.create_ssm_mask(hs[k], cache[tm.ssm_idx]) is None, "PFLM: an ssm mask (padding?)"
            sync = stage and L == tm._ple_stage_idx      # the PLE stage feeds chunk k's PLE read: consume it before k+1's
            if sync:
                ple = tm.layers[tm._ple_stage_idx].ple
                ple.ple_embedding.stage(x, cache[tm._ple_stage_idx], ple.NGRAM_IDX)
            h = hs[k]
            if "ple" in layer:
                h = h + layer.ple(h, x, c)
            mixed, hyper, inject = layer.attn_hyper_connection(h)
            bo = layer.linear_attn(mixed, None, c) if layer.is_linear else layer.self_attn(mixed, c)
            mixed, hyper, inject = layer.mlp_hyper_connection(hyper, pending=(bo, inject))
            pend.append((mixed, hyper, inject))
            outs = [a for a in (mixed, hyper, inject) if isinstance(a, mx.array)] + list(states([c]))
            (mx.eval if sync else mx.async_eval)(*outs)
        if ahead:
            _read_all(t)                                 # CPU read || the GPU's queued attention parts
        for g in groups:
            M = pend[g[0]][0] if len(g) == 1 else mx.concatenate([pend[k][0] for k in g], axis=1)
            fix = len(g) > 1 and seg                     # R57_PFLM_SEG (default 1): the shared expert's gate per chunk slice
            if fix:
                mlp_ = layer.mlp
                seg0 = mlp_.shared_expert_gate
                mlp_.shared_expert_gate = _SegPerChunk(seg0, [pend[k][0].shape[1] for k in g])
            try:
                Y = layer.mlp(M)                         # router + shared expert + the padded SwitchGLU (tier wrapper)
            finally:
                if fix:
                    mlp_.shared_expert_gate = seg0
            off = 0
            for k in g:
                n_ = pend[k][0].shape[1]
                hs[k] = Q._hyper_residual_write(pend[k][1], Y if len(g) == 1 else Y[:, off:off + n_], pend[k][2])
                off += n_
                if on_layer is not None:
                    on_layer(layer, hs[k])
            mx.eval(*[hs[k] for k in g])
            del M, Y
        del pend
        if cc:
            mx.clear_cache()


def prefill_layer_major(model, ids, chunk, states, on_chunk=None, on_layer=None):
    """The screen's chunk-major prefill, layer-major. Returns (cache, logits of the last chunk's last 256 rows).
    on_chunk(k, h_k) runs after the LAST layer for each chunk k (the widened stream, for the MTP head). on_layer(layer, h_k):
    R57_PFLM=3 only, after each (layer, chunk) step (modes 1 / 2 call layer(...), whose screen wrapper taps itself)."""
    import mtplx.models.qwen4_exp as Q
    import bigmoe.tier as BT
    lm = model.language_model
    tm = lm.model
    cache = model.make_cache()
    xs = [mx.array([ids[a:a + chunk]]) for a in range(0, len(ids), chunk)]

    def run():
        hs = []
        for x in xs:
            h = tm.embed_tokens(x)
            hs.append(mx.tile(h, (1, 1, tm.args.hc_count)))
        mx.eval(*hs)
        stage = tm._ple_stage_idx is not None and Q._COMPILED_VERIFY_PLE.get() is None
        BT._reuse_drop()
        LMC.update(on=True, t=None, have=set())
        try:
            if LMC["mode"] == 3:
                _split_layers(tm, xs, hs, cache, states, stage, on_layer)
            for L, (layer, c) in enumerate(zip(tm.layers, cache) if LMC["mode"] != 3 else ()):
                for k, x in enumerate(xs):
                    if L == 0:                           # as _forward: the ssm mask of a B=1 unpadded chunk is None
                        assert Q.create_ssm_mask(hs[k], cache[tm.ssm_idx]) is None, "PFLM: an ssm mask (padding?)"
                    if stage and L == tm._ple_stage_idx:   # as _forward stages chunk k's n-grams before its layers: the
                        ple = tm.layers[tm._ple_stage_idx].ple   # stage only touches the PLE layer's cache, which holds
                        ple.ple_embedding.stage(x, cache[tm._ple_stage_idx], ple.NGRAM_IDX)   # chunks 0..k-1 here too
                    hs[k] = layer(hs[k], input_ids=x, ssm_mask=None, cache=c)
                    mx.eval(hs[k], *states([c]))
        finally:
            LMC.update(on=False, t=None, have=set(), sc=None)
            mx.clear_cache()
        if on_chunk is not None:
            for k, h in enumerate(hs):
                on_chunk(k, h)
        tm._last_widened = hs[-1]
        out = tm.hyper_connection_mixer(hs[-1])[:, -256:]   # TextModel(logits_keep=256): the mixer over the whole chunk
        return lm._head_logits(out)

    if Q.qwen4_opdiet_enabled("rope"):
        with Q._rope_table_scope():
            lg = run()
    else:
        lg = run()
    return cache, lg


# ---------------------------------------------------------------- PF-D (R57_PFD=1)
> (a quote from the project owner, kept private)
# prefill reads EVERY routed expert-layer from records3 (bytes = routed x 2.79 MB), although 65.5 % of them have their MSB-3
# base and 25.1 % their LSB side part in the 45 GB pools; TTFT = 0.32 s + bytes / 7.33 GB/s. Strata's prompt path (MIT,
# ~/StrataEval/src: stream.cpp at_layer) reads only the routed experts its arena lacks. Ours needs the 4-bit pieces in a
# scratch (tier.prefill_call: the same gather_qmm call on the call's sorted unique experts), so PF-D only changes where each
# scratch row's bytes come from and keeps the call itself:
#   A  base + side resident: rebuilt on the GPU from the two pool slots;
#   B  base resident only: the LSB part (0.72 of 2.79 MB) read from records3 (pread, F_NOCACHE, threads), rebuilt on the GPU;
#   C  base absent: tier._read_rebuilt as today (the ext's CPU rebuild of the full record).
# The GPU rebuild is the ext's, op for op (bigmoe_ext.cpp unnative / unp11 / rebuild_w4 / halve_bf16, native+p11 layout 2):
# a pool slot holds its record part's pieces verbatim. R57_PFD_CHECK=1 compares every rebuilt row with tier._read_rebuilt's
# (extra reads: timing void) and counts mismatching rows of A and B.
import fcntl
from concurrent.futures import ThreadPoolExecutor

PFD = {"calls": 0, "A": 0, "B": 0, "C": 0, "ssd": 0, "checked": 0, "bad_A": 0, "bad_B": 0, "fallback": 0}
_and, _or, _shl, _shr = mx.bitwise_and, mx.bitwise_or, mx.left_shift, mx.right_shift


def _u(v):
    return mx.array(v, dtype=mx.uint32)


_R32 = np.arange(32)
_WI, _SH = (11 * _R32) >> 5, (11 * _R32) & 31            # unp11: code r at bits 11r .. 11r + 10 of an 11-word block
_NEED = _SH > 21


def _spread8(x, l):                                      # 8 weights: 24 code bits + 8 low bits -> 8 nibbles (ext spread8)
    a = _or(_and(x, _u(0xFFF)), _shl(_and(x, _u(0xFFF000)), _u(4)))
    a = _or(_and(a, _u(0x003F003F)), _shl(_and(a, _u(0x0FC00FC0)), _u(2)))
    a = _or(_and(a, _u(0x07070707)), _shl(_and(a, _u(0x38383838)), _u(1)))
    y = _and(l, _u(0xFF))
    y = _and(_or(y, _shl(y, _u(12))), _u(0x000F000F))
    y = _and(_or(y, _shl(y, _u(6))), _u(0x03030303))
    y = _and(_or(y, _shl(y, _u(3))), _u(0x11111111))
    return _or(_shl(a, _u(1)), y)


def _unnative(a, O, KG, cw):                             # native chunk (t*KG + g)*32 + r -> row-major (t*32 + r)*KG + g
    n = a.shape[0]
    return a.reshape(n, O // 32, KG, 32, cw).transpose(0, 1, 3, 2, 4).reshape(n, O, KG * cw)


def _unp11(wd, O, KG):                                   # (n, words) p11 piece -> (n, O, KG) bf16 bits (in uint32)
    n, nb = wd.shape[0], O // 32 * KG
    q = wd[:, :11 * nb].reshape(n, nb, 11)
    lo = _shr(mx.take(q, mx.array(_WI.astype(np.int32)), axis=2), _u(_SH.astype(np.uint32)))
    hi = _shl(mx.take(q, mx.array(np.minimum(_WI + 1, 10).astype(np.int32)), axis=2),
              _u(np.where(_NEED, 32 - _SH, 0).astype(np.uint32)))
    c = mx.where(mx.array(_NEED), _or(lo, hi), lo)
    base = _shl(wd[:, 11 * nb], _u(7)).reshape(n, 1, 1)
    v = _or(_shl(_and(c, _u(0x400)), _u(5)), _and(c, _u(0x3FF)) + base)
    return v.reshape(n, O // 32, KG, 32).transpose(0, 1, 3, 2).reshape(n, O, KG)


def _w4(w3, l1, O, KG):                                  # row-major w3 (n, O, 6KG) + l1 (n, O, 2KG) -> 4-bit (n, O, 8KG)
    n = w3.shape[0]
    w = w3.reshape(n, O, 2 * KG, 3)
    a, b, c = w[..., 0], w[..., 1], w[..., 2]
    o0 = _spread8(_and(a, _u(0xFFFFFF)), l1)
    o1 = _spread8(_or(_shr(a, _u(24)), _shl(_and(b, _u(0xFFFF)), _u(8))), _shr(l1, _u(8)))
    o2 = _spread8(_or(_shr(b, _u(16)), _shl(_and(c, _u(0xFF)), _u(16))), _shr(l1, _u(16)))
    o3 = _spread8(_shr(c, _u(8)), _shr(l1, _u(24)))
    return mx.stack([o0, o1, o2, o3], axis=-1).reshape(n, O, 8 * KG)


def _bf16(v):
    return v.astype(mx.uint16).view(mx.bfloat16)


def rebuild_parts(t, w3s, s3s, l1s, bs):
    """The 9 4-bit pieces (PIECES order) of n experts from their part pieces: per projection w3 (n, O, 6KG) and l1 (n, O, 2KG)
    in native order, s3 / b as (n, words) p11 pieces. Exactly the ext's read_expert on a native+p11 record."""
    out = []
    for p in range(3):
        O, KG = int(t["rows3"][p]), int(t["shapes4"][3 * p][0][1]) // 8
        W = _w4(_unnative(w3s[p], O, KG, 6), _unnative(l1s[p], O, KG, 2), O, KG)
        h = _unp11(s3s[p], O, KG)
        S = mx.where(_and(h, _u(0x7FFF)) == 0, h, h - _u(0x80))   # halve_bf16: s = s3 / 2 (exponent - 1; zeros kept)
        out += [W, _bf16(S), _bf16(_unp11(bs[p], O, KG))]
    return out


def lsb_pieces(t, buf):
    """records3 LSB parts (n, lsb bytes) -> per projection the l1 (n, O, 2KG) and b (n, words) pieces (index offsets)."""
    r, msb, n = t["r"], int(t["msb_sz"]), buf.shape[0]
    l1s, bs = [], []
    for p in range(3):
        O, KG = int(t["rows3"][p]), int(t["shapes4"][3 * p][0][1]) // 8
        o1, z1 = int(t["offs"][9 + 2 * p]) - msb, int(r["lsb_piece_size"][2 * p])
        o2, z2 = int(t["offs"][10 + 2 * p]) - msb, int(r["lsb_piece_size"][2 * p + 1])
        l1s.append(mx.array(np.ascontiguousarray(buf[:, o1:o1 + z1]).view(np.uint32)).reshape(n, O, 2 * KG))
        bs.append(mx.array(np.ascontiguousarray(buf[:, o2:o2 + z2]).view(np.uint32)))
    return l1s, bs


def msb_pieces(t, buf):
    """records3 MSB parts (n, msb bytes) -> per projection the w3 (n, O, 6KG) and s3 (n, words) pieces (unit test)."""
    r, n = t["r"], buf.shape[0]
    w3s, s3s = [], []
    for p in range(3):
        O, KG = int(t["rows3"][p]), int(t["shapes4"][3 * p][0][1]) // 8
        o1, z1 = int(t["offs"][3 * p]), int(r["msb_piece_size"][3 * p])
        o2, z2 = int(t["offs"][3 * p + 1]), int(r["msb_piece_size"][3 * p + 1])
        w3s.append(mx.array(np.ascontiguousarray(buf[:, o1:o1 + z1]).view(np.uint32)).reshape(n, O, 6 * KG))
        s3s.append(mx.array(np.ascontiguousarray(buf[:, o2:o2 + z2]).view(np.uint32)))
    return w3s, s3s


_PFD_FD, _PFD_POOL = {}, []


def read_parts(t, ids, off, size):
    """bytes [off, off + size) of each record ids[k] (F_NOCACHE preads on R57_PFD_THREADS threads) -> (n, size) uint8."""
    buf = np.empty((len(ids), size), np.uint8)
    fd = _PFD_FD.get(t["path"])
    if fd is None:
        fd = _PFD_FD[t["path"]] = os.open(t["path"], os.O_RDONLY)
        fcntl.fcntl(fd, fcntl.F_NOCACHE, 1)
    if not _PFD_POOL:
        _PFD_POOL.append(ThreadPoolExecutor(max_workers=int(os.environ.get("R57_PFD_THREADS", "12"))))

    def one(k):
        mv, base, got = memoryview(buf[k]), int(ids[k]) * int(t["recsz"]) + off, 0
        while got < size:
            n_ = os.preadv(fd, [mv[got:]], base + got)
            if n_ <= 0:
                raise OSError(f"PF-D: short read of record {int(ids[k])} at {base + got}")
            got += n_
    list(_PFD_POOL[0].map(one, range(len(ids))))
    return buf


def install_pfd(tier, check=False):
    """Wrap tier.prefill_call (after PF-A's install, before the screen's PFSTAT wrapper). Falls back to the wrapped call
    for PF-A's layer-major prefill (LMC on), the grouped prefill, a layer without a sidecar, or a layout other than 2."""
    if getattr(tier, "_pfd_installed", False):
        return
    orig = tier.prefill_call
    from bigmoe.stream import PIECES

    def prefill_call(cls, self, x, indices, bm, *a, **kw):
        t = bm["tier"]
        ids = np.array(indices)
        uniq = np.unique(ids)
        G = getattr(tier, "_PF_GROUP", 0)
        if (LMC["on"] or t.get("layout") != 2 or t.get("sideP") is None or t.get("side") is None
                or (G and len(uniq) > G and ids.size >= 16 and ids.size >= 4 * len(uniq))):
            PFD["fallback"] += 1
            return orig(cls, self, x, indices, bm, *a, **kw)
        tier.STATS["prefill_calls"] += 1
        u32 = uniq.astype(np.int32).tolist()
        sb = np.array(t["ext"].lookup(bm["L"], u32), np.int64)
        ss = np.array(t["ext"].lookup(t["side"], u32), np.int64)
        rows = np.arange(len(uniq))
        A, B, C = rows[(sb >= 0) & (ss >= 0)], rows[(sb >= 0) & (ss < 0)], rows[sb < 0]
        msb, lsz = int(t["msb_sz"]), int(t["recsz"]) - int(t["msb_sz"])
        lsb = read_parts(t, uniq[B], msb, lsz) if len(B) else None
        tier._reuse_drop()
        scr = [mx.zeros((len(uniq), *sh), dt) for sh, dt in t["shapes4"]]
        mx.eval(*scr)
        if len(C):                                       # C: today's path, into those rows
            tier._read_rebuilt(t, uniq[C].astype(np.int32).tolist(), C.astype(np.int32).tolist(), scr)
        AB = np.concatenate([A, B])
        if len(AB):
            gi = mx.array(sb[AB].astype(np.int32))
            w3s = [mx.take(t["base"][p_]["w3"], gi, axis=0) for p_ in ("gate_proj", "up_proj", "down_proj")]
            s3s = [mx.take(t["base"][p_]["s3"], gi, axis=0) for p_ in ("gate_proj", "up_proj", "down_proj")]
            l1s, bs = [[], [], []], [[], [], []]
            if len(A):
                si = mx.array(ss[A].astype(np.int32))
                for p, p_ in enumerate(("gate_proj", "up_proj", "down_proj")):
                    l1s[p].append(mx.take(t["sideP"][p_]["l1"], si, axis=0))
                    bs[p].append(mx.take(t["sideP"][p_]["b"], si, axis=0))
            if len(B):
                l1B, bB = lsb_pieces(t, lsb)
                for p in range(3):
                    l1s[p].append(l1B[p])
                    bs[p].append(bB[p])
            cat = lambda v: v[0] if len(v) == 1 else mx.concatenate(v, axis=0)
            reb = rebuild_parts(t, w3s, s3s, [cat(v) for v in l1s], [cat(v) for v in bs])
            if check:
                _pfd_check(tier, t, uniq[AB], reb, len(A))
            ix = mx.array(AB.astype(np.int32))
            for i in range(len(scr)):
                scr[i][ix] = reb[i]
            del reb, w3s, s3s, l1s, bs
        PFD["calls"] += 1
        PFD["A"] += len(A)
        PFD["B"] += len(B)
        PFD["C"] += len(C)
        PFD["ssd"] += len(B) * lsz + len(C) * int(t["recsz"])
        compact = np.searchsorted(uniq, ids).astype(np.int32)
        saved = [getattr(getattr(self, proj), field) for proj, field in PIECES]
        for (proj, field), arr in zip(PIECES, scr):
            setattr(getattr(self, proj), field, arr)
        try:
            y = cls.__call__(self, x, mx.array(compact).astype(indices.dtype), *a, **kw)
            mx.eval(y)
        finally:
            for (proj, field), arr in zip(PIECES, saved):
                setattr(getattr(self, proj), field, arr)
        del scr
        mx.clear_cache()
        return y

    tier.prefill_call = prefill_call
    tier._pfd_installed = True


def _pfd_check(tier, t, ids, reb, nA):
    """R57_PFD_CHECK: the same rows from tier._read_rebuilt; counts rows of A (pool side) and B (read side) that differ."""
    ref = [mx.zeros((len(ids), *sh), dt) for sh, dt in t["shapes4"]]
    mx.eval(*ref)
    tier._read_rebuilt(t, ids.astype(np.int32).tolist(), list(range(len(ids))), ref)
    bad = np.zeros(len(ids), bool)
    for g, r_ in zip(reb, ref):
        gv = np.array(g.view(mx.uint16) if g.dtype == mx.bfloat16 else g).reshape(len(ids), -1)
        rv = np.array(r_.view(mx.uint16) if r_.dtype == mx.bfloat16 else r_).reshape(len(ids), -1)
        bad |= (gv != rv).any(axis=1)
    PFD["checked"] += len(ids)
    PFD["bad_A"] += int(bad[:nA].sum())
    PFD["bad_B"] += int(bad[nA:].sum())
