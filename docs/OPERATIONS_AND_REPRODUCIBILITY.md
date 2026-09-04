# Kavi operations and reproducibility

Author: Arnav123-s
Status: operating guide for the finite local prototypes

## What this guide runs

These commands run small generated arithmetic, ASCII-glyph, and Unicode-scalar
experiments, plus one optional locally reviewed textbook-concept lesson. They
do not download a model, use a network, install dependencies, begin a
background job, or start a general training program. Their main purpose is to
show the complete route and update decision in a low-overhead terminal trace.

## Requirements

- Python 3.11 or later.
- A checkout of this repository.
- No third-party runtime packages are required for the current prototype.
- The optional textbook stage additionally needs its separately reviewed local PDF, extract, and lesson manifest under ignored `private/` paths; the public checkout deliberately does not supply them.

The reference smoke tests for this release were run with Python 3.13.5. Record
the exact interpreter version for any new result because a different runtime
can change elapsed-time measurements.

## Verify a clean checkout

From the repository root, normally C:\Kavi:

    python --version
    python -m unittest discover -s tests -v
    python -m kavi.source_cli

The test command should discover the stage-0, explanation-learning, generated
Unicode, source-manifest, and bounded textbook-core tests. The source command only validates and prints
metadata; it does not fetch the linked documents.

## Inspect the model-shaped pathways

    python -u -m kavi paths

This prints the fixed pipe contracts for the current experiment. It is a useful
first check because a route that violates its declared input, output, or scope
contract should not be considered a valid reasoning path.

## Run the target-only experiment

    python -u -m kavi live --steps 24 --seed 7 --ask 7 5 add

Important options:

| Option | Meaning |
| --- | --- |
| --steps N | Run exactly at most N generated events. N must be positive. |
| --seed N | Make the generated curriculum reproducible. |
| --max-active-routes N | Bound active path fan-out. Two facets need at least two routes. |
| --workers 1 or 2 | Use at most two workers for independent evaluation only. |
| --conflict-every N | Insert an incompatible phase-style case every N events; zero disables it. |
| --interval-ms N | Delay visible event lines; zero minimizes waiting. |
| --ask LEFT RIGHT add-or-subtract | Ask one query after the finite run. |

The trace labels a number as initially correct only when it was correct before
the event’s feedback. Candidate promotions are separate and should not be read
as evidence of broad generalization.

## Run the explanation-learning experiment

    python -u -m kavi.lesson_cli --steps 24 --seed 7 --ask 9 4 subtract

Each lesson is a locally verified arithmetic rule. The output includes the
verified explanation after the normal pathway and candidate trace. It is still
a finite local run.

## Inspect or continue the source-free curriculum

This does not start a run:

    python -m kavi.school_cli --list

The list shows which stages are runnable and which remain blocked. The Unicode
contract and generated script-pathway stages contain only declared individual
scalars; they do not access the catalog or source URLs.

Only after the owner explicitly authorizes a finite continuation from an
existing local checkpoint containing the bootstrap stages, run at most the two
Unicode stages with:

    python -u -m kavi.school_cli --max-stages 2 --lessons-per-stage 24 --symbol-batch-size 11 --interval-ms 80 --state-file runs\kavi-school-state.json

The trace prints the scalar, code point, hard path, candidate gate, protected
and held-out metrics, and compact model ledger. It then stops at the still
locked word-learning stage. See [UNICODE_SCRIPT_STAGE.md](UNICODE_SCRIPT_STAGE.md)
for the scope of that small experiment.

## Run the reviewed textbook-concept stage

This stage is intentionally unavailable from a bare public checkout. After the
four generated foundations are present in the selected local checkpoint, and
only when the ignored local lesson, source PDF, and extract fingerprints match,
run one declared stage visibly:

    python -u -m kavi.school_cli --max-stages 1 --interval-ms 750 --state-file runs\kavi-school-state.json

The trace shows each local notation event, fixed pipe sequence, structural
facets, response or abstention, candidate gate, resource estimate, and
protected/held-out readouts. It never fetches a textbook. A missing lesson or
mismatched hash produces a visible refusal rather than a substitute dataset or
silent retry. See [TEXTBOOK_CONCEPT_STAGE.md](TEXTBOOK_CONCEPT_STAGE.md) for
its exact scope.

## Pause and stop controls

Use explicit, user-controlled files when a longer finite trace is desired:

    python -u -m kavi live --steps 100 --pause-file C:\Kavi\PAUSE --stop-file C:\Kavi\STOP

- Create the PAUSE file to pause at a control check.
- Delete only the PAUSE file to resume.
- Create the STOP file to end at the next control check.
- The runtime never creates, deletes, or modifies either control file.
- A stopped run does not save training state; its parent exists only in the
  process memory until that process exits.

Use a separate terminal to create or remove a control file. Do not force-kill a
process if the stop control can be used safely.

## Resource interpretation

The visible ledger reports a model-level estimate: persistent scalar count,
active pipe count, and an estimated transient-byte figure for the small
prototype. It is not a measurement of all memory used by Python, the operating
system, other applications, graphics hardware, or a device’s temperature.

Kavi chooses serial pathway microsteps by default. The optional second worker
is limited to independent evaluator cases, so device load can be compared
explicitly. The program does not alter fans, power profiles, thermal cutoffs,
or any hardware safety setting. Keep normal operating-system protections
enabled.

## Reproducible experiment record

Before considering any experiment a result, create a compact record in
experiments using the requirements in [experiments/README.md](../experiments/README.md).
At minimum include the source commit, interpreter version, command, seed,
resource configuration, fixed manifests, elapsed time, observed outputs,
failures, and decision. Never publish credentials, personal data, raw private
inputs, unreviewed documents, or large binary artifacts.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Import error for kavi | Run commands from the repository root, or install the package in an isolated environment if deliberately needed. |
| Runtime stays paused | Check whether the supplied pause-file path still exists. |
| Runtime ends early | Check whether the supplied stop-file path exists. |
| A candidate is rejected | Read protected and held-out metrics; rejection preserves the frozen parent by design. |
| Source is not admitted | Inspect curriculum/source-manifest.json and complete document-specific rights review outside the public repository. |
| Textbook lesson is rejected | Check the approved source ID plus the local PDF and extract SHA-256 fingerprints; do not bypass the gate or substitute a generated corpus. |

For the exact implementation boundary, see
[IMPLEMENTATION_REFERENCE.md](IMPLEMENTATION_REFERENCE.md).
