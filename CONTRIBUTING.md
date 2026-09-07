# Engineering standards

Author: [Arnav123-s](https://github.com/Arnav123-s)

Keep the model core, teaching process and evaluator independently inspectable. Document whether a mechanism is proposed, implemented or measured. Every capability claim needs a corresponding test domain, configuration and result.

Use original papers and source records for research. Retain third-party attribution. Keep source bodies, private conversations, credentials, checkpoints and full runtime logs in ignored local folders.

## Changes and experiments

- Define the behavior a change is intended to improve and the earlier behavior it must preserve.
- Keep final evaluation separate from training and candidate selection.
- Count persistent state, temporary memory, external storage and all search work.
- Record failures, regressions and unavailable measurements.
- Verify semantic rewrites under explicit assumptions; distinguish them from behavior-changing repairs.
- Use finite experiment budgets and preserve pause and stop controls.

Curriculum runs use a reviewed, documented configuration approved by the project owner. Restarts, background services and changes to hardware limits also need that approval. Learning changes the model's configuration; Kavi does not rewrite its own source code.

## Version control

Describe the problem, the change and the evidence in each contribution. Keep commits focused, review their contents and preserve published history. Publication requires the project owner's approval.

Include reproduction steps for experiments and regression checks for executable changes. Check equations, references, metadata and diagrams when revising documentation.
