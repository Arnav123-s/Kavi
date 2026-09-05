# Teaching from historical works

Author: [Arnav123-s](https://github.com/Arnav123-s)

Revision: 5 September 2026

Status: curriculum and implementation plan. No historical-work training result is reported here. The measured structural result remains the [addition experiment](../experiments/2026-09-05-circuit-learning.md).

## Present capability

The structural learner accepts integer examples and searches for a Boolean transition circuit under a supplied bit-processing loop. It has no sentence parser, document comprehension model, general procedure library or representation of philosophical arguments. Its five-gate addition graph cannot acquire those capabilities by receiving more text through the existing interface.

The earlier recurrent core accepts text, but it is a separate numerical model with documented limitations. Feeding books to that core would test a different implementation. Its results must not be attributed to the structural circuit.

The existing [people-and-works catalog](../curriculum/people-and-works.json) has eight tracks and 51 entries, including generated foundations, historical works, traditions and modern references. It is an educational catalog, not evidence that the works were ingested or their contents learned. Selection should depend on the concept to acquire, prerequisites and a credible test. An author's reputation is not a correctness verifier.

## Source sequence

The following three sources provide a concrete progression from exact operations to argument analysis. Their proposed learning tasks are engineering choices; the authors did not specify this machine-learning curriculum.

| Source and inspected scope | Proposed lesson | Evidence of acquisition |
| --- | --- | --- |
| Augustus De Morgan, *Elements of Arithmetic*, Book I, numeration and addition/subtraction | Quantity, carrying, borrowing and the relation between inverse operations | Correct new operands, longer inputs, actual reuse and preserved addition behavior |
| George Boole, *An Investigation of the Laws of Thought*, Chapters II and III | Class intersection, complement, equivalence and inconsistent conditions in a declared finite universe | New class memberships and formulas; executed learned structure; independent exhaustive checks |
| David Hume, *An Enquiry Concerning Human Understanding*, Section IV | Distinguish deductive claims from expectations based on experience; reconstruct an argument's assumptions | Faithful argument reconstruction, unfamiliar counterexamples and explicit unresolved conclusions |

De Morgan's [original English text](https://www.gutenberg.org/cache/epub/68662/pg68662-images.html) develops numeration and arithmetic through quantities and operations. Boole's [original work](https://www.gutenberg.org/files/15114/15114-pdf.pdf) develops symbolic class operations and their laws; historical notation must be interpreted explicitly rather than silently equated with every modern Boolean convention. Hume's [Section IV](https://davidhume.org/texts/e/4) distinguishes relations of ideas from matters of fact and examines the justification of inference from experience.

De Morgan already has a reviewed source record for earlier teaching. The new lesson must still identify the exact admitted extract and its changed use. The Boole and Hume references above are research references, not new ingestion approvals. Exact editions, translations, scope and local fingerprints belong in the source record before source bodies enter a teacher. Existing catalog entries from other languages and traditions remain part of the longer curriculum; this initial sequence is chosen for tractable verification and inspected source access.

## Teaching interface

An initial source-backed teacher should produce one lesson at a time with a source locator, declared concept, input/output types, examples, counterexamples and a verifier. It should keep the reference procedure and final test bank outside learner-visible data. The learner receives the teaching interface; inference receives the resulting program and a new input.

Two experiments must remain distinguishable:

1. A teacher interprets a passage and supplies formal exercises. The learner acquires a procedure from those exercises. This measures source-guided formal learning.
2. The learner interprets the passage itself, identifies its operative rule and acquires a procedure. This additionally measures language-to-program learning.

The first is a feasible intermediate target. It does not establish the second. If an external language model prepares lessons, its contribution and verification cost must be recorded. The learned circuit cannot receive credit for that model's reading or reasoning.

## First extension

Extend the current runtime to retain several named operations, with explicit signatures and output contracts. Keep task selection supplied at first and record that assumption. Add acquisition of nonnegative subtraction from examples, then a bounded composition task that can reuse the learned addition and subtraction procedures. Do not install the target subtraction arrangement or target composition as a primitive and call it learned.

Measure the difference between acquiring each task independently and acquiring it with access to earlier learned procedures. Also compare against supplied procedures and a lookup control. Merely storing two separate graphs does not demonstrate useful transfer. A reuse claim requires executed calls to the acquired component and reduced learning cost or improved held-out behavior under matched budgets.

Logic follows when the interpreter supports Boolean values, finite sets and typed expressions. Since AND and NOT are already primitive gates, reproducing them is not a new discovery. The useful target is acquisition of larger relations or compositions from examples under a disclosed grammar. Control-flow discovery, arbitrary proof search and general language need additional experiments.

## Evaluation

Preserve the current addition model and its regression bank before extension. Use separate teaching, development and final banks. Generate new operand values, longer inputs, new expression structures and renamed entities after freezing the learner and selection procedure. Different numbers alone do not test discovery of a new kind of algorithm.

For each stage, report exact task correctness, correct-to-wrong changes on earlier tasks, counterexamples, all candidate work, wall and CPU time, model and library bytes, external teacher storage and peak working memory. Compare the same exposure and execution budgets. Record failure and timeout alongside successful results.

For philosophy, grade distinct obligations separately: what the author asserted; which premises an inference requires; whether the conclusion follows under a stated formal interpretation; and what remains contested or unsupported. A mathematical identity can have an exact verifier. An ethical or metaphysical position cannot be made universally correct by assigning its author's answer as a training label. Language and interpretation assessments need independent review and reported disagreement.

## Visible trial procedure

For an observed trial, establish a visible terminal before starting the teacher. Display the selected implementation, sources, configuration, initial model and finite budget. Let the operator start from that terminal once the view is ready. An open request or a running background process alone does not establish visibility.

Show actual counterexamples, candidate changes, accepted repairs, retention checks and final results as they occur. Keep the transcript available after completion. A later playback must be labeled as a replay; delays in the display must not be counted as learning time. Leave a query interface available for inspecting the saved procedure.

The next result should answer a precise question: does access to an acquired operation help Kavi learn another operation or composition while preserving the first? Broad historical reading becomes meaningful only as the architecture gains the ability to represent and test what those works teach.
