#!/usr/bin/env python3
"""
EdisCore — Held-Out Verification Instrument
===========================================
Pre-registered: PREREGISTRATION_2026-08-19.md (predictions frozen there).

This is a MINIMAL DIFF of the canonical engine (ediscore_verified.py, the
script that produced canonical_eval_400.json). PROMPT, RETRY, fmt, extract,
verify, params — copied verbatim. What is added, and only this:

  1. Fixed 88-task list (12 liars + 32 withdrawn-correct + 44 controls).
  2. Held-out split: the LAST training pair is hidden from the model.
     Verification (ship condition) runs on the visible pairs only — unchanged
     mechanics. The shipped code is then executed once on the hidden pair;
     the result is recorded and never fed back.
  3. Code is logged per pass (closing the retroactive-analysis gap).
  4. Final analysis printed against the pre-registered thresholds.

Usage:
    export ANTHROPIC_API_KEY=...
    python ediscore_heldout.py                  # uses arc_eval_tasks_cache.json
    python ediscore_heldout.py --only ac0c5833  # debug single task
"""

import anthropic, json, os, sys, re, time, subprocess, tempfile, hashlib
from datetime import datetime
from pathlib import Path

# --- canonical engine parameters (verbatim) ---------------------------------
MODEL = "claude-opus-4-6"
THINKING = {"type": "enabled", "budget_tokens": 10000}
TEMPERATURE = 1
LANE = "heldout"

PROMPT = """Solve this ARC-AGI puzzle. Study the training examples.
Find the rule. Be exhaustive in observation.
Be ruthless in verification.

You must output TWO things:

1. A Python function that implements your rule:
<code>
def transform(grid):
    # grid is list of lists of ints
    # return the transformed grid
    return output
</code>

2. Your answer for the test input:
<answer>[[1,2,3],[4,5,6]]</answer>"""

RETRY = """Your previous code failed verification.

{error}

Find a DIFFERENT rule. Do not repeat the same approach.

<code>
def transform(grid):
    return output
</code>

<answer>[[1,2,3],[4,5,6]]</answer>"""

# --- frozen task sets (pre-registration, seed-42 control) -------------------
LIARS = ["ac0c5833","f3b10344","c64f1187","0d87d2a6","5ffb2104","ac2e8ecf",
         "351d6448","58743b76","11e1fe23","79369cc6","f9a67cb5","31adaf00"]
WITHDRAWN_CORRECT = ["9110e3c5","b1fc8b8e","40f6cd08","15113be4","de493100",
    "67b4a34d","626c0bcc","0e671a1a","7953d61e","60a26a3e","604001fa","b7cb93ac",
    "af24b4cc","d492a647","c48954c1","833dafe3","103eff5b","2546ccf6","1da012fc",
    "64a7c07e","90347967","aa300dc3","fafd9572","85fa5666","bf699163","47996f11",
    "ea959feb","cfb2ce5a","5833af48","32e9702f","e78887d1","f0afb749"]
CONTROL = ["03560426","05a7bcf2","0607ce86","0c786b71","12997ef3","17b80ad2",
    "18419cfa","21f83797","27f8ce4f","281123b4","29700607","2c0b0aff","2f0c5170",
    "332efdb3","3979b1a8","4364c1c4","4b6b68e5","4c177718","4e45f183","642d658d",
    "695367ec","696d4842","73182012","7d18a6fb","817e6c09","84f2aca1","88207623",
    "8dae5dfc","8ee62060","917bccba","9def23fe","a096bf4d","a57f2f04","aab50785",
    "b20f7c8b","b7f8a4d8","b7fb29bc","ba9d41b8","cd3c21df","cf133acc","d2acf2cb",
    "e345f17b","f823c43c","f8be4b64"]
POOL = {**{t: "liar" for t in LIARS},
        **{t: "withdrawn_correct" for t in WITHDRAWN_CORRECT},
        **{t: "control" for t in CONTROL}}

# --- canonical functions (verbatim) -----------------------------------------
def fmt(task):
    s = ""
    for i, ex in enumerate(task["train"]):
        s += f"Example {i+1} Input:\n{json.dumps(ex['input'])}\nOutput:\n{json.dumps(ex['output'])}\n\n"
    s += f"Test Input:\n{json.dumps(task['test'][0]['input'])}"
    return s

def extract(text, tag):
    m = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    if not m: return None
    return m.group(1).strip()

def verify(code, train, test_input):
    script = f"""
import json, copy
{code}
train = {json.dumps(train)}
test = {json.dumps(test_input)}
errors = []
for i, ex in enumerate(train):
    try:
        got = transform(copy.deepcopy(ex["input"]))
        if got != ex["output"]:
            if got is None:
                errors.append(f"Ex {{i+1}}: returned None")
            elif len(got) != len(ex["output"]):
                errors.append(f"Ex {{i+1}}: wrong height {{len(got)}} vs {{len(ex['output'])}}")
            else:
                for r in range(len(ex["output"])):
                    for c in range(len(ex["output"][r])):
                        if got[r][c] != ex["output"][r][c]:
                            errors.append(f"Ex {{i+1}}: row {{r}} col {{c}} got {{got[r][c]}} expected {{ex['output'][r][c]}}")
                            break
                    if len(errors) > 0 and errors[-1].startswith(f"Ex {{i+1}}"): break
    except Exception as e:
        errors.append(f"Ex {{i+1}}: {{e}}")
if errors:
    print(json.dumps({{"ok": False, "errors": errors[:5]}}))
else:
    try:
        out = transform(copy.deepcopy(test))
        print(json.dumps({{"ok": True, "output": out}}))
    except Exception as e:
        print(json.dumps({{"ok": False, "errors": [f"Test: {{e}}"]}}))
"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script); p = f.name
        r = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=10)
        os.unlink(p)
        if r.returncode != 0:
            return False, None, f"Crashed:\n{r.stderr.strip()[:300]}"
        d = json.loads(r.stdout.strip())
        if d["ok"]:
            return True, d["output"], None
        return False, None, "\n".join(d["errors"])
    except subprocess.TimeoutExpired:
        try: os.unlink(p)
        except: pass
        return False, None, "Timed out"
    except Exception as e:
        return False, None, str(e)

# --- held-out instrument (the diff) -----------------------------------------
def run_on_pair(code, pair):
    """Execute shipped code once on the held-out pair. Same subprocess
    mechanics as verify(), single pair, nothing fed back to the model."""
    ok, out, err = verify(code, [pair], pair["input"])
    return {"pass": ok, "reason": err or "ok"}

def solve_heldout(client, task, task_id, max_tries=3):
    """Canonical solve loop, but the model sees train[:-1] only.
    Code is logged per pass."""
    full_train = task["train"]
    visible = {"train": full_train[:-1], "test": task["test"]}
    hidden = full_train[-1]
    expected = task["test"][0]["output"]
    total_tok, t0, passes, last_err = 0, time.time(), [], None

    for attempt in range(max_tries):
        if attempt == 0:
            msg = f"{PROMPT}\n\n{fmt(visible)}"
        else:
            msg = f"{RETRY.format(error=last_err)}\n\n{fmt(visible)}"
        r = client.messages.create(
            model=MODEL, max_tokens=16000, thinking=THINKING,
            messages=[{"role": "user", "content": msg}], temperature=TEMPERATURE,
        )
        text = "\n".join(b.text for b in r.content if b.type == "text")
        total_tok += r.usage.input_tokens + r.usage.output_tokens
        code = extract(text, "code")
        answer = extract(text, "answer")
        if answer:
            try: answer = json.loads(answer)
            except: answer = None
        rec = {"attempt": attempt + 1, "code": code}          # code logged per pass
        if code:
            ok, out, err = verify(code, visible["train"], task["test"][0]["input"])
            rec["verified"] = ok; rec["error"] = err
            passes.append(rec)
            if ok:
                heldout = run_on_pair(code, hidden)
                return {
                    "id": task_id, "pool": POOL[task_id],
                    "n_train": len(full_train), "small_train": len(full_train) < 3,
                    "shipped": True, "correct": out == expected,
                    "heldout_pass": heldout["pass"], "heldout_reason": heldout["reason"],
                    "passes": attempt + 1, "pass_log": passes,
                    "tokens": total_tok, "time": round(time.time() - t0, 1),
                }
            last_err = err or "Unknown error"
        else:
            rec["verified"] = False; rec["error"] = "No code produced"
            passes.append(rec)
            last_err = "No code produced"
    correct = answer == expected if answer else False
    return {
        "id": task_id, "pool": POOL[task_id],
        "n_train": len(full_train), "small_train": len(full_train) < 3,
        "shipped": False, "correct": correct,
        "passes": max_tries, "pass_log": passes,
        "tokens": total_tok, "time": round(time.time() - t0, 1),
    }

# --- main -------------------------------------------------------------------
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path,
                    default=Path(__file__).with_name("arc_eval_tasks_cache.json"))
    ap.add_argument("--only", nargs="*", help="subset of task ids (debug)")
    args = ap.parse_args()

    tasks = json.loads(args.cache.read_text())
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prereg = Path(__file__).with_name("PREREGISTRATION_2026-08-19.md")
    prereg_sha = hashlib.sha256(prereg.read_bytes()).hexdigest() if prereg.exists() else None

    # Verdict-first order: P1+P2 (liars, controls) resolve before the expensive
    # recovery pool. Task set and analysis unchanged from the pre-registration.
    sel = args.only or (LIARS + CONTROL + WITHDRAWN_CORRECT)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(__file__).with_name("results"); outdir.mkdir(exist_ok=True)
    outfile = outdir / f"heldout_88_{ts}.json"

    print(f"\n EdisCore HELD-OUT — {len(sel)} tasks | canonical engine, last pair hidden")
    print(f" thinking: enabled/10k | temp: 1 | lane: {LANE}")
    print(f" Pre-registration sha256: {prereg_sha}\n")

    results = []
    def save(final=False):
        outfile.write_text(json.dumps({
            "results": results, "model": MODEL, "dataset": "evaluation",
            "lane": LANE, "params": {"thinking": THINKING, "temperature": TEMPERATURE,
                                     "max_tokens": 16000, "max_tries": 3},
            "preregistration_sha256": prereg_sha, "final": final,
        }, indent=1))

    try:
        for i, tid in enumerate(sel):
            vr = solve_heldout(client, tasks[tid], tid)
            results.append(vr)
            flag = "" if not vr["shipped"] else (" HO✓" if vr["heldout_pass"] else " HO✗")
            print(f" [{i+1}/{len(sel)}] {tid} {vr['pool'][:4]} "
                  f"{'✅' if vr['correct'] else '❌'}{vr['passes']}"
                  f"{'✓' if vr['shipped'] else '△'}{flag} "
                  f"({vr['time']}s, {vr['tokens']}tok)")
            save()
    except KeyboardInterrupt:
        print(f"\n ⚠ Interrupted at {len(results)}/{len(sel)}. Partial results saved.")
        save(); sys.exit(0)
    save(final=True)

    # --- against the pre-registration ---------------------------------------
    def pool_big(p): return [r for r in results if r["pool"] == p and not r["small_train"]]
    liars = [r for r in pool_big("liar") if r["shipped"]]
    flags = sum(1 for r in liars if not r["heldout_pass"])
    ctrl = [r for r in pool_big("control") if r["shipped"]]
    ff = sum(1 for r in ctrl if not r["heldout_pass"])
    wc = pool_big("withdrawn_correct")
    wcs = [r for r in wc if r["shipped"]]
    wch = sum(1 for r in wcs if r["heldout_pass"])
    small = [r for r in results if r["small_train"]]
    print(f"\n {'='*56}\n AGAINST THE PRE-REGISTRATION (3+ train pairs)")
    print(f" P1 liars flagged:            {flags}/{len(liars)} shipped   (pass: >=9 of 12 pool)")
    print(f" P2 control false flags:      {ff}/{len(ctrl)} shipped   (pass: <=4 of 44 pool)")
    print(f" P3 withdrawn-correct shipped: {len(wcs)}/{len(wc)}          (pass: >=16 of 32 pool)")
    print(f" P4 of those, held-out pass:   {wch}/{len(wcs) or 1}          (pass: >=90%)")
    print(f" Small-train tasks (separate analysis): {len(small)}")
    print(f" The misses publish either way.\n Saved: {outfile}\n {'='*56}")

if __name__ == "__main__":
    main()
