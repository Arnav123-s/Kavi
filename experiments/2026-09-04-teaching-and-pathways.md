# Teaching order and pathway plasticity

Author: Arnav123-s. Protocol written before execution, 2026-09-04.

Status: completed bounded comparison; results appended after the sealed run.
This is not an authorized rollout into the paused live learner.

## Question

Which of six teaching recipes best improves the present byte-level circuit on
copying, joining, and selecting the first/last symbol? Does changing its route
plasticity or connectivity improve that result while retaining earlier answers?

The [previous comparison](2026-09-04-contrast-teaching.md) gave the contrasting
teacher less exposure to longer strings. This experiment matches total training
examples, optimizer updates, task frequencies, and focus-string lengths. It does
not equate unique examples or compute: repeated lessons reuse examples and the
mistake-focused teacher makes extra practice queries. These are measured.

## Frozen input and partitions

- Source revision before this experiment: `9b25373`.
- Same private input checkpoint as the previous comparison: 79,979 updates,
  SHA-256 `1bf6a57d0afa527ed498607b396c4baf78015fd6b7655231f4b8a8e858c98686`.
  This is earlier than the live pause, not an assertion about its latest state.
- Every candidate starts from identical network AND optimizer state.
- Three question partitions are generated and sealed before any trial answers:
  teacher selection, pathway selection, and final confirmation.
- Each partition: 96 three-symbol questions, 96 four-symbol questions, 64
  five-symbol transfer questions, 64 mixed-script transfer questions, 24 familiar
  two-symbol retention checks, and 75 single-symbol retention checks: 419 total.
- Copy/join/first/last are equally represented in each non-retention group.
- Non-retention test strings and their reversals must be absent from the frozen
  exposure ledger under all four task keys. All multi-symbol assessment strings
  and reversals, including those from the earlier experiment, are excluded from
  this experiment's practice. Retention single symbols are intentionally taught.
- Questions within a partition share strings across operations; they are not
  independent statistical samples. Three teaching seeds share one initial model.
- Generated, exact-graded symbol exercises are teacher-authored practice, not
  quotations from textbooks and not a test of language comprehension.

## Teaching recipes

Each of seeds 53101, 53102, and 53103 receives 360 optimizer updates, four
independent examples per update: 1,440 presentations. Every fifth update uses
the same seeded rehearsal schedule (288 presentations). The remaining 1,152
presentations have equal copy/join/first/last counts and equal length-2/3/4
counts. There is no development gate that changes the length budget.

| Recipe | Change to practice |
| --- | --- |
| Mixed | Independent examples shuffled within 24-example groups. |
| Blocked | Exactly the mixed recipe's example multiset, sorted into operation blocks across the trial; common review still interrupts each fifth update. |
| Reversal | Four commands on one string and its reverse at each practiced length. |
| Boundary | Length-2/3/4 prefix chains and their reversals: appending preserves first; prepending preserves last. |
| Spaced | Every fourth group revisits a group from three groups earlier. |
| Mistakes | Query up to two practice candidates of the same operation and length, choose a wrong answer when found, then teach the verified answer. |

Common rehearsal covers known single symbols plus two- and three-symbol copying.
Mixed-script operations and length-five operations are transfer tests, not focus
training. Extra queries, unique training questions, bytes, and elapsed times are
reported; mistake selection does not receive free compute in the interpretation.

## Route variants

After teacher selection is sealed, test its chosen recipe with four variants,
using the same seeds and starting checkpoint. Reuse its already-trained standard
candidates instead of training duplicates. There are 27 trained candidates in
total: 18 teacher candidates and nine additional pathway candidates.

| Variant | Exact intervention |
| --- | --- |
| Standard | Original Adam answer-learning update. |
| Damped routes | After each Adam step, retain 25% of the proposed displacement of edge logits, phases, conductances, and activity gains. All other parameters use the ordinary update. Adam moments are still updated normally. |
| Rewire | At update 180, change the weakest base-strength incoming source of every node to its nearest unused source. Reset those parameter slots' optimizer moments. No parameter growth. |
| Split growth | At update 180, duplicate the weakest incoming route per node; subtract log(2) from the old and duplicate route logits; copy their source, conductance, activity gain, and phase. Then perturb each new phase by alternating +/-0.015 radians. |

Without phase perturbation, the split preserves the forward map in exact
arithmetic; a unit test checks numerical agreement. Perturbation and subsequent
optimization remove that equivalence. This is not a proof against forgetting.
Weakness is measured from base gates, not average input-conditioned traffic.

The initial network has 64 nodes, 256 route slots, and 66,880 parameters. Split
growth keeps 64 nodes and allocates 320 route slots and 67,136 parameters: 256
additional float32 parameters (1,024 bytes), plus optimizer state and buffers.
New slots duplicate sources, not destinations. Allocating slots does not prove
that the model uses them profitably. Rewiring changes 64 sources, not 64 nodes.
These are scheduled trial interventions, not autonomous self-redesign.

## Selection and confirmation

1. Rank teachers on their selection partition. Prefer methods with zero lost
   baseline-correct retention answers in every seed. Next prefer fewer mean
   retention losses, then higher mean pooled primary length-3/4 accuracy. Ties
   use the recipe name. If all methods regress, the choice is exploratory only.
2. Seal the teacher choice before training/ranking the four route variants on
   the separate pathway partition, using the same retention-first rule.
3. Seal the finalist list before generating any final-confirmation answers:
   mixed/standard, the two leading teachers/standard, and the selected teacher
   with the selected route variant. Deduplicate combinations.
4. Evaluate these saved models on confirmation without further teaching, plus
   the original frozen checkpoint. Report all finalists, not just a favorable
   result. Confirmation is not reused to adjust this experiment.

Repeated 16-question selection probes at 120, 240, and 360 updates are progress
indicators, not fresh final tests. They do not change lessons or stopping rules.
Expected answers are withheld from model inference and evaluation cannot update
weights. Retention is a finite test of formerly correct answers, not universal
protection. A pooled score is not a 90%-per-skill advancement gate.

## Device budget and control

Candidates run serially, on one numerical CPU thread, with a 10 ms rest after
each optimizer update. Four-example updates can be computed as 4, 2+2, or
1+1+1+1 rows; gradients accumulate before one optimizer step. A test checks
equivalence within float32 rounding. This changes execution, not model size.

Use four rows only with at least 6 GiB available RAM and working set below
640 MiB; two with at least 4 GiB available RAM and working set below 768 MiB;
otherwise one. Unknown telemetry falls back to one row. Stop on available RAM
below 2 GiB, working set above 1 GiB, free disk below 2 GiB, or 1,800 seconds.
Check resource readings at most two seconds apart between bounded operations.
CPU temperature is unavailable: these controls do not guarantee temperature or
absence of thermal stress. Hardware protection limits remain untouched.

Live training must remain paused. An experiment-local `stop.request`, removal
of the live pause marker, or interruption stops the experiment without changing
the live learner. No background service, model replacement, or curriculum
advancement is part of this experiment.

## Reproduce

With the original private frozen artifacts present, run from the repository:

```powershell
python -m unittest discover -s tests -v
python -u scripts/run-strategy-trials.py --frozen-experiment runs/contrast-comparison-20260904 --live-run runs/learning-live-20260904-143553 --output runs/teaching-and-pathway-trials-20260904 --steps 360 --seeds 53101 53102 53103 --max-seconds 1800
```

Use a new output directory for a repeat. Private manifests seal source hashes,
question partitions, budgets, checkpoints, and per-question results. None of
those runtime artifacts are published here. Without the historical checkpoint,
the unit tests and algorithm are reproducible but the exact measured experiment
is not reproducible from the public repository alone.

## Research influences, not claimed reproductions

- [Net2Net, Chen, Goodfellow, and Shlens](https://arxiv.org/html/1511.05641v4):
  preserve a function while expanding its parameterization, then break symmetry.
  Here a softmax-normalized route is split, not a full Net2Wider network.
- [Dynamic Sparse Reparameterization, Mostafa and Wang](https://proceedings.mlr.press/v97/mostafa19a.html):
  reconsider connectivity under a fixed budget. The single weakest-base-route
  change here is a small heuristic, not that paper's complete algorithm.
- [Prioritized Experience Replay, Schaul and colleagues](https://arxiv.org/abs/1511.05952):
  allocate some practice to errors. This teacher uses exact symbol-answer
  mistakes, not temporal-difference errors or the published RL replay method.
- [A Trainable Spaced Repetition Model for Language Learning, Settles and Meeder](https://aclanthology.org/P16-1174/):
  review scheduling as a learning variable. This experiment uses a fixed lag,
  not a fitted half-life model or claims about a human memory curve.
- [Generalization without Systematicity, Lake and Baroni](https://arxiv.org/abs/1711.00350):
  assess new compositions and lengths separately from practiced examples. The
  tasks here are much narrower than the paper's sequence-learning benchmark.

## Measured results

All 27 trained candidates completed; all started from the sealed input. Each
received 360 updates, giving 9,720 experimental updates in total. Source hashes
and the frozen input were unchanged. Live training remained paused, and no
candidate was installed. The full suite passed 129 tests after the additional
repair/projection unit tests were added; the first trial began after 120 tests
passed. Unit tests demonstrate implementation behavior, not task mastery.

### Teacher selection: partition A

Original checkpoint: 80/192 primary answers (41.67%). Earlier-skill retention
started at 21/24 copying pairs and 75/75 single symbols. Only the 96
baseline-correct retention answers are protected in this partition.

| Recipe | Mean primary accuracy | Primary accuracy by seed | Lost old answers by seed |
| --- | ---: | --- | --- |
| Mixed | 49.65% | 49.48%, 52.08%, 47.40% | 0, 1, 2 |
| Reversal | 48.78% | 46.35%, 47.92%, 52.08% | 3, 2, 1 |
| Mistakes | 47.40% | 44.27%, 50.00%, 47.92% | 1, 1, 1 |
| Spaced | 46.01% | 48.96%, 43.75%, 45.31% | 2, 2, 0 |
| Blocked | 45.31% | 44.27%, 47.92%, 43.75% | 3, 1, 3 |
| Boundary | 44.62% | 42.19%, 45.83%, 45.83% | 1, 2, 0 |

Mixed was selected under the prespecified retention-first rule. Mistakes ranked
second under that rule even though reversal had a higher primary mean, because
reversal lost more earlier answers. No recipe preserved all protected answers
in all three seeds; therefore this was exploratory selection, not promotion.

Mixed and blocked used identical practice-question multisets, so their
difference specifically tests order/grouping under this schedule. The other
recipes also change example relationships or repetition. Their differences
cannot be attributed to ordering alone.

### Pathway selection: partition B

Original checkpoint: 80/192 primary (41.67%), 23/24 pairs and 75/75 symbols;
98 formerly correct retention questions. The table is scored on B, not A.

| Variant with mixed teaching | Mean primary accuracy | Lost old answers by seed | Parameters |
| --- | ---: | --- | ---: |
| Standard | 45.66% | 0, 1, 3 | 66,880 |
| Damped routes | 47.40% | 1, 0, 1 | 66,880 |
| Rewire | 45.49% | 1, 1, 3 | 66,880 |
| Split growth | 45.66% | 0, 0, 2 | 67,136 |

Damping and splitting tied on mean old-answer losses; damping had the higher
primary mean and was selected. Neither preserved all old answers across seeds.
Adding 64 route slots did not increase mean primary accuracy above standard on
this partition. This rejects an automatic "more paths means smarter" inference
for this bounded test, not every possible growth rule.

### Untouched confirmation: partition C

All rows below use the same previously unopened final questions. Candidate rows
are means across three teaching seeds. Baseline is the original unchanged model.

| Candidate | Primary, length 3/4 | Length 5 | Mixed-script operations | Old-answer losses by seed |
| --- | ---: | ---: | ---: | --- |
| Original checkpoint | 37.50% | 3.13% | 43.75% | 0 by definition |
| Mixed / standard | 42.01% | 10.42% | 31.77% | 0, 0, 1 |
| Mistakes / standard | 43.23% | 10.94% | 33.33% | 2, 1, 0 |
| Mixed / damped routes | 42.36% | 9.38% | 33.85% | 1, 1, 1 |

Final primary accuracy by seed was 40.63%, 45.31%, 40.10% for mixed/standard;
41.67%, 48.44%, 39.58% for mistakes/standard; and 42.19%, 45.31%, 39.58% for
mixed/damped. Rounding of individual half-percentage values can differ by
0.01 point with tie-breaking conventions; counts in the private report are exact.

Mistake-focused teaching had the highest final primary mean, but only 1.22
percentage points above mixed practice, with more earlier-answer losses and
substantial extra query cost. Damping's gain over standard was only 0.35 point
and did not improve retention on confirmation. The selection winner is not
claimed to have been decisively confirmed. No method reached a 90% mastery
gate, and mixed-script operation accuracy regressed for every finalist.

### Diagnosis supported by the measurements

Length generalization remains a larger problem than simple alphabet retention.
For mixed/standard, final length-three accuracy was 56.94% versus baseline
60.42%, while length-four accuracy improved from 14.58% to 27.08%. Final single
symbol copying stayed 75/75 in every finalist. Better performance in one group
can coexist with worse performance in another.

In the original final bank's 24 three-symbol Last questions, 11 were correct,
10 selected the middle symbol, one selected the first, and two produced some
other wrong output. In 24 four-symbol Last questions, nine were correct, five
selected the penultimate symbol, three selected position two, and seven produced
other wrong outputs. These are actual position biases, not evidence of visual
perception or human-style thinking. The core receives bytes, not glyph images.

The retention metric protects copying pairs and single symbols only. It must
not be interpreted as protection of every previously learned operation. The
separate primary and transfer regressions make that limitation visible.

### Resources and fairness

Total wall time: 1,235.24 seconds (20 minutes 35 seconds); process CPU time:
1,127.80 seconds. Peak process working set: 520,003,584 bytes (495.9 MiB).
The private artifact inventory before the last report write was 35,534,969
bytes (about 33.9 MiB); output-directory overhead and the final write are extra.
At the final sample, about 19.5 GiB RAM was available. These are process and
sampled-memory observations, not complete device-wide energy or thermal data.

Every trial used four-row batches on one numerical CPU thread; memory headroom
never required the 2/1-row fallback. Unit tests checked fallback policy and
serial-gradient equivalence. No GPU execution or multicore model parallelism
was used. The process peak includes runtime/allocations, not only weights.
There is no measured CPU-temperature claim. Brief development unit tests and
ordinary desktop activity could affect wall timings, so no hardware speedup
claim is drawn from small timing differences.

Mixed practice averaged 29.83 seconds of optimizer-training time per trial.
The mistake-focused recipe averaged 24.03 training seconds plus 28.92 seconds
of extra practice selection, before evaluation and pacing. It made 1,884,
1,884, and 1,883 extra generation calls. Unique trained questions were
1,259/1,251/1,256 for mixed, versus 857/863/860 for mistakes and 973/966/973
for spaced review. Repetition and extra query cost are not hidden as equal data
or equal compute. A final mean difference from three seeds on one checkpoint
is not a statistically established efficiency advantage.

## Decision

Keep the live learner paused and unchanged. Mixed practice is the reasonable
control for the next experiment, not a universal best teaching method. The
next [small-repair comparison](2026-09-04-small-repair-connections.md) tests
context-dependent additions and a non-frozen retention constraint on fresh
partitions. The broader [adaptive-circuit response plan](../docs/ADAPTIVE_CIRCUIT_RESPONSE_PLAN.md)
is a separate proposal; these results do not validate its unimplemented parts.
