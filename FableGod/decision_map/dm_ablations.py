"""Perturbations for the decision map. Each setup registers ACTIVE[kind] = post(layer_idx, self, args, y) -> y'
(or ACTIVE[kind+"_pre"] = pre(layer_idx, self, args) -> args') for kinds att, gdn, hc, and PERT (dm_common) for the MoE
block (routed experts + shared expert; see dm_common's WIRED note A5).
WIRED (Breakthrough, Mon 2026-11-02; Fable's original in dm_ablations.py.orig):
- topk{k}: SCORE masking, not index masking (the block's ids are in argpartition order): ranks >= k get weight 0 and the
  kept experts keep the model's own weights ("mass"); topk{k}r also rescales the kept weights to the row's original routed
  weight ("renorm"). Q1 = topk2 (and topk2r) on code-sure / code-mid.
- hc_static: every HC read uses its gates' mean over the chunk's positions (per stream and channel) instead of the
  per-token learned gates, on the normed streams, as the model's own read; the input scale stays the model's.
  hc_mean_raw: Fable's literal version (the plain mean of the 4 written residual streams, no norm, no gates).
- shared_zero, moe reuse / fake-quant: inside the MoE block wrapper (routed part only for reuse and quant).
- *_q4 on att / gdn / hc: 4-bit fake quantisation of the layer OUTPUT (per row, max-abs scale), as Fable wrote it:
  an activation test, not the weight test HC4 was at 12 GB."""
import mlx.core as mx
import mlx.nn as nn
from dm_common import ACTIVE, PREV, LAYERS, PERT, _shift, _fq

def topk_experts(k, renorm=False):
    def setup(): PERT.update(topk=k, renorm=renorm)
    return setup

def hc_static():
    def post(li, self, a, y):
        if not isinstance(y, tuple): return y
        hyper = y[1]                                     # the written stream the read used
        hc, D = self.hc_count, self.hidden_size
        normed = self.hc_norm(hyper)
        mix = nn.silu(self.input_mix_weight_down(normed) / hc)
        mix = mx.sigmoid(self.input_mix_weight_up(mix))
        mix = mix.reshape(*mix.shape[:-1], hc, D)
        mix = mx.broadcast_to(mix.mean(axis=-3, keepdims=True), mix.shape) if mix.ndim >= 3 else mix
        grouped = normed.reshape(*normed.shape[:-1], hc, D)
        return (mx.mean(mix * grouped, axis=-2).astype(y[0].dtype),) + tuple(y[1:])
    def setup(): ACTIVE["hc"] = post
    return setup

def hc_mean_raw():
    def post(li, self, a, y):
        if not isinstance(y, tuple): return y
        hyper = y[1]
        mean = hyper.reshape(*hyper.shape[:-1], self.hc_count, self.hidden_size).mean(axis=-2)
        return (mean.astype(y[0].dtype),) + tuple(y[1:])
    def setup(): ACTIVE["hc"] = post
    return setup

def shared_zero():
    def setup(): PERT.update(shared_zero=True)
    return setup

def reuse_prev(kind, layers=None, lag=1, chain=False, chain_max=0):
    if kind == "moe":                                    # lag / chain (/ bounded chain): dm_common._reuse (night 2)
        def setup(): PERT.update(reuse="all" if layers is None else set(layers), lag=lag, chain=chain,
                                 chain_max=chain_max)
        return setup
    assert lag == 1 and not chain, "lag / chain are wired for the MoE block only"
    def post(li, self, a, y):
        if layers is not None and li not in layers: return y
        z = y[0] if isinstance(y, tuple) else y
        shifted = _shift(z, -2)
        return (shifted,) + tuple(y[1:]) if isinstance(y, tuple) else shifted
    def setup(): ACTIVE[kind] = post
    return setup

def fake_quant(kind, bits, layers=None):
    if kind == "moe":
        def setup(): PERT.update(q=bits)
        return setup
    def post(li, self, a, y):
        if layers is not None and li not in layers: return y
        return (_fq(y[0], bits).astype(y[0].dtype),) + tuple(y[1:]) if isinstance(y, tuple) else _fq(y, bits).astype(y.dtype)
    def setup(): ACTIVE[kind] = post
    return setup

def gate_k(spec):
    """DAY9 Q1 / Q2 (Breakthrough, Mon 2026-11-02): per-row expert counts from the REALIZABLE gate (dm_gate.py: DFlash2's
    cf for the draft each row verifies), the kept experts at the model's own weights (mass, no renorm)."""
    def setup(): PERT.update(gate=spec, renorm=False)
    return setup

def hc8w(ple=True, bits=8, group_size=64):
    """DAY9 Q3: the HC mixers (input_mix_weight_down / up of every trunk GatedResidual) and, with ple, the PLE key / value
    projections at MLX affine 8-bit, group 64: the 12 GB line's HC8 (~/Breakthrough/v3n/hc8.py's recipe) as a WEIGHT
    change. Only the new modules are evaluated (the streamed model is never forced whole); clear() restores bf16.
    Quantized mixers fail GatedResidual._fused_read_applies (it checks for scales), so reads take the eager chain."""
    def setup():
        from dm_common import RT, TEARDOWN, Q
        rt = RT["rt"]; model = rt.model if hasattr(rt, "model") else rt
        TM = getattr(model, "language_model", model); undo = []
        for name, mod in TM.named_modules():
            if name.startswith("mtp"): continue
            tg = (["input_mix_weight_down", "input_mix_weight_up"] if isinstance(mod, Q.GatedResidual) else
                  ["key_proj", "value_proj"] if ple and isinstance(mod, Q.PLELayer) else [])
            for attr in tg:
                lin = getattr(mod, attr)
                if not isinstance(lin, nn.Linear) or lin.weight.shape[1] % group_size: continue
                q = nn.QuantizedLinear.from_linear(lin, group_size, bits); mx.eval(q.parameters())
                setattr(mod, attr, q); undo.append((mod, attr, lin))
        def restore():
            for mod, attr, lin in undo: setattr(mod, attr, lin)
        TEARDOWN.append(restore)
        assert len(undo) >= 96, f"hc8w swapped only {len(undo)} linears"
        print(f"[dm] hc8w: {len(undo)} linears at {bits} bits, group {group_size} (ple {ple})", flush=True)
    return setup

def gdn_state_bf16():
    def setup(): raise NotImplementedError("gdn_state_bf16 needs the GDN cache patch (A3); not wired")
    return setup

ABLATIONS = {
    "topk2": topk_experts(2), "topk2r": topk_experts(2, renorm=True), "topk5": topk_experts(5), "topk8": topk_experts(8),
    "topk10": topk_experts(10),                          # identity through the wrapper (a self-check: 0 flips expected)
    "hc_static": hc_static(), "hc_mean_raw": hc_mean_raw(), "shared_zero": shared_zero(),
    "moe_reuse_prev_all": reuse_prev("moe"), "att_reuse_prev": reuse_prev("att"), "gdn_reuse_prev": reuse_prev("gdn"),
    "moe_q4_all": fake_quant("moe", 4), "hc_q4": fake_quant("hc", 4), "att_q4": fake_quant("att", 4), "gdn_q4": fake_quant("gdn", 4),
    "gdn_state_bf16": gdn_state_bf16(),
    "gate_bands": gate_k(("bands",)), "hc8w": hc8w(), "hc8w_mix": hc8w(ple=False),
}
for g in range(4):                                   # per-group MoE reuse (12 layers each), then per layer on night 2
    ABLATIONS[f"moe_reuse_prev_g{g}"] = reuse_prev("moe", set(range(12 * g, 12 * g + 12)))
for L in range(48):
    ABLATIONS[f"moe_reuse_prev_L{L:02d}"] = reuse_prev("moe", {L})

import re
def ablation(name):
    """ABLATIONS[name], or night 2's MoE reuse family by name (NewIdeas stage 1, Mon 2026-11-02):
    moe_reuse_{prev|lag<k>|chain[<S>]}_L<a>_<b>[_topk<k>] reuses the routed output on layers a..b inclusive: prev =
    lag 1, lag<k> = copy from row t - k, chain = sure rows (baseline class) take the last computed row's output, chain<S>
    = the same with a refresh so no output is reused more than S rows on (stage 2); _topk<k> stacks top-k (mass) on
    every row and layer; e.g. moe_reuse_prev_L12_35, moe_reuse_lag4_L12_35, moe_reuse_chain1_L08_35_topk2."""
    if name in ABLATIONS: return ABLATIONS[name]
    g = re.fullmatch(r"gate_top(\d+)_cf(0\d+)", name)       # DAY9 Q1: e.g. gate_top2_cf099 (cf >= 0.99), _cf0999
    if g: return gate_k(("top", float("0." + g.group(2)[1:]), int(g.group(1))))
    c = re.fullmatch(r"cert_top(\d+)_p(0\d+)", name)          # mission 20's two-pass check: e.g. cert_top2_p099, cert_top5_p09
    if c: return gate_k(("cert", "topk" + c.group(1), float("0." + c.group(2)[1:]), int(c.group(1))))
    c = re.fullmatch(r"acert_top(\d+)_p(0\d+)_p(0\d+)_cf(0\d+)", name)   # the adaptive certificate: e.g. acert_top2_p07_p09_cf099
    if c: return gate_k(("acert", "topk" + c.group(1), *(float("0." + c.group(i)[1:]) for i in (2, 3, 4)), int(c.group(1))))
    t = re.fullmatch(r"gate_top2t([34])_cf(0\d+)", name)      # M-18: gated rows' top-2 from records3 at 3 bits (t4 = control)
    if t:
        spec = ("t3", float("0." + t.group(2)[1:]))
        def setup(): PERT.update(gate=spec, renorm=False, t3=int(t.group(1)))
        return setup
    m = re.fullmatch(r"moe_reuse_(prev|lag(\d+)|chain(\d*))_L(\d+)_(\d+)(?:_topk(\d+))?(?:_dcf(0\d+))?", name)
    if not m: raise KeyError(name)
    lo, hi = int(m.group(4)), int(m.group(5)); assert 0 <= lo <= hi < 48, name
    base = reuse_prev("moe", set(range(lo, hi + 1)), lag=int(m.group(2) or 1), chain=m.group(1).startswith("chain"),
                      chain_max=int(m.group(3) or 0))
    if m.group(7):                                       # _dcf<thr>: the chain skips by the drafter's cf (realizable)
        assert m.group(1).startswith("chain"), name
        b0 = base; thr = float("0." + m.group(7)[1:])
        def base(): b0(); PERT.update(chain_gate=thr)
    if not m.group(6): return base
    def setup(): base(); PERT.update(topk=int(m.group(6)), renorm=False)
    return setup
