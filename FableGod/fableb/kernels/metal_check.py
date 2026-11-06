"""metal_check.py (Fable B): CPU-only compile of the draft kernels with Apple's offline Metal compiler (xcrun metal -c).
Nothing runs on the GPU. The harness stands in for what mx.fast.metal_kernel generates: the signature from the input /
output names, T = half in place of bfloat16. It proves syntax and types only. Run: python3 -I metal_check.py"""
import importlib.util, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = "#include <metal_stdlib>\nusing namespace metal;\n#define EPS 1e-6f\n"
ATTR = ["uint3 thread_position_in_grid [[thread_position_in_grid]]",
        "uint thread_index_in_threadgroup [[thread_index_in_threadgroup]]",
        "uint3 thread_position_in_threadgroup [[thread_position_in_threadgroup]]",
        "uint3 threadgroup_position_in_grid [[threadgroup_position_in_grid]]"]


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def wrap(m, tmpl, inst, src=None):
    args = [f"const device {m.TYPES.get(n, 'T')}* {n} [[buffer({i})]]" for i, n in enumerate(m.IN)]
    args += [f"device {m.TYPES.get(n, 'T')}* {n} [[buffer({len(m.IN) + i})]]" for i, n in enumerate(m.OUT)]
    return (PRE + m.HDR + f"\ntemplate <{tmpl}>\n[[kernel]] void kfn(\n    " + ",\n    ".join(args + ATTR) + ")\n{\n"
            + (src or m.SRC) + "\n}\n" + f"template [[host_name(\"k_inst\")]] [[kernel]] decltype(kfn<{inst}>) kfn<{inst}>;\n")


ok = True
for name, tmpl, insts in (("gdn_w", "typename T, int S_C", ["half, 16", "half, 2"]),
                          ("hc_d", "typename T, int PEND", ["half, 1", "half, 0"]),
                          ("gdn_chunk", "typename T, int S_C, int NSG", ["half, 16, 16", "half, 2, 8", "half, 16, 32"]),
                          ("hc_k2c", "typename T, int LR, int HC, int NP, int NC, int D", ["half, 320, 4, 16, 352, 2560"]),
                          ("eprep", "typename TS, int K_C, int M_C, int R4, int HAS_Q, int HAS_SPLIT, int HAS_NL",
                           ["float, 10, 16, 2, 1, 1, 1", "half, 10, 2, 0, 0, 0, 0"])):
    if not os.path.exists(os.path.join(HERE, name + ".py")):
        continue
    m = load(name)
    for inst in insts:
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "k.metal")
            open(f, "w").write(wrap(m, tmpl, inst))
            p = subprocess.run(["xcrun", "-sdk", "macosx", "metal", "-std=metal4.0", "-c", f, "-o", os.path.join(d, "k.air")],
                               capture_output=True, text=True)
            errs = [l for l in p.stderr.splitlines() if "error" in l]
            ok &= p.returncode == 0
            print("%-6s <%s>: %s (%d errors)%s" % (name, inst, "compiles" if p.returncode == 0 else "FAILS", len(errs),
                                                   "".join("\n    " + e[e.find("k.metal"):][:260] for e in errs[:8])))
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
