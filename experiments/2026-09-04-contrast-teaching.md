# Paired-contrast teaching experiment

Date: 2026-09-04. Owner-approved comparison on saved learner copies.
Base project commit: `febc5423720837ba8c71869c19311a48d53fa034`.

## Question and scope

Can a short, prerequisite-based sequence of contrasting demonstrations improve
first/last selection more efficiently than independent mixed exercises?

The existing sparse recurrent model, learned parameters, optimizer state,
learning rate and answer-only learning objective are preserved at the starting
point. Only the teacher's example selection and presentation order differ.
No candidate is connected to the live teacher or automatically deployed.

This tests a teaching hypothesis, not a new architecture, unrestricted language
understanding, reduced general-intelligence resource requirements, or quantum
advantage. Printed explanations are not claimed as understood by the model.

## Prespecified comparison

The runner seals its manifest and exact question partitions before evaluating
experimental outcomes. Defaults are three teaching seeds (43011, 43012, 43013),
384 optimizer updates per arm, four examples per update, and alternating arm
order across seeds. Every arm starts from the same immutable checkpoint and
optimizer state. Teaching seeds vary examples, not pretrained models.

| Controlled property | Random-mixed arm | Contrast arm |
| --- | --- | --- |
| Operation examples | Independent three-symbol Latin strings | Same string with different commands; also reverse its order |
| Starting difficulty | Three symbols | Two symbols, unless development checks already pass |
| Progression | Fixed three-symbol control | Move to three only after both first and last reach 90% on development checks |
| Operations | Copy, join, first, last | The same counts for every operation |
| Earlier-skill rehearsal | Identical scheduled batches | Identical scheduled batches |
| Network and optimizer | Same initial values | Same initial values |

The random arm matches the current quiz *style*, not the entire live teacher.
For this controlled comparison, operation teaching uses Latin in both arms;
multiscript command transfer is held out. It does not replay the live teacher's
full source lessons, correction queue, rollbacks, or changing script lanes.
Accordingly, results cannot establish that the complete new teacher beats the
complete live workflow.

An eight-example contrast group pairs `First AB` with `Last AB`, repeats those
operations after reversing the string, and includes matched copy/join examples.
The learner receives only ordinary question and answer bytes. Exercise-generation
and grading helpers do not answer questions during model inference.

Every fifth update rehearses older characters or short copying exercises. These
batches are identical across paired arms. The same source-reviewed written
characters are reused; no additional sources are downloaded by this experiment.

## Assessments and leakage controls

- Development: 12 two-symbol strings and 12 three-symbol strings, with both
  first and last asked for each. Repeated measurements are labeled development,
  not fresh final examinations. Two-symbol calibration allows familiar strings
  because the old copying pool was exhausted.
- Primary final test: 32 new three-symbol strings, both positional commands;
  report first and last separately as well as combined accuracy.
- Length transfer: 32 new four-symbol strings, both commands. Neither arm
  teaches four-symbol operation examples during the experiment.
- Script transfer: 16 new mixed-script strings, both commands, when the frozen
  learner has previously correct additional-script characters.
- Copy/join transfer: 16 new three-symbol strings, both operations.
- Retention: 24 two-symbol copy questions plus the original Latin characters
  and previously correct additional-script characters. Count every loss of an
  answer that was correct at the initial checkpoint.

Every underlying development and non-retention final string, each protected
copy pair, and their reverses are excluded across all four operation families
in experimental teaching. Single-character retention deliberately rechecks
familiar rehearsed characters. For non-retention final
strings, all four question keys and reverse-string keys are checked against the
frozen prior-exposure ledger. The final labels never enter learning or lesson
selection. Final assessment generates actual answers with parameters frozen.
No incomplete arm is used to claim an equal-budget comparison.

This is a small pilot with correlated questions and one starting model. Repeated
teaching seeds do not justify population-wide or statistical-significance claims.
Curriculum stages and shorter strings change the information per example;
equal example counts do not imply equal input-token or compute counts.

## Efficiency and resource accounting

Record presentations, distinct question keys, optimizer updates, UTF-8 prefix
bytes, supervised answer bytes, training wall time, and the first development
checkpoint to reach 90% on *both* three-symbol positional tasks. A missing
threshold crossing means "not reached within this budget," not infinite cost.

Run arms serially, with one numerical CPU thread, a five-millisecond rest per
update, a ten-minute default total wall limit, a two-GiB free-disk guard, and
Ctrl+C / experiment-local `stop.request` support. These controls never stop or
restart the separate live learner. No hardware safety limits are changed.

The report also records parameter/optimizer bytes, total experiment CPU and wall
time, Windows peak process working set (including native tensor allocations),
and persistent artifact sizes. These figures do not include the concurrently
running live teacher; its CPU contention can affect timings. The runner does
not claim to measure CPU temperature or total laptop energy consumption.

The owner requested pausing live teaching during the comparison. Its documented
CLI pause was sent and the live status confirmed `paused`. This happened late
in the final experimental arm, so competing CPU load was not constant across
all timing measurements. No speed advantage is inferred from this run.

Private manifests, raw questions/answers, exposure ledgers and checkpoint copies
stay under ignored `runs/`. The public record includes only code, protocol and
aggregate measured outcomes.

## Running and controls

```powershell
python -u scripts/compare-teaching-methods.py --source-run runs/learning-live-20260904-143553 --output runs/contrast-comparison-20260904 --steps 384 --seeds 43011 43012 43013 --max-seconds 600
```

The output directory must not already exist. Terminal updates report each
development check and final test. Full teaching events are written locally to
`events.jsonl`. `report.json` preserves completed arms even if the remaining
experiment stops. Candidate checkpoint files are never installed into the live
run. A new live curriculum or restart requires separate owner approval.

## Research inspected

- Bengio, Louradour, Collobert and Weston, [Curriculum Learning (2009)](https://icml.cc/2009/papers/119.pdf):
  original paper's curriculum framing, easy-to-harder distributions and limits
  of the proposed optimization interpretation. This motivates the progression;
  it does not predict a numerical gain for Kavi.
- Lake and Baroni, [Generalization without systematicity (2018)](https://arxiv.org/abs/1711.00350):
  original paper's SCAN setup and comparison of random versus systematically
  different test commands. This motivates separate combination/length transfer
  checks rather than interpreting random quiz performance as general reasoning.

## Measured outcomes

All six arms completed at the prespecified budget. The frozen starting model
had 79,979 prior updates and 66,880 parameters. Its checkpoint SHA-256 was
`1bf6a57d0afa527ed498607b396c4baf78015fd6b7655231f4b8a8e858c98686`.
The original experimental input remained byte-for-byte unchanged. Every arm
made exactly 384 additional updates and saw 1,536 example presentations:
612 copy, 308 first, 308 join and 308 last, including common copy rehearsal.

The starting model scored 35/64 on three-symbol position, 16/64 on four-symbol
position, 16/32 on multiscript position, 19/32 on copy/join transfer, and all
99 protected retention questions correctly (75 characters and 24 pairs).

| Teacher / seed | Three-symbol position /64 | Four-symbol position /64 | Multiscript /32 | Copy/join /32 | Earlier correct items lost /99 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random / 43011 | 41 | 25 | 18 | 23 | 0 |
| Contrast / 43011 | 30 | 8 | 13 | 6 | 1 |
| Random / 43012 | 38 | 29 | 18 | 21 | 1 |
| Contrast / 43012 | 39 | 22 | 21 | 11 | 1 |
| Random / 43013 | 39 | 29 | 16 | 18 | 1 |
| Contrast / 43013 | 40 | 22 | 22 | 16 | 1 |

Average primary accuracy was **61.46% random versus 56.77% contrast**. These
are averages over three repetitions of the same held-out bank, not 192 distinct
questions or independent starting models. Contrast was slightly higher in two
repetitions but substantially lower in one; it did not establish an improvement.
Its mean four-symbol and copy/join transfer scores were also lower. Multiscript
transfer averaged 54.17% random versus 58.33% contrast, a secondary result that
does not override the primary outcome or retention failures.

Both methods retained all 75 individual characters in every repetition. All
contrast runs and two random runs lost one previously correct two-symbol copy
answer. No run reached the prespecified three-symbol development threshold of
90% on both first and last within the budget. Therefore the experiment does
not demonstrate fewer examples needed to reach that target.

### What the progression actually did

Contrast seed 43011 never cleared the two-symbol development gate. Seeds 43012
and 43013 cleared it at updates 320 and 192 respectively. Consequently, their
exposure to three-symbol operation lessons differed substantially. Staying on
short strings is a plausible contributor to the weak transfer, but this trial
does not isolate that effect from pairing and presentation order.

Unique training question counts were 1,325 / 1,325 / 1,326 for random, and
1,245 / 1,286 / 1,325 for contrast. Equal presentation counts, unequal unique
counts and unequal token counts are all reported rather than conflated as
equal amounts of information.

Per-arm training wall times were 19.76 / 19.47 / 19.87 seconds for random and
17.77 / 19.22 / 18.50 seconds for contrast. Shorter examples and the changing
concurrent load confound speed interpretation. The complete experiment took
173.16 seconds wall time and 159.38 seconds process CPU time. Peak working set
was 504,201,216 bytes (about 481 MiB), not merely the 267,520 parameter bytes.
The final report recorded 9,859,939 bytes of persistent artifacts immediately
before its last report write. These artifacts remain private and local.

### Positional-error observation

On the starting model's 32 four-symbol `Last` questions, nine answers were
correct. Of the 23 errors, 11 selected position three (the second-last symbol),
two selected position two, three selected position one, and seven were not a
single input symbol. Thus the owner's second-last observation has measurable
support in this narrow test. There is no human comparison group, and the model
receives bytes rather than glyph images; this does not establish human-like
visual perception or a shared cognitive mechanism. The exercise generator
labels the actual final symbol as correct; it does not label second-last as last.

### Decision and next hypothesis

**Do not deploy this contrast recipe.** No candidate was installed. Live teaching
remains paused at the owner's request; no automatic resume is scheduled.

A useful next, separately specified comparison would hold sequence-length
exposure constant and contrast appending/prepending symbols: appending changes
the last answer but should preserve the first; prepending does the reverse.
That would test sensitivity to sequence boundaries and help distinguish the
effects of paired examples from the easy-to-hard schedule. It has not been
implemented or measured in this record. The failed pilot is retained in history.

## Verification

`python -m unittest discover -s tests -q`: 109 tests passed (8.579 seconds).
Added checks cover matched task budgets at every step, identical rehearsal,
partition separation including reversed strings, exhausted short-string pools,
the two-task development gate, question-only evaluation, checkpoint path/hash
validation, and retention-loss accounting. Mock checks validate control logic,
not intelligence. All six real runs additionally verified unchanged input,
unchanged parameter count, exact update budgets and frozen assessment weights.
