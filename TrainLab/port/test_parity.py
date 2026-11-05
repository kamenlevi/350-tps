"""PORT parity, PyTorch side (MTP Head, Wed 11-04 20:2x). Compares the port with port/ref_mlx.py's output (the MLX
trainer's own code on MLX's CPU device), same args:
  fwd   REF.npz : one batch -> hidden, logits rows, the top-16 candidate sets, selector scores, loss.
  train REF.npz : --steps optimizer steps on the same fixed items (first --layers layers) -> per-step loss, grad norm.
Usage: [TrainLab .venv-torch] python test_parity.py fwd|train REF.npz [--A 8] [--groups 1] [--steps 5] [--layers 1]
       [--pmask 0.5] [--attn explicit|sdpa]"""
import argparse, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
import dflash2_torch as M
import data_port as DP
from optim_port import MLXAdamW, clip_grad_norm_mlx, lr_schedule

ap = argparse.ArgumentParser()
ap.add_argument("mode"); ap.add_argument("ref")
ap.add_argument("--A", type=int, default=8); ap.add_argument("--groups", type=int, default=1)
ap.add_argument("--steps", type=int, default=5); ap.add_argument("--layers", type=int, default=0)
ap.add_argument("--pmask", type=float, default=0.5); ap.add_argument("--bs", type=int, default=32)
ap.add_argument("--lr", type=float, default=2e-5); ap.add_argument("--S", type=int, default=1)
ap.add_argument("--attn", default="explicit"); ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--freeze-layers", action="store_true")   # grad: only the final norm + the selector get gradients
ap.add_argument("--ckpt-layers", action="store_true"); ap.add_argument("--attn-chunk", type=int, default=0)
ap.add_argument("--rows", type=int, default=256)          # the trainer's recompute / chunking options (Thu 11-05)
ap.add_argument("--data", default="~/Leap/data/l120")       # a folder with only the windows needed (memory)
ap.add_argument("--freeze-selector", action="store_true")   # train: no selector parameters (memory)
r = ap.parse_args()
torch.set_num_threads(r.threads)
t0 = time.time()
m = M.build(n_layers=(r.layers or None), attn_impl=r.attn)      # the first --layers layers of the HF drafter
m.head.q4.unpack_u8(); m.head.q4.packed = torch.empty(0, dtype=torch.int32)
if r.layers:
    m.layers = m.layers[:r.layers]
m.ckpt_layers, m.attn_chunk = r.ckpt_layers, r.attn_chunk
if r.freeze_layers:
    for p in m.layers.parameters():
        p.requires_grad_(False)
if r.freeze_selector:
    for p in m.candidate_selector.parameters():
        p.requires_grad_(False)
ref = np.load(os.path.expanduser(r.ref)) if r.mode != "grad" else None   # grad: r.ref is the OUTPUT json
wins = DP.load_windows(r.data)
tr = [g for w_ in wins if w_["split"] == "train" for g in DP.groups_of(w_, r.A)]
pm = np.random.default_rng(20)                       # the MLX trainer's PM_RNG
print(f"[port] loaded in {time.time() - t0:.0f}s; {len(wins)} windows, {len(tr)} train groups, layers {len(m.layers)}, "
      f"attn {r.attn}", flush=True)
res = {}
if r.mode == "grad":                     # Thu 11-05: one batch's loss + full gradient -> port/grad_stats.py JSON
    import grad_stats as GS
    import resource
    b = DP.to_torch(DP.make_batch(tr[:r.groups], r.A, r.bs, m.MASK, r.pmask, pm), "cpu")
    norm = max(1.0, float(b["w"].sum()))
    l = m.loss_sum(m.fwd(b["hc"], b["upos"], b["anc"], b["tok"]), b["pred"], b["tkl"], b["lpl"], b["y"], b["w"],
                   rows=r.rows) / norm
    l.backward()
    per = {n: GS.stats(n, p.grad.detach().float().numpy()) for n, p in m.named_parameters() if p.grad is not None}
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30
    GS.save(os.path.expanduser(r.ref), float(l), per, dict(norm=norm, rss_peak_gb=rss))
    print(f"[port] grad loss {float(l):.6f} (norm {norm:.0f}); {len(per)} parameters; rss peak {rss:.2f} GB", flush=True)
    sys.exit(0)
if r.mode == "fwd":
    nb = DP.make_batch(tr[:r.groups], r.A, r.bs, m.MASK, r.pmask, pm)
    same_in = all(np.array_equal(nb[k], ref[k]) for k in ("w", "tok", "tkl", "pred", "y"))
    b = DP.to_torch(nb, "cpu")
    with torch.no_grad():
        hid = m.fwd(b["hc"], b["upos"], b["anc"], b["tok"])
        norm = max(1.0, float(b["w"].sum()))
        loss = float(m.loss_sum(hid, b["pred"], b["tkl"], b["lpl"], b["y"], b["w"])) / norm
        rows = torch.from_numpy(ref["rows"].astype(np.int64))
        hr = hid.reshape(-1, hid.shape[-1])[rows]
        lg = m.head(hr) * m.OUTM
        cand = torch.topk(lg, m.top_k, dim=-1).indices
    rh, rl = ref["hid"], ref["logits_rows"]
    dh = float(np.abs(hid.numpy() - rh).max()); sh = float(np.abs(rh).max())
    dl = float(np.abs(lg.numpy() - rl).max())
    rc = ref["cand"].reshape(-1, ref["cand"].shape[-1])[ref["rows"]]
    cand_same = float(np.mean([set(a) == set(b_) for a, b_ in zip(np.sort(cand.numpy(), -1), rc)]))
    am_same = float((lg.argmax(-1).numpy() == rl.argmax(-1)).mean())
    res = dict(inputs_identical=same_in, hid_maxdiff=dh, hid_maxabs=sh, logits_maxdiff=dl, cand_set_agree=cand_same,
               argmax_agree=am_same, loss_port=loss, loss_mlx=float(ref["loss"]),
               loss_reldiff=abs(loss - float(ref["loss"])) / abs(float(ref["loss"])))
else:
    params = [p for p in m.parameters() if p.requires_grad]
    opt = MLXAdamW(params, lr=r.lr, weight_decay=0.0)
    lr_at = lr_schedule(r.lr, max(1, int(math.ceil(2 * len(tr) / r.S))))
    losses, gnorms = [], []
    for s in range(r.steps):
        items = [tr[(s * r.S + k) % len(tr)] for k in range(r.S)]
        parts = [DP.make_batch(items[k:k + 1], r.A, r.bs, m.MASK, r.pmask, pm) for k in range(len(items))]
        norm = max(1.0, sum(float(p_["w"].sum()) for p_ in parts))
        opt.zero_grad(set_to_none=True)
        loss = 0.0
        for nb in parts:
            b = DP.to_torch(nb, "cpu")
            l = m.loss_sum(m.fwd(b["hc"], b["upos"], b["anc"], b["tok"]), b["pred"], b["tkl"], b["lpl"], b["y"],
                           b["w"]) / norm
            l.backward()
            loss += float(l)
        gn = clip_grad_norm_mlx(params, 1.0)
        for g_ in opt.param_groups:
            g_["lr"] = lr_at(s)
        opt.step()
        losses.append(loss); gnorms.append(gn)
        print(f"[port] step {s + 1}: loss {loss:.6f} (mlx {ref['losses'][s]:.6f}) grad-norm {gn:.4f} "
              f"(mlx {ref['gnorms'][s]:.4f})", flush=True)
    rl = ref["losses"][:len(losses)]
    res = dict(losses_port=losses, losses_mlx=rl.tolist(), gnorms_port=gnorms, gnorms_mlx=ref["gnorms"][:len(gnorms)].tolist(),
               max_rel_loss_diff=float(np.max(np.abs(np.array(losses) - rl) / np.abs(rl))))
print("[port] RESULT " + " ".join(f"{k}={v}" for k, v in res.items()), flush=True)
