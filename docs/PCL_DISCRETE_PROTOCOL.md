# PCL discrete mathematics: propositional logic

Author: [Arnav123-s](https://github.com/Arnav123-s)

Protocol fixed before model fitting, 8 September 2026.

## Objective and teaching source

Learn the truth functions of conjunction, disjunction, implication, biconditional and negation from original textbook cells, then compose them on compound formulas absent from teaching. This is the first discrete-mathematics stage. Sets, relations, graph theory, counting and proofs remain later subjects.

Source: Oscar Levin, *Discrete Mathematics: An Open Introduction*, third edition, [section 3.1](https://discrete.openmathbooks.org/dmoi3/sec_propositional.html), original English, CC BY-SA 4.0 as stated in the [colophon](https://discrete.openmathbooks.org/dmoi3/front-colophon.html). Local HTML SHA-256 is `d45179154bbce0faea7f15e2cf56f33cc2b6b8307ad53faa3cb52ea43c3f106d`. Use the displayed truth-table cells, not generated assignments or computed labels. Original source HTML and extracted examples remain local.

The first five HTML tables supply 18 primitive input/output cases. Stage one teaches the eight AND/OR cases; stage two teaches all 18 and requires preserving the original eight. Development uses the four displayed rows for example 3.1.1. Final evaluation uses the final column of example 3.1.2 and both compound columns of examples 3.1.3 and 3.1.5: five formula structures, 32 source rows/columns. The adjacent repeated equivalence table is excluded. These are unfamiliar formulas from the same author, not independent-author or unfamiliar-primitive tests.

The finite primitive domain is fully taught. Do not describe primitive accuracy as unseen generalization. The evaluation question is whether supplied composition can reuse acquired truth functions on previously untrained compound structures.

## Representation and supplied mechanisms

Truth inputs are integer 0 and 1, encoded as false and true events. Binary calls emit left truth value, operator, right truth value; negation emits not followed by its input. Learned circuit outputs 0 or 1 are used as subsequent operands. Unknown transitions or unresolved outputs propagate as no answer.

Formula syntax trees, variable binding, connective arities and postorder traversal are supplied. The executor does not implement the truth functions with Python AND, OR, NOT, implication or equivalence. Source formulas are transcribed into tuple syntax trees; their expected answers are extracted from the author's cells. No natural-language parsing or independently learned decomposition is claimed. Working memory includes the syntax tree, traversal plan, operand stack and current phase states.

## Models, search and limits

Use a stable template with moduli (3,5,7,11), one tick and coupling capacities zero or six. Initial impulses assign the seven event symbols cyclically to four counters. Use seeds 7,19,41; each of two teaching stages proposes 256 complete candidates, exact readout binding, 10,000,000 named operations per fit. Existing dynamics are tried first; later complete candidates inherit and redraw impulses and couplings. Protected targets are the original eight truth cases. The current full-consistency binder remains unchanged.

Report development without using it for selection. Complete all six model fits before final evaluation. Do not refit after looking at final answers. Whole-run limits are five minutes, 512 MiB working set and one visible worker, with Pause/Resume/Stop controls and no restart. Cases used by software tests are not curriculum evidence.

## Verification and interpretation

Report every seed: stage accuracy, retention, compatible candidates, bytes, couplings, work and final correct/wrong/unresolved counts. Count original source storage, temporary workspace, wall/CPU time and memory telemetry. A constant-true baseline is measured on the same final cases. An untrained circuit with the same composition executor is another control: scheduling alone must not supply truth semantics.

Check all 18 primitive cases after fitting. If all pass, a structural induction gives a conditional correctness argument for well-formed finite formulas built from those five operators: leaves have supplied truth assignments, each internal node receives already correct child results, and its learned connective returns the correct truth value. The argument assumes the executor is correct, the circuit is frozen, inputs are Boolean, and sufficient resources exist. This is standard compositional reasoning, not a new theorem or evidence of general intelligence. Exhaustive primitive checking and sampled compound evaluation must be reported separately.
