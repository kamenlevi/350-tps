"""Items for RELAX's long-code drift re-check (docs/PREREG_relax_drift_2026-11-05.md). Two steps, because evalplus is
only in EvalSuite's venv and the chat template (jinja2) only in BigMoE's:
  .venv/bin/python tools/drift_build.py dump                 # HumanEval+'s problems outside the core 60 -> results/drift/he_rest.json
  ~/BigMoE/.venv/bin/python tools/drift_build.py build       # -> data/items/dec_humanevalx.jsonl, dec_agentlong.jsonl
dec_humanevalx: the 104 HumanEval+ problems not in dec_humaneval, with its template (data._he_user) and max_tokens 768;
build first checks that the template still gives the core 60's saved prompt ids. dec_agentlong: dec_agent's 17 write /
edit turns (real code into files) with max_tokens 1024 instead of 128."""
import hashlib, json, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from evalsuite import data as D

OUT = os.path.join(ROOT, "results", "drift")
REST = os.path.join(OUT, "he_rest.json")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]


def dump():
    from evalplus.data import get_human_eval_plus
    he = get_human_eval_plus()
    core = {it["task_id"] for it in D.load("dec_humaneval")}
    rest = [dict(task_id=t, prompt=he[t]["prompt"], entry_point=he[t]["entry_point"]) for t in sorted(he) if t not in core]
    assert len(he) == 164 and len(core) == 60 and len(rest) == 104, (len(he), len(core), len(rest))
    os.makedirs(OUT, exist_ok=True)
    json.dump(rest, open(REST, "w"))
    print(f"{os.path.relpath(REST, ROOT)}: {len(rest)} problems, sha256 {sha(REST)}")


def build():
    tok = D.tokenizer()
    core = D.load("dec_humaneval")
    bad = [it["key"] for it in core if D.chat(tok, D._he_user(it["prompt"])) != it["prompt_ids"]]
    assert not bad, f"the chat template no longer gives dec_humaneval's prompt ids: {bad[:3]}"
    rest = json.load(open(REST))
    rows = [dict(key=f"humanevalx/{r['task_id']}", set="humanevalx", task_id=r["task_id"], entry_point=r["entry_point"],
                 prompt=r["prompt"], max_tokens=768, user=D._he_user(r["prompt"]),
                 prompt_ids=D.chat(tok, D._he_user(r["prompt"]))) for r in rest]
    assert len(rows) == 104
    D.write("dec_humanevalx", rows)
    ag = [dict(it, key="agentlong/" + it["key"].split("/", 1)[1], set="agentlong", max_tokens=1024)
          for it in D.load("dec_agent") if it["key"].startswith(("agent/write", "agent/edit"))]
    assert len(ag) == 17, len(ag)
    D.write("dec_agentlong", ag)
    for n in ("dec_humanevalx", "dec_agentlong"):
        p = os.path.join(D.ITEMS, n + ".jsonl")
        print(f"{os.path.relpath(p, ROOT)}: sha256 {sha(p)}")
    keys = os.path.join(OUT, "keys_B.txt")             # the re-check's keys for arm B: all 121 rows
    open(keys, "w").write("\n".join([r["key"] for r in rows] + [r["key"] for r in ag]) + "\n")
    print(f"{os.path.relpath(keys, ROOT)}: {len(rows) + len(ag)} keys, sha256 {sha(keys)}")


if __name__ == "__main__":
    {"dump": dump, "build": build}[sys.argv[1]]()
