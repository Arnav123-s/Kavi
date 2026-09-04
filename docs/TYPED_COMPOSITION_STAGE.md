# Typed compositional pathways

Author: Arnav123-s

Status: implemented bounded Phase 2A experiment

## Why this is the next phase

The first unified-circuit experiment showed that Kavi could form compact
routes, reuse earlier sources through jump adapters, reject regressions, and
replace an active parent safely. Its largest limitation was that most tasks
still arrived as prebuilt feature vectors. The routes selected an answer, but
they did not yet form a deeper reusable computation.

Phase 2A tests the next part of the pathway-first idea: a route may trigger
other verified routes, join their typed outputs, and become a larger executable
path. Algebra is not the target. Arithmetic, glyph, and script paths are small
available building blocks used to test a domain-independent composition rule.

## Child-simple picture

Imagine labeled pipes:

```text
glyph pipe -----> glyph-kind path ------\
                                         equality path ---\
script pipe ----> script path ----------/                  \
                                                            select path --> answer
number pipe ----> add/subtract paths -----------------------/
```

The pipes do not vote as separate experts. Each pipe has an input and output
type. A connection may form only when the shapes fit. A nested task sends
information through several small paths, then joins their results in a later
path. At most four source paths are placed in one activation wave on this
device; a larger tree proceeds through several trace groups. Actual execution is serial; these groups are not parallel worker scheduling.

## Persistent learned object

A composition route stores:

```text
(operator, ordered input types, output type, target path,
 source path IDs, support, resistance, coupling, phase, revision)
```

It does not store the teaching program, its literal values, expected answer, or
display text. Those exist only in the runtime evaluator. State schema 2 adds a
`composition_routes` collection while retaining backward loading for schema 1.

The route contract is hard typed. For example:

```text
add : (integer, integer) -> integer -> path/arithmetic/add
glyph-kind : (scalar) -> concept-label -> task/glyph-kind
same-label : (concept-label, concept-label) -> boolean
```

A rule cannot relabel an arithmetic target as a Boolean path or send a scalar
into an integer input. An unknown signature abstains instead of searching
unrelated paths.

## Execution

For a literal node, the result is its temporary typed value. For a call node
with children `c_1 ... c_m`, Kavi first executes the children, obtains their
types, and selects the exact compatible learned route:

```text
r = route(operator, type(c_1), ..., type(c_m))
value(node) = target_r(value(c_1), ..., value(c_m))
```

The active source set contains the operator detector, input-type paths, target
path, and paths selected by the children. It is divided into waves of size at
most `B = 4`:

```text
W_k = sources[kB : (k + 1)B]
```

For learned adapters entering route `r`, the classical complex amplitude is:

```text
      c_r
A_r = ------------------------- sum_j g_j exp(i(theta_r + theta_j))
      (1 + R_r) sqrt(max(1, J))

intensity(r) = |A_r|^2
```

`c_r` is coupling, `R_r` resistance, `g_j` adapter conductance, and `J` the
number of conducting jumps. These are ordinary complex-number calculations on
classical hardware. “Quantum-inspired” describes interference-like routing
math, not a quantum computer, physical superposition, or quantum advantage.

The executor has hard limits of eight tree levels and 64 nodes by default. It
evaluates both branches of the current integer-selection path, making the
both branch computations visible while preserving a finite budget. Arithmetic operands are limited to magnitude 2^52 because the underlying transform uses floating-point values. Scalar inputs reject surrogate code points.

## Learning and replacement

The teacher supplies one verified structural contract, including its target. This installs a typed connection; it does not infer that connection from examples. Equality, selection, features, and input trees are supplied by software. The displayed route score is heuristic, not a calibrated probability. It does not train Kavi
by adding the evaluator programs to model memory. A candidate adds or reshapes
only that composition route and the small adapters entering it:

```text
support' = support + 1
R' = max(0.08, 0.90 R)
c' = min(1.50, c + 0.06)
```

Before promotion, the candidate must:

1. improve the current contract checks;
2. not regress cumulative protected composition programs;
3. not regress cumulative held-out composition programs;
4. retain 100% of the earlier glyph, arithmetic, Unicode-contract, script, and
   notation checks; and
5. make an explicit structural change.

The complete parent is then frozen in the ignored run archive with
`active_during_inference: false`. Only the promoted child remains active.

## Implemented contracts

| Operator | Input -> output | Reused target |
| --- | --- | --- |
| `add` | two integers -> integer | learned addition transform |
| `subtract` | two integers -> integer | learned subtraction transform |
| `glyph-kind` | scalar -> concept label | learned letter/digit task paths |
| `unicode-script` | scalar -> concept label | learned script-oriented paths |
| `same-label` | two concept labels -> Boolean | exact equality transformer |
| `select-integer` | Boolean and two integers -> integer | exact typed selector |

The protected and held-out sets influence promotion and are validation sets. A separate seeded 64-program audit exposed two baseline errors; automatic corrective teaching and a fresh harder exam are documented in DEVELOPMENTAL_TEACHING.md. The deepest validation checks combine script classification, label comparison,
nested addition and subtraction, and selection. Their literal values and tree
shapes do not occur in the route contracts.

## What success means—and does not mean

A passing Phase 2A run means that this implementation can learn six typed
connections, execute its fixed unseen program manifest, preserve all earlier
checks, serialize compact structural state, and expose each call in the live
pathway feed.

It does not mean Kavi understands words, reads textbooks, learns arbitrary
operators from prose, has infinite context, proves mathematics, or has
frontier-level intelligence. The next natural-language stage still requires a
sequence-aware text representation, language-specific boundary and morphology
paths, approved exact sources, qualified review, and independent held-out
tests. Phase 2A builds the compositional machinery without pretending that
machinery is already language understanding.
