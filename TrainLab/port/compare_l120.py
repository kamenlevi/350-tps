"""PORT steps check (MTP Head, Wed 11-04 22:0x): compare a train_port.py log (--log-json) with L1-20's logged per-step
losses (~/Leap/data/l120_ft.state.json, the MLX trainer on the GPU). PASS = every compared step within 2e-3 relative
(set before the run: step 1 already agrees to 1e-4; later steps add GPU/CPU accumulation-order drift through Adam).
Usage: python compare_l120.py PORT_LOG.json"""
import json, os, sys
port = json.load(open(os.path.expanduser(sys.argv[1])))["loss"]
ref = json.load(open(os.path.expanduser("~/Leap/data/l120_ft.state.json")))["log"]["loss"]
worst = 0.0
for s, (a, b) in enumerate(zip(port, ref)):
    rel = abs(a - b) / abs(b)
    worst = max(worst, rel)
    print(f"step {s + 1}: port {a:.6f}  L1-20 {b:.6f}  rel {rel:.2e}")
print(f"STEPS CHECK ({len(port)} steps): max rel {worst:.2e} -> {'PASS' if worst < 2e-3 else 'FAIL'} (line 2e-3)")
