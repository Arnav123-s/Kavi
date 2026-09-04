# Kavi's learner, teacher, and experiment manager

Author: Arnav123-s

Status: implemented for the bounded foundation circuit; language development remains unfinished.

## In simple words

Kavi is a small network of reusable paths. A question enters the network,
travels through compatible paths, and produces an answer. Learning changes
the shapes and connections of those paths. An older skill can contribute to a
new task without making a separate model for that task.

The teacher sits outside this network. It chooses a lesson, checks an answer,
identifies a mistake, and presents different examples. The examiner checks
new questions without changing the learner. An experiment manager tries a
few candidate updates and chooses a passing one. These helpers do not become
part of the model that answers questions.

```text
Original source -> teacher -> candidate pathway changes
                                  |
                          experiment manager
                                  |
                    current mistakes + older-skill checks
                                  |
                    choose an improved, retaining candidate
                                  |
                     replace active model; archive parent
                                  |
                         harder new-question exam
                                  |
                       advance or diagnose and repeat
```

## What actually learns today

The first categorical paths learn running-average feature centers and
connection strengths. Arithmetic receives verified transform weights from
the teacher. Composition receives explicit operator-to-target contracts.
Equality and selection are supplied software operations. The tree structure
of each test question is also supplied. Kavi does not discover these
algorithms, parse natural language into programs, or understand the source's
explanation as prose.

The correction loop changes the actual active model parameters. It does not
replace the model's answer with the teacher's lookup result. The Unicode
reference is available only to the teacher. Normal inference has no source
table lookup, archived-parent lookup, or external model call.

In the measured development run, the unchanged foundation circuit answered
62/64 wider composition questions correctly. The two errors came from
classifying the Han character 語 as Hangul. The original Unicode 17 script
reference identifies its range as Han. The teacher selected different
characters, 誟 and 誝, for correction. Updating one existing Han path corrected
the diagnosed error while preserving earlier checks. A fresh 64-question
test with larger integers and deeper arithmetic paths then scored 64/64.
This is a small composition result, not a language or intelligence benchmark.

## The teaching policy

[teaching-policy.json](../curriculum/teaching-policy.json) records the requested
developmental order:

1. Symbols and numbers.
2. Language-specific words and meanings alongside addition and subtraction.
3. Sentences alongside multiplication and division.
4. Fractions, grammar, and reading.
5. Algebra and introductory sciences.
6. Logic, literature, history, and philosophy.
7. Advanced mathematics and sciences.
8. Original research and independent verification.

The language lanes come from
[multilingual-foundations.json](../curriculum/multilingual-foundations.json).
They are expandable and retain historical language distinctions. Character
systems without an alphabet need their own appropriate foundation lessons.
Passing a script test does not pass every language that uses that script.

The author catalog includes original works associated with Pāṇini,
Tolkāppiyar, Sejong and his scholars, Āryabhaṭa, Brahmagupta, al-Khwārizmī,
Euclid, Ibn al-Haytham, Shen Kuo, Newton, Curie, and others. These are catalog
entries, not a completed training corpus. Selection uses source quality,
clarity, prerequisites, and reliable assessment; there is no objective
historical intelligence ranking.

Only the six small foundation stages currently have executable handlers.
Word meaning, sentence formation, multiplication/division learning, and
broad textbook reading are missing model capabilities. Listing them in a
policy does not implement them. The controller reports this boundary and
ends instead of counting repeated foundation drills as progress on reading.

## Tests, corrections, and candidate selection

The original 6 protected and 7 held-out composition cases participate in
promotion, so they are validation cases. A separate 64-question audit is run
after the six contracts are installed. Its original exact-pass threshold is
preserved. In automatic teaching mode, mistakes from that audit become
feedback and therefore it is no longer an untouched final test.

After correction, the teacher generates a fresh 64-question harder test.
It changes the seed, increases integer magnitudes, and increases the maximum
depth of one arithmetic branch. Whole questions are checked against previous
tests to prevent accidental reuse. The question family and supplied operators
remain the same; this is not transfer to an unrelated domain.

The new mastery rule is:

```text
harder_test_accuracy >= 0.90
AND every earlier fixed foundation check still passes
AND the original exact composition audit is repaired
```

The teacher diagnoses incorrect script calls using the fingerprinted original
Unicode reference. It excludes all previously shown test characters and
foundation teaching/test characters when choosing alternative examples.
Candidate updates use 1, 2, or 4 of these different examples. Every candidate
starts from the same active parent. The experiment manager ranks eligible
candidates by:

```text
(newly allocated routes/adapters, remaining mistakes, state bytes, changed objects)
```

Eligibility requires fewer diagnosed errors, complete earlier-skill retention,
no newly wrong previously correct composition question, and saved model state
below the policy's size ceiling. Rejected candidates never replace the parent.
Only the winner is promoted; the parent is archived outside inference.

The current categorical update remains:

```text
mu_new = mu_old + (example_features - mu_old) / (support + 1)
```

The search first prefers passing reconfigurations that allocate no new routes or adapters. See [CONFIGURATION_FIRST_MODEL.md](CONFIGURATION_FIRST_MODEL.md) for the clarified stable-network objective. The search is outside the model and could accept proposals from other learning
methods later. Current code uses bounded candidate search; it does not invent
source code, discover new architectures, or install dependencies by itself.
Correction is currently implemented for script mistakes only. Other failures
are reported as requiring a new learning method.

## Live operation

With the reviewed private sources present:

```powershell
.\scripts\start-live-pathways.ps1 -AutoTeach -IntervalMs 350 -StartDelaySeconds 10
```

Seven tabs show the controller, teacher explanations, actual answers,
pathway execution, candidate changes, test grades, and controls. The normal
view uses plain words. To inspect route IDs and numeric details, use:

```powershell
python -m kavi.pathway_cli watch --run-dir runs\YOUR-RUN --channel pathways --technical
```

Pause, resume, and stop operate on the selected run only. The teacher runs as
an ordinary local process without the assistant or an external model. This
command creates no scheduled background service and does not change device
power or temperature limits. All computation is currently serial CPU work.
The displayed groups of up to four paths are trace groupings, not a measured
four-worker speedup or GPU parallelism.

The default loop permits six repair rounds and at most three candidate trials
per round. Unsupported capabilities produce a visible boundary. The 1 MiB
candidate-state ceiling covers compact serialized model data only; it is not
a cap on process memory, source tables, Python objects, traces, or archives.
Those external costs must be counted in any future efficiency comparison.

The active checkpoint, every parent archive, JSONL feeds, status, and
`teaching-report.json` stay in the ignored run directory. Earlier failed
scores remain in the record even if later correction succeeds.

## Educational source selection

The source lesson gate now requires both admitted provenance and an explicit
educational purpose from an original authored work or original technical
reference. See [source-selection-policy.json](../curriculum/source-selection-policy.json).
Poetry and stories are excluded as filler; respected literature may be used
for a specific assessed skill or idea. The already recorded generated
foundation experiment is not relabeled as an original-text curriculum.

## Original reference used for correction

- [Unicode 17.0.0 Scripts.txt](https://www.unicode.org/Public/17.0.0/ucd/Scripts.txt): exact script-property data from its maintainer.
- [Unicode Script Property specification](https://www.unicode.org/reports/tr24/): script properties are distinct from language understanding.
- [Unicode License V3](https://www.unicode.org/license.txt): source terms; the downloaded license remains beside the private source.

Expected SHA-256 for the admitted script file:
`9f5e50d3abaee7d6ce09480f325c706f485ae3240912527e651954d2d6b035bf`.
