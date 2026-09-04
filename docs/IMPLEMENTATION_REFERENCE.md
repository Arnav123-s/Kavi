# Kavi implementation reference

Author: Arnav123-s
Status: describes the code currently present in this repository

## Scope

Kavi currently contains deliberately narrow, executable model cores. One learns
from generated lowercase glyphs and decimal digits by compressing evidence into
class prototypes; another learns generated addition and subtraction through a
typed arithmetic pathway; and a third learns eleven bounded Unicode
script-oriented scalar prototypes. A fourth core learns a compact
expression-versus-relation distinction from one locally fingerprinted,
reviewed algebra lesson. An exact one-scalar Unicode contract sits in front of
the third core. The supporting runner makes routing, verification, candidate
promotion, explanation checking, and resource reporting observable before a
broader curriculum is attempted.

It is not a general-purpose language system, a trained textbook reader, a web
agent, a background service, or a self-modifying program.

## Package map

| Module | Responsibility |
| --- | --- |
| kavi.types | Immutable event, pathway, inference, feedback, and metric contracts. |
| kavi.graph | The typed PathwayFabric, deterministic route selection, join, readout, eligibility, and small resource ledger. |
| kavi.learning | Fixed protected and held-out manifests, independent scoring, and candidate-only target learning. |
| kavi.runtime | Finite serial event runtime, visible trace, pause/stop controls, and generated arithmetic curriculum. |
| kavi.cli | Main command-line interface for inspecting paths and running the target-only experiment. |
| kavi.lessons | Structured arithmetic lessons whose explanation and target transformation are locally verifiable. |
| kavi.explanation_learning | Explanation-guided candidate generation with the same independent evaluation boundary. |
| kavi.lesson_runtime | Finite explanation-learning runtime using the standard controls. |
| kavi.lesson_cli | Command-line entry point for the explanation-learning experiment. |
| kavi.source_manifest | Source metadata, rights-status, and lesson-admission validation. |
| kavi.source_cli | Read-only inspection of the curriculum source manifest. |
| kavi.symbol_core | Compact glyph-to-prototype learning core with protected and held-out gates. |
| kavi.symbol_runtime | Finite generated glyph curriculum and visible candidate traces. |
| kavi.unicode_core | Exact one-scalar Unicode contract and compact generated script-pathway prototype core. |
| kavi.unicode_runtime | Finite Unicode contract and script-pathway curricula, fixed manifests, and visible traces. |
| kavi.textbook_core | Compact expression/relation prototypes, a restricted exact symbolic evaluator, and candidate-only promotion. |
| kavi.textbook_runtime | Local-only lesson loader, PDF/extract fingerprint verification, finite source-event trace, pause/stop controls, and protected/held-out readouts. |
| kavi.school | Model-first finite curriculum sequencer, opt-in checkpointing, and hard waiting gates. |
| kavi.school_cli | Command-line entry point for listing or running only declared curriculum stages. |
| kavi.catalog_cli | Read-only review of the people-and-works catalog. |

## Inference path

An ArithmeticEvent carries two operands, an operation, an event identifier, and
a correlation identifier. The pathway fabric splits one event into quantity and
relation facets. A route is eligible only when its input type, output type,
operation scope, capacity, and event correlation agree with the request.

For each eligible facet, Dijkstra route selection chooses the lowest declared
cost compatible path. The two facets then meet at a typed join. The join uses
ordinary complex-number arithmetic to represent a phase-style compatibility
signal. This is a classical calculation, not quantum hardware or a claim of a
quantum advantage. A destructive or insufficient join produces an abstention
instead of an invented answer.

The readout maps a valid joined signal to a raw numeric value, rounds it only
for the displayed exact answer, and reports confidence and uncertainty. The
trace prints the actual selected pipe identifiers, join state, answer or
abstention, verification result, candidate decision, and a small explicit
state estimate.

## Unicode scalar and script-pathway inference

`UnicodeSignalContract.inspect` accepts exactly one Unicode scalar. It preserves
the original character and code point, reports local Unicode metadata, and only
records whether an NFC view equals the input; it does not rewrite the scalar.
An empty string, multi-scalar string, or surrogate is rejected.

The generated script core turns that exact code point into `x = code_point /
0x10FFFF`, then compares it against one learned centroid for each of eleven
declared pathways. It abstains until every pathway has verified support or when
the closest two centroid distances are too similar. A candidate batch may be
promoted only when current, protected, and held-out error do not worsen. The
core keeps compact centroids and support counts, not presented glyphs or a
source corpus.

Its declared examples are single generated scalars; the core is neither a full
Unicode Script-property implementation nor a script/language detector. See
[UNICODE_SCRIPT_STAGE.md](UNICODE_SCRIPT_STAGE.md) for its exact manifest and
limits.

## Reviewed textbook concept inference

The first source-backed core accepts only a compact algebra notation subset.
It converts an input into five structural facets, compares it with two learned
prototype centers, and reports a label only after both have verified support.
A restricted integer-and-fraction evaluator separately checks variable-free
values or relation truth. Unknown variables remain unknown.

Its private lesson loader verifies the approved source record plus exact PDF
and extract SHA-256 fingerprints before exposing a fixed local event manifest.
The core's persistent state holds two five-facet centers, two support counts,
and a promotion count; it does not retain PDF text or a growing notation
archive. See [TEXTBOOK_CONCEPT_STAGE.md](TEXTBOOK_CONCEPT_STAGE.md) for the
mathematics, source boundary, and visible run command.

## Learning path

For a target-only event, the exact arithmetic verifier produces positive,
negative, or neutral feedback.

| Feedback | Action |
| --- | --- |
| Correct answer | Increase support on the active paths. |
| Abstention | Preserve uncertainty; do not claim an answer. |
| Wrong answer | Create candidate readout weights and evaluate them before any promotion. |

Candidate updates are intentionally narrow: only the three readout weights are
changed. The frozen parent stays intact while an IndependentEvaluator compares
parent and candidate on the current event, a protected manifest, and a
held-out manifest. A candidate must improve current raw error while not
increasing protected or held-out mean absolute error. Once the protected set
is sufficiently accurate in the explanation variant, exact protected accuracy
may not decrease either.

This is not end-to-end training. It is a small, auditable local update test.

## Explanation-learning path

The separate lesson experiment creates a VerifiedLesson for each generated
event. A lesson has an event, a rule identifier, a human-readable explanation,
and target readout weights. Its local verifier confirms that the claimed rule
matches the event before it can guide a candidate.

The lesson blends a local error-directed candidate with its verified
scope-specific rule. It still cannot force a change. The same protected and
held-out evaluation policy decides whether to promote it. This lets the code
test the claim that a verified explanation can guide a local update without
letting prose bypass evaluation.

## Curriculum source gate

The public source manifest contains metadata only. It records original URLs,
creators, license classifications, review notes, subjects, and level labels.
No textbook body, paper body, PDF cache, or private source collection belongs
in the repository. A SourceLesson needs an approved source, a locator, a
concept, prerequisites, verifier identity, and an extract fingerprint.

The manifest approves the NASA metadata record and one narrowly reviewed CC BY-SA algebra lesson, and keeps
other source classes quarantined pending document-specific review. See
[DOCUMENT_CURRICULUM_GATE.md](DOCUMENT_CURRICULUM_GATE.md) for the policy.

## Runtime controls and persistence

Every runtime invocation has a finite step count. It uses one serial inference
path per event. One or two evaluator workers may score independent evaluation
cases, but they do not parallelize the causal inference path. The runtime
neither contacts the network nor writes its learned state to disk.

A caller may supply pause and stop file paths. While the pause file exists,
the process waits. When the stop file exists, the next control check ends the
finite run while retaining the in-memory parent only for that process. Kavi
never creates, removes, or ignores either file.

## Files outside the package

| Location | Role |
| --- | --- |
| curriculum/sequence.json | Prerequisite ordering for future curriculum stages. |
| curriculum/source-manifest.json | Reviewed source metadata and admission status. |
| tests | Unit tests for stage 0, explanation learning, source validation, Unicode pathways, and the bounded local textbook core. |
| experiments | Compact, reproducible records of authorized smoke tests. |
| docs | Design proposals, research notes, implementation guides, and operating policy. |

## Explicit non-features

- No downloaded model weights or external model runtime.
- No unreviewed or public-repository raw textbook or paper ingestion.
- No web access from the learner.
- No continuous daemon, scheduled work, or automatic restart.
- No source-code changes by the learner.
- No adjustment of system power, temperature, fan, or hardware limits.
- No claim that this prototype solves open mathematical problems.

Use [OPERATIONS_AND_REPRODUCIBILITY.md](OPERATIONS_AND_REPRODUCIBILITY.md) to
run the code and [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md) to interpret
its results.
