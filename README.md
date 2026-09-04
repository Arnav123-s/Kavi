# Kavi

**Author:** [Arnav123-s](https://github.com/Arnav123-s)

Kavi is a model-first research project for a developmental learner with bounded growth. The model core is the project; the curriculum, evaluator, source gate, and CLI are supporting infrastructure used to teach and measure it under a hard device resource limit.

## Current status

Kavi contains three narrow, implemented model cores: an arithmetic pathway with
a verified local readout; a generated ASCII glyph pathway that compresses
letter/digit evidence into prototypes; and a generated Unicode script-pathway
prototype that learns eleven bounded scalar lanes. A separate scalar contract
preserves one Unicode input exactly before that third core runs. All use finite
runs, candidate-only updates, protected and held-out checks, and visible
terminal traces. They are not a general learner, a textbook-trained model, or
evidence of broad intelligence. See the [model-first curriculum](docs/MODEL_FIRST_CURRICULUM.md),
[Unicode scalar and script stage](docs/UNICODE_SCRIPT_STAGE.md), and
[implementation reference](docs/IMPLEMENTATION_REFERENCE.md) for the exact
code boundary.

The broader developmental architecture remains research. Any new finite stage
must be reviewed and explicitly authorized by the owner before a real run; text
and source stages remain locked behind their separate review gates. Kavi does
not include autonomous source-code modification, background persistence, web
learning, or hardware-limit changes. The proposed replacement for end-to-end
backpropagation and the proposed consolidation mechanism remain open questions.

## Central idea

Learn and grow, test on unfamiliar examples, compress into a smaller representation, verify retained abilities, and use that compact learner as the starting point for the next stage. A stage's progress score can return to zero after promotion, but the learned knowledge must remain. Zero means a new baseline, not empty memory or infinite storage.

The allocated learner size may change. The hard device resource limit does not increase merely because the learner starts another stage. Compression is a research objective, not a guarantee that arbitrary knowledge can fit into one weight.

## Project map

- [Design](docs/DESIGN.md): interpretation, constraints, and unresolved mechanisms.
- [Growth and compression cycles](docs/GROWTH_CYCLES.md): changing learner size under a fixed device ceiling.
- [Model-first curriculum](docs/MODEL_FIRST_CURRICULUM.md): implemented early cores, teaching order, and automation boundaries.
- [Unicode scalar and script stage](docs/UNICODE_SCRIPT_STAGE.md): implemented bounded Unicode signal and glyph-pathway core, with exact limits.
- [Multilingual foundations](docs/MULTILINGUAL_FOUNDATIONS.md): prerequisite-first script, language, original-source, and cultural-protocol plan.
- [People and works catalog](curriculum/people-and-works.json): reviewable global catalog of original works, traditions, and textbook candidates.
- [Source access records](curriculum/access-records.json): direct catalog or archive links; access is not source admission or permission to scrape.
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
