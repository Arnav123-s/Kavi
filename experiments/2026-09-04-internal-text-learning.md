# Original-text internal learning: initial live observations

Status: **running, no mastery claim**. These are point-in-time observations, not
a completed curriculum result or a controlled comparison of architectures.

## Change under test

Added an untrained complex-valued sparse recurrent text component with 64 mixing
points, 256 available directed links, two hops per byte, and 66,880 float32
parameters. The core updates its own embeddings, transmission strengths,
activity-dependent gate parameters, phases and output readout using truncated
backpropagation. No pretrained weights or external answer-generating model
were used. The older symbolic circuit was retained separately and passed its
64-case structured retention check; those results are not text-model results.

The admitted original source is Augustus De Morgan's English *Elements of
arithmetic*, 1858 digital witness, Book I. Exact source information and its
SHA-256 fingerprint are in `curriculum/arithmetic-original.json`. The executable
sequence has nine mathematics units, not the full global/graduate curriculum.

## Initial measurements

- A 20.15-second smoke run applied 131 optimizer updates to 8,045 byte targets.
  It stopped on its explicit time budget, with no unit passed.
- A checkpoint-resume check continued to 308 cumulative updates and 18,262 byte
  targets. It completed one bounded teaching round, not a curriculum level.
- The first visible long run reached at least 1,101 updates. Early 32-question
  English numeration exams scored 3.125% and 0%. The system correctly withheld
  promotion. Lower prediction loss did not mean correct answers.
- A visible conversation asked `What is one plus one?`. Its pre-update answer
  was `6`. The supplied correction `2` and explanation caused an accepted
  internal update. A later separate interaction answered `332`; this is
  evidence that one correction does not establish mastery or reliable retention.
- One observed learner process used 502,824,960 bytes working set, with
  504,881,152 peak working set. That includes its runtime, not just weights.
  Learned parameter storage is 267,520 bytes; initialized optimizer tensors
  occupy 535,072 bytes. Viewer/shell processes, books, logs and snapshots add
  further resource use. No device-wide memory or temperature guarantee follows.

## Failure and recovery

The first long run failed on a Windows access/sharing error while atomically
replacing `status.json`, after several teaching rounds. Its last durable model
had 1,001 updates; uncheckpointed work was not claimed recovered.

Added bounded retries for transient access/sharing failures in atomic status
and checkpoint replacement, with permanent errors still surfaced. Added tests
for successful retry, persistent failure and complete JSON writes. Added an
emergency checkpoint attempt on unexpected teacher failure.

The repaired visible run resumed the durable checkpoint with an explicit
48-round-per-unit and 24-hour budget. At a later check it was learning in the
seventh numeration teaching round at 2,216 cumulative updates. No unit had
passed. Checkpoint/session provenance preserves the earlier failed run rather
than overwriting it. Waiting after a finite round budget is labeled waiting,
not endless learning.

## Verification and boundaries

The test suite passed 76 tests after the file-retry change. New checks cover
internally changed phases/gates at fixed parameter count, read-only generation
and measurement, byte streaming, checkpoint/optimizer continuity, supervised
boundaries, stopping, source paragraph disjointness and exact independent
numeric grading. These engineering tests are not the learner's exam score.

No matched real-valued baseline, learned shortest-path comparison, physics
advantage, unrestricted multilingual reasoning, complete textbook mastery,
unlimited memory or graduate competence has been demonstrated. Conversation
data and all source text remain in ignored local storage and are not published.
