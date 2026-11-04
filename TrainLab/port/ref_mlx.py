"""PORT reference (MTP Head, Wed 11-04 20:2x): runs the MLX trainer's own code (sticky/d09_train.py, executed up to its
'modes' section, so fwd / heads / loss_fn / make_batch are the trainer's, not copies) on MLX's CPU device, and saves what
the PyTorch port must reproduce.
  fwd   : one batch (the first --groups train groups, pmask from the trainer's PM_RNG): hidden, logits rows, loss.
  train : --steps optimizer steps on fixed items (step k uses train group k), first --layers layers only (memory),
          the trainer's own step(): micro-batches, summed grads, clip 1.0, MLX AdamW (no bias correction).
Usage: [BigMoE venv] python ref_mlx.py fwd|train OUT.npz [--A 8] [--groups 1] [--steps 5] [--layers 1] [--pmask 0.5]"""
import argparse, gc, math, os, sys
ap = argparse.ArgumentParser()
ap.add_argument("mode"); ap.add_argument("out")
ap.add_argument("--A", type=int, default=8); ap.add_argument("--groups", type=int, default=1)
ap.add_argument("--steps", type=int, default=5); ap.add_argument("--layers", type=int, default=0)
ap.add_argument("--pmask", type=float, default=0.5); ap.add_argument("--bs", type=int, default=32)
ap.add_argument("--lr", type=float, default=2e-5); ap.add_argument("--S", type=int, default=1)
r = ap.parse_args()
import mlx.core as mx
mx.set_default_device(mx.cpu)
src = open(os.path.expanduser("~/TrainLab/sticky/d09_train.py")).read()
src = src[:src.index("# ---------------------------------------------------------------- modes")]
sys.argv = ["d09_train.py", "--A", str(r.A), "--S", str(r.S), "--bs", str(r.bs), "--micro", "1", "--pmask", str(r.pmask),
            "--lr", str(r.lr), "--data", "~/Leap/data/l120", "--epochs", "2"]
ns = {"__name__": "d09_ref"}
exec(compile(src, "d09_train.py", "exec"), ns)
import numpy as np
draft, A = ns["draft"], ns["A"]
if r.layers:
    draft.layers = draft.layers[:r.layers]
    ns["TRAIN"] = None
    gc.collect()
wins = ns["load_windows"]()
tr = [g for w_ in wins if w_["split"] == "train" for g in ns["groups_of"](w_)]
print(f"[ref] {len(wins)} windows, {len(tr)} train groups (A {A.A}), layers {len(draft.layers)}", flush=True)
out = {}
if r.mode == "fwd":
    b = ns["make_batch"](tr[:r.groups], A.pmask)
    hctx, upos, anc, tok, tkl, lpl, y, pred, w = b
    hid = ns["fwd"](hctx, upos, anc, tok)
    logits, cand, sc = ns["heads"](hid, pred)
    norm = mx.array(max(1.0, float(w.sum())))
    loss = ns["loss_fn"](b, norm)
    mx.eval(hid, logits, cand, sc, loss)
    rows = np.nonzero(np.array(w).reshape(-1) > 0)[0][:64]
    out = dict(hid=np.array(hid), logits_rows=np.array(logits.reshape(-1, logits.shape[-1]))[rows], rows=rows,
               cand=np.sort(np.array(cand), -1), sc=np.sort(np.array(sc), -1), loss=float(loss),
               w=np.array(w), tok=np.array(tok), tkl=np.array(tkl), pred=np.array(pred), y=np.array(y))
    print(f"[ref] fwd loss {float(loss):.6f} (norm {float(norm):.0f})", flush=True)
else:
    import mlx.nn as nn, mlx.optimizers as optim
    from mlx.utils import tree_map
    loss_and_grad = nn.value_and_grad(draft, lambda m, b, norm: ns["loss_fn"](b, norm))
    opt = optim.AdamW(learning_rate=r.lr, weight_decay=0.0)
    steps_total = max(1, int(math.ceil(2 * len(tr) / A.S)))
    warm = min(20, steps_total // 10 + 1)
    lr_at = lambda s: r.lr * (0.01 + 0.99 * s / warm) if s < warm else \
        r.lr * (0.1 + 0.45 * (1 + math.cos(math.pi * min(1.0, (s - warm) / max(1, steps_total - warm)))))
    losses, gnorms = [], []
    for s in range(r.steps):
        items = [tr[(s * A.S + k) % len(tr)] for k in range(A.S)]
        parts = [ns["make_batch"](items[k:k + 1], A.pmask) for k in range(len(items))]
        norm = mx.array(max(1.0, sum(float(b[-1].sum()) for b in parts)))
        loss, acc = 0.0, None
        for b in parts:
            l, g = loss_and_grad(draft, b, norm)
            acc = g if acc is None else tree_map(mx.add, acc, g)
            mx.eval(l, acc)
            loss += float(l)
        acc, gn = optim.clip_grad_norm(acc, 1.0)
        opt.learning_rate = lr_at(s)
        opt.update(draft, acc)
        mx.eval(draft.trainable_parameters(), opt.state)
        losses.append(loss); gnorms.append(float(gn))
        print(f"[ref] step {s + 1}: loss {loss:.6f} grad-norm {float(gn):.4f} lr {lr_at(s):.3e}", flush=True)
    out = dict(losses=np.array(losses), gnorms=np.array(gnorms))
np.savez(os.path.expanduser(r.out), **out)
print(f"[ref] saved {r.out}", flush=True)
