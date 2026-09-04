# Kavi: internally learned configurations and finite memory

## What this implementation is

The wave text core is a small sparse recurrent neural network trained from
scratch, not a pretrained language model. Its fixed graph contains 64 mixing
points, four candidate incoming links per point, and two recurrent propagation
hops per input byte. Input-dependent gates, transmission strengths, phases,
input embeddings and output projections are learned by the core itself.

It complements the earlier symbolic circuit. The saved symbolic checkpoint is
preserved and audited separately. Its successful structured-program results do
**not** count as the new text core's results. Transfer between those two
representations, automatic topology discovery, and a unified general reasoner
are not implemented. This is a measured development extension, not the finished
architecture envisioned by the owner.

The teacher presents original text and source-grounded practice/corrections.
`WaveLearner.learn` performs truncated backpropagation and clipped Adam updates.
The teacher does not write particular answer weights or edit connection tensors.
Backpropagation was permitted by the owner. Human-written code still defines
the learning rule and available graph; Kavi does not autonomously rewrite it.

## Signal flow and mathematics

For input byte \(x_t\), an embedding supplies complex coordinates
\(e_t\in\mathbb C^N\). Real and imaginary coordinates are stored as two ordinary
float32 numbers. A learned retention gate \(d=\sigma(v)\) initializes the step:

\[
z^{(0)}=d\odot z_{t-1}+(1-d)\odot e_t.
\]

Each receiving point \(j\) has a fixed set \(S_j\) of at most four sources.
For every hop, the activity-dependent transmission is

\[
g_{ji}(z)=\operatorname{softmax}_{i\in S_j}
   [\ell_{ji}+\tanh(b_{ji})|z_i|],\qquad
m_j=\sum_{i\in S_j}g_{ji}(z)\sigma(c_{ji})e^{\mathrm i\phi_{ji}}z_i.
\]

The bounded nonlinear update is

\[
u_j=z_j+0.5m_j+0.25e_{t,j},\qquad
z_j\leftarrow u_j/\sqrt{1+|u_j|^2}.
\]

A learned linear readout of real and imaginary coordinates predicts the next
UTF-8 byte. Training minimizes next-byte cross-entropy. For supplied corrections,
only the answer/explanation positions receive supervised loss; question tokens
provide conditioning. A normal conversation input can be learned as an
unverified observation. The model's own generated answer is never automatically
treated as ground truth.

This supports continuous input-dependent rerouting and shared, learned wave-like
mixing in classical software. It is **not** a unitary quantum circuit, physical
entanglement, a simulation of the universe, or evidence of quantum speedup.
All four available incoming links are evaluated; this implementation does not
learn a guaranteed shortest or perfectly correct path. Hop count is currently
bounded configuration, not a learned optimal stopping policy.

## Memory: what is and is not stored

The learned parameters are long-term compressed memory. Recurrent activity is
temporary working context. A single circuit can reuse its parameters across
many different inputs without allocating one stored example per input.

For example, recognizing `a` can be shared between a person's name and an
algebraic expression. The surrounding input and current activity distinguish
the roles. Neither shared spelling nor shared routing implies that the model
can forget context and always choose correctly. `a+b` may also be quoted text.

The addition rule describes a potentially unbounded mathematical family of
questions; storing that rule is not the same as remembering every past question.
For a device with B bits of total internal state there are at most 2^B distinct
states. More distinct histories than states necessarily collide. If two
histories produce precisely the same state, the machine cannot later recover
which history occurred without extra information. Finite precision, time and
number representation also bound actual execution.

Consequently this project targets compact generalization, not lossless infinite
memory. It cannot promise no forgetting. Previous passing tests are rechecked;
failed configurations can be rolled back. Finite testing still cannot guarantee
retention of every possible input.

The core checkpoint contains parameters, optimizer state, counters and graph
configuration, **not a transcript database**. Nevertheless the overall system
does store books, prompts, answers, logs and archived checkpoints outside the
active core, under ignored `private/` and `runs/`. That external storage grows
during a run and must be counted. It is not queried by text inference. The
learner resets transient activity between separate documents/questions; a new
conversation is not automatically an exact continuation of all prior context.

## Teaching, prerequisites and honest boundaries

The executable original-book sequence currently covers nine arithmetic units:
numeration; addition/subtraction; multiplication; division; fractions; decimals;
square roots; proportion; and pair counting within combinations. Some exams
sample only a narrow subskill of their chapter, not every concept in it.

Original paragraphs are split as whole, disjoint paragraphs before teaching.
Additional paragraphs support remediation. Withheld text prediction is recorded
separately from English question answering. Fresh arithmetic questions have
independent exact rational graders; nonsense containing a correct digit fails.
After feedback a question ceases to be unseen and is excluded from later fresh
exams. A 90% calibration pass must be followed by a fresh harder 90% pass and
retention checks before the next unit unlocks.

Original works are not automatically correct, culturally neutral, or sufficient
pedagogy. The historical textbook's prejudicial framing is not endorsed. The
quantitative grader uses mathematical correctness, not the author's authority.

The global original-language author/language catalogs remain in
`curriculum/people-and-works.json` and `curriculum/multilingual-foundations.json`.
They have **not** all become admitted, executable lessons. Reading French or
Sanskrit bytes does not demonstrate English translation or comprehension.
Master's-level breadth across fields, autonomous scientific discovery, and the
Riemann hypothesis are **not demonstrated and not covered by these exams**.

## Operation and visibility

Launch from the repository:

```powershell
.\scripts\start-live-learning.ps1
```

Seven terminal tabs show the teacher, original passages, generated answers,
learned link parameters, internal updates, English grading, and Chat/Controls.
The Chat tab accepts a question or a supplied correction:

```text
/teach What is one plus one? => 2 || Two groups of one make two.
/status
/pause
/resume
/stop
```

Question answering runs before learning that new input. Live byte output is an
actual model output, often wrong or repetitive while untrained. Link displays
are numeric execution/parameter observations, not a claimed human-like hidden
thought process. Private conversation logs never go to the public repository.

The CPU-only default uses two numerical worker threads; GPU and temperature
limits are unchanged. One OS-held training lock prevents duplicate wave
trainers. Pause/stop act between bounded updates. A run has finite teaching and
24-hour wall-clock budgets. After exhausting automatic rounds, an optional live
service waits for questions/corrections; waiting is explicitly not training.
The teacher cannot invent a missing curriculum, verifier or architecture merely
by repeating a chapter. More original works and capable mechanisms still need
development when the measured boundary is reached.

Atomic snapshot pointers preserve optimizer state and teacher progress. Resume
to a **new** run directory using `--resume <previous-run>`. An interrupted
incomplete teaching round is repeated; a resume is not exact instruction-level
replay. Old snapshots remain outside the answering model. The app does not
install startup persistence, close unrelated programs, or modify hardware
safety controls.

## Research context and inspected scope

- [Trabelsi et al., Deep Complex Networks](https://arxiv.org/abs/1705.09792):
  abstract inspected. Establishes relevant complex-valued learning context;
  this implementation is not a reproduction of their architectures or results.
- [Graves, Adaptive Computation Time](https://arxiv.org/abs/1603.08983): abstract
  inspected. Relevant to a future learned traversal-length experiment, not a
  claim that this code implements ACT. The abstract reports that its character
  language experiment did not show large performance gains.
- [De Morgan, Elements of arithmetic](https://www.gutenberg.org/ebooks/68662):
  catalog and selected original sections inspected; exact digital witness,
  fingerprint, exclusions and scope are in `curriculum/arithmetic-original.json`.

No claim of novelty, quantum advantage, general language understanding, or
unlimited memory follows from these references. Comparative experiments are
required before claiming the wave mechanism improves quality or resource use.
