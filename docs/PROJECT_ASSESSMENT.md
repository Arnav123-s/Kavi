# Kavi: capabilities, evidence and remaining work

Author: [Arnav123-s](https://github.com/Arnav123-s)

Assessment through 7 September 2026. The latest [experiment report](../experiments/2026-09-07-mechanism-audit.md) contains the methods, measured costs, failures and diagrams. Earlier experiment records remain authoritative for their own configurations.

## The project in plain language

Kavi is an experimental system that learns small executable arrangements. Think of components joined into a machine. Teaching helps select the components and their connections; a new input then runs through that arrangement. The arrangement can represent a rule that works for many inputs, instead of storing a separate answer for each one.

There are several experimental cores, not yet one general-purpose brain. One learns logic gates for arithmetic. Another combines acquired procedures. Another learns recurrent connections from streams of symbols. Recent work connects the recurrent core to arithmetic and adds a supervised route for admitting newly composed computations.

The distinction from ordinary numerical weight training is the object being learned: discrete connections, gates and executable programs. That still requires persistent information. Connections, operation choices and retained parameters are the model's knowledge. Temporary signal state disappears between queries; the learned configuration persists.

## The biggest achievement

The strongest correctness result is the learned addition circuit. It contains five gates, occupies 321 serialized bytes and implements a reusable binary addition rule. A local certificate plus the executor assumptions explains why it works beyond the finite examples used to acquire it.

The strongest configuration-change result is the recurrent successor. An earlier two-state rule was replaced by an eight-state arrangement that handles additional events and later selectors while preserving the earlier task for every finite sequence in its original alphabet. The old graph does not have to remain inside the new one as a separate copy. Earlier behavior constrains the successor, rather than freezing its exact wiring.

The newest composition result is a small example of the proposed cycle: use old configurations to propose a new one, check outputs, admit it under supervision and retest earlier skills. From four input/output examples, Kavi selected a graph that adds two values once, then multiplies that intermediate by itself. It passed 48 promotion examples, 128 fresh inputs and 104 earlier-operation checks.

These are meaningful engineering results. They are not evidence that the system has surpassed existing program-learning research, learned general reasoning or discovered a new law of computation.

## What the addition theorem says

Imagine adding long numbers one column at a time. Each column receives two digits and the carry from the previous column. In binary there are only eight possible combinations of those three bits.

Kavi's acquired circuit gets every one of those eight local cases right. If each column correctly passes its carry onward, repeating the same circuit keeps the whole addition correct, however many finite columns the abstract input has. The argument is mathematical induction: start correctly, preserve correctness at the next column, and finish by emitting the final carry.

Formally, the checked local rule is

$$e+2c'=a+b+c,$$

where $e$ is the emitted bit and $c'$ is the next carry. The [proof](ADDITION_CORRECTNESS.md) states the invariant, bit order, zero initialization and final carry-flush assumptions. The actual implementation accepts inputs up to 4,096 bits; the abstract theorem does not remove that runtime limit or prove the Python interpreter correct.

The addition theorem is established mathematics. The project-specific achievement is that the acquired artifact satisfies its certificate. The original circuit selection used 129 operand pairs, so describing this as an unprecedented addition theorem learned from three examples would be inaccurate.

## What it can currently do

| Capability | Evidence and practical boundary |
| --- | --- |
| Reusable arithmetic | Learned addition/subtraction gates and compositions including multiplication, powers and factorials, within the relevant numeric and execution limits |
| Interchangeable operands | The compiled multiplication connector gives swapped operands the same canonical execution order; this optimization was engineered and checked |
| Exact fractions | A separate rational layer handles signed fractions using supplied normalization and division semantics plus acquired compositions |
| Structured sentence calculations | Known sentence frames can invoke arithmetic; six supported calculation probes passed in the latest audit |
| Recurrent input processing | Learned loops handle event counts and late selection; exact finite-state checks support the declared stream task |
| Shared notation | `a` and `α` acquired identical destinations at all eight states in three trials, without an alias substitution supplied to the learner |
| Feedback-selected arithmetic | Ambiguous numerical lessons stayed unresolved until further evidence distinguished addition from multiplication; 128 fresh combined cases passed |
| New configurations from old ones | A two-call graph with a shared intermediate was learned, admitted and executed without its teaching examples |
| Structural repair | Exhaustive one-edge search repaired all three introduced faults while preserving the old task; several heuristic searches failed |

An arithmetic result such as $20^{10}$ does not mean the system understands advanced mathematics. A sentence about kinetic energy can call a quantity computation without explaining mechanics, checking arbitrary physical units or deriving the formula. Identifying the parts of a claim does not establish whether the claim is true.

## How smart is it?

There is no defensible IQ, age or degree-level score for the current system. It is precise on a small collection of formal tasks with strong supplied structure. It is still limited when the representation, wording, specification or required reasoning is unfamiliar.

The latest six broad requests—an unfamiliar proof, a calculus derivation, a physical explanation, literary interpretation, a comparison of philosophers and creative writing—were unsupported. That result does not measure everything the architecture could eventually learn. It does establish that the present interface and acquired models do not meet the three master’s-level targets.

The compact arithmetic/controller/catalog bundle occupies 2,856 bytes, excluding runtime, learning and other checkpoints. The latest worker peaked at about 38.9 MiB, with a separate visible process and about 2.67 MB of local run evidence. Comparing the model bytes alone with a large language model's parameters would confuse a few specialized skills with a broad capability set. See the [model-family and size study](MODEL_FAMILIES_AND_SIZE_COMPARISON.md) for the accounting framework.

## The closest mathematical and research relatives

The closest mathematical description of the recurrent core is a **deterministic finite-state machine**: an input token chooses a transition, and the reached state determines an output. The arithmetic gate core is a finite-state transducer applied repeatedly to a bit stream. The composition layer is **program synthesis and library learning**: construct a program that fits a specification or examples, using existing operations.

The closest established research family for the broader reuse goal includes [DreamCoder](https://arxiv.org/abs/2006.08381), which combines acquired program abstractions with a trained neural search guide. Kavi's new small composition search enumerates a fixed grammar and does not learn a comparable search model. [Babble](https://arxiv.org/abs/2212.04596) learns reusable abstractions from program corpora using an equational theory, e-graphs and anti-unification. Kavi does not currently implement that abstraction machinery. These are conceptual comparisons, not head-to-head benchmarks.

The finite-state learner belongs to the family of compatible state-merging methods discussed in the [state-merging literature](https://www.bcl.hamilton.ie/~barak/papers/icgi98.pdf). Its first-compatible merge procedure is supplied, rather than an independently discovered learning algorithm. The broader intention—new knowledge changing the whole configuration while retaining earlier valid behavior—extends beyond the demonstrated finite tasks.

## What the physics and chemistry ideas mean here

The useful hypothesis is that mechanisms inspired by physics or chemistry can help build and refine configurations. Better resulting configurations may then improve the overall model. The mechanisms are tools for learning and construction; the objective is reliable capability, not structural complexity for its own sake.

The latest test gave temperature one precise role: sometimes accept a temporarily worse structural candidate, then reduce that freedom as search continues. Error-path priority gave another role: propose changes more often along connections involved in failed examples. This is a small classical optimization experiment. It does not reproduce chemistry or quantum mechanics.

The heated conditions repaired none of the three faults exactly. Greedy methods each repaired one. An exhaustive one-edge search repaired all three with a larger, completely covered neighborhood. These results support neither a general temperature advantage nor a conclusion that physical inspiration cannot work. They identify a particular mechanism, schedule and budget that did not improve the measured outcome.

Quantum interference, gravity, reaction dynamics and learning to redesign the updater require their own executable definitions and comparisons. Researching their equations is not the same as installing them in Kavi, and simulating a process does not inherit free computational power from the physical system.

## Which ideas have actually been tried?

| Idea | Status through this report |
| --- | --- |
| Learn a reusable rule instead of an answer table | Measured in circuit and program acquisition |
| Shared paths for interchangeable inputs | Measured; some connectors are engineered, while the new notation connections are learned |
| Inputs determine which recurrent connections activate | Measured on finite stream tasks; broader semantic interpretation remains open |
| Later information changes the interpretation of earlier input | Measured through late stream selectors and constrained sentence experiments |
| Corrections change a rule and transfer | Measured, including failures, nonmonotonic improvement and successful coverage repairs |
| Replace old wiring while retaining valid old behavior | Measured for the recurrent successor; exact equivalence is domain-specific |
| Build a new configuration from acquired components | Measured in program learning and the new shared graph |
| Check and admit a new configuration under supervision | Implemented and measured with separate promotion and final banks |
| Heat/cooling and targeted proposal rates | Measured as limited search proxies; the heated settings did not improve exact repair |
| Progressively shorter, faster configurations | Checked compilation and bounded reuse measured; general autonomous compression remains open |
| Learning during use | Feedback-driven experiments exist; final evaluation remains frozen so progress can be measured honestly |
| Configurations learn to change their own learning rules | Not demonstrated; the update procedures are supplied |
| Internal semantic dynamics, learned physical mechanisms, unrestricted quantum-inspired learning | Research proposals; algebra examples are not learning results |
| Language, literature, science and philosophy at master’s level | Target not achieved |

The [neural](NEURAL_PATHWAY_LEARNING.md), [animal-learning](ANIMAL_LEARNING_AND_CONFIGURATION_CHANGE.md), [physical-pathway](PHYSICAL_PATHWAY_RESEARCH.md) and [quantum/software](CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md) studies retain the detailed research and proposals. Earlier external-review recommendations remain recorded and deferred. This report closes the scheduled audit, not every possible experiment that could be imagined from those studies.

## What would count as success next?

A useful near-term outcome is a reliable learner of compact, inspectable domain procedures. The evidence now justifies testing a broader set of unseen compositions, richer input structures and supervised corrections. It does not yet justify a prediction of general intelligence.

The next capability gap is handling an unfamiliar problem specification: identify relevant quantities and relations, choose or construct a representation, propose computations, and find trustworthy checks for their answers. Supplying a few examples of a known numerical relation covers only a small part of that job. Learning from literature additionally needs grounded meanings, argument structure, uncertainty and reasoning beyond matching familiar sentence frames.

A convincing advance would solve reserved families of problems with less total teaching and search work, retain prior skills, tolerate changed wording and structure, and outperform explicit alternatives under matched budgets. If a physical mechanism helps, its effect should appear in those measurements. If the learner acquires a better update rule, a later curriculum should improve with that rule frozen and without extra hidden supervision.

The current claim—learning reusable computational configurations, with some correction, sharing and retention—is supported in the declared domains. The larger claim of an increasingly general, self-configuring intelligence remains a research objective.
