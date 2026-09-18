# AMENDMENT 002 to PREREGISTRATION_2026-08-19
**Written:** 2026-09-18 — before any results exist. `results\` holds only the
August failed-launch console log, in two byte-identical copies
(`console_FAILED-401_v3.log`, published here; `console.log`, an untracked local
copy; sha256 `7d98c97b11e7566b61f39fd4fbedb507d0281da77c7206a90eea8bb57ca82ee7`).
Each records one request — one request id, one 401 `invalid x-api-key` — and a
logged command line showing the placeholder `<your-key>` where a key belongs.
WITNESS.md describes this log as the instrument's first two launch attempts; the
bytes on file record one request, and this amendment states only that. No task
received a model response. No results JSON exists on either the Desktop or Drive
side (both trees read 2026-09-18). The only API response on file is that 401. No
API response bearing on P1–P4 has ever been received.
**Amends:** `PREREGISTRATION_2026-08-19.md`,
sha256 `700dcf28d54f84ed136ce8e9b2f72552199ea47a57b140b8b1261f46d60b1990`
(unmodified — this file is separate and additive; the original hash still verifies).
**Author:** Claude (second mind). Ratification is the architect's: firing the
run with this file on disk ratifies it; deleting it before firing vetoes it.
Published on the architect's word, 2026-09-18.
**Engine delta:** none. Runner stays v3, byte-identical to the witnessed commit
(`fd72dc0`, unchanged at `800721f`), sha256
`3f947a0150fe428a54a4f9ed741f2d2ea37805403f8c60f103ad9a9d370b21d2`. This
amendment replaces the three-word parenthesis in §3's prompt sentence and
touches nothing else.

---

## The defect

The prompt sentence of §3 (Engine equivalence) reads, in full:

> The exact canonical prompt (the 1,833-character one) must be pasted into the
> runner before execution — the record says augmented prompts underperform it;
> do not "improve" it.

On the published record, the parenthesis names the wrong prompt. Found in
pre-flight on 2026-09-18, from bytes:

| Prompt | Characters | sha256 of its UTF-8 bytes |
|---|---|---|
| `PROMPT` of `ediscore_verified.py` | **402** | `e2583d5453d5710bab0e81d33eaa0c6cc4f795ed6a62a4d93f8a07526451f6e5` |
| The "original 1,833-char" EdisCore framework prompt | **1,833** | `0b981ac57729a8f1bbe7be13dea4ab508af500b15ceab14b5da3004c0355ddb6` |

**What a reader can check in this repository:**

- `ediscore_verified.py` — listed in the README as "The canonical 200-line
  verification script"; line 23 `LANE = "canonical"`; line 216 writes
  `ediscore_opus_eval_canonical_{ts}.json` — carries the 402-character `PROMPT`.
  The file is byte-identical (sha256
  `dc591ff335337c4b2955c13457663933c884711ed3a3c558ff67d78dcf8a8c54`) at every
  one of the eight commits that contain it, from `50b001b` to `800721f`. Its
  prompt was never different.
- `results/canonical_eval_400.json` records `"model": "claude-opus-4-6"`,
  `"lane": "canonical"` and `"params": {"thinking": {"type": "enabled",
  "budget_tokens": 10000}, "temperature": 1, "max_tokens": 16000, "max_tries": 3}`
  — the runner's parameters exactly.
- The runner `heldout/ediscore_heldout.py` carries the same 402-character
  `PROMPT`, same hash, and has since its first public commit. WITNESS.md already
  describes it as "the canonical engine verbatim (prompt, retry, params,
  mechanical verification)".
- The string "1,833" entered this repository's history in one commit only:
  `fd72dc0`, the preregistration itself.

**What only the author's machine shows (not public; offered as context, read
2026-09-18):** in the local evaluation archive, ten scripts carry the
402-character string (seven as `PROMPT`, three as `PROMPT_A`), and every one of
them names `claude-opus-4-6` and no other Claude model. Four scripts carry the
1,833-character string — `arc_ediscore_thinking_benchmark.py`,
`arc_ediscore_benchmark.py`, `arc_ediscore_clean.py` and
`arc_ediscore_verified.py` — and every one of them names
`claude-sonnet-4-20250514` and no other Claude model. In no script found that calls an
Opus model does the framework prompt appear. The last of those four,
`arc_ediscore_verified.py`, is a Sonnet-era predecessor whose name is one prefix
away from the canonical `ediscore_verified.py`; that collision is a likely
origin of the error. The committed `canonical_eval_400.json` is the LF form of
the archive's `ediscore_opus_eval_canonical_20260322_152439.json` — a filename
that only `ediscore_verified.py` writes.

As registered, §3 contradicts itself: its heading demands equivalence with the
canonical run, and its parenthesis names a prompt that, on every byte available,
the canonical run did not use. Obeying the parenthesis would break the
equivalence the section exists to protect. That is a drafting error, not a
scientific judgment, and it must be corrected while no results exist.

## The correction

Struck: *(the 1,833-character one)*.

In its place: *(the 402-character `PROMPT` of `ediscore_verified.py` at commit
`800721f`; sha256 of its UTF-8 bytes
`e2583d5453d5710bab0e81d33eaa0c6cc4f795ed6a62a4d93f8a07526451f6e5`)*.

The rest of the sentence stands as registered. Its instruction — the prompt in
the runner before execution — is already met: the witnessed runner has carried
that prompt, byte-identical, since `fd72dc0`. Nothing is pasted now and the
runner is not edited. The clause "the record says augmented prompts underperform
it" is left as registered; this amendment does not examine it, and it bears on
no prediction, threshold or parameter.

## What this amendment is not

It does not touch the engine, the prompt in the runner, the parameters, the task
lists, the held-out mechanic, the ship condition, any prediction, or any
threshold. Amendment 001 (sha256
`bd87b67f2cbf7afa245fb9156660316c87403857c97c81f413c792bb61748ab4`) stands
unchanged and independent of this one. It resolves the contradiction in the
direction that §3's own heading and the already-witnessed runner point, leaving
every witnessed byte as it is. No result exists to inform either reading.

## The limit, stated

No byte on file records the prompt that was sent on 2026-03-22. The ledger
contains the word "prompt" zero times and carries no script hash. That the
402-character prompt produced the canonical ledger is an inference — a strong
one, resting on the script that alone writes `lane: canonical` results under
that filename, unchanged at every commit of this repository that contains it —
and not a hash inside the results file. If the architect knows the canonical run used a
different prompt, he deletes this file and the run does not fire until the
record is straight.

---

*A sentence that cannot be obeyed without breaking its own purpose is not a
stricter rule — it is a broken one. Fixed before first reading, on the record,
under its own hash.*
