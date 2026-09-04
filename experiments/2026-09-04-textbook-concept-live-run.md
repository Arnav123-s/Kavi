# Reviewed textbook-concept live run

Date: 2026-09-04

Source commit: `1216f226cad67d197d509bafbd866c1e04826560`

## Hypothesis

A small, reviewed symbolic lesson can create compact, auditable
expression-versus-relation prototypes without keeping a source-text archive.
Promotion should occur only when fixed current, protected, and held-out checks
do not regress.

## Provenance and separation

- Source record: `basic-algebra-with-applications-6e`, *Basic Algebra with
  Applications*, 6th edition, Ivan G. Zaigralin; CC BY-SA 4.0 is recorded in
  `curriculum/source-manifest.json`.
- The reviewed PDF, its selected local extract, and the event manifest remained
  under ignored `private/` paths. No source body, raw event manifest, PDF,
  fingerprint value, checkpoint, or terminal log is committed here.
- The private manifest supplied six training events, four protected events, and
  four held-out events. The test partitions were fixed before the run.

## Configuration

```text
Interpreter: Python 3.13.5
Command: python -u -m kavi.school_cli --max-stages 1 --interval-ms 750 --state-file runs\kavi-school-state.json
Checkpoint before run: four generated prerequisite stages complete
Textbook batch size: 2 verified events (runtime default)
Persistent model estimate: 13 scalars
Active pipes: 4
Estimated transient model state: 64 bytes
```

The process did not fetch a source, access the network, write learned weights,
change hardware settings, schedule background work, or bypass pause/stop
controls.

## Promotion rule

For each two-event candidate, support had to increase while current, protected,
and held-out error did not worsen. The parent stayed frozen until the gate
accepted the candidate.

## Observed result

The first two training events abstained because both compact prototypes lacked
verified support. Their candidate passed the gate. The next four events produced
the bounded concept label and an independent exact result where the restricted
evaluator could determine one.

| Measure | Result |
| --- | ---: |
| Training events processed | 6 |
| Candidate promotions | 3 |
| Protected exact accuracy | 1.00 |
| Held-out exact accuracy | 1.00 |
| Stage outcome | passed |
| Process stop flag | false |
| Observed command wall time | 5.07 s |

After the stage passed, the school stopped at the declared word-form and
definition gate because Kavi has no text representation or language-specific
evaluator.

## Limitations and decision

This result tests one tiny structural distinction under a fixed manifest. It is
not evidence of textbook comprehension, language skill, general algebra,
continuous learning, dynamically growing pathways, or broad intelligence.
No host-wide memory, GPU, temperature, or energy measurement was collected;
the resource numbers above are model-state estimates only.

Decision: retain the bounded stage and its public documentation. Keep the next
language stage locked until it has its own representation, source review,
verifier, and held-out tests.
