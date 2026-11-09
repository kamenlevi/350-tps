"""Fit12 ifb12_merge.py (Mon 9 Nov 23:4x): merge ifb12.sh's chunk outputs for EvalSuite. READ-ONLY on the chunk files; writes
RUN_DIR/ifb12_ids.json ({key: {arm: [[ids]]}}, EvalSuite's tools/r57rows.py input, as each chunk's F12_IDS_OUT) and
RUN_DIR/ifb12_ids_meta.json ({key: arm, theta, n, cap, finish, pf_s, dec_s, tok_s, checks, paused_s}). A key in two chunks
must have the same ids (P2' is history-independent), else it is reported and the later chunk's row is NOT taken.
Prints: keys merged / 300, finish stop / length, tokens, the largest lifetime footprint any chunk's harness reported.
Usage: python -I -B ifb12_merge.py RUN_DIR"""
import glob, json, os, re, sys

O = sys.argv[1]
ids, meta, clash, life = {}, {}, [], []
for f in sorted(glob.glob(os.path.join(O, "ifb12c*_ids.json"))):
    if f.endswith("_meta.json"):
        continue
    a = json.load(open(f))
    mf = f[:-len(".json")] + "_meta.json"
    m = json.load(open(mf)) if os.path.exists(mf) else {}
    for k, v in a.items():
        if k in ids:
            if ids[k] != v:
                clash.append(k)
            continue
        ids[k] = v
        if k in m:
            meta[k] = m[k]
    t = f[:-len("_ids.json")] + ".txt"
    if os.path.exists(t):
        life += [float(x) for x in re.findall(r"lifetime ([\d.]+) GB", open(t).read())]
for p, o in ((os.path.join(O, "ifb12_ids.json"), ids), (os.path.join(O, "ifb12_ids_meta.json"), meta)):
    json.dump(o, open(p + ".tmp", "w"))
    os.replace(p + ".tmp", p)
fin = [v.get("finish") for v in meta.values()]
print(f"ifb12 merge ({O}): {len(ids)} / 300 keys; finish stop {fin.count('stop')}, length {fin.count('length')}; tokens "
      f"{sum(v.get('n', 0) for v in meta.values())}; largest harness lifetime {max(life) if life else 'n/a'} GB; "
      f"clashes {clash if clash else 'none'}")
