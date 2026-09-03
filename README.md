# Kavi

**Author:** [Arnav123-s](https://github.com/Arnav123-s)

Kavi is an experimental proposal for a developmental learner with bounded growth: expand while learning, compress useful knowledge into a smaller foundation, and repeat within a hard device resource limit.

## Current status

Kavi contains a narrow, implemented Stage-0 prototype: an inspectable,
generated addition/subtraction pathway experiment with finite runs, exact
verification, candidate-only updates, protected and held-out checks, and a
visible terminal trace. It is not a general learner, a textbook-trained model,
or evidence of broad intelligence. See the
[implementation reference](docs/IMPLEMENTATION_REFERENCE.md) for its exact
boundary and [operations guide](docs/OPERATIONS_AND_REPRODUCIBILITY.md) to run
it.

The broader developmental architecture remains research. It does not start
training merely because this repository exists, and it does not include
autonomous source-code modification, background persistence, web learning, or
hardware-limit changes. The proposed replacement for end-to-end
backpropagation and the proposed consolidation mechanism remain open questions.

## Central idea

Learn and grow, test on unfamiliar examples, compress into a smaller representation, verify retained abilities, and use that compact learner as the starting point for the next stage. A stage's progress score can return to zero after promotion, but the learned knowledge must remain. Zero means a new baseline, not empty memory or infinite storage.

The allocated learner size may change. The hard device resource limit does not increase merely because the learner starts another stage. Compression is a research objective, not a guarantee that arbitrary knowledge can fit into one weight.

## Project map

- [Design](docs/DESIGN.md): interpretation, constraints, and unresolved mechanisms.
- [Growth and compression cycles](docs/GROWTH_CYCLES.md): changing learner size under a fixed device ceiling.
- [Implementation reference](docs/IMPLEMENTATION_REFERENCE.md): the code’s actual modules, data flow, and explicit non-features.
- [Operations and reproducibility](docs/OPERATIONS_AND_REPRODUCIBILITY.md): finite CLI runs, controls, and resource interpretation.
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md): fixed test partitions and promotion criteria.
- [Documentation index](docs/DOCUMENTATION_INDEX.md): all design, research, code, and evidence documents by status.
- [Primary research](docs/RESEARCH.md): related work and its limitations.
- [Decisions](docs/DECISIONS.md): dated scope and design decisions.
- [Experiment records](experiments/README.md): requirements for future measurements.
- [Author](AUTHORS.md).

## History and publication

This repository records project history from its creation onward. Earlier private conversations and local runtime history are not reconstructed as historical commits.

Only deliberately reviewed project materials belong here. Credentials, personal information, private transcripts, third-party books, datasets, model weights, and runtime logs are excluded. Research references retain their original attribution.

No software license has been selected yet.
