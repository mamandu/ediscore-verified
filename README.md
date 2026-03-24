# EdisCore Verified

**Code-execution verification for AI reasoning tasks.**

A 200-line Python script that forces AI to prove its answers by writing executable code, then mechanically checks the output against training data. If the code doesn't reproduce every training example, the answer doesn't ship.

## Results

**ARC-AGI-1 Public Evaluation Set — 400 tasks**

| Metric | Value |
|--------|-------|
| Correct | 336 / 400 (84.0%) |
| Shipped (verified) | 304 |
| False passes | 12 |
| Trust on shipped answers | 96.2% |
| Withdrawn (refused to ship) | 52 |
| Cost | ~$0.50/task |
| Model | Claude Opus 4.6 |

304 answers were verified correct by code execution. 12 passed verification but were wrong (false passes — the model wrote code that happened to produce correct training outputs but encoded the wrong rule). 52 tasks were withdrawn: the system could not verify an answer and chose silence over guessing.

When the system says "verified," it is correct 96.2% of the time.

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

Each pass uses Claude Opus 4.5 with extended thinking (10K token budget). Temperature 1. No fine-tuning. No ensemble. No external tools beyond the Python executor.

## Failure Analysis

12 false passes across 400 tasks (3% false pass rate).

All 12 are **replicating liars**: the model writes code that produces correct outputs on training data but encodes the wrong transformation rule. The code passes mechanical verification because it overfits to the specific examples rather than capturing the general pattern.

- 10 occurred on pass 1 (fast, confident, wrong)
- 1 on pass 2
- 1 on pass 3

These are irreducible by single-path verification alone. Addressing them requires parallel independent solves with consensus checking (implemented in V3, evaluation forthcoming).

## Cost

~$0.50/task on Claude Opus 4.6 with prompt caching. Total cost for the 400-task evaluation: approximately $200.

Token distribution: 9.2M total, averaging 23K tokens/task. The cost is dominated by hard tasks that burn three retry passes (~56K tokens each). Easy tasks that verify on pass 1 average ~8K tokens.

## Files

| File | Description |
|------|-------------|
| `ediscore_verified.py` | The canonical 200-line verification script |
| `results/canonical_eval_400.json` | Full results for all 400 evaluation tasks |
| `ediscore.pdf` | EdisCore framework document |

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
- Preliminary pilot: 19/20 correct, 0 false passes

Full 400-task V3 evaluation forthcoming.

## Citation

If you use this work, please cite:

```
EdisCore Verified — Code-execution verification for AI reasoning
Edis Shekaxhi, 2026
https://github.com/byedis/ediscore-verified
```

## License

MIT

---

*Built in silence. Transmitted in truth.*
