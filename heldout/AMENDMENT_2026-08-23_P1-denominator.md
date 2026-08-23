# AMENDMENT 001 to PREREGISTRATION_2026-08-19
**Written:** 2026-08-23 — before any results exist. `results\` holds only two
failed-launch console logs (401 auth errors, zero tasks attempted, no results
JSON on either the Desktop or Drive side). No API response bearing on P1–P4
has ever been received.
**Amends:** `PREREGISTRATION_2026-08-19.md`,
sha256 `700dcf28d54f84ed136ce8e9b2f72552199ea47a57b140b8b1261f46d60b1990`
(unmodified — this file is separate and additive; the original hash still verifies).
**Author:** Claude (second mind). Ratification is the architect's: firing the
run with this file on disk ratifies it; deleting it before firing vetoes it.
**Engine delta:** none. Runner stays v3, byte-identical. This amendment touches
analysis arithmetic only.

---

## The defect

The preregistration contradicts itself, discovered in pre-flight validation
(2026-08-23) of the frozen task lists against `arc_eval_tasks_cache.json`:

- **§2** states tasks with fewer than 3 training pairs are run but **analyzed
  separately** (holding out 1 of 2 pairs changes difficulty materially).
- **P1** states **"≥ 9/12"** of shipped liar solutions must fail the held-out pair.

Four of the twelve liars have fewer than 3 training pairs
(`c64f1187, 351d6448, 58743b76, 11e1fe23`). Under §2 they leave the main
analysis. The main-analysis liar denominator is therefore **8**, and 9 of 8 is
unattainable. Meanwhile the registered fail branch ("liars flagged < 6/12") is
attainable at 6 of 8. **As registered, the instrument can be falsified but
cannot pass.** That asymmetry is a drafting error, not a scientific judgment,
and it must be corrected while no results exist.

The full small-train split, from the frozen pools (15 of 88 tasks):

| Pool | Total | Small-train (<3 pairs) | Analyzed (≥3 pairs) |
|---|---|---|---|
| Liars | 12 | 4 | **8** |
| Withdrawn-correct | 32 | 7 | **25** |
| Controls | 44 | 4 | **40** |

## The correction

Each registered threshold was a **rate** written against the full pool. The
rates are unchanged. They are restated here against the analyzed denominators,
with every rounding taken **against** the instrument:

| # | Registered | Rate | Restated (analyzed set) | Rounding direction |
|---|---|---|---|---|
| P1 | ≥ 9/12 flagged | 75% | **≥ 6/8** | exact (6/8 = 75%) |
| P2 | ≤ 4/44 false flags | 9.09% | **≤ 3/40** | 3.64 → 3 (stricter) |
| P3 | ≥ 16/32 shipped | 50% | **≥ 13/25** | 12.5 → 13 (stricter) |
| P4 | ≥ 90% of P3's shipped pass held-out | 90% | **unchanged** (already a rate) | — |

Pass / fail, restated identically:

- **INSTRUMENT PASSES:** P1 ≥ 6/8 flagged **and** P2 ≤ 3/40 false flags.
- **INSTRUMENT FAILS (rung falsified):** liars flagged < 4/8 (registered rate:
  < 50%) **or** false flags ≥ 8/40 (registered rate: > 18.2%; 8/40 = 20%).
- Anything between: inconclusive — one iteration permitted on the analysis,
  zero on the predictions. Unchanged.

Small-train tasks are still **run** and reported separately and non-decisively,
exactly as §2 registered. The 4 small-train liars' held-out outcomes publish
alongside the main analysis either way.

## What this amendment is not

It does not touch the engine, the prompt, the parameters, the task lists, the
held-out mechanic, the ship condition, or any prediction's registered rate. It
converts pool-denominator thresholds to analyzed-set thresholds that §2 already
implied, and resolves the drafting contradiction in the only direction that
does not require knowing any result. The misses publish either way.

---

*An instrument that cannot pass is not a harder test — it is a broken gauge.
Fixed before first reading, on the record, under its own hash.*
