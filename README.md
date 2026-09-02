# Kritjnah

**Author:** [Arnav123-s](https://github.com/Arnav123-s)

Kritjnah is an experimental proposal for a fixed-budget developmental learner: learn basic skills, consolidate them into reusable foundations, and build more advanced skills without continually enlarging the learner.

## Current status

Design and research only. No learner has been implemented, trained, or evaluated in this repository. Autonomous self-modification is out of scope for this phase. Creating this repository does not start training or resume any previously paused process.

The desired learning method avoids end-to-end backpropagation. The replacement update rule, architecture, and consolidation mechanism remain open research questions; this repository does not claim they have been solved.

## Central idea

Learn a skill, test it on unfamiliar examples, consolidate it, and use it as the starting point for the next skill. A stage's progress score can return to zero after promotion, but the learned knowledge must remain. Zero means a new baseline, not empty memory or infinite storage.

The first question is whether a learner can acquire useful abstractions under a fixed resource budget while retaining earlier abilities.

## Project map

- [Design](docs/DESIGN.md): interpretation, constraints, and unresolved mechanisms.
- [Primary research](docs/RESEARCH.md): related work and its limitations.
- [Decisions](docs/DECISIONS.md): dated scope and design decisions.
- [Experiment records](experiments/README.md): requirements for future measurements.
- [Author](AUTHORS.md).

## History and publication

This repository records project history from its creation onward. Earlier private conversations and local runtime history are not reconstructed as historical commits.

Only deliberately reviewed project materials belong here. Credentials, personal information, private transcripts, third-party books, datasets, model weights, and runtime logs are excluded. Research references retain their original attribution.

No software license has been selected yet.
