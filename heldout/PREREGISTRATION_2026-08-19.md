# PRE-REGISTRATION — Held-Out Verification Instrument
**Registered:** 2026-08-19, evening (America/Chicago) — before any instrument code was run
**Authors:** Edis Shekagji (architect) · Claude (second mind — predictions below are Claude's, written to be wrong in public)
**Applies to:** EdisCore Verified engine, canonical ARC-AGI-1 ledger (`results/canonical_eval_400.json`, seed 42)

---

## The claim

Mechanical verification against *visible* training pairs can be passed by lucky code —
12 of 316 shipped answers encoded the wrong rule and shipped anyway (the liars).
**Claim:** verifying generated code on a *held-out* training pair discriminates true
rules from lucky ones. If true, the gate can be hardened at near-zero cost to real
solves, which is what makes scaling N proposers safe.

## Protocol (fixed before the run)

1. **Task set — 88 tasks, frozen below.** 12 liars + 32 withdrawn-correct + 44
   matched controls from the verified-correct pool (control selection: seed-42
   stratified sample matching the target pool's passes profile; script:
   `select_control.py` logic embedded in the runner, deterministic).
2. **Held-out rule.** For each task with N training pairs, the LAST pair (index
   N−1) is hidden. The engine sees pairs 0..N−2 only. Tasks with fewer than 3
   training pairs are run but analyzed separately (holding out 1 of 2 pairs
   changes difficulty materially).
3. **Engine equivalence.** Same architecture and parameters as the canonical run:
   temperature 1, thinking budget 10,000, max_tokens 16,000, max 3 passes,
   mechanical cell-by-cell verification, no LLM judging. The exact canonical
   prompt (the 1,833-character one) must be pasted into the runner before
   execution — the record says augmented prompts underperform it; do not "improve" it.
4. **Ship condition unchanged:** code passes all *visible* pairs.
   **Instrument reading:** the shipped code is then executed on the held-out pair.
   Pass/fail on that pair is recorded but never fed back to the model.
5. **Code per pass is logged** — closing the gap that made this instrument
   impossible to run retroactively on the canonical ledger.
6. **Model string, date, and this file's SHA-256 are recorded in the results JSON.**

## Predictions (numeric, before code)

| # | Population | Prediction | Reasoning on record |
|---|------------|------------|---------------------|
| P1 | 12 liars (re-solved, held-out read) | **≥ 9/12** of shipped solutions fail the held-out pair | Liars fit visible pairs by luck; luck should not transfer |
| P2 | 44 controls (verified-correct) | **≤ 4/44** falsely flagged (held-out fail) | True rules transfer; some tasks have genuinely ambiguous last pairs |
| P3 | 32 withdrawn-correct (fresh re-solve) | **≥ 16/32** ship under the fresh solve | Independence recovers — the +23 result from the V3 simulation |
| P4 | Of P3's shipped | **≥ 90%** pass the held-out pair | What ships under the harder gate should be real |

## Pass / fail (decided now, not after)

- **INSTRUMENT PASSES:** P1 ≥ 9/12 flagged **and** P2 ≤ 4/44 false flags.
- **INSTRUMENT FAILS (rung falsified):** liars flagged < 6/12 **or** false flags > 8/44.
- Anything between: inconclusive — one iteration permitted on the *analysis*,
  zero iterations on the predictions. The misses publish either way.

## Cost & honesty

- ~88 tasks × ~35K tokens (target-pool mean) ≈ **3.1M tokens**, hours not minutes.
  Runs on the ROG with the architect's key. Nothing here spends without his hand.
- **Visible-set caveat:** all 88 tasks have touched the design since March. This
  measures the *instrument's* discriminating power, not generalization. The
  competition's hidden set remains the only true holdout.
- **The liar count is small.** 12 is enough to falsify, not enough to estimate a
  rate with precision. The record will say so.
- Predictions are Claude's. If they are wrong, that goes in the arc under its own title.

## Frozen task lists

**Liars (12):**
`ac0c5833, f3b10344, c64f1187, 0d87d2a6, 5ffb2104, ac2e8ecf, 351d6448, 58743b76, 11e1fe23, 79369cc6, f9a67cb5, 31adaf00`

**Withdrawn-correct (32):**
`9110e3c5, b1fc8b8e, 40f6cd08, 15113be4, de493100, 67b4a34d, 626c0bcc, 0e671a1a, 7953d61e, 60a26a3e, 604001fa, b7cb93ac, af24b4cc, d492a647, c48954c1, 833dafe3, 103eff5b, 2546ccf6, 1da012fc, 64a7c07e, 90347967, aa300dc3, fafd9572, 85fa5666, bf699163, 47996f11, ea959feb, cfb2ce5a, 5833af48, 32e9702f, e78887d1, f0afb749`

**Matched control (44, seed-42 stratified from verified-correct):**
`03560426, 05a7bcf2, 0607ce86, 0c786b71, 12997ef3, 17b80ad2, 18419cfa, 21f83797, 27f8ce4f, 281123b4, 29700607, 2c0b0aff, 2f0c5170, 332efdb3, 3979b1a8, 4364c1c4, 4b6b68e5, 4c177718, 4e45f183, 642d658d, 695367ec, 696d4842, 73182012, 7d18a6fb, 817e6c09, 84f2aca1, 88207623, 8dae5dfc, 8ee62060, 917bccba, 9def23fe, a096bf4d, a57f2f04, aab50785, b20f7c8b, b7f8a4d8, b7fb29bc, ba9d41b8, cd3c21df, cf133acc, d2acf2cb, e345f17b, f823c43c, f8be4b64`

---

*Nothing counts unless it could have failed. This file is the thing that can fail.*
