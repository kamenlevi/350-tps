"""TRL-G (Leap, Wed 2026-11-04 20:4x; TRELLIS FULL-STORE prep, the orchestrator 20:0x item 2): the routed expert GLU served
straight from trellis codes (trl_encode.py's format), grouped per distinct expert like NAX (gpu_grp; no tiers).
  Format per expert (trl_encode.py): {p}_w uint32 [O/16, K/16, TW] (16 x 16 tiles of W' = W R, row-major in the tile;
  bitstream = s_0's 12 bits then k bits per value, MSB first; TW = 17 words at k 2, 25 at k 3), {p}_s bf16 [O] (row RMS
  sc). Weight (o, i) = inst3(state) / RMS3 x sc[o]; state of tile value t = bits [k t, k t + 12) of the tile's stream.
  So tile row r (16 values) = bits [16 k r, 16 k r + 15 k + 12): k 2 -> words r, r + 1; k 3 -> words 3r/2 .. +2 (bit
  offset 16 when r is odd).
  y = W x = W' (R^T x): x' = H512(s_L * x) once per token (per-layer signs, seed L); h' = H128(s_e * h) per pair (seed
  1000 L + e); H = Sylvester / sqrt(n) blocks (fit_q.hadamard; mx.hadamard_transform's order).
Kernels: A = gate + up + SwiGLU, B = down. One threadgroup = (group, block of output rows); lane = one output row: it walks
its row's tiles, decodes 16 states from a 64-bit window, computes 3INST (no LUT), and serves up to 4 rows of the group per
pass (a group of m rows takes ceil(m / 4) passes; S 16 calls have ~2.6 rows per expert).
API: tier_glu_trl(x, P, slot, grp=None) -> y per pair [M R, D] bf16; trl_moe(...) adds the combine (combine_phase, as
NAX6-N's harness). P = pools: wg / wu [E, 40, 160, TWg], wd [E, 160, 40, TWd] uint32; sg / su [E, 640], sd [E, 2560] bf16;
sx [2560] f32; sdn [E, 640] f32; kg / kd bits.
usage: [BigMoE venv] tierglu_trl.py test -> ~/Leap/data/tierglu_trl_test.txt (GPU; MEM < 2 GB; share lock)"""
import math, os, sys, time
from functools import lru_cache
import numpy as np
import mlx.core as mx
sys.path.insert(0, os.path.expanduser("~/Leap/third_party/ms_gdn"))
sys.path.insert(0, os.path.expanduser("~/Leap/scripts"))
import trl_metal as TM

K, N, D = 2560, 640, 2560
TWK = {2: 17, 3: 25}
INV_RMS3 = 1.0 / TM.RMS3

_HDR = f"constant constexpr float INV_C = {INV_RMS3!r}f;\n" + r"""
inline float inst3(uint s) {                                // QTIP 3INST: an LCG, a mask, a sum of two fp16 halves
    const uint xq = 89226354u * s + 64248484u;
    const uint mq = (xq & 0x8FFF8FFFu) ^ 0x3B603B60u;
    const half2 hv = as_type<half2>(mq);
    return static_cast<float>(hv.x) + static_cast<float>(hv.y);
}
// the 64-bit window holding tile row rr's states (bits [16 KBT rr, 16 KBT rr + 15 KBT + 12) of the tile's stream)
template <int KBT> inline ulong trl_win(const device uint* wt, uint rr) {
    if (KBT == 2) return ((ulong)wt[rr] << 32) | (ulong)wt[rr + 1];
    const uint wi = (3u * rr) >> 1;
    const uint w0 = wt[wi], w1 = wt[wi + 1];
    if ((rr & 1u) == 0u) return ((ulong)w0 << 32) | (ulong)w1;
    const uint w2 = wt[wi + 2];
    return ((ulong)((w0 << 16) | (w1 >> 16)) << 32) | (ulong)((w1 << 16) | (w2 >> 16));
}
// 16 states of the window -> dot products with up to RP_C rows (16 values each, float4 x 4)
#define TRL_DOT4(KBT, WIN, XR, NROW, ACC)                                                           \
    {                                                                                               \
        float wv[16];                                                                               \
        for (int c = 0; c < 16; ++c) wv[c] = inst3((uint)((WIN) >> (52 - KBT * c)) & 0xFFFu);       \
        for (int i = 0; i < RP_C; ++i) {                                                            \
            if (i < (NROW)) {                                                                       \
                const device float4* xv = (const device float4*)(XR[i]);                            \
                float a = 0.0f;                                                                     \
                for (int q = 0; q < 4; ++q) {                                                       \
                    const float4 t = xv[q];                                                         \
                    a = fma(wv[4 * q], t.x, a); a = fma(wv[4 * q + 1], t.y, a);                     \
                    a = fma(wv[4 * q + 2], t.z, a); a = fma(wv[4 * q + 3], t.w, a);                 \
                }                                                                                   \
                ACC[i] += a;                                                                        \
            }                                                                                       \
        }                                                                                           \
    }
"""

_A = r"""
    constexpr int KK = K_C, NN = N_C, NSG = NSG_C, HS = NSG / 2, KT = KK / 16, NT = NN / 16, TW = KG == 2 ? 17 : 25;
    threadgroup float gv[RP_C][HS * 32];
    const uint lane = thread_index_in_simdgroup, sgi = simdgroup_index_in_threadgroup;
    const uint g = threadgroup_position_in_grid.y;
    if (g >= (uint)nseg[0]) return;
    const int s0 = seg[g], m = seg[g + 1] - s0;
    const bool up = sgi >= (uint)HS;
    const uint lr = (sgi % HS) * 32 + lane;
    const uint row = threadgroup_position_in_grid.x * (HS * 32) + lr;
    const uint e = (uint)slot[pidx[s0]];
    const device uint* W = (up ? wu : wg) + (((size_t)e * NT + (row >> 4)) * KT) * TW;
    const uint rr = row & 15u;
    const float sc = static_cast<float>((up ? su : sg)[(size_t)e * NN + row]) * INV_C;
    for (int c0 = 0; c0 < m; c0 += RP_C) {
        const int nrow = min(RP_C, m - c0);
        float acc[RP_C];
        const device float* xb[RP_C];
        for (int i = 0; i < RP_C; ++i) { acc[i] = 0.0f; xb[i] = xq + (size_t)(pidx[s0 + c0 + min(i, nrow - 1)] / NR_C) * KK; }
        for (int tc = 0; tc < KT; ++tc) {
            const ulong win = trl_win<KG>(W + tc * TW, rr);
            const device float* xr[RP_C];
            for (int i = 0; i < RP_C; ++i) xr[i] = xb[i] + tc * 16;
            TRL_DOT4(KG, win, xr, nrow, acc)
        }
        if (!up) for (int i = 0; i < RP_C; ++i) gv[i][lr] = acc[i] * sc;
        threadgroup_barrier(mem_flags::mem_threadgroup);
        if (up) {
            for (int i = 0; i < nrow; ++i) {
                const float gg = gv[i][lr];
                h[(size_t)pidx[s0 + c0 + i] * NN + row] = gg / (1.0f + metal::exp(-gg)) * (acc[i] * sc);
            }
        }
        threadgroup_barrier(mem_flags::mem_threadgroup);
    }
"""

_B = r"""
    constexpr int NN = N_C, DD = D_C, NSG = NSG_C, NT = NN / 16, TW = KD == 2 ? 17 : 25;
    const uint lane = thread_index_in_simdgroup, sgi = simdgroup_index_in_threadgroup;
    const uint g = threadgroup_position_in_grid.y;
    if (g >= (uint)nseg[0]) return;
    const int s0 = seg[g], m = seg[g + 1] - s0;
    const uint row = (threadgroup_position_in_grid.x * NSG + sgi) * 32 + lane;
    const uint e = (uint)slot[pidx[s0]];
    const device uint* W = wd + (((size_t)e * (DD / 16) + (row >> 4)) * NT) * TW;
    const uint rr = row & 15u;
    const float sc = static_cast<float>(sd[(size_t)e * DD + row]) * INV_C;
    for (int c0 = 0; c0 < m; c0 += RP_C) {
        const int nrow = min(RP_C, m - c0);
        float acc[RP_C];
        const device float* hb[RP_C];
        for (int i = 0; i < RP_C; ++i) { acc[i] = 0.0f; hb[i] = hq + (size_t)pidx[s0 + c0 + min(i, nrow - 1)] * NN; }
        for (int tc = 0; tc < NT; ++tc) {
            const ulong win = trl_win<KD>(W + tc * TW, rr);
            const device float* hr[RP_C];
            for (int i = 0; i < RP_C; ++i) hr[i] = hb[i] + tc * 16;
            TRL_DOT4(KD, win, hr, nrow, acc)
        }
        for (int i = 0; i < nrow; ++i) y[(size_t)pidx[s0 + c0 + i] * DD + row] = static_cast<TO>(acc[i] * sc);
    }
"""

# A2: lane = gate row o AND up row o; x' rows loaded once for both; SwiGLU in registers
_A2 = r"""
    constexpr int KK = K_C, NN = N_C, NSG = NSG_C, KT = KK / 16, NT = NN / 16, TW = KG == 2 ? 17 : 25;
    const uint lane = thread_index_in_simdgroup, sgi = simdgroup_index_in_threadgroup;
    const uint g = threadgroup_position_in_grid.y;
    if (g >= (uint)nseg[0]) return;
    const int s0 = seg[g], m = seg[g + 1] - s0;
    const uint row = (threadgroup_position_in_grid.x * NSG + sgi) * 32 + lane;
    const uint e = (uint)slot[pidx[s0]];
    const size_t tb = (((size_t)e * NT + (row >> 4)) * KT) * TW;
    const device uint* Wg = wg + tb;
    const device uint* Wu = wu + tb;
    const uint rr = row & 15u;
    const float scg = static_cast<float>(sg[(size_t)e * NN + row]) * INV_C;
    const float scu = static_cast<float>(su[(size_t)e * NN + row]) * INV_C;
    for (int c0 = 0; c0 < m; c0 += RP_C) {
        const int nrow = min(RP_C, m - c0);
        float ag[RP_C], au[RP_C];
        const device float* xb[RP_C];
        for (int i = 0; i < RP_C; ++i) { ag[i] = 0.0f; au[i] = 0.0f; xb[i] = xq + (size_t)(pidx[s0 + c0 + min(i, nrow - 1)] / NR_C) * KK; }
        for (int tc = 0; tc < KT; ++tc) {
            const ulong w1 = trl_win<KG>(Wg + tc * TW, rr), w2 = trl_win<KG>(Wu + tc * TW, rr);
            float vg[16], vu[16];
            for (int c = 0; c < 16; ++c) {
                vg[c] = inst3((uint)(w1 >> (52 - KG * c)) & 0xFFFu);
                vu[c] = inst3((uint)(w2 >> (52 - KG * c)) & 0xFFFu);
            }
            for (int i = 0; i < RP_C; ++i) {
                if (i < nrow) {
                    const device float4* xv = (const device float4*)(xb[i] + tc * 16);
                    float a = 0.0f, b = 0.0f;
                    for (int q = 0; q < 4; ++q) {
                        const float4 t = xv[q];
                        a = fma(vg[4 * q], t.x, a); a = fma(vg[4 * q + 1], t.y, a);
                        a = fma(vg[4 * q + 2], t.z, a); a = fma(vg[4 * q + 3], t.w, a);
                        b = fma(vu[4 * q], t.x, b); b = fma(vu[4 * q + 1], t.y, b);
                        b = fma(vu[4 * q + 2], t.z, b); b = fma(vu[4 * q + 3], t.w, b);
                    }
                    ag[i] += a; au[i] += b;
                }
            }
        }
        for (int i = 0; i < nrow; ++i) {
            const float gg = ag[i] * scg;
            h[(size_t)pidx[s0 + c0 + i] * NN + row] = gg / (1.0f + metal::exp(-gg)) * (au[i] * scu);
        }
    }
"""


@lru_cache(None)
def _ka2():
    return mx.fast.metal_kernel(name="trl_g_a2", input_names=["xq", "wg", "wu", "sg", "su", "slot", "pidx", "seg", "nseg"],
                                output_names=["h"], source=_A2, header=_HDR)


@lru_cache(None)
def _ka():
    return mx.fast.metal_kernel(name="trl_g_a", input_names=["xq", "wg", "wu", "sg", "su", "slot", "pidx", "seg", "nseg"],
                                output_names=["h"], source=_A, header=_HDR)


@lru_cache(None)
def _kb():
    return mx.fast.metal_kernel(name="trl_g_b", input_names=["hq", "wd", "sd", "slot", "pidx", "seg", "nseg"],
                                output_names=["y"], source=_B, header=_HDR)


def signs(L, E=512):
    """fit_b3.rot's sign vectors: per layer (gate / up, seed L) and per expert (down, seed 1000 L + e)"""
    sx = np.random.default_rng(L).choice(np.array([-1.0, 1.0]), K).astype(np.float32)
    sdn = np.stack([np.random.default_rng(1000 * L + e).choice(np.array([-1.0, 1.0]), N) for e in range(E)]).astype(np.float32)
    return sx, sdn


def grp_of(slot, R):
    """gpu_grp with a tier-free plan: groups = distinct experts (split every 16 pairs)"""
    import tierglu_nax6 as N6
    ms = slot.reshape(-1, R)
    return N6.gpu_grp(ms, ms[:, :1], "3" * R)


def tier_glu_trl(x, P, slot, R=10, grp=None, nsg_a=4, nsg_b=4, out=mx.bfloat16, a2=False, rp=4):
    """x [M, K] bf16; slot [M, R] int (experts, rank order) -> y per pair [M R, D] bf16"""
    M = x.shape[0]
    NP = M * R
    slot = slot.astype(mx.int32).reshape(-1)
    if grp is None:
        grp = grp_of(slot, R)
    pidx, seg, nseg = grp[:3]
    xq = mx.hadamard_transform((x.astype(mx.float32) * P["sx"]).reshape(M, K // 512, 512),
                               scale=1 / math.sqrt(512)).reshape(M, K)
    hs = (nsg_a // 2) * 32 if not a2 else nsg_a * 32
    (h,) = (_ka2() if a2 else _ka())(inputs=[xq, P["wg"], P["wu"], P["sg"], P["su"], slot, pidx, seg, nseg],
                                     template=[("KG", P["kg"]), ("K_C", K), ("N_C", N), ("NSG_C", nsg_a), ("NR_C", R), ("RP_C", rp)],
                                     grid=(N // hs * 32 * nsg_a, NP, 1), threadgroup=(32 * nsg_a, 1, 1),
                                     output_shapes=[(NP, N)], output_dtypes=[mx.float32])
    hq = mx.hadamard_transform((h * P["sdn"][slot]).reshape(NP, N // 128, 128), scale=1 / math.sqrt(128)).reshape(NP, N)
    (y,) = _kb()(inputs=[hq, P["wd"], P["sd"], slot, pidx, seg, nseg],
                 template=[("KD", P["kd"]), ("N_C", N), ("D_C", D), ("NSG_C", nsg_b), ("TO", out), ("RP_C", rp)],
                 grid=(D // (32 * nsg_b) * 32 * nsg_b, NP, 1), threadgroup=(32 * nsg_b, 1, 1),
                 output_shapes=[(NP, D)], output_dtypes=[out])
    return y


def trl_moe(x, P, slot, scores, R=10, grp=None, **kw):
    import tierglu as TG
    y = tier_glu_trl(x, P, slot, R, grp, **kw)
    M = x.shape[0]
    return TG.combine_phase(y, y, mx.ones((M, R), mx.int32), scores)


def random_pools(E=512, kg=2, kd=3, seed=0, L=18):
    rng = np.random.default_rng(seed)
    P = {"kg": kg, "kd": kd}
    for nm, (O, I, k) in (("g", (N, K, kg)), ("u", (N, K, kg)), ("d", (D, N, kd))):
        P["w" + nm] = mx.array(rng.integers(0, 1 << 32, (E, O // 16, I // 16, TWK[k]), dtype=np.uint32))
        P["s" + nm] = mx.array((rng.uniform(0.6, 1.4, (E, O)) * 0.02).astype(np.float32)).astype(mx.bfloat16)
    sx, sdn = signs(L, E)
    P["sx"], P["sdn"] = mx.array(sx), mx.array(sdn)
    mx.eval([v for v in P.values() if isinstance(v, mx.array)])
    return P


def ref_forward(x, P, ids, scores, pairs=False):
    """float64 numpy: dense Q = LUT3[states] x sc per expert from the streams (TM.unpack_states), the same rotations"""
    import fit_q as F                                             # Fit12's hadamard (Sylvester / sqrt n), read only
    xs = np.array(x.astype(mx.float32)).astype(np.float64)
    ids = np.array(ids).astype(np.int64)
    sc = {k: np.array(P[k].astype(mx.float32)).astype(np.float64) for k in ("sg", "su", "sd")}
    sx, sdn = np.array(P["sx"]).astype(np.float64), np.array(P["sdn"]).astype(np.float64)
    H512, H128 = F.hadamard(512).astype(np.float64), F.hadamard(128).astype(np.float64)
    cache = {}

    def Q(nm, e, O, I, k):
        if (nm, e) not in cache:
            w = np.array(P["w" + nm][e]).reshape(-1, TWK[k])
            st = TM.unpack_states(w, k).reshape(O // 16, I // 16, 16, 16)
            cache[(nm, e)] = TM.LUT3[st.astype(np.int64)].astype(np.float64).transpose(0, 2, 1, 3).reshape(O, I) \
                * sc["s" + nm][e][:, None]
        return cache[(nm, e)]
    M, R = ids.shape
    out = np.zeros((M, D))
    yp = np.zeros((M * R, D))
    sco = np.array(scores.astype(mx.float32)).astype(np.float64)
    for m in range(M):
        xp = ((xs[m] * sx).reshape(-1, 512) @ H512).reshape(-1)
        for r in range(R):
            e = int(ids[m, r])
            g, u = Q("g", e, N, K, P["kg"]) @ xp, Q("u", e, N, K, P["kg"]) @ xp
            hh = g / (1 + np.exp(-g)) * u
            hp = ((hh * sdn[e]).reshape(-1, 128) @ H128).reshape(-1)
            yp[m * R + r] = Q("d", e, D, N, P["kd"]) @ hp
            out[m] += sco[m, r] * yp[m * R + r]
    return yp if pairs else out


def _say(path):
    def say(s=""):
        print(s, flush=True)
        open(path, "a").write(s + "\n")
    return say


def test():
    sys.path.insert(0, os.path.expanduser("~/Fit12/scripts"))
    say = _say(os.path.expanduser("~/Leap/data/tierglu_trl_test.txt"))
    say(f"\nTRL-G test {time.strftime('%a %H:%M:%S')}: MLX {mx.__version__}")
    ok = True
    for kg, kd in ((2, 3), (3, 3), (2, 2)):
        P = random_pools(E=64, kg=kg, kd=kd, seed=kg * 10 + kd)
        rng = np.random.default_rng(5)
        for M in (1, 3, 16):
            ids = np.stack([rng.choice(64 if M < 16 else 12, 10, replace=False) for _ in range(M)]).astype(np.int32)
            x = mx.array(rng.standard_normal((M, K)).astype(np.float32) * 0.5).astype(mx.bfloat16)
            sco = mx.softmax(mx.array(rng.standard_normal((M, 10)).astype(np.float32)), axis=-1).astype(mx.bfloat16)
            yk = trl_moe(x, P, mx.array(ids), sco)
            y32 = tier_glu_trl(x, P, mx.array(ids), out=mx.float32)
            y32b = tier_glu_trl(x, P, mx.array(ids), out=mx.float32, a2=True, nsg_a=2)
            y32c = tier_glu_trl(x, P, mx.array(ids), out=mx.float32, a2=True, nsg_a=2, rp=8)
            mx.eval(yk, y32, y32b, y32c)
            a2same = bool(mx.array_equal(y32, y32b).item()) and bool(mx.array_equal(y32, y32c).item())
            yr = ref_forward(x, P, ids, sco)
            yrp = ref_forward(x, P, ids, sco, pairs=True)
            err = float(np.abs(np.array(yk.astype(mx.float32)) - yr).max() / np.abs(yr).max())
            d32 = np.array(y32) - yrp
            e32 = float(np.abs(d32).max() / np.abs(yrp).max())
            r32 = float(np.sqrt((d32 ** 2).mean() / (yrp ** 2).mean()))
            ok &= e32 <= 1e-4
            say(f"k {kg} / {kd}, M {M:2d} ({'shared experts, groups up to 16 rows' if M == 16 else 'random experts'}): "
                f"fp32 per pair: max |dy| / max |y| {e32:.2e}, rms {r32:.2e} {'ok' if e32 <= 1e-4 else 'FAIL'}; "
                f"bf16 combined (engine path): {err:.2e}; A2 and A2 rp 8 == A bitwise {a2same}")
    say(f"TRL-G test: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if test() else 1)
