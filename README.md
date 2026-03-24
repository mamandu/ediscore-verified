<div align="center">

# EdisCore Verified

**Code-execution verification for AI reasoning tasks.**

*Don't trust the answer. Trust the proof.*

[![Accuracy](https://img.shields.io/badge/ARC--AGI--1-84%25-brightgreen?style=flat-square)]()
[![Trust](https://img.shields.io/badge/Trust-96.2%25-blue?style=flat-square)]()
[![Cost](https://img.shields.io/badge/Cost-~%240.50%2Ftask-orange?style=flat-square)]()
[![Model](https://img.shields.io/badge/Claude-Opus%204.6-8A2BE2?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)]()

</div>

---

A 200-line Python script that forces AI to prove its answers by writing executable code, then mechanically checks the output against training data. If the code doesn't reproduce every training example, the answer doesn't ship.

## Results

**ARC-AGI-1 Public Evaluation Set — 400 tasks**

| Metric | Value |
|--------|-------|
| Correct | **336 / 400 (84.0%)** |
| Shipped (verified) | **304** |
| False passes | 12 |
| Trust on shipped answers | **96.2%** |
| Withdrawn (refused to ship) | 52 |
| Cost | ~$0.50/task |
| Model | Claude Opus 4.6 |

304 answers were verified correct by code execution. 12 passed verification but were wrong (false passes — the model wrote code that happened to produce correct training outputs but encoded the wrong rule). 52 tasks were withdrawn: the system could not verify an answer and chose silence over guessing.

> When the system says "verified," it is correct 96.2% of the time.

## How It Works

```
Solve → Write Python code implementing the rule → Execute code against training data → Ship or silence
```

1. **Solve**: Ask the model to find the transformation rule and express it as executable Python
2. **Verify**: Run the generated code against every training input/output pair
3. **Retry**: If verification fails, feed the specific error back and retry (up to 3 passes)
4. **Ship or silence**: Only verified answers are shipped. Everything else is withdrawn

The verification is mechanical — no LLM judges the output. Python executes the code, compares the result grid cell by cell, and returns pass or fail. The model cannot talk its way past the check.

### The Core Insight

AI checking its own work has the same blind spots as the original solver. Ask a model to verify its own answer and it will confidently confirm its own mistakes. But code has no blind spots. It matches or it doesn't. There is no interpretation. No negotiation. Pure execution.

### What Makes This Different

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

## Evaluation Breakdown

### Pass Distribution

```
Pass 1  ████████████████████████████████████████  287 tasks (71.8%)
Pass 2  ██                                        17 tasks  (4.2%)
Pass 3  ████████████                              96 tasks (24.0%)
```

Most tasks verify on the first attempt. When the model is right, it usually knows immediately.

### Token Economy

| | Avg Tokens | Avg Time |
|--|-----------|----------|
| 1-pass solves | ~8K | ~70s |
| 3-pass solves | ~56K | ~580s |
| **Total** | **9.2M tokens** | **~$200** |

Hard tasks that burn three retry passes cost ~7x more than easy ones. The long tail is expensive.

### Outcome Matrix

```
                    Verified    Unverified
                  ┌───────────┬───────────┐
    Correct       │    304    │     32    │
                  ├───────────┼───────────┤
    Incorrect     │     12    │     52    │
                  └───────────┴───────────┘
```

- **304 verified correct** — the system works as intended
- **32 correct but unverified** — the model got it right but couldn't prove it (conservative misses)
- **12 false passes** — verified but wrong (the dangerous quadrant)
- **52 withdrawn** — couldn't verify, didn't ship (safe failures)

## Failure Analysis

12 false passes across 400 tasks (3% false pass rate).

All 12 are **replicating liars**: the model writes code that produces correct outputs on training data but encodes the wrong transformation rule. The code passes mechanical verification because it overfits to the specific examples rather than capturing the general pattern.

- 10 occurred on pass 1 (fast, confident, wrong)
- 1 on pass 2
- 1 on pass 3

These are irreducible by single-path verification alone. Addressing them requires parallel independent solves with consensus checking.

## Cost

~$0.50/task on Claude Opus 4.6 with prompt caching. Total cost for the 400-task evaluation: approximately $200.

Token distribution: 9.2M total, averaging 23K tokens/task. The cost is dominated by hard tasks that burn three retry passes (~56K tokens each). Easy tasks that verify on pass 1 average ~8K tokens.

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

## What This Is Not

- Not a fine-tuned model. The script wraps a stock Claude Opus 4.6 API call.
- Not an ensemble. One model, one path per pass, up to three passes.
- Not competing on ARC-AGI-2. These results are on ARC-AGI-1 public evaluation (400 tasks). Different dataset, different difficulty. Numbers across benchmarks are not directly comparable.

## V3 (In Progress)

Parallel verification architecture addressing the false pass problem:

- Two independent solves run in parallel with different prompts
- Corroboration required before shipping: both must verify and agree
- Deep tiebreak solver (25K thinking budget) for disagreements
- Pilot results: 19/20 correct, 0 false passes, 100% trust on verified

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

*Built in silence. Transmitted in truth.*

</div>
