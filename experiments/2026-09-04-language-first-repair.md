# Repeated-answer diagnosis and language-first repair

Date: 2026-09-04. Baseline code: `05fbbdb`.

## Question and intervention

The owner reported repetitive answers and inadequate early teaching. Inspect
the actual text core, not the separately successful symbolic circuit. Test
whether question-dependent state and internal learning exist, whether the
answer/explanation objective obscures answer learning, and whether explicit
language prerequisites can produce differentiated answers.

Changes: answer-only balanced batches; a separately gated language-first
curriculum; consistent live-chat prompt format; retention checks; explicit
finite-test-pool exhaustion handling; reviewed original-source packets. Multiple
changes are applied together in the live run, so that run is not a controlled
ablation attributing improvement to one mechanism.

## Baseline and isolated probe

The previous live run failed in numeration at round 17 because its unused
question pool was exhausted. Its recovery checkpoint preserved 6,437 updates;
no arithmetic unit had passed. Checkpoint fingerprint:

`d24b67743e158c9162e6da5744aaa8aa92e68fe8c1927003e8a887a0eca0c653`.

Frozen probe outputs:

| Prompt | Output |
| --- | --- |
| What is one plus one? | `633` |
| What is two plus two? | `633` |
| Write five using decimal digits. | `122` |
| Write nine using decimal digits. | `122` |

The recurrent state RMS differences from the first question were 0.07744,
0.17163 and 0.16545. Thus these questions did not all produce identical internal
states, even though pairs produced identical answers. Learned gate sigmoid
values ranged from 0.09799 to 0.85961 (mean 0.65717). This does not rule out poor
memory, collapsed representations, or inadequate model capacity.

Two independent copies of the same checkpoint received 12 correction calls
for `one plus one`, with identical question and supplied answer:

| Condition | Probability of the correct first answer byte `2` | Greedy answer |
| --- | --- | --- |
| Before teaching | 0.09539 | `633` |
| Answer plus a long explanation | 0.26998 | `2` |
| Answer only | 0.72289 | `2` |

This isolated probe uses the old `learn` method for both conditions, not the new
balanced batch method. It measures training fit on one question, not an unseen
test, and supplies no variance or statistical generalization claim. It supports
investigating the training objective; it does not establish a complete cause.
The active model was never altered by the probe.

Reproduce with an authorized private baseline checkpoint:

```powershell
python scripts/probe-answer-learning.py runs/previous-run
```

The script reports the actual checkpoint update count, frozen answers, state
distances and both conditions. Results depend on the checkpoint supplied.

## Real language-first run

The saved 6,437-update core was continued, not replaced with pretrained weights
or an answer table. A one-round smoke run reached 6,454 updates and answered
`Copy a/b/c/d` with `c/b/c/d`: 3/4 correct, 75%. It did not pass the 90% gate.

The subsequent visible continuation progressively enlarged the familiar letter
set. A measured intermediate test produced 28/28 correct answers and 28 distinct
outputs. These were **familiar single letters**, not unseen words or English
comprehension. The complete letter stage remains gated separately by fresh
combinations and harder combinations. Further results are written by the local
run; this record does not predict them or certify completion.

The initial smoke run took 3.56 seconds inside the teacher, excluding interpreter
and numerical-runtime startup. Configuration remained 64 mixing points, 256
candidate links, two propagation hops, two numerical CPU threads and 66,880
parameters. Parameters occupied 267,520 bytes and recorded optimizer tensors
535,072 bytes. These figures exclude Python/runtime overhead, transient
activations, sources, logs and archived checkpoints. No new peak RAM or thermal
measurement was made in this experiment.

## Engineering checks and limits

`python -m unittest discover -s tests -q`: 90 tests passed after the repair.
Added checks cover internal phase/parameter updates without model growth,
prefix gradients, answer-only target accounting, independent batch states,
checkpoint continuation, exact grading, prerequisite enforcement, no answer
injection into inference, frozen grading, retention, exhausted pools, source
admission, private path boundaries and file hashes. Mock-controller tests are
explicitly not learner capability tests.

The live run is a bounded 24-hour local session with stop/pause controls and
two CPU threads. Failed rounds continue teaching within that session. Only
reviewed source URLs can be fetched; no private bodies or model checkpoints are
published. No hardware safety limit was changed. The model has not demonstrated
general English, multilingual understanding, master's-level competence,
shortest-path discovery, autonomous architecture changes or quantum advantage.
