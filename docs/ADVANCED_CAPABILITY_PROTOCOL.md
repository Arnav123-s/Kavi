# From operation learning to advanced subject capability

Author: [Arnav123-s](https://github.com/Arnav123-s)

Revision: 5 September 2026

Status: development and assessment protocol. Advanced subject capability has not been demonstrated.

## What the target means

A master's-level target needs a subject, a defined assessment and evidence beyond exercises used to build the learner. The working technical track here is mathematics and computer science. It does not establish a degree equivalent, and it does not cover every field in which a master's degree is offered.

The present system can search a small language of natural-number procedures. It cannot read a graduate problem statement, select a mathematical model from prose, write a proof, analyze a dataset or defend a philosophical interpretation. More teaching records cannot make an unavailable operation expressible. The representation and learning interface must advance alongside the curriculum.

Official course descriptions help identify the gap. MIT's graduate [Advanced Algorithms syllabus](https://ocw.mit.edu/courses/6-854j-advanced-algorithms-fall-2005/pages/syllabus/) includes algorithm design, analysis and reading research, with undergraduate algorithms and probability as prerequisites. Its [project guidance](https://ocw.mit.edu/courses/6-854j-advanced-algorithms-fall-2005/pages/projects/) requires independent work with difficult material, implementations or theoretical ideas. These are useful task categories, not a Kavi certification standard.

MIT's graduate [Machine Learning syllabus](https://ocw.mit.edu/courses/6-867-machine-learning-fall-2006/pages/syllabus/) combines statistical inference, theoretical and applied problems, exams and a project. Boyd and Vandenberghe's [Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/) provides an authoritative mathematical reference for a later optimization track. These sources are assessment references here; their books, exams and solutions have not been ingested into the structural learner.

## Engineering sequence

| Stage | Required mechanism | Evidence before advancing |
| --- | --- | --- |
| Reusable operations | Acquired bit transitions and executable composition | New operands, lengths, actual calls and full cost records |
| Efficient procedures | Data-dependent branching, bit access and controllable iteration | Scale with input length; test both operand orders and worst cases |
| Typed structures | Signed integers, rationals, sequences, trees and finite graphs | Boundary cases, invalid inputs and new structure sizes |
| Shared abstraction and repair | Discover common subprograms; change an existing dependency safely | Lower total description cost, improved new-task acquisition and preserved dependent behavior |
| Symbolic mathematics | Variables, binding, expressions, assumptions and proof objects | Independently checked transformations and counterexamples to invalid claims |
| Language to formal tasks | Interpret statements, resolve references and identify missing assumptions | Unfamiliar wording and entities; separate parsing from solution accuracy |
| Advanced subject work | Compose models, algorithms, proofs and empirical investigations | Independent task families, expert assessment and reproducible project work |

The current `repeat` and `range` instructions have supplied semantics. Selecting one from examples is a learned program arrangement. It is not discovery of the general idea of looping. Likewise, a supplied theorem checker can verify a proposed proof without making the learner responsible for discovering the checker's rules.

A near-term implementation should keep control constructs explicit and small. For example, binary multiplication needs access to operand bits, shifts, conditional addition and an accumulator. The learner must choose their arrangement from exercises. Installing a complete host multiplication function as an inference primitive would change the learning boundary and must be labeled as supplied knowledge.

## Assessment domains

The following are proposed project assessments, informed by the references above. They are not copied exams or measured results.

| Domain | Example obligation | Independent check |
| --- | --- | --- |
| Discrete mathematics and logic | State an invariant, prove preservation, or produce a counterexample | A small proof kernel where applicable, plus a declared logic and assumptions |
| Algorithms and data structures | Design a procedure for an unfamiliar graph or sequence problem; justify its cost | Hidden input families, adversarial cases, complexity argument and implementation measurements |
| Linear algebra and analysis | Derive a result, identify conditions, and distinguish exact from approximate computation | Symbolic checks, exact small instances and explicit numerical tolerances |
| Probability and statistics | Derive an estimator, identify uncertainty and diagnose a failed assumption | Independent derivation and simulations with held-back seeds or data |
| Machine learning and optimization | Formulate an objective, compare methods, explain generalization and failure | Separated data partitions, mathematical review and reproduced experiments |
| Research practice | Understand a paper, reproduce a central result and investigate one limitation | Source-faithful interpretation, executable artifact and an independently assessed report |

Learning about models with numerical parameters does not require Kavi's own stored core to become a dense numerical network. However, a statistical model's fitted coefficients, if retained, are persistent information and must be counted. Representing them in a graph does not eliminate that storage.

Physics would add dimensional analysis, mathematical modeling, conservation assumptions, numerical stability and comparison with measurements. Philosophy would add faithful interpretation, explicit premises, competing readings, counterarguments and uncertainty. Neither track can be certified through exact arithmetic alone. An author's prestige is not an answer key.

## Separation of teaching and assessment

Freeze the learner source, grammar, initial library, teaching budget, allowed tools and scoring rubric before the final stage. Record every source and every task the developer or learner has seen. A public exercise used to choose an implementation becomes development evidence. Rewording it does not necessarily create a new problem.

Use separate task-family partitions as well as different input values. Teaching a graph algorithm on one graph and testing it on another tests instance transfer. Requiring a different algorithm or a new combination of ideas tests a different claim. Report both separately. Retain failed and unsupported tasks in the denominator.

For exact outputs, report correctness, coverage and resource failures. For proofs, distinguish a correct result from a valid derivation and an independently checked proof object. For explanations and research work, use a fixed rubric, independent qualified reviewers and reported disagreements. Fluent text alone is insufficient. A claim about human graduate performance would require a comparable human assessment under declared conditions; no such comparison exists for Kavi.

There is no automatic promotion from a high arithmetic percentage to a degree label. Establish subject-specific criteria before testing, then report the resulting capability profile and its limits. One successful course-style task does not establish performance across a curriculum.

## Testing the storage hypothesis

Let `L_t` be the deployed procedure library after task `t`, measured using a fixed canonical encoding. Record:

```text
B_t = bytes(L_t)
delta_t = B_t - B_(t-1)
```

For each accepted task, also record candidate work, peak temporary memory, learning time, inference calls and gate evaluations. Keep the interpreter, source corpus, teaching banks, caches and raw evidence in separate cost fields. Their exclusion from the small model artifact is a measurement boundary, not a claim that they cost nothing.

The mathematical idea is conditional description length: a new task can have a short description given useful earlier procedures. A square operation can call an existing product with the same argument twice. This makes the extra program small even though it describes many possible calculations. [DreamCoder](https://arxiv.org/abs/2006.08381) is a close research relative because it combines program induction with acquired abstractions and guidance for later search. Kavi's current fixed enumerator does not implement DreamCoder's learned search system or automatic abstraction invention.

A stronger storage claim needs more than related arithmetic examples. Compare shared descriptions with independent packaging, compressed flat programs and matched libraries that omit the acquired abstractions. Test increasingly different task families and curriculum orders. Plot marginal bytes and adaptation cost together with retained correctness. If all later tasks are variants of the same operation, cheap descriptions are expected and say little about unrelated knowledge.

There is a basic counting limit. A fixed `B`-bit representation distinguishes at most `2^B` configurations. Arbitrary independent facts cannot all enter that representation without increasing storage, losing distinctions or using additional external information. Reuse may reduce redundancy; it cannot guarantee almost-free storage of every future discovery. The current architecture also preserves earlier procedures by keeping their definitions unchanged. Its storage curve therefore does not measure consolidation through safe shared rewrites.

## Decision rules from the current mechanism

If a correct procedure fails on larger inputs because its work grows with the operand's value, teach or acquire a better algorithm before increasing the resource ceiling. Repeated addition for multiplication can require work exponential in the bit length of the repeated operand. A short program is not necessarily an efficient program.

If a useful library makes enumeration slower, measure how the new vocabulary changes candidate branching and ordering. Improve proposal ranking or abstraction selection with separate development tasks, and count any learned proposal state. Do not select only the tasks where reuse helped.

If a new wrapper restores downstream performance while leaving a costly old procedure untouched, record that as append-only adaptation. Shared repair requires modifying an earlier definition and checking all affected dependents, including previously untested input regions. Retention under isolation does not establish that result.

If the learner cannot express a task, record it as unsupported. Feeding more books through the same interface is not a remedy. Add the missing representation or learning mechanism, then run a new finite protocol with fresh assessment evidence.

## Practical outlook

An inspectable specialist that acquires and composes exact procedures is a credible engineering target. Potential uses include small program synthesis tasks, verifiable transformations and domain-specific computation where a compact executable result matters. Whether Kavi is useful requires comparison with existing synthesizers, ordinary implementations and any numerical baseline appropriate to that domain.

Broad advanced capability remains an open research objective. Its central difficulty is choosing useful representations, procedures and abstractions from diverse evidence while keeping search and revision affordable. The current experiments test pieces of that problem. Their size and accuracy do not yet establish an upper capability level, a scaling law or a timetable for reaching one.
