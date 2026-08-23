# WITNESS — The Held-Out Instrument, Published Before Its First Reading

**Pushed to the public record before any result exists.**

This folder extends the canonical result in this repository (304 verified /
12 false passes / 52 withdrawn, ARC-AGI-1 public eval, seed 42) with a
pre-registered follow-up instrument. The claim under test: verifying generated
code on a *held-out* training pair discriminates true rules from the lucky
code that produced the 12 false passes.

The push timestamp of this commit is the external witness that the
predictions, thresholds, and analysis rules below were fixed **before the
instrument produced a single reading**.

## The witnessed files

| File | sha256 |
|---|---|
| `PREREGISTRATION_2026-08-19.md` | `700dcf28d54f84ed136ce8e9b2f72552199ea47a57b140b8b1261f46d60b1990` |
| `AMENDMENT_2026-08-23_P1-denominator.md` | `bd87b67f2cbf7afa245fb9156660316c87403857c97c81f413c792bb61748ab4` |

- **`ediscore_heldout.py`** — runner v3: the canonical engine verbatim
  (prompt, retry, params, mechanical verification), plus only the held-out
  diff — the model sees train[:-1]; shipped code is executed once on the
  hidden pair; the result is recorded and never fed back.
- **`arc_eval_tasks_cache.json`** — the 400 public-eval tasks
  (ARC-AGI-1, F. Chollet — public data), cached so the instrument is
  reproducible byte-for-byte.
- **`results/console_FAILED-401_v3.log`** — the instrument's first two launch
  attempts died on authentication errors before any task ran. The misses
  publish either way; that starts now.

## State at witness time

Zero API responses bearing on the predictions have ever been received. The
run is armed and unfired. The amendment (written 2026-08-23, also before any
result) resolves a drafting contradiction between §2 and P1 of the
preregistration — pool denominators restated against the analyzed set, every
rounding taken against the instrument. The engine is untouched.

## The standing commitment

The results publish either way — to this repository. If the predictions are
wrong, that is the result, under its own title.

*Nothing counts unless it could have failed. As of this push, that sentence
has a timestamp that does not belong to us.*
