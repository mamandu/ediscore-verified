<div align="center">

# EdisCore Verified

**Not a new way to solve. A new way to know when you've solved.**

*Verification as a metric, not just a mechanism.*

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

</div>

---

Code-execution verification for AI reasoning tasks. EdisCore asks a model to express a solution as executable Python, runs that code against the training examples, and ships only when the result survives mechanical checking. The contribution is not the solve-and-verify pattern itself, but the measurement layer around it: verified vs. unverified answers, false-pass rate, and trust on shipped outputs.

The ARC-AGI-1 leaderboard emphasizes score and cost; this project adds false-pass rate, shipped-vs-withdrawn accounting, and trust on shipped answers.

## What This Measures

Most benchmarks report one number: accuracy. EdisCore reports four:

| Metric | Value | What it means |
|--------|-------|---------------|
| Accuracy | 84.0% (336/400) | How often the system got the right answer |
| Verified correct | 76.0% (304/400) | How often it got the right answer *and proved it* |
| Trust on shipped | 96.2% (304/316) | When it says "verified," how often it's right |
| False pass rate | 3.0% (12/400) | How often verification passed but the answer was wrong |

The trust rate is the headline. When the system ships a verified answer, it is correct 96.2% of the time. When full verification fails, the system withdraws rather than guess. The remaining risk is false passes: code that fits the training examples but encodes the wrong rule.

## Results

**ARC-AGI-1 Public Evaluation Set — 400 tasks**

| Metric | Value |
|--------|-------|
| Correct | 336 / 400 (84.0%) |
| Shipped (verified) | 316 |
| Verified correct | 304 |
| False passes | 12 |
| Trust on shipped answers | 96.2% |
| Withdrawn (refused to ship) | 84 |
| Cost | ~$0.50/task |
| Model | Claude Opus 4.6 |

## How It Works

```
Solve → Write Python code implementing the rule → Execute code against training data → Ship or silence
```

1. **Solve**: Ask the model to find the transformation rule and express it as executable Python
2. **Verify**: Run the generated code against every training input/output pair
3. **Retry**: If verification fails, feed the specific error back and retry (up to 3 passes)
4. **Ship or silence**: Only verified answers are shipped. Everything else is withdrawn

The verification is mechanical — no LLM judges the output. Python executes the code, compares the result grid cell by cell, and returns pass or fail. The model cannot talk its way past the check.

### Why Mechanical Verification

AI checking its own work has the same blind spots as the original solver. Ask a model to verify its own answer and it will confidently confirm its own mistakes. Code has no blind spots. It matches or it doesn't. There is no interpretation. No negotiation. Pure execution.

### Three Outcomes

Every task produces one of three results:

- **Verified correct** (304) — the system proved its answer and was right. Safe to ship.
- **Conservative miss** (32) — the system got the right answer but couldn't prove it. Withdrawn anyway.
- **Safe failure** (52) — the system couldn't verify and didn't ship. Silence over guessing.

The dangerous quadrant — verified but wrong — is the false pass problem. 12 out of 400 tasks.

## Outcome Matrix

```
                    Verified    Unverified
                  ┌───────────┬───────────┐
    Correct       │    304    │     32    │
                  ├───────────┼───────────┤
    Incorrect     │     12    │     52    │
                  └───────────┴───────────┘
```

## Architecture

```
Pass 1: Solve → verify 100% → ship if verified
Pass 2: Solve with error feedback → verify 100% → ship if verified
Pass 3: Solve with accumulated errors → verify 100% → ship if verified
         If still unverified → withdraw (silence)
```

Each pass uses Claude Opus 4.6 with extended thinking (10K token budget). Temperature 1. No fine-tuning. No ensemble. No external tools beyond the Python executor.

## Pass Distribution

```
Resolved on pass 1  ████████████████████████████████████████  287 tasks (71.8%)
Resolved on pass 2  ██                                        17 tasks  (4.2%)
Reached pass 3      ████████████                              96 tasks (24.0%)
```

Most successful verifications happen on the first attempt.

## Token Economy

| Bucket | Avg Tokens | Avg Time |
|--------|-----------|----------|
| 1-pass solves | ~8K | ~70s |
| 3-pass solves | ~56K | ~580s |

Total tokens: ~9.2M across 400 tasks. Estimated total cost: ~$200.

Hard tasks that burn three retry passes cost ~7x more than easy ones. The long tail is expensive.

## Failure Analysis

12 false passes across 400 tasks (3% false pass rate).

All 12 are **replicating liars**: the model writes code that produces correct outputs on training data but encodes the wrong transformation rule. The code passes mechanical verification because it overfits to the specific examples rather than capturing the general pattern.

- 10 occurred on pass 1 (fast, confident, wrong)
- 1 on pass 2
- 1 on pass 3

These are irreducible by single-path verification alone. Addressing them requires parallel independent solves with consensus checking.

## Files

| File | Description |
|------|-------------|
| `ediscore_verified.py` | The canonical 200-line verification script |
| `results/canonical_eval_400.json` | Full results for all 400 evaluation tasks |

## Usage

```bash
# Requires: ANTHROPIC_API_KEY environment variable, Python 3.10+
# ARC-AGI-1 evaluation data auto-downloads from GitHub on first run

python ediscore_verified.py --tasks 400

# Results saved as JSON with per-task breakdown
```

## What This Is

- A verification layer that separates proven answers from guesses
- A trust metric that reports *when the system knows it's right*, not just how often it's right
- A measurement framework: false pass rate, verified vs unverified, trust at cost

## What This Is Not

- Not a new architecture. Code-verified solvers exist. The contribution is the measurement.
- Not a fine-tuned model. The script wraps a stock Claude Opus 4.6 API call.
- Not an ensemble. One model, one path per pass, up to three passes.
- Not competing on ARC-AGI-2. These results are on ARC-AGI-1 public evaluation (400 tasks). Different dataset, different difficulty.

## V3 (In Progress)

Parallel verification architecture addressing the false pass problem:

- Two independent solves run in parallel with different prompts
- Corroboration required before shipping: both must verify and agree
- Deep tiebreak solver (25K thinking budget) for disagreements

In a targeted 20-task V3 pilot: 19/20 correct, 17 verified correct, 0 false passes. The only miss occurred outside the verified lane.

Full 400-task V3 evaluation forthcoming.

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

<div align="center">

*Not a new way to solve. A new way to know when you've solved.*

</div>