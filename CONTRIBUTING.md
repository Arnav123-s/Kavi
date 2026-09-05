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

Real curriculum runs, restarts, background persistence and hardware-policy changes require a reviewed run configuration and explicit project authorization. Autonomous source-code modification remains outside the current scope.

## Version control

Use small, reviewable commits and explicitly stage intended files. Inspect the diff and staged names before committing. Use the repository-local Arnav123-s identity. Preserve published history and obtain release authorization before pushing changes.

Run checks appropriate to the change. Documentation revisions need link, mathematical, metadata and formatting checks; executable changes need the relevant implementation regressions.
