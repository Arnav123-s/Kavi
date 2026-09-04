# Reviewed textbook concept stage

Author: Arnav123-s

## What now runs

`textbook-concepts-expressions-relations` is Kavi's first deliberately narrow
source-backed model stage. It teaches one distinction from a reviewed algebra
lesson: whether a small symbolic notation denotes a number-like expression or
a truth-valued relation. It can also make a bounded exact check for
variable-free notation.

It is not a general language model, a general algebra system, evidence of
textbook comprehension, or a claim of multilingual ability. It is a compact
experiment in turning a reviewed lesson into an auditable pathway with
protected and held-out checks.

## Source and rights

The admitted source is *Basic Algebra with Applications, 6th edition* by Ivan
G. Zaigralin. Its [Open Textbook Library record](https://open.umn.edu/opentextbooks/textbooks/basic-algebra-with-applications)
identifies the work and the reviewed edition declares [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

The public repository contains only the source record, license link, lesson
identifier, and program logic. The reviewed PDF, a small private extract, the
event manifest, and their SHA-256 fingerprints remain local under `private/`,
which Git ignores. Kavi refuses the lesson unless both the PDF and extract
match the fingerprints declared in that local manifest.

## What the small model stores

The source notation passes through a fixed pathway:

```text
notation ingress
  -> five structural facets
  -> expression/relation compact prototypes
  -> independent exact response
```

For notation `n`, the feature vector is

```text
f(n) = (
  relation-sign count,
  min(arithmetic-operator count, 4) / 4,
  min(variable count, 4) / 4,
  min(digit count, 4) / 4,
  min(notation length, 16) / 16
)
```

There are exactly two prototypes: one for `expression`, one for `relation`.
Each stores a five-number running center and a support count. For verified
features `f`, a prototype center `c`, and prior support `s`, the update is

```text
c_next = c + (f - c) / (s + 1)
s_next = s + 1
```

The persistent learning state is therefore two five-dimensional centers, two
support counts, and one promotion counter: 13 explicitly counted scalars.
It does not retain PDF text, lesson strings, a token corpus, hidden prose
memory, or a growing example store.

Inference uses Euclidean distance to the two centers. It abstains until each
prototype has verified support or if the two distances are too close. Its
reported confidence is a relative distance gap, not a probability or a broad
truth claim:

```text
confidence = |d_expression - d_relation| / (d_expression + d_relation)
```

## Independent checks and promotion

The syntax checker independently determines whether the notation has a single
relation sign. The exact evaluator permits only a deliberately small algebra
notation subset and evaluates variable-free integer arithmetic through a
restricted abstract syntax tree with rational arithmetic. Inputs involving
unknown variables report that their value or truth is unknown rather than
inventing one.

The runtime receives a private fixed manifest split into train, protected, and
held-out partitions. A candidate state is promoted only when it has more
verified support and does not worsen error on the current batch, protected
examples, or held-out examples. A rejected candidate leaves the parent state
unchanged. Every local run is finite, shows its decisions line by line, and
honors pause and stop files.

## Run it visibly

After the four completed generated foundations, run one source-backed stage:

```powershell
python -u -m kavi.school_cli --max-stages 1 --interval-ms 750 --state-file runs\kavi-school-state.json
```

The terminal prints each notation, the active hard path, structural facets,
current model response, candidate gate, compact resource ledger, and
protected/held-out readouts. It never downloads a book or starts a background
worker. If the local private lesson is absent or its fingerprint is wrong, the
stage visibly refuses to run.

To pause a running pass, create the selected pause file; remove it to resume.
To stop, create the selected stop file. Both controls are explicit owner
controls, not hidden persistence.

## Next boundary

This stage does not unlock the language stage. Reading definitions, prose,
proofs, or entire books needs a new text representation, a language-specific
verifier, source-by-source review, and tests that demonstrate transfer beyond
this small symbolic distinction.
