# EdisCore Verified

**Code-execution verification for AI reasoning tasks.**

A ~270-line Python script that forces AI to prove its answers by writing executable code, then mechanically checks the output against training data. If the code doesn't reproduce every training example, the answer doesn't ship.

## Results

**ARC-AGI-1 Public Evaluation Set — 400 tasks**

| Metric | Value |
|--------|-------|
| Correct | 336 / 400 (84.0%) |
| Shipped (verified) | 316 |
| Verified correct | 304 |
| False passes | 12 |
| Trust on shipped answers | 96.2% (304 / 316) |
| Withdrawn (refused to ship) | 84 |
| Cost | ~$0.50/task |
| Model | Claude Opus 4.6 |

### Outcome matrix

```
                    Verified    Unverified
                  ┌───────────┬───────────┐
    Correct       │    304    │     32    │
                  ├───────────┼───────────┤
    Incorrect     │     12    │     52    │
                  └───────────┴───────────┘
```

304 answers were verified correct by code execution. 12 passed verification but were wrong — false passes, where the model wrote code that reproduced the training outputs while encoding the wrong rule. 84 tasks were withdrawn because the system could not verify an answer and chose silence over guessing; 32 of those were in fact correct, and giving them up is the price of the refusal.

When the system says "verified," it is correct 96.2% of the time.

## The Held-Out Instrument — and its first reading

A follow-up instrument was pre-registered in `heldout/` and pushed to this repository **before it produced a single reading**, with its predictions, thresholds and analysis rules fixed in advance and hashed in `heldout/WITNESS.md`. The claim under test: that verifying generated code on a *held-out* training pair separates true rules from the lucky code behind the 12 false passes above.

It was fired on 2026-09-18.

| Prediction | Threshold (Amendment 001) | Reading |
|---|---|---|
| P1 — shipped liars flagged | ≥ 6/8 to pass; < 4/8 falsifies | **1 of 8** — falsified |
| P2 — control false flags | ≤ 3/40 | 1 of 40 — hit |
| P3 — withdrawn-correct shipped | ≥ 13/25 | 15 of 25 — hit |
| P4 — held-out pass rate | ≥ 90% | **73.3%** (11 of 15) — miss |

Scope: the 96.2% above is the canonical 400-task evaluation and is not affected by this reading. The held-out check was a proposed *improvement* to it, registered separately and judged on its own terms.

**INSTRUMENT FAILS.** The held-out check did not discriminate the replicating liars, which was its central prediction. It went out before it could flatter anyone, and it is reported here at the size it would have been reported had it succeeded. Reader script, console logs and the full result JSON are in `heldout/`.

## How It Works

```
Solve → Write Python code implementing the rule → Execute code against training data → Ship or silence
```

1. **Solve**: Ask the model to find the transformation rule and express it as executable Python
2. **Verify**: Run the generated code against every training input/output pair
3. **Retry**: If verification fails, feed the error back and retry (up to 3 passes)
4. **Ship or silence**: Only verified answers are shipped. Everything else is withdrawn

The verification is mechanical — no LLM judges the output. Python executes the code, compares the result grid cell by cell, and returns pass or fail. The model cannot talk its way past the check.

### What makes this different

Most AI benchmarking treats every answer equally. EdisCore splits the world into two categories:

- **Verified**: the model wrote code that reproduces all training examples. High confidence.
- **Unverified**: the model couldn't prove its answer. Withdrawn.

This creates a trust layer. Instead of asking "is the model smart enough?", you ask "does the model know when it's right?"

## Architecture

```
Pass 1: Solve → verify 100% → ship if verified
Pass 2: Solve with error feedback → verify 100% → ship if verified
Pass 3: Solve with accumulated errors → verify 100% → ship if verified
         If still unverified → withdraw (silence)
```

Each pass uses Claude Opus 4.6 with extended thinking (10K token budget). Temperature 1. No fine-tuning. No ensemble. No external tools beyond the Python executor.

### Pass distribution

```
Resolved on pass 1  ████████████████████████████████████████  287 tasks (71.8%)
Resolved on pass 2  ██                                        17 tasks  (4.2%)
Reached pass 3      ████████████                              96 tasks (24.0%)
```

Most successful verifications happen on the first attempt.

## Failure Analysis

12 false passes across 400 tasks (3.0% false pass rate).

All 12 are **replicating liars**: the model writes code that produces correct outputs on training data but encodes the wrong transformation rule. The code passes mechanical verification because it overfits to the specific examples rather than capturing the general pattern.

- 10 occurred on pass 1 (fast, confident, wrong)
- 1 on pass 2
- 1 on pass 3

These are irreducible by single-path verification alone. Addressing them requires parallel independent solves with consensus checking. The held-out instrument registered above was one attempt and it did not reach them; V3 below is the next.

## Cost and token economy

~$0.50/task on Claude Opus 4.6 with prompt caching. Total cost for the 400-task evaluation: approximately $200. Total tokens ~9.2M, averaging 23K per task.

| Bucket | Avg Tokens | Avg Time |
|--------|-----------|----------|
| 1-pass solves | ~8K | ~70s |
| 3-pass solves | ~56K | ~580s |

Hard tasks that burn three retry passes cost ~7x more than easy ones. The long tail is expensive.

## Files

| File | Description |
|------|-------------|
| `ediscore_verified.py` | The canonical ~270-line verification script |
| `results/canonical_eval_400.json` | Full results for all 400 evaluation tasks |
| `heldout/` | The pre-registered held-out instrument: registration, two amendments, witness, runner, results |

## Usage

```bash
# Requires: ANTHROPIC_API_KEY environment variable, Python 3.10+
# Requires: ARC-AGI-1 evaluation data (auto-downloaded from GitHub)

# Run on a specific number of tasks
python ediscore_verified.py --tasks 400

# Results saved as JSON with per-task breakdown
```

## What This Is Not

- Not a fine-tuned model. The script wraps a stock Claude Opus 4.6 API call.
- Not an ensemble. One model, one path per pass, up to three passes.
- Not competing on ARC-AGI-2. These results are on ARC-AGI-1 public evaluation (400 tasks). Different dataset, different difficulty. Numbers across benchmarks are not directly comparable.

## V3 (In Progress)

Parallel verification architecture addressing the false pass problem:

- Two independent solves (A + B) run in parallel with different prompts
- Corroboration required before shipping: both must verify and agree
- Tiebreak solver C (25K thinking budget) for disagreements
- Preliminary pilot: 19 of 20 correct, 0 false passes

**Not pre-registered.** The pilot is n = 20, and the full 400-task V3 evaluation has no registered predictions or thresholds. The held-out instrument above had both, which is why its failure could be reported as a failure. Read the V3 numbers as what they are: an unregistered pilot on twenty tasks, pointing somewhere, proving nothing yet.

## Citation

If you use this work, please cite:

```
EdisCore Verified — Code-execution verification for AI reasoning
Edis Shekaxhi, 2026
https://github.com/mamandu/ediscore-verified
```

## License

MIT

---

*Built in silence. Transmitted in truth.*
