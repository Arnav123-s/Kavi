# Related primary research

These are related mechanisms, not a claim that their combination has already produced Kavi. This note summarizes inspected paper sections or abstracts, not an exhaustive literature review. No third-party implementation or dataset is vendored here.

## Learn, then consolidate

**Jonathan Schwarz and colleagues, Progress & Compress: A scalable framework for continual learning (2018).**

[Original paper](https://arxiv.org/html/1805.06370v2)

Relevant material inspected: introduction, progress and compress mechanisms, and discussion of fixed capacity and forgetting.

An active component learns new tasks; learned behavior is then distilled into a knowledge component while regularization limits damage to earlier skills. This is relevant to making mastered skills a foundation for later learning. It still uses gradient-based training and has finite-capacity tradeoffs. It does not demonstrate unlimited knowledge storage.

## Fast and slow internal states in connections

**Marcus K. Benna and Stefano Fusi, Computational principles of biological memory (2015 preprint).**

[Original paper](https://arxiv.org/html/1507.07580v1)

Relevant material inspected: memory benchmark, synaptic model construction, discretization, and scaling discussion.

The model uses interacting internal variables with different timescales. Its connection to Kavi is the possibility of richer internal memory dynamics within a connection. Additional variables remain real storage costs. The paper studies memory properties under specified assumptions, not complete language or educational mastery.

## Local learning without an end-to-end backward pass

**Geoffrey Hinton, The Forward-Forward Algorithm: Some Preliminary Investigations (2022).**

[Original paper](https://arxiv.org/html/2212.13345v1)

Relevant material inspected: motivation, layer-local learning mechanism, and stated experimental limitations.

The method uses positive and negative examples with local objectives. It avoids the usual end-to-end backward pass but still involves local derivatives. The original paper reports limitations on small benchmarks, including cases of slower learning and weaker generalization than its backpropagation baseline. It is a candidate for investigation, not an established speed improvement for this project.

## Gradient-free weight search

**Felipe Petroski Such and colleagues, Deep Neuroevolution: Genetic Algorithms Are a Competitive Alternative for Training Deep Neural Networks for Reinforcement Learning (2017).**

[Original paper](https://arxiv.org/abs/1712.06567)

Material inspected: abstract.

The authors demonstrate gradient-free population-based search over network weights in selected control tasks. This supports the existence of a genuinely gradient-free route, but does not establish efficiency for a developmental language learner. Candidate evaluation and population state must be counted in resource comparisons.

## Unicode signal standards for the generated scalar stage

**Unicode Consortium, Unicode Standard Annex #15: Unicode Normalization Forms;
Unicode Standard Annex #24: Unicode Script Property; and Unicode Technical
Standard #39: Unicode Security Mechanisms.**

[UAX #15](https://unicode.org/reports/tr15/) · [UAX #24](https://unicode.org/reports/tr24/) · [UTS #39](https://unicode.org/reports/tr39/)

Relevant material inspected: the normalization distinction, Script and
Script_Extensions property scope, and the explanation of visually confusable
characters. These standards motivate preserving original scalar code points,
keeping normalization as an explicit choice, and testing look-alike scalars as
distinct inputs.

Kavi intentionally does not implement a full Unicode-property database,
normalization engine, confusable-security checker, grapheme-sequence processor,
or language detector. Its implemented stage is a small source-free prototype
with eleven declared scalar pathways. The detailed boundary is in
[UNICODE_SCRIPT_STAGE.md](UNICODE_SCRIPT_STAGE.md).

## What these sources do not establish

- That removing backpropagation is sufficient to produce more capable reasoning.
- That school-like ordering alone supplies a learning algorithm.
- That a finite learner can retain unlimited independent information.
- That consolidating a stage automatically preserves all earlier skills.
- That a proposed combination has been implemented, trained, or validated here.
