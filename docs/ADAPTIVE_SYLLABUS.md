# Adaptive syllabus loop

Author: Arnav123-s

## What it automates

`python -m kavi.adaptive_cli` is the visible, finite teaching loop for the
current textbook-concept core. It automates the repeatable work around a model:

```text
approved local lesson
  -> randomized verified teaching order
  -> candidate-only compact update
  -> randomized protected questions
  -> randomized held-out questions
  -> 90% / 90% gate
  -> next declared unit, or approved repair lesson
```

It does not automate uncontrolled web browsing, source downloading, arbitrary
textbook ingestion, code changes, hardware settings, hidden background work,
or removal of the owner pause/stop controls.

## What “random questions” means here

Each local lesson has separately declared training, protected, and held-out
question banks. The adaptive runner selects a reproducible random order using
a recorded seed and samples without replacement from the selected test bank.
It does not generate questions, alter a held-out answer, or turn a failed
held-out question into training data.

This matters: a failed test should reveal a gap, not silently become an answer
key. The next teaching attempt can use only a separately reviewed repair lesson
listed in the private syllabus.

## The 90% promotion rule

For each unit, both independently scored partitions must meet the configured
threshold:

```text
protected exact accuracy >= 0.90
held-out exact accuracy  >= 0.90
```

The default private syllabus applies the same threshold to the current algebra
symbol unit. A candidate update must also improve support without worsening
current, protected, or held-out error before the model is allowed to retain it.

## Failure, diagnosis, and repair

The live terminal prints every test as `PASS` or `FAIL`. A failure includes:

- the independently verified expected concept;
- the model’s label or abstention;
- the evaluator’s bounded value/truth result where available;
- confidence and a concrete abstention or route-difference reason.

The test target is displayed for diagnosis but is not trained on. If either
test partition is under 90%, the loop selects the next declared local repair
lesson. The repair lesson must pass the same source-license, PDF, extract hash,
concept, and verifier checks as the primary lesson.

If no repair lesson is declared, or the finite attempt budget ends, Kavi stops
with `needs-reviewed-repair-lesson` or `not-mastered`. It never substitutes a
random dataset, invents a book, or claims the unit passed.

## Local state and persistence

An optional adaptive checkpoint contains only unit IDs, attempt counts, two
five-number prototype centers, support counts, and a promotion count. It
contains no textbook body, question strings, document extract, PDF, or growing
example archive. The checkpoint is written only when `--state-file` is given.

## Run it in a terminal

The current local-only syllabus is already prepared on this device:

```powershell
python -u -m kavi.adaptive_cli --syllabus private\syllabi\adaptive-textbook-syllabus.json --state-file runs\kavi-adaptive-state.json --interval-ms 500
```

Use `--wait-for-enter` to open the CLI before teaching starts. Use `--interval-ms 0` for the fastest finite pass. Omit `--state-file` to run a
fresh visible demonstration without saving compact state. Use `--seed N` to
reproduce or vary question order. `--pause-file` and `--stop-file` work like
the other Kavi runtimes.

The present syllabus has one approved algebra unit. It will master that unit
and stop because no next text-capable unit or reviewed repair lesson has been
declared. Adding another book means creating and reviewing a specific local
lesson first; it is not something the current tiny model can safely decide on
its own.

## Current scope

This is adaptive orchestration around a very small expression/relation model,
not an agent that understands arbitrary explanations or whole books. The model
can use a verified symbolic label and compact features; it cannot yet explain
prose, judge a novel textbook, or choose a correct repair source by itself.
