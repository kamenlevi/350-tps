#!/bin/bash
> (a quote from the project owner, kept private)
# for the prefill. If we can't reach them"): a chat prefill call serves its pool-resident experts from the 45 GB pools (the base +
# side slots rebuilt to 4-bit on the GPU, op for op the ext's rebuild; only the LSB part read when just the base is resident;
# absent bases read as today), into the same scratch for the same gather_qmm call: bitwise by construction. CT1 (d44ec7a): the chat
# prefill read routed x 2.79 MB (20.4 GB per prompt) with 65.5 % / 25.1 % of the routed base / side parts resident.
# Plus Leap's PF-B fix (16:5x, 6553fcb; R57_PFLM_SEG, default on: the shared expert's q4 N = 1 gate per chunk slice) on the agent prompts.
# Gate 0: scripts/pfd_unit.py (records of 3 layers rebuilt from their parts on the GPU == the ext's rebuild), else nothing runs.
# Part A (the 12 N45 IFEval prompts, C 256, R57_PFSTAT + R57_LOGHASH, one process per arm):
#   pde0 = E (exact; control), pde1 = E + PF-D, pde1k = E + PF-D + R57_PFD_CHECK (every rebuilt row vs the ext's; extra reads, timing
#   void), CAP 64; pdz0 = zs (M1-B + COH + SB1, the chat config), pdz1 = zs + PF-D, CAP 256 (chat-length answers keep the pools real).
# Part B (the 3 PFX agent prompts, E, CAP 64; only with >= 47.2 GB NO-SWAP): pdpa1 = PF-A (control), pdb38s = PF-B TOK 8192 + seg per
#   chunk, pdb32s = PF-B TOK 2048 + seg per chunk (Leap: ~0.4 GB of transient MoE activations instead of ~1.6, the 45.0 line).
# REPORT data/pfd/pfd_report.txt: per prompt TTFT, prefill SSD GB, PF-D rows A / B / C, tokens and logits hash vs the control, == AR.
# usage: NOTAFTER=hh:mm NOWAIT45=1 GAP0=0 GAP=0 MARGIN=4 bash scripts/turn45.sh 34 25 "..." /bin/bash scripts/pfd.sh
export PATH="$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "${PFD_ROOT:-$HOME/BigMoE}" || exit 1
D=data/pfd; mkdir -p $D
LOG="$PWD/$D/pfd.log"
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$LOG"; }
PY=${PFD_PY:-$HOME/BigMoE/.venv/bin/python}
avail_gb() { vm_stat | awk '/page size of/ {ps=$8} /^Pages (free|speculative|purgeable):/ || /^File-backed pages:/ {v=$NF; sub("[.]","",v); s+=v} END {printf "%.1f", s*ps/1e9}'; }
A=${PFD_AVAIL:-$(avail_gb)}
awk -v a="$A" 'BEGIN {exit !(a >= 47.2)}' || { say "NO-SWAP $A GB < 47.2: not run"; exit 0; }
[ -n "$PFD_DRYRUN" ] || sleep 20
A=${PFD_AVAIL:-$(avail_gb)}
awk -v a="$A" 'BEGIN {exit !(a >= 47.2)}' || { say "NO-SWAP $A GB < 47.2 at the 20 s look-again: not run"; exit 0; }
BUN="BIGMOE_PAUSE_EVERY_MS=50,R57_S0CARRY=1,REF2_SB_FIRST=1,REF2_PLE_LATE=1,REF2_COMMIT_SUB=9,R57_DQ1=1"
E="R57_NAX=1,REF2_KEEP_CACHES=1,R57_WIRED=1,$BUN"
L=$(grep -v '^#' data/stack/s5p_env.txt | grep . | tail -1 | sed 's/,R57_QOM_SETS=humaneval,mbpp$//')
ZS="$L,R57_QOM_MTP=2,REF2_NAX_COH=1,R57_SB1=1"
KP="agent/edit10,agent/write13,agent/write11"
KI=$(sed -n 1p data/n45/keys.txt)
[ "$(echo "$KI" | tr ',' '\n' | grep -c '^ifeval/')" = 12 ] || { say "data/n45/keys.txt line 1 is not 12 IFEval keys: not run"; exit 2; }
FR=$(bash scripts/deep_freeze.sh pfd) || { say "freeze failed: $FR"; exit 2; }
SD=data/r57/snap/pfd
grep -q 'def install_pfd' "$SD/pflm.py" && grep -q '_SegPerChunk' "$SD/pflm.py" && grep -q 'PFD_ON' "$SD/r57_screen_pfd.py" \
  || { say "the frozen pflm.py / screen has no PF-D (install_pfd, PFD_ON) or no seg fix (_SegPerChunk): not run"; exit 2; }
[ -n "$PFD_DRYRUN" ] && { echo "dry run: $FR; E $(echo "$E" | tr ',' '\n' | grep -c =) K=V, ZS $(echo "$ZS" | tr ',' '\n' | grep -c =) K=V, KI $(echo "$KI" | tr ',' '\n' | grep -c .)"; exit 0; }
"$PY" scripts/pfd_unit.py 6 >> "$LOG" 2>&1 || { say "pfd_unit.py FAILED (the GPU rebuild != the ext's): not run"; exit 4; }
git add data/r57/snap/frozen_pfd ':!data/r57/snap/frozen_pfd/**/__pycache__/**' "$SD" ":!$SD/__pycache__/**" data/r57/snap/c45_runner_pfd.sh \
> (a quote from the project owner, kept private)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011DvdV6eUB4NgBbVkyVFPrT" || { say "snapshot commit failed: not run"; exit 3; }
SNAP=$(git rev-parse --short HEAD)
RUN="/bin/bash data/r57/snap/c45_runner_pfd.sh"
export C45_OUT="$PWD/$D" C45_SWAP0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print $6 / 1024}') C45_ALARM=2400 \
  MG=4 C45_DEADLINE=$(date -v+60M +%H%M) C45_SCREEN="$SD/r57_screen_pfd.py" C45_REFTOK= R57_QOM_SETS=humaneval,mbpp R57_MODMAN=1
rm -f $D/DONE
say "PFD start (pid $$, NO-SWAP $A GB, snapshot $SNAP)"
TAGS=""
arm() {   # tag cap keys qom_sets env
  rm -f data/r57/${1}_256_* $D/${1}_256.txt
  R57_KEYS=$3 C45_CAP=$2 R57_PFSTAT=1 R57_LOGHASH=1 R57_QOM_SETS=$4 C45_ARMS="${1}_256:256:$5" $RUN
  say "$1 rc=$?"; TAGS="$TAGS $1"
}
QC="humaneval,mbpp"; QZ="humaneval,mbpp,ifeval,multi"
arm pde0 64 "$KI" $QC "$E"
arm pde1 64 "$KI" $QC "$E,R57_PFD=1"
arm pde1k 16 "$KI" $QC "$E,R57_PFD=1,R57_PFD_CHECK=1"
arm pdz0 256 "$KI" $QZ "$ZS"
arm pdz1 256 "$KI" $QZ "$ZS,R57_PFD=1"
A=$(avail_gb)
if awk -v a="$A" 'BEGIN {exit !(a >= 47.2)}'; then
  P0="R57_PFCHUNK=1024,R57_PFNOLOG=1"
  arm pdpa1 64 "$KP" $QC "$E,$P0,R57_PFLM=1"
  arm pdb38s 64 "$KP" $QC "$E,$P0,R57_PFLM=3,R57_PFLM_TOK=8192"
  arm pdb32s 64 "$KP" $QC "$E,$P0,R57_PFLM=3,R57_PFLM_TOK=2048"
else
  say "part B skipped: NO-SWAP $A GB < 47.2"
fi
"$PY" -I - "$SNAP" >> "$LOG" 2>&1 <<'EOF'
import json, re, sys, statistics as S
snap = sys.argv[1]
peak = {}
for ln in open("data/pfd/c45.log"):
    m = re.search(r"done (\S+) rc=\d+:.*lifetime peak ([\d.]+) GB", ln)
    if m:
        peak[m.group(1)] = float(m.group(2))
def load(t):
    try:
        return ({r["key"]: r for r in json.load(open(f"data/r57/{t}_256_runs.json"))},
                {k: list(v.values())[0][0] for k, v in json.load(open(f"data/r57/{t}_256_tokens.json")).items()})
    except (OSError, ValueError, KeyError):
        return {}, {}
AR = json.load(open("data/n45/ar_ref_tokens.json"))
def eq_ar(T):
    n = 0
    for k, o in T.items():
        r_ = (AR.get(k) or {}).get("gate+t", [None])[0]
        if r_ is not None and o[:min(len(o), len(r_))] == r_[:min(len(o), len(r_))]:
            n += 1
    return n
L = [f"PFD (data/pfd; snapshot {snap}; C 256; quiet): per prompt TTFT (pfs), prefill SSD GB (PFSTAT), PF-D rows A (base + side pooled) / "
     f"B (base pooled, side read) / C (read as today); tokens and logits hash vs the arm's control; lifetime peak (line 45.0)"]
def part_a(t, ctl, nm):
    R, T = load(t)
    R0, T0 = load(ctl)
    if not R:
        L.append(f"  {t} {nm}: MISSING")
        return
    rows = []
    for k in sorted(R):
        r, r0 = R[k], R0.get(k) or {}
        h, h0 = r.get("lh") or [], r0.get("lh") or []
        pd, gb = r.get("pfd") or {}, (r.get("pfst") or {}).get("gb")
        rows.append((k, r["P"], r.get("pfs"), gb, pd, T.get(k) == T0.get(k) if t != ctl else None,
                     sum(1 for a_, b_ in zip(h, h0) if a_ == b_), min(len(h), len(h0))))
    ttft = [x[2] for x in rows if x[2]]
    gbs = [x[3] for x in rows if x[3] is not None]
    pdA, pdB, pdC = (sum(x[4].get(c, 0) for x in rows) for c in ("A", "B", "C"))
    tok = "" if t == ctl else f"; tokens == {ctl} {sum(1 for x in rows if x[5])}/{len(rows)}; logits hash {sum(x[6] for x in rows)}/{sum(x[7] for x in rows)}"
    chk = ""
    if any(x[4].get("checked") for x in rows):
        chk = (f"; CHECK rows {sum(x[4].get('checked', 0) for x in rows)}, differing A {sum(x[4].get('bad_A', 0) for x in rows)} / "
               f"B {sum(x[4].get('bad_B', 0) for x in rows)}")
    L.append(f"  {t} {nm}: TTFT mean {S.mean(ttft):.2f} s (median {S.median(ttft):.2f}, {min(ttft):.2f}-{max(ttft):.2f}); SSD "
             f"{S.mean(gbs) if gbs else float('nan'):.1f} GB per prompt; rows A {pdA} / B {pdB} / C {pdC}{tok}; == AR {eq_ar(T)}/{len(T)}"
             f"{chk}; lifetime peak {peak.get(f'{t}_256', float('nan')):.2f} GB")
    for k, P, pfs, gb, pd, same, hs, hn in rows:
        L.append(f"      {k}: P {P}, TTFT {pfs:.2f} s, SSD {gb if gb is not None else float('nan'):.1f} GB, A/B/C {pd.get('A', '-')}/"
                 f"{pd.get('B', '-')}/{pd.get('C', '-')}" + ("" if same is None else f", tokens {'==' if same else 'DIFF'}, hash {hs}/{hn}"))
L.append("Part A (the 12 N45 IFEval prompts)")
part_a("pde0", "pde0", "E (exact; control), CAP 64")
part_a("pde1", "pde0", "E + PF-D, CAP 64")
part_a("pde1k", "pde0", "E + PF-D + CHECK (timing void), CAP 16")
part_a("pdz0", "pdz0", "zs = M1-B + COH + SB1 (chat; control), CAP 256")
part_a("pdz1", "pdz0", "zs + PF-D, CAP 256")
R0, T0 = load("pdpa1")
if R0:
    L.append("Part B (the 3 PFX agent prompts, E, CAP 64): prefill TTFT, x vs PF-A, tokens and logits hash vs PF-A")
    for t, nm in (("pdpa1", "PF-A (R57_PFLM=1, control)"), ("pdb38s", "PF-B TOK 8192 + seg per chunk"), ("pdb32s", "PF-B TOK 2048 + seg per chunk")):
        R, T = load(t)
        cells = []
        for k in ("agent/edit10", "agent/write13", "agent/write11"):
            r, r0 = R.get(k), R0.get(k) or {}
            if r and r.get("pfs"):
                same = "==" if T.get(k) == T0.get(k) and T0.get(k) is not None else "DIFF"
                h, h0 = r.get("lh") or [], r0.get("lh") or []
                x = f"x{r0['pfs'] / r['pfs']:.2f}" if r0.get("pfs") else "x?"
                cells.append(f"{k.split('/')[-1]} P {r['P']}: {r['pfs']:.1f} s = {r['P'] / r['pfs']:.0f} tok/s ({x}; tokens {same}; logits hash "
                             f"{sum(1 for a_, b_ in zip(h, h0) if a_ == b_)}/{min(len(h), len(h0))})")
            else:
                cells.append(f"{k.split('/')[-1]}: MISSING")
        L.append(f"  {t} {nm}: lifetime peak {peak.get(f'{t}_256', float('nan')):.2f} GB")
        L += [f"      {c}" for c in cells]
open("data/pfd/pfd_report.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))
EOF
say "report rc=$? ($D/pfd_report.txt)"
git add $D $(for t in $TAGS; do echo data/r57/${t}_256_*; done) 2>/dev/null
> (a quote from the project owner, kept private)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011DvdV6eUB4NgBbVkyVFPrT"
touch $D/DONE
say "PFD end"
