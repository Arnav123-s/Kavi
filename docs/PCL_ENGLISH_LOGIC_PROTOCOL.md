# Harder logic and an English-to-logic bridge

Author: [Arnav123-s](https://github.com/Arnav123-s)

Protocol fixed before this run, 8 September 2026.

## Frozen harder evaluation

Retain all three successful circuits from the [discrete-logic course](../experiments/2026-09-08-pcl-discrete.md), with their published hashes. No further fitting of their truth functions. First evaluate 36 previously unused source truth-table cells from Levin third-edition section 3.1 (zero-based HTML tables 13,19,21,23,25). Then solve two source puzzles: the Holmes clothing investigation in section 3.1 and the three trolls investigation in section 0.2. Formal premises and expected solutions are teacher annotations of those original questions. No invented puzzle is used for teaching.

The constraint solver enumerates Boolean assignments and uses the learned circuit for every compound premise. Assignment enumeration and aggregation are supplied mechanisms, not learned search. These enumerated assignments are the solver's work, not synthetic training examples. Maximum 12 variables. Record unresolved assignments rather than inventing a solution. Formalization assumes a bow tie counts as wearing a tie and the two stated suit choices are exhaustive. Holmes's four variables encode tweed suit, sandals, purple shirt and tie; expected unique assignment is (0,1,1,1). The trolls' knight indicators have expected unique assignment (1,0,1).

## English teaching

Use original examples from Oscar Levin, *Discrete Mathematics: An Open Introduction*, third edition, [section 0.2](https://discrete.openmathbooks.org/dmoi3/sec_intro-statements.html), original English, CC BY-SA 4.0. HTML fingerprint: `953b886b8b046b569e183f8304ea9ee7ebe899b0c5de8a48f8a7bec6ce6bfe25`. Public source-offset annotations reconstruct eight teaching and eight final examples without publishing source bodies. The local HTML is authoritative. Teacher labels identify AND, OR, forward implication, reverse implication or equivalence from the author's explanation.

The caller marks two exact atomic clause spans. Replace each with the same clause event, lowercase the remaining words and discard punctuation. Assign P to the first clause in sentence order and Q to the second. This supplies boundaries and abstraction; the learner does not understand clause vocabulary. A separate PCL phrase circuit learns the event-sequence-to-formula-port mapping. Five formula templates and their output-port interface are supplied. Connector words are not mapped to operators by the interpreter.

Teach the first four examples (AND, OR, prefix conditional, equivalence), then all eight (adding if, only if, necessary and sufficient formulations), protecting the original four targets. Three seeds 7,19,41; stable moduli (3,5,7,11), ticks one, six coupling capacity, 256 complete proposals per stage and 10 million named operations per fit. Exact readout binding. Complete all three fits before final evaluation. The original logic circuit from seed 7 is preselected as the shared downstream evaluator; do not choose it by this run's results.

Five final examples reuse teaching connector patterns with different source clauses. Three use untrained connector formulations. Report these groups separately. Reused-pattern success measures caller-supplied abstraction plus learned mapping, not novel-pattern generalization. No development bank or candidate tuning against the final examples. Source atomic meanings and factual truth are not learned here.

For each final English example, measure exact formula-port correctness and end-to-end Boolean behavior under all four assignments. Expected truth values come from the original primitive table cells and the author's formula annotation, outside model inference. Those assignments are exhaustive diagnostic probes, not extra English teaching. Eight sentence interpretations and 32 valuation checks are distinct denominators.

## Controls, costs and limits

Report an untrained phrase-circuit control and a fixed forward-implication control. Preserve original logic hashes and recheck all 18 primitive cases after bridge teaching. No claim of a single consolidated circuit or cross-domain learned compression: phrase and logic circuits remain separate.

Use one visible worker, five-minute and 512 MiB limits, existing pause/stop controls and no restart. Record model sizes, source/implementation hashes, work, timing, memory, known failures and private run storage. Full source text, expanded teaching examples and checkpoints stay local. Neither arbitrary English conversation nor research-grade theorem proving is an acceptance claim for this run.
