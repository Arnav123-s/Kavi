# Kritjnah: developmental learning proposal

## Purpose

Investigate whether a fixed-budget learner can develop increasingly useful representations through education, consolidation, and reuse. The current phase defines and tests learning mechanisms; it does not enable autonomous code changes or claim a general-purpose intelligent system.

## The stage metaphor

A stage starts at a relative progress score of zero. The learner receives structured examples and questions. After demonstrating mastery, it consolidates the skill and advances. Its new stage again starts at zero, with its earlier abilities intact.

The score is a progress indicator, not a storage mechanism or a universal measure of intelligence. Separate skill measurements are needed because a single score can conceal regressions.

An illustrative progression is quantities and counting, addition, multiplication, and increasingly compositional problems. Language, reading, and other fields introduce additional abilities rather than a guaranteed single linear ladder. Recognizing a symbol is distinct from understanding the quantity or concept it represents.

## What consolidation must accomplish

Consolidation should turn experiences into reusable representations while preserving useful earlier abilities. For example, a general addition procedure is more useful than an isolated list of remembered sums.

Promotion must not erase memory, initialize all weights to zero, or merely rename the score. A consolidation method is successful only if measurements demonstrate retention, transfer, and acceptable resource use.

## Fixed size and deeper understanding

The proposed resource budget must include more than parameter count:

- Persistent parameter values and their numerical precision.
- Internal memory states and any learning or optimization state.
- Replay examples, learned rules, and other retained information.
- Working memory and processing time during learning and answering.
- Any external reference library, measured separately from the learner itself.

Three mechanisms could fit different interpretations of deeper understanding:

1. Better representations in the same finite state: reusable patterns replace inefficient memorization.
2. Repeated computation using the same network: parameter count stays fixed, but more thinking steps consume time and potentially working memory.
3. Multiple internal states per connection: fast-changing and slower-changing components support different memory timescales. These states consume memory and must be included in the initial budget if total size is fixed.

None of these mechanisms implies unlimited lossless storage of unrelated facts. The human-development analogy motivates questions but does not establish biological equivalence.

## Learning without end-to-end backpropagation

The owner wants to investigate a learning method without end-to-end backpropagation. The curriculum alone does not provide that method.

The replacement must specify how an observation or wrong answer determines which internal values change, by how much, and how earlier learning is protected. Increasing a connection value is not inherently learning; decreasing one is not inherently forgetting. Both directions can support correct behavior.

Local learning rules and gradient-free candidate search are research candidates, not selected implementations. A method that avoids end-to-end backward error propagation may still use local derivatives. Completely gradient-free learning is a stricter requirement that must be stated explicitly when choosing a mechanism.

## Proposed first-phase evaluation

Start with a small, bounded curriculum rather than assuming all elementary education across languages will be fast. Keep training examples separate from evaluation examples.

Measure at least:

- Performance on new, withheld examples of the current skill.
- Retention of earlier skills before and after consolidation.
- Transfer to combinations or variants not directly demonstrated.
- Persistent memory, peak working memory, elapsed time, and available energy or thermal measurements.

Define promotion thresholds before running an experiment. A failed retention check is a recorded failure, not successful promotion. Compare candidate learning mechanisms under the same measured budget when practical.

## Open questions

- What is the smallest useful initial curriculum?
- What representation connects symbols to quantities and other concepts?
- What precise update rule replaces end-to-end backpropagation?
- What operation consolidates knowledge, and what information can it discard?
- How will the learner distinguish abstraction from memorization?
- How much fixed memory belongs to fast and slow internal states?
- What evidence justifies promotion to the next stage?

## Locked later phase

Autonomous self-modification, architecture search controlled by the learner, and open-ended operation are not authorized by this design document. They require a later, explicit decision after the basic learner is understood and evaluated.
