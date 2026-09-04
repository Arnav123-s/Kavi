# Developmental teaching and typed composition: live run

Author: Arnav123-s

## Reproduction

- Source commit: `c6776ee6052d5f4d9406500f33ec69ac5e453193`.
- Command: `scripts/start-live-pathways.ps1 -AutoTeach -IntervalMs 350 -StartDelaySeconds 10 -MaxParallelPaths 4`.
- Local run: `runs/pathway-live-20260904-123010` (ignored).
- Started: 2026-09-04 12:30:10.598, America/Los_Angeles.
- Finished: 2026-09-04 12:31:46.890, America/Los_Angeles.
- Approximate wall time: 96.29 seconds, including the 10-second startup delay,
  intentional display pacing, file writes, and concurrent viewer activity.
- Sources: the already reviewed local algebra lesson and Unicode 17.0.0
  `Scripts.txt`, fingerprint
  `9f5e50d3abaee7d6ce09480f325c706f485ae3240912527e651954d2d6b035bf`.

This run reproduced the first five foundation stages from an empty active
state, added six supplied composition contracts, and ran the new corrective
teacher. It did not resume the previous run's checkpoint.

## Results and failure history

The earlier glyph, arithmetic, exact Unicode, script, and notation checks
passed. The composition promotion validation passed its 6 protected and 7
held-out cases. Both sets influence promotion and therefore are validation,
not untouched final testing.

The wider 64-program audit scored **62/64 (96.875%)**. It failed the original
100% audit gate. Two wrong composite answers came from one cause: the Han
character 語 was classified as Hangul by the small coordinate prototype.
The incorrect branch choices produced 94 instead of -26 and 46 instead of 88.
These failures remain in the grading log.

The external teacher checked the original Unicode script reference and chose
different nearby characters. It compared three isolated candidate updates:

| Candidate | Remaining diagnosed character errors | Earlier checks retained | Eligible |
| --- | ---: | --- | --- |
| One different example | 1 | Yes | No |
| Two different examples | 0 | Yes | Yes |
| Four different examples | 0 | Yes | Yes |

The selected candidate used two examples, 誟 and 誝. The experiment manager
selected it using error, saved-state size, changed-object count, and the
deterministic proposal identifier tie break. Later configuration-first
ranking refinements are separately committed and do not change this recorded
selection among candidates that all allocate zero new objects.

After correction, the original 64-case audit scored 64/64. Because its
mistakes had informed the teacher, this retest is a correction check.

The subsequent harder test used seed **20260905**, larger integer magnitudes,
deeper arithmetic subtrees, and **64 previously unused whole questions**.
It scored **64/64 (100%)**, above the requested 90% mastery threshold. Model
state remained unchanged during testing. All earlier fixed checks remained
correct. This is transfer within the same tiny supplied program language.

## Actual model changes

| Quantity | Before correction | After correction |
| --- | ---: | ---: |
| Active routes | 23 | 23 |
| Jump adapters | 61 | 61 |
| Han route support | 3 | 5 |
| Han coordinate center | 0.017967389844159753 | 0.023520995663807286 |
| Han coupling | 0.6800000000000002 | 0.8000000000000003 |
| Han resistance | 0.7290000000000001 | 0.5904900000000002 |

The Han route's configuration and existing adapter support changed. It did
not allocate a new path or adapter. The phase stayed zero; this result is not
evidence that quantum-inspired interference improved learning.

There were 30 promotions and 30 frozen parent archives across the full run.
The correction parent is in `archive/parent-0030.json`. Archived states are
not used for inference.

## Resource observations

- Numeric model payload estimate: 2,864 bytes.
- Formatted active-state JSON: 30,819 bytes.
- The experiment manager's compact JSON size measure was 23,551 bytes for
  each corrective candidate; this is a different serialization format.
- Parent archive files: 383,122 bytes in total.
- All run files, including verbose live traces: 2,891,949 bytes.
- During stage 4, the controller's observed peak working set was 26,230,784
  bytes. Five viewer processes each used approximately 23.8-24.0 MB.

The process snapshot is not a complete end-to-end peak-memory measurement.
It excludes the terminal application's memory, PowerShell shells, OS caching,
and later possible peaks. The source reference is teacher-side state and is
not included in the tiny numeric model payload. These observations do not
establish a speed or memory advantage over other learning architectures.

The run used serial CPU computation. Groups of four paths in the trace are
logical display groups, not measured parallel workers or GPU execution.

## Visible behavior and stopping point

Seven terminal tabs displayed the controller, teacher, answers, pathways,
changes, grades, and controls. The viewers exited normally after completion;
the shells and their output remained open. The previous six completed Kavi
shells were closed, with their run files preserved.

The run ended after the six implemented stages. Word meaning, sentence
formation, multiplication/division learning, and original-language textbook
understanding remain unimplemented. No language catalog entry was marked
learned simply because its script appeared in the foundation checks.

The prototype still receives engineered features, arithmetic transform
weights, typed operator targets, equality/selection operations, and structured
test trees from software. It has not demonstrated autonomous algorithm
discovery, general architectural rewiring, all-language learning, arbitrary
lossless compression, or broad intelligence.

## Verification

The implementation commit passed 63 tests. Follow-up source-selection and
configuration-priority checks bring the current suite to 65 tests. The suite
explicitly preserves the baseline 62/64 failure and requires the external
teacher to correct it, retain earlier checks, and pass the fresh harder test.
Raw sources, local lesson bodies, checkpoints, and runtime logs are excluded
from the public repository.
