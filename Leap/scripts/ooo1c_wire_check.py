"""OOO-1C wiring check (Leap, Wed 2026-11-04; TABLE_350 'OOO-1C'): ref2 with ref2_ooo1c_patch.py, on real records3 pools of
layer 20, a stand-in gate (release regions in BigMoE's layout: 128 entries x gated.PAIRS x 32 * (2 + XLINES) ints) and a
stand-in post (dep = [0, pre-resolved slots ...]), regions released before the call:
 (a) 3c: ref2._ooo_sel with ooo_1c on == tier_glu(scores) on the released slots, bitwise; COUNTS ooo_1c +1;
 (b) NAX: tier_nax_ooo + ooo_1c: _ooo_sel -> _ooo_nax6 -> one call == NAX6 on the released slots + combine_phase;
 (c) ooo_1c off: the old route (a stand-in for BigMoE's _ooo_call is what runs);
 (d) a gate without regions (event mode): the one-call path declines and the old route runs;
 (e) ref2.self_test PASS.
Usage: [BigMoE venv] ooo1c_wire_check.py -> ~/Leap/data/ooo1c_wire_check.txt (GPU, MEM ~2 GB; share lock)"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.expanduser("~/BigMoE"))
sys.path.insert(0, os.path.expanduser("~/Leap/third_party/ms_gdn"))
sys.path.insert(0, os.path.expanduser("~/Leap/scripts"))
import mlx.core as mx
import ref2
import bigmoe.gated as BG
import bigmoe.tier as BT
import tierglu_nax6 as N6
import ooo1c as OC

OUT = os.path.expanduser("~/Leap/data/ooo1c_wire_check.txt")
def say(s):
    print(s, flush=True)
    open(OUT, "a").write(s + "\n")
say(f"\nOOO-1C wiring check {time.strftime('%a %H:%M:%S')} (gated MODE {BG.MODE}, PAIRS {BG.PAIRS}, XLINES {BG.XLINES})")
assert "ooo_1c" in ref2.CFG and not ref2.CFG["ooo_1c"], "patch missing or switch not default off"
PLAN, M, K, R4, L, NL = "4433333333", 16, 10, 2, 20, 96
BT.PLAN = PLAN
ref2.apply()
TG = BT._tier_glu_mod()
RD = os.path.expanduser("~/BigMoE/models/bare/records3")
r = json.load(open(f"{RD}/index.json"))["layers"][str(L)]
SH = {"gate_proj": (640, 2560), "up_proj": (640, 2560), "down_proj": (2560, 640)}
raw = np.memmap(f"{RD}/{r['file']}", dtype=np.uint8, mode="r", shape=(r["E"], r["recsz"]))
msb, lsb = {}, {}
for p, pr in enumerate(("gate_proj", "up_proj", "down_proj")):
    o, i = SH[pr]
    ow, os_, ob = r["msb_piece_off"][3 * p:3 * p + 3]
    lw, lb = r["lsb_piece_off"][2 * p:2 * p + 2]
    msb[pr] = {"w3": mx.array(np.ascontiguousarray(raw[:, ow:ow + o * i * 3 // 8]).view(np.uint32).reshape(-1, o, i * 3 // 32)),
               "s3": mx.array(np.ascontiguousarray(raw[:, os_:os_ + o * i // 32]).view(np.uint16).reshape(-1, o, i // 64)).view(mx.bfloat16),
               "b3": mx.array(np.ascontiguousarray(raw[:, ob:ob + o * i // 32]).view(np.uint16).reshape(-1, o, i // 64)).view(mx.bfloat16)}
    lsb[pr] = {"l1": mx.array(np.ascontiguousarray(raw[:, lw:lw + o * i // 8]).view(np.uint32).reshape(-1, o, i // 32)),
               "b": mx.array(np.ascontiguousarray(raw[:, lb:lb + o * i // 32]).view(np.uint16).reshape(-1, o, i // 64)).view(mx.bfloat16)}
mx.eval([v for d in (msb, lsb) for pr in d for v in d[pr].values()])
del raw
RS = 32 * (2 + BG.XLINES)

class Gate:                                                    # the parts of gated.Gate the one-call path reads
    def __init__(self, regions=True):
        self.nl, self.nreg, self.seq = NL, 128, 9
        if regions:
            self.region = mx.zeros((self.nreg * BG.PAIRS * RS,), mx.int32)
            self.status = mx.zeros((4096,), mx.int32)
            mx.eval(self.region, self.status)
            self.REG = np.frombuffer(memoryview(self.region), dtype=np.int32)
            self.REG.setflags(write=True)
    def release(self, Lx, slots):
        off = ((self.seq * self.nl + Lx) % self.nreg) * BG.PAIRS * RS
        for i, v in enumerate(OC.release_words(slots, self.seq)):
            self.REG[off + 32 * (i // 31) + 1 + i % 31] = np.int32(np.uint32(v).view(np.int32))
        for j in range(RS // 32 - 1, -1, -1):
            self.REG[off + 32 * j] = self.seq

rng = np.random.default_rng(8)
ids = np.stack([rng.choice(512, K, replace=False) for _ in range(M)]).astype(np.int32)
uniq = np.unique(ids)
res_m = set(rng.choice(uniq, int(0.9 * len(uniq)), replace=False).tolist())
res_l = set(rng.choice(uniq, int(0.9 * len(uniq)), replace=False).tolist())
sm, sl = ids.copy(), ids[:, :R4].copy()
pre_m = np.where(np.isin(ids, list(res_m)), ids, -1).astype(np.int32)
pre_l = np.where(np.isin(sl, list(res_l)), sl, -1).astype(np.int32)
t = {"base": msb, "sideP": lsb, "segs": [(0, 2, 4), (2, 10, 3)], "side": NL // 2 + L}
pre = {L: pre_m.reshape(-1), NL // 2 + L: pre_l.reshape(-1)}
def post(Lx, ids_, after=None):
    flat = pre[Lx]
    return mx.array(np.concatenate([[0], flat]).astype(np.int32)), int(flat.size)
x = (mx.random.normal((M, 2560)) * 0.5).astype(mx.bfloat16)
sc = mx.softmax(mx.random.normal((M, K)), axis=-1).astype(mx.bfloat16)
mx.eval(x, sc)
eqb = lambda a, b: bool(a.shape == b.shape and mx.all(a.view(mx.uint16) == b.view(mx.uint16)).item())
gate = Gate()
gate.release(L, sm.reshape(-1).tolist()); gate.release(NL // 2 + L, sl.reshape(-1).tolist())
bm = {"gate": gate, "L": L}
ok = True
# (a) 3c
ref2.CFG["ooo_1c"], ref2.CFG["tier_nax_ooo"] = True, False
c0 = ref2.COUNTS["ooo_1c"]
y = ref2._ooo_sel(x, mx.array(ids), bm, dict(t), post, sc, None)
y_ref = TG.tier_glu(x, msb, lsb, mx.array(sm), mx.array(sl), plan=PLAN, scores=sc)
mx.eval(y, y_ref)
a_ok = eqb(y, y_ref) and ref2.COUNTS["ooo_1c"] == c0 + 1 and int(np.frombuffer(memoryview(gate.status), np.int32)[0]) == 0
ok &= a_ok
say(f"(a) 3c one call via ref2._ooo_sel == tier_glu(scores) on the released slots: {a_ok}")
# (b) NAX
ref2.CFG["tier_nax_ooo"] = True
c0 = ref2.COUNTS["ooo_1c"]
y = ref2._ooo_sel(x, mx.array(ids), bm, dict(t), post, sc, None)
yn = N6.tier_glu_nax6(x, msb, lsb, mx.array(sm), mx.array(sl), plan=PLAN, grp=N6.gpu_grp(mx.array(sm), mx.array(sl), PLAN))
y_ref = TG.combine_phase(yn.reshape(M * K, -1), yn.reshape(M * K, -1), mx.ones((M, K), mx.int32), sc)
mx.eval(y, y_ref)
b_ok = eqb(y, y_ref) and ref2.COUNTS["ooo_1c"] == c0 + 1
ok &= b_ok
say(f"(b) NAX one call via _ooo_sel -> _ooo_nax6 == NAX6 on the released slots + combine_phase: {b_ok}")
ref2.CFG["tier_nax_ooo"] = False
# (c) / (d): the old route
called = []
orig = ref2._ORIG["ooo_call"]
ref2._ORIG["ooo_call"] = lambda *a, **k: called.append(1) or "old route"
try:
    ref2.CFG["ooo_1c"] = False
    c_ok = ref2._ooo_sel(x, mx.array(ids), bm, dict(t), post, sc, None) == "old route" and called == [1]
    ref2.CFG["ooo_1c"] = True
    d_ok = ref2._ooo_sel(x, mx.array(ids), {"gate": Gate(regions=False), "L": L}, dict(t), post, sc, None) == "old route" \
        and called == [1, 1]
finally:
    ref2._ORIG["ooo_call"] = orig
    ref2.CFG["ooo_1c"] = False
ok &= c_ok and d_ok
say(f"(c) ooo_1c off -> the old route: {c_ok}; (d) a gate without regions -> the old route: {d_ok}")
st = ref2.self_test()
st_ok = all(bool(v) for v in st.values())
ok &= st_ok
say(f"(e) ref2.self_test: {'PASS' if st_ok else 'FAIL ' + str(st)}")
# (f) U3's 3-bit sure rows (t["nolsb"], BigMoE's _ooo_call_t3) on the 3c path, with BigMoE's LP1 kernel patch as U3 runs it
BT._lp1_patch()
TG = BT._tier_glu_mod()
sure = np.zeros(M, bool); sure[::2] = True                      # every other row sure
nl = mx.array(sure)
gate2 = Gate(); gate2.seq = 11
sl_t3 = np.where(sure[:, None], -2, sl).astype(np.int32)      # final sidecar slots as _ooo_call_t3's phase 2 sees them
gate2.release(L, sm.reshape(-1).tolist()); gate2.release(NL // 2 + L, sl.reshape(-1).tolist())
t3 = dict(t); t3["nolsb"] = (nl, sure)
ref2.CFG["ooo_1c"] = True
try:
    y = ref2._ooo_sel(x, mx.array(ids), {"gate": gate2, "L": L}, t3, post, sc, None)
finally:
    ref2.CFG["ooo_1c"] = False
y_ref = TG.tier_glu(x, msb, lsb, mx.array(sm), mx.array(sl_t3), plan=PLAN, scores=sc)
okp = (pre_m >= 0) & np.concatenate([(pre_l >= 0) | sure[:, None], np.ones((M, K - R4), bool)], axis=1)
ph = mx.array(np.where(okp, 1, 2).astype(np.int32))
l1 = mx.array(np.where(sure[:, None], -2, np.maximum(pre_l, 0)).astype(np.int32))
y1 = TG.tier_glu_phase(x, msb, lsb, mx.array(pre_m), l1, ph, 1, plan=PLAN)
y2 = TG.tier_glu_phase(x, msb, lsb, mx.array(sm), mx.array(sl_t3), ph, 2, plan=PLAN)
y_2p = TG.combine_phase(y1, y2, ph, sc)
mx.eval(y, y_ref, y_2p)
f_ok = eqb(y, y_ref) and eqb(y, y_2p) and "nolsb" not in t3
ok &= f_ok
say(f"(f) U3 sure rows (nolsb) via ref2: one call == tier_glu(scores) with sidecar -2 == _ooo_call_t3's two phases: {f_ok}")
say(f"OOO-1C wiring: {'PASS' if ok else 'FAIL'}")
