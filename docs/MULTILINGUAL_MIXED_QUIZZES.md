# Small multilingual curriculum bridge and harder mixed quizzes

## Scope

This is a change to the external teacher, **not** a replacement or enlargement
of Kavi's learned network. The same parameters and optimizer continue from the
saved checkpoint. The source and lesson policy is in
[`multilingual-bridge.json`](../curriculum/multilingual-bridge.json).

The previous familiar-letter test reached 52/52, but that did not establish
unfamiliar sequence handling. Rather than falsely passing that gate, the bridge
introduces more challenging **teaching**, while keeping capability certification
separate. The old exhausted two-letter test history is retained, not cleared.

## What the teacher presents

- Exact copying of two-/three-letter sequences, expanding practice to four when
  the reserved three-letter assessment reaches 90%.
- Copied written number words (`one`, `two`, `six`, `ten`) verified against the
  admitted original De Morgan number-name table. Copying is not word meaning.
- Joining separated symbols and selecting the first or last symbol in logical
  order. These are explicitly teacher-defined operations, not author quotations.
- Small writing-system subsets: independent Devanagari vowels for a Hindi lane,
  Arabic base letters, and additional Latin written forms used in Spanish.

Each additional lane starts with four forms and expands after 90% familiar
reproduction, up to the small reviewed subset (8, 8 and 7 respectively).
These are **not complete alphabets, vocabulary or language-comprehension
courses**. Native word meanings and grammar remain pending reviewed
original-language primers and their own verifiers. English instructions and
exact character copying do not demonstrate understanding of another language.

The original [Unicode data](https://www.unicode.org/Public/17.0.0/ucd/UnicodeData.txt)
supplies character identities; the [Unicode FAQ](https://www.unicode.org/faq/basic_q.html)
explains that scripts and languages are not the same thing. Preserve exact code
points and logical order, including Arabic. The selected Spanish forms include
accented vowels, not seven additional alphabet letters. This narrow exercise
does not implement universal grapheme segmentation or text rendering.

## Three different checks

| Check | What appears live | What its score means |
| --- | --- | --- |
| Familiar practice and retention | Brief scores, with new-script practice answers visible | Reproduction/retention of taught items, not new-question generalization |
| Fresh mixed quiz | New complete prompts every quiz, with actual answers and corrections | Current performance on copy/join/first/last tasks at the stated difficulty |
| Reserved assessment | Brief repeated three-/four-letter scores; full cases in local grading logs | Comparable performance over time on a fixed bank excluded from automatic teaching |

The main quiz contains 32 questions, balanced across the four operations.
Lengths start at three symbols. The ceiling rises one step, up to six, only
when every operation reaches 90%. Newly taught script forms can be mixed with
Latin letters. Full prompt fingerprints are excluded after use; reused
practice is not relabeled a fresh quiz. Difficulty and per-operation accuracy
are recorded so unlike tests are not treated as the same score.

Quizzes are graded without parameter changes and without giving expected
answers to model inference. Their mistakes become labeled familiar teaching
examples in the next cycle. The model, not a string-operation helper, generates
the answer. Exact string operations exist only in the independent teacher/grader.

Two fixed banks (64 three-letter and 64 four-letter cases) are reserved before
automatic bridge teaching. Their sequences are excluded across *all* automatic
operation families, including different question formats. They are intentionally
repeated for longitudinal validation, clearly labeled as such, and never used
as automatic corrections. Owner interaction with a reserved copy question
invalidates its assessment use. These are not a guarantee against every possible
form of incidental exposure in unrestricted future interaction.

To certify the English sequence stage, both reserved scores must reach 90%,
then separate unused three- and four-letter confirmation tests must each reach
90%, with protected skills retained. A mixed-quiz improvement alone does not
bypass that gate. No numeric threshold is reduced because a question pool
became inconvenient or the model struggled.

## Rehearsal, regression and rollback

New lessons mix in the 52 familiar Latin letters and every previously correct
character from all active script lanes. Each candidate is tested against
protected earlier answers. On a regression, the teacher rehearses those earlier
forms together with the new forms, re-evaluates, and restores the pre-cycle
model/optimizer if retention still fails.

The initial live extension exposed cross-script forgetting: a new script could
be reproduced correctly while older script answers regressed. Those candidates
were rolled back. The subsequent rehearsal correction includes all previously
learned scripts in each cycle, rather than rehearsing only Latin and the current
script. The retention threshold stays unchanged.

An accepted candidate means its **finite protected checks** passed. It does not
mean every capability improved, every untested fact was retained, or scores
must rise monotonically. Update counts can decrease after a rollback; that is
restoration of an earlier model, not evidence of undetected progress.

Partial candidates are not published as accepted periodic checkpoints. Clean
interruption restores the pre-cycle witness before saving. Event logs preserve
the failed attempt outside the active core.

## Running and inspecting

```powershell
.\scripts\start-live-learning.ps1 -Resume 'runs\previous-run' -MultilingualBridge
```

Use only after owner authorization to switch a running teacher. The
`Kavi MULTILINGUAL` tabs show lessons, answers, learned link parameters,
updates, grades and Chat/Controls. The previous run and checkpoints are kept.
Only one live wave teacher holds the process lock. No unrelated application
is closed, no startup persistence is installed and no hardware safety limit is
changed. CPU threads remain two; batches remain at most four.

The launcher's explicit session budget is at most 24 hours. Failed teaching
cycles continue within that budget; pause and stop remain owner-controlled.
The source policy still uses exact reviewed URLs and fingerprints, not an
unrestricted crawler or downloaded translated material.

For an offline, read-only checkpoint comparison:

```powershell
python scripts/compare-language-checkpoints.py --older runs/older --current runs/current --output runs/comparison.json
```

It evaluates independent copies on identical questions, checks that inference
does not change parameters, and leaves the active learner untouched. Its
freshness claim is relative to the two durable checkpoints' recorded exposure
hashes, not to unrecorded external history. The report and raw answers remain
private. See the [measured rollout record](../experiments/2026-09-04-multilingual-bridge.md).
