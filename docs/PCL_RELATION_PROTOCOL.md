# PCL ordered-relation course

Author: [Arnav123-s](https://github.com/Arnav123-s)

Protocol fixed before candidate fitting and final evaluation, 8 September 2026.

## Question and source

Can whole-circuit reconstruction learn an ordered distinction and retain earlier teaching outcomes when more original examples are introduced?

Use the [Universal Dependencies English Web Treebank](https://github.com/UniversalDependencies/UD_English-EWT/tree/4dc8e10cf32352e11ab2c46e024b19853b91546e), release r2.15, commit `4dc8e10cf32352e11ab2c46e024b19853b91546e`. The source comprises original web English with basic grammatical dependency annotations. Credit Natalia Silveira, Timothy Dozat, Marie-Catherine de Marneffe, Samuel Bowman, Miriam Connor, John Bauer, Christopher D. Manning and the treebank contributors. Annotations and database rights are CC BY-SA 4.0; underlying text rights vary. Keep complete source files and projected teaching records local. No generated sentences or Gutenberg material.

Use basic CoNLL-U dependencies, not enhanced automatic dependencies. Eligible sentences have 4–18 integer-indexed tokens and one root tagged VERB. Each eligible query selects a direct root dependent labelled exactly nsubj or obj. Passive-subject subtypes are excluded. Preserve the original token order. Emit candidate at the selected token, predicate at the root, and other elsewhere. The teacher's target is 0 for nsubj and 1 for obj. Tokenization, root selection and the queried dependent are supplied annotations. The model is not asked to discover words, parse an unannotated sentence or infer whether an arbitrary token is a dependent.

This deliberately restricted projection omits lexical meaning and can be ambiguous. It is a test of structural learning from authentic annotations, not English comprehension. Selection chooses one representative per projected sequence; excluded duplicates and representation loss limit conclusions about the full corpus.

## Partitions

Honor the original train/dev/test files. Within each, sort eligible queries by SHA-256 of sentence ID plus dependent ID. Select 24 examples per class for training, 12 per class for development and 24 per class for final evaluation. Choose at most one query for each projected sequence in a partition. Exclude previously selected projected sequences and documents from later partitions. Document identity is the sentence identifier without its last hyphen-delimited sentence suffix.

Stage one uses the first 12 selected training examples per class. Stage two uses all 48 training examples and protects the earlier 24 target outcomes. Additional lessons can correct predictions on the added cases. No incorrect labels are fabricated. This does not test natural-language explanations of mistakes, nor preservation of the separate flower classifier.

All bank construction is fixed independently of model predictions. Source labels are used for eligibility and class quotas; final labels never enter fitting or candidate selection. Development is reported, not used to choose a model. All six fits finish before any final scores are exposed. Final projection patterns and selected documents are absent from teaching and development. Reusing a final failure in a future course requires a fresh final bank.

## Models and controls

Two arms use stable phase moduli (3,5,7,11), one tick per event and interval readouts. The uncoupled arm has zero coupling capacity; the coupled arm permits four couplings. Initial impulses count candidate, predicate and other in separate coordinates. Seeds are 7,19,41. Each stage proposes 64 complete circuits with the existing reconstruct procedure, reusing existing dynamics first. Every candidate rebuilds its readout from declared evidence. Selection minimizes teaching errors then serialized circuit bytes, subject to the protected bank. No model-generated source code.

Each fit has a 5,000,000 named-operation ceiling. Compare equal candidate ceilings; record actual work separately because arms may use different amounts. A work-ceiling failure preserves the preceding generation and is reported. Whole-run ceilings are five minutes, 512 MiB working set and one visible worker, using the existing Pause/Resume/Stop controls. No automatic restart.

Controls: fixed majority class (ties choose subject) and a supplied position rule predicting subject before the predicate, object after it. The latter is a strong task-specific rule, not learned by Kavi. No tuning against final answers.

## Measurements

Record teaching, development, protected and final correct/wrong/unresolved counts; bytes, couplings, proposal compatibility, hashes and named work. Record wall time, CPU time, memory telemetry, source and local run storage. Compare each final query executed from zero with execution branched after its prefix before the candidate token; predictions must match while the parent state is unchanged. This measures continuation integrity, not counterfactual reasoning.

Report all arms. A high training score with poor final performance fails the generalization objective. Coupling count alone is not evidence that interaction is useful. No research-level, language-understanding, emotional or internal-world capability follows from this narrow task.
