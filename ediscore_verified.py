#!/usr/bin/env python3
"""
EdisCore Verified — Opus Edition (EVALUATION SET — CANONICAL)
===============================================================
Exact parameters from the 95/100 training run.
Same thinking mode. Same temperature. Same method.
Solve. Prove. Ship.

Lane 1: Discovery lineage.

Usage:
  python ediscore_opus_eval_canonical.py --tasks 10
  python ediscore_opus_eval_canonical.py --tasks 400
"""

import anthropic, json, os, sys, re, random, time, subprocess, tempfile, urllib.request
from datetime import datetime
from pathlib import Path

MODEL = "claude-opus-4-6"
THINKING = {"type": "enabled", "budget_tokens": 10000}
TEMPERATURE = 1
LANE = "canonical"

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


def load_eval_tasks():
    cache = Path("arc_eval_tasks_cache.json")
    if cache.exists():
        with open(cache) as f:
            data = json.load(f)
            print(f"  Loaded {len(data)} evaluation tasks from cache.")
            return data

    print("  Downloading ARC-AGI-1 evaluation task list...")
    index_url = "https://api.github.com/repos/fchollet/ARC-AGI/contents/data/evaluation"
    req = urllib.request.Request(index_url, headers={"User-Agent": "EdisCore"})
    with urllib.request.urlopen(req) as r:
        files = json.loads(r.read())

    task_files = [f for f in files if f["name"].endswith(".json")]
    print(f"  Found {len(task_files)} evaluation tasks. Downloading...")

    tasks = {}
    for i, f in enumerate(task_files):
        tid = f["name"].replace(".json", "")
        url = f["download_url"]
        req = urllib.request.Request(url, headers={"User-Agent": "EdisCore"})
        with urllib.request.urlopen(req) as r:
            tasks[tid] = json.loads(r.read())
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(task_files)} downloaded...")

    with open(cache, "w") as f:
        json.dump(tasks, f)
    print(f"  Cached {len(tasks)} evaluation tasks.")
    return tasks


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

def solve(client, task, task_id, max_tries=3):
    expected = task["test"][0]["output"]
    total_tok = 0
    t0 = time.time()

    for attempt in range(max_tries):
        if attempt == 0:
            msg = f"{PROMPT}\n\n{fmt(task)}"
        else:
            msg = f"{RETRY.format(error=last_err)}\n\n{fmt(task)}"

        r = client.messages.create(
            model=MODEL, max_tokens=16000,
            thinking=THINKING,
            messages=[{"role": "user", "content": msg}], temperature=TEMPERATURE,
        )
        text = "\n".join(b.text for b in r.content if b.type == "text")
        total_tok += r.usage.input_tokens + r.usage.output_tokens

        code = extract(text, "code")
        answer = extract(text, "answer")
        if answer:
            try: answer = json.loads(answer)
            except: answer = None

        if code:
            ok, out, err = verify(code, task["train"], task["test"][0]["input"])
            if ok:
                return {
                    "id": task_id, "correct": out == expected,
                    "verified": True, "passes": attempt + 1,
                    "tokens": total_tok, "time": round(time.time() - t0, 1),
                }
            last_err = err or "Unknown error"
        else:
            last_err = "No code produced"

    correct = answer == expected if answer else False
    return {
        "id": task_id, "correct": correct,
        "verified": False, "passes": max_tries,
        "tokens": total_tok, "time": round(time.time() - t0, 1),
    }

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", type=int, default=400)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    tasks = load_eval_tasks()
    ids = list(tasks.keys())
    random.seed(args.seed)
    random.shuffle(ids)
    sel = ids[:args.tasks]

    print(f"\n  EdisCore Verified — OPUS — EVAL — CANONICAL — {len(sel)} tasks")
    print(f"  thinking: enabled/10k | temp: 1 | lane: canonical")
    print(f"  Solve. Prove. Ship.\n")

    results = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = f"ediscore_opus_eval_canonical_{ts}.json"

    def save_results(results, sel, args, final=False):
        n = len(results)
        if n == 0: return
        vc = sum(1 for r in results if r["correct"])
        vvc = sum(1 for r in results if r["verified"] and r["correct"])
        vvw = sum(1 for r in results if r["verified"] and not r["correct"])
        vt = sum(r["tokens"] for r in results)
        with open(outfile, "w") as f:
            json.dump({
                "results": results, "model": MODEL, "dataset": "evaluation",
                "lane": LANE,
                "params": {"thinking": THINKING, "temperature": TEMPERATURE, "max_tokens": 16000, "max_tries": 3},
                "seed": args.seed, "tasks_requested": args.tasks,
                "task_ids": sel, "final": final,
                "summary": {
                    "correct": vc, "total": n, "false_passes": vvw, "tokens": vt,
                }
            }, f, indent=2)

    try:
        for i, tid in enumerate(sel):
            task = tasks[tid]
            vr = solve(client, task, tid)
            results.append(vr)
            vm = "✅" if vr["correct"] else "❌"
            vf = "✓" if vr["verified"] else "△"
            vc = sum(1 for r in results if r["correct"])
            print(f"  [{i+1}/{len(sel)}] {tid}  {vm}{vr['passes']}{vf}  ({vr['time']}s, {vr['tokens']}tok)  [{vc}/{i+1}]")
            save_results(results, sel, args)
    except KeyboardInterrupt:
        print(f"\n  ⚠ Interrupted at {len(results)}/{len(sel)} tasks. Saving partial results...")
        save_results(results, sel, args, final=False)
        print(f"  Saved: {outfile}\n")
        sys.exit(0)

    n = len(results)
    vc = sum(1 for r in results if r["correct"])
    vvc = sum(1 for r in results if r["verified"] and r["correct"])
    vvw = sum(1 for r in results if r["verified"] and not r["correct"])
    vt = sum(r["tokens"] for r in results)

    print(f"\n  {'='*50}")
    print(f"  Opus EVAL CANONICAL: {vc}/{n} ({100*vc/n:.0f}%)")
    print(f"  Trust:               {vvc} verified correct, {vvw} false passes")
    print(f"  Tokens:              {vt:,}")
    print(f"  {'='*50}")

    save_results(results, sel, args, final=True)
    print(f"  Saved: {outfile}\n")

if __name__ == "__main__":
    main()
