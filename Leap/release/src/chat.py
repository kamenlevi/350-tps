#!/usr/bin/env python3
"""chat.py: chat with the 125B model in the terminal and watch its speed live.

  .venv/bin/python chat.py                            # the 32 GB chat config, up to 16,384 tokens per answer
  .venv/bin/python chat.py --kind code                # code requests: the DFlash2 drafter (--drafter dfl)
  .venv/bin/python chat.py --mem 45 --max-tokens 1024

The engine loads once (about a minute, with a short discarded warm-up) and stays loaded between messages. Every answer
runs through the same decode loop as run.py (engine/loop/r57_screen_<snapshot>.py), unchanged: chat.py hands the loop one
prompt item per message (the harness's chat template over the conversation so far, non-thinking) and reads the tokens each
check commits through the session-vocabulary hook the chat configs already run, to print them as they arrive with a live
tok/s line. After each answer it prints the loop's own numbers: tokens, whole decode tok/s, first token, lifetime peak.
Ctrl-C stops the current answer (the process keeps running), /clear starts a new conversation, /exit (or Ctrl-D) quits.
At --mem 32 and 24 long prompts prefill layer-major (PF-A: the same tokens, a faster first token, a little more memory);
R57_PFLM=0 in the shell turns that off.
The engine's own log goes to out/<tag>.log; each answer's numbers, message and text go to out/<tag>.jsonl. Ctrl-Z is caught
(a suspended chat would keep its memory)."""
import argparse, importlib.abc, importlib.util, json, os, runpy, shutil, signal, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import run as R                                            # read_config, tokenizer, drafter_cached, DRAFTER, KIND_SET

NMAX = 999                                                 # messages per session (the loop's prompt list is fixed at start)


class UI:
    """the terminal (a copy of the original stdout; the engine's own prints go to the log), with a status line at the bottom"""

    def __init__(self):
        self.f = os.fdopen(os.dup(1), "w", buffering=1)
        self.tty = self.f.isatty()
        self.rows = 0

    def region(self):
        if not self.tty:
            return
        r = shutil.get_terminal_size((100, 30)).lines
        if r != self.rows:
            self.rows = r
            self.f.write("\n\033[1A\0337" + f"\033[1;{r - 1}r" + "\0338")   # every row but the last scrolls
            self.f.flush()

    def write(self, s):
        self.f.write(s)
        self.f.flush()

    def status(self, s):
        if not self.tty:
            return
        self.region()
        self.f.write("\0337" + f"\033[{self.rows};1H\033[2K\033[7m {s[:max(10, shutil.get_terminal_size().columns - 2)]} \033[0m" + "\0338")
        self.f.flush()

    def close(self):
        if self.tty and self.rows:
            self.f.write("\0337" + f"\033[{self.rows};1H\033[2K" + "\0338\033[r")
        self.f.write("\n")
        self.f.flush()


class State:
    def __init__(self):
        self.i = 0              # messages handed to the loop
        self.active = False     # an answer is being generated
        self.stop = False       # Ctrl-C during an answer
        self.pending = False    # an answer finished but is not reported yet
        self.ids, self.shown, self.t0, self.t1, self.last = [], "", 0.0, None, 0.0

    def begin(self):
        self.active, self.stop, self.pending = True, False, True
        self.ids, self.shown, self.t0, self.t1, self.last = [], "", time.perf_counter(), None, 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="chat", choices=("exact", "lossy", "chat"))
    ap.add_argument("--mem", default="32", choices=("45", "32", "24"))
    ap.add_argument("--max-tokens", type=int, default=16384, help="the most one answer may generate (default 16384)")
    ap.add_argument("--kind", default="chat", choices=tuple(R.KIND_SET),
                    help="which benchmark family's switches apply (code also implies --drafter dfl)")
    ap.add_argument("--drafter", choices=("auto", "dfl", "mtp"),
                    help="dfl: every message takes the engine's code path (the DFlash2 block drafter); mtp: its chat path (the "
                         "model's MTP head); auto: the engine's type rule picks per message (default; --kind code: dfl)")
    ap.add_argument("--system", help="an optional system message")
    ap.add_argument("--no-warmup", action="store_true", help="skip the discarded warm-up (the first answer then runs cold)")
    ap.add_argument("--_screen", help=argparse.SUPPRESS)  # tests: a stand-in loop instead of the engine's
    a = ap.parse_args()
    os.environ["HF_HUB_OFFLINE"] = "1"                     # before anything imports huggingface_hub (one process here)

    C, cenv, cpath = R.read_config(a.config, a.mem)
    store = os.path.join(ROOT, "engine", "models", "bare")
    if not os.path.isdir(os.path.join(store, "records3")):
        sys.exit("chat.py: engine/models/bare is not linked to a converted store (install.sh --store <dir>)")
    if R.drafter_cached() is None:
        sys.exit(f"chat.py: the block drafter's base {R.DRAFTER[0]} @ {R.DRAFTER[1][:7]} is not in the Hugging Face cache "
                 f"(see WEIGHTS.md)")
    snap = R.snapshot(cpath)                               # the config's decode loop (24 GB: w24), as in run.py
    screen = a._screen or os.path.join(ROOT, "engine", "loop", f"r57_screen_{snap}.py")
    out = os.path.join(ROOT, "out")
    os.makedirs(out, exist_ok=True)
    tag = time.strftime("chat_%m%d_%H%M%S")
    s = R.KIND_SET[a.kind]
    pre = s if s != "math" else "math500"
    keys = [f"{pre}/{tag}_{i:03d}" for i in range(1, NMAX + 1)]
    env = {"R57_PRESET": "45", "R57_PROMPTS": str(NMAX), "R57_REPS": "1", "R57_WARM": "0" if a.no_warmup else "1",
           "R57_TAG": tag, "R57_REFTOK": "", "R57_KEYS": ",".join(keys), "R57_QOM_SETS": "humaneval,mbpp",
           "HF_HUB_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    env.update(cenv)                                       # the config's own line wins, as in run.py
    env["BIGMOE_EXT_BUILD"] = "build"
    if a.mem in ("32", "24"):                              # PF-A (R57_PFLM=1): layer-major prefill on prompts over one chunk;
        env["R57_PFLM"] = os.environ.get("R57_PFLM", "1")  # the same tokens as the default prefill (bitwise at 30K tokens;
    os.environ.update(env)                                 # identical answers at 32 and 24 GB), a 2.4-3.8x faster first token
                                                           # on long prompts, +0.3-3.2 GB. R57_PFLM=0 in the shell turns it off.

    ui, st = UI(), State()
    ui.write("Powered by MTPLX\nhttps://github.com/youssofal/mtplx\n")   # MTPLX's NOTICE (Apache-2.0 section 4(d))
    ui.write(f"ExactStream chat: config {a.config}-{a.mem} (C {C}), up to {a.max_tokens} tokens per answer. Loading the "
             f"engine (about a minute)...\n")
    tok = R.tokenizer(store)
    msgs = [{"role": "system", "content": a.system}] if a.system else []
    sysn = len(msgs)

    def G():                                              # the loop's globals (it runs as __main__ via runpy)
        return sys.modules["__main__"].__dict__

    def report():
        st.active = False
        if not st.pending:
            return
        st.pending = False
        g = G()
        r = g["RUNS"][-1] if g.get("RUNS") else None
        text = tok.decode(st.ids, skip_special_tokens=True)
        if text[len(st.shown):]:
            ui.write(text[len(st.shown):])
        msgs.append({"role": "assistant", "content": text.strip()})
        if r:
            peak = r["mem"][6] if r.get("mem") and len(r["mem"]) > 6 else float("nan")
            pfs = r.get("pfs")
            ui.write(f"\n\n[{r['n']} tokens | whole decode {r['tps']:.1f} tok/s | first token "
                     f"{pfs if pfs is None else round(pfs, 2)} s | lifetime peak {peak:.2f} GB | drafter {r.get('drafter')}, "
                     f"{r.get('kept') or 0:.2f} tokens per check"
                     + (" | stopped" if st.stop else "")
                     + (f" | {r['bad'].strip()}" if r.get("bad") and "0.0 s waited" not in r["bad"] else "") + "]\n")
            ui.status(f"last answer: {r['n']} tokens, {r['tps']:.1f} tok/s, first token "
                      f"{pfs if pfs is None else round(pfs, 2)} s, peak {peak:.1f} GB")
        try:                                               # one line per answer (the loop writes no run record in a chat):
            rec = {k: r.get(k) for k in ("key", "type", "drafter", "P", "n", "tps", "kept", "checks", "cyc", "ck", "drf",
                                          "miss", "io", "pfs", "bad", "cut")} if r else {}
            rec.update(time=time.strftime("%H:%M:%S"), peak=(r["mem"][6] if r and r.get("mem") and len(r["mem"]) > 6 else None),
                       stopped=st.stop, config=f"{a.config}-{a.mem}", user=msgs[-2]["content"] if len(msgs) > 1 else "",
                       answer=text)
            with open(os.path.join(out, f"{tag}.jsonl"), "a") as jf:
                jf.write(json.dumps(rec) + "\n")
        except Exception:
            pass

    drafter = a.drafter or ("dfl" if a.kind == "code" else "auto")
    forced = {"dfl": "code", "mtp": "chat"}.get(drafter)  # the loop's prompt type: "code" -> DFlash2, "chat" -> MTP head

    def next_item():
        report()
        g = G()
        g["HARD"] = 1e12                                   # the research runner's 600 s job budget: none in a chat
        g["CAP"] = a.max_tokens                            # (a Ctrl-C lowers it for one answer)
        if forced and not getattr(next_item, "ruled", False):   # the loop calls rule(item) right after it gets the item;
            orig = g["rule"]                               # chat.py's messages get the forced type, everything else the
            g["rule"] = lambda item, _o=orig: forced if str(item.get("key", "")).startswith(f"{pre}/{tag}_") else _o(item)
            next_item.ruled = True                         # engine's own rule (the loop file is unchanged)
        while True:
            ui.write("\n> ")
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                ui.write("\n(Ctrl-C: type /exit to quit)")
                continue
            if not line:
                raise SystemExit(0)
            text = line.strip()
            if not text:
                continue
            if text in ("/exit", "/quit"):
                raise SystemExit(0)
            if text == "/clear":
                del msgs[sysn:]
                ui.write("(new conversation)")
                continue
            break
        msgs.append({"role": "user", "content": text})
        prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False, tokenize=False)
        ids = tok.encode(prompt, add_special_tokens=False)
        st.i += 1
        if st.i > NMAX:
            ui.write("(the session's message limit is reached: restart chat.py)\n")
            raise SystemExit(0)
        if os.path.exists(str(g.get("PAUSE", ""))):
            ui.status("waiting: the research PAUSE file exists")
        else:
            ui.status(f"prefill: {len(ids)} prompt tokens")
        ui.write("\n")
        st.begin()
        return [dict(key=keys[st.i - 1], set=s, prompt=text, user=text, prompt_ids=ids)]

    def on_new_prompt(ids):
        if st.active:
            st.t0 = time.perf_counter()

    def on_commit(new):
        if not st.active:
            return
        now = time.perf_counter()
        if st.t1 is None:
            st.t1 = now
        st.ids.extend(int(x) for x in new)
        text = tok.decode(st.ids, skip_special_tokens=True).rstrip("�")
        if text.startswith(st.shown) and len(text) > len(st.shown):
            ui.write(text[len(st.shown):])
            st.shown = text
        n, d = len(st.ids), now - st.t1
        if now - st.last > 0.1 or n < 3:
            st.last = now
            head = f"{n} tokens | {(n - 1) / d:.1f} tok/s" if d > 0 and n > 1 else f"{n} tokens"
            ui.status(head + f" | first token {st.t1 - st.t0:.2f} s" + (" | stopping" if st.stop else " | Ctrl-C stops"))
        if st.stop:
            G()["CAP"] = n                                 # the loop ends this answer at its next check

    def _items(mod):                                       # the harness's item loader: the loop's main loop asks for each
        base = mod.load                                    # prompt item; chat.py answers with the next message

        def load(nm):
            caller = sys._getframe(1)
            if nm == f"dec_{s}" and caller.f_code.co_filename == screen:
                return next_item()
            return base(nm)
        mod.load = load

    def _drafter(mod):                                     # the drafter's loader gets DRAFTER's revision, as in run.py
        sd = mod.snapshot_download

        def snapshot_download(repo_id, *args, **kw):
            if repo_id == R.DRAFTER[0] and not kw.get("revision"):
                kw["revision"] = R.DRAFTER[1]
                kw.setdefault("local_files_only", True)
            return sd(repo_id, *args, **kw)
        mod.snapshot_download = snapshot_download

    def _session(mod):                                     # the per-check commits (observation only: the original runs)
        cls = mod.SessionVocab
        np_, cm_ = cls.new_prompt, cls.committed

        def new_prompt(self, ids, *a_, **kw):
            on_new_prompt(ids)
            return np_(self, ids, *a_, **kw)

        def committed(self, ids, *a_, **kw):
            r_ = cm_(self, ids, *a_, **kw)
            on_commit(ids)
            return r_
        cls.new_prompt, cls.committed = new_prompt, committed
    patch = {"evalsuite.data": _items, "dflash_model_mlx": _drafter, "session_vocab": _session}

    class _Hook(importlib.abc.MetaPathFinder):             # patches each module right after the loop imports it (run.py's)
        def find_spec(self, name, path, target=None):
            if name not in patch:
                return None
            fn = patch.pop(name)
            sys.meta_path.remove(self)
            try:
                sp = importlib.util.find_spec(name)
            finally:
                if patch:
                    sys.meta_path.insert(0, self)
            if sp is None:
                return None
            orig = sp.loader.exec_module

            def exec_module(m):
                orig(m)
                fn(m)
            sp.loader.exec_module = exec_module
            return sp
    sys.meta_path.insert(0, _Hook())

    def on_sigint(signum, frame):
        if st.active:
            st.stop = True
            return
        raise KeyboardInterrupt
    signal.signal(signal.SIGINT, on_sigint)

    def on_sigtstp(signum, frame):                         # Ctrl-Z would leave the loaded engine (31+ GB) suspended in memory
        ui.write("\n(Ctrl-Z is off here: a suspended chat keeps its 31 GB; use Ctrl-C to stop an answer, /exit to quit)\n")
    signal.signal(signal.SIGTSTP, on_sigtstp)

    log = os.path.join(out, f"{tag}.log")
    lf = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    sys.stdout.flush(); sys.stderr.flush()
    os.dup2(lf, 1)                                         # the engine's own prints (Python and native) go to the log
    os.dup2(lf, 2)
    os.chdir(os.path.join(ROOT, "engine"))
    sys.argv = [screen, str(C), str(a.max_tokens)]
    sys.path.insert(0, os.path.dirname(screen))
    ui.status("loading the engine")
    rc = 0
    try:
        runpy.run_path(screen, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 0
    except KeyboardInterrupt:
        rc = 130
    except BaseException as e:                             # an engine error: say where the log is
        ui.write(f"\nchat.py: the engine stopped: {type(e).__name__}: {e}\n")
        rc = 1
    finally:
        try:
            report()
        except Exception:
            pass
        ui.close()
        ui.write(f"log: {log}\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
