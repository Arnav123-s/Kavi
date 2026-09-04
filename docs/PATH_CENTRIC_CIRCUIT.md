# Path-centric adaptive circuit

## Implemented status

Kavi now has one experimental circuit state that persists across every
currently runnable curriculum stage. The learned objects are whole routes and
small jump adapters. Individual elements only detect, gate, resist, retain a
temporary event signal, join, loop, jump, or transform flow. No individual
element is treated as a concept or a thinking unit.

This implementation is a bounded classical experiment. It is not a language
model, quantum computer, general learner, calculus system, or demonstration of
frontier intelligence. Algebra is only the first source-backed integration
example. The route-and-adapter mechanism is task-independent by design, but
other domains remain unimplemented until they have their own representations,
lessons, verifiers, and retained-skill tests.

## What the active brain contains

The active state contains:

- categorical routes, each with a task context, output, learned shape, source
  paths, support, resistance, coupling, phase, and revision;
- arithmetic transform routes with a verified local transformation;
- jump adapters connecting reusable source paths to later routes;
- identifiers for externally verified foundation paths; and
- a promotion count.

It contains no textbook pages, lesson strings, questions, answers, runtime
logs, or archived parents. Those boundaries are checked by tests.

The same spelling or symbol can participate in different contexts without
forcing the same meaning. A route's `task_id` is a hard context contract. For
example, a learned letter route may supply an algebra route, while the algebra
route's context and relation switches determine the symbol's algebraic role.
Changing the algebra route does not rewrite the glyph route.

## Flow and sparse activation

Each event produces a small set of source-path activations. The runtime divides
them into bounded waves, with at most four simultaneous paths by default.
Inactive paths are not evaluated as active sources. Later stages can activate
earlier learned paths:

```text
glyph/digit ----\
glyph/letter ----+--> jump adapters --> notation/expression or notation/relation
arithmetic/add --+
relation switch -/
```

The algebra lesson therefore does not create copies of alphabet, digit, and
addition knowledge. It creates small connections from those already verified
routes to the new context route.

## Classical quantum-inspired route score

For a normalized input shape `x` and a route center `mu`, Kavi first computes
the root-mean-square distance

```text
d(x, mu) = sqrt(sum_i (x_i - mu_i)^2 / D)
```

For the active jump adapters `J_r` entering route `r`, the classical complex
amplitude is

```text
                    c_r                 1
A_r = ------------------------------- * ------- * sum_j g_j a_j exp(i theta_j)
      (1 + R_r) sqrt(max(1, |J_r|))     eps + d
```

where:

- `R_r` is route resistance;
- `c_r` is route coupling;
- `g_j` is adapter conductance;
- `a_j` is the current source-path activation;
- `theta_j` combines route phase, adapter phase, and a bounded mismatch phase;
  and
- `eps` prevents division by zero.

The observable route intensity is `|A_r|^2`. The strongest compatible route is
selected only when its normalized margin over the second route exceeds the
declared confidence floor. Otherwise Kavi abstains.

This uses complex numbers, phase, constructive combination, and competition as
engineering tools. It does not imply physical superposition, entanglement,
measurement collapse, quantum advantage, or quantum hardware.

## How a pathway changes

For support count `n`, a verified example updates only its target route:

```text
mu' = mu + (x - mu) / (n + 1)
R'  = max(0.08, 0.90 R)
c'  = min(1.50, c + 0.06)
```

An existing jump adapter updates its conductance with the same bounded running
mean. A missing connection may create one small jump component. Unrelated
routes remain byte-for-byte equal in the candidate state.

Every change is first made in an isolated candidate. The parent remains frozen
while the candidate answers:

1. the current teaching batch;
2. protected earlier cases; and
3. held-out unfamiliar cases.

A candidate is promoted only when it increases verified support, does not
worsen any of those error counts, and makes at least one explicit structural
change. The external curriculum gate then requires the stage's fixed accuracy,
including 90% protected and held-out accuracy for the reviewed textbook stage.

## Active replacement and frozen archives

Before promotion, the complete parent state is written under the run's local
`archive` directory with `active_during_inference: false`. Promotion then
replaces the one active in-memory state. The core has no archive lookup during
inference, so old routes and components are not part of the active brain and
cannot vote, retrieve, or silently influence an answer.

Archives exist only for evidence and deliberate recovery research. Kavi does
not automatically restore or consult them when performance changes.

## Currently runnable curriculum

The unified runtime executes, in prerequisite order:

1. generated lowercase ASCII letter and digit routes;
2. exact generated addition and subtraction transform routes;
3. exact Unicode scalar preservation;
4. eleven generated script-oriented scalar routes; and
5. one fingerprinted local textbook lesson distinguishing expressions from
   relations.

It then stops at `word-forms-and-definitions`, because word composition,
sentence meaning, qualified multilingual review, and the necessary source
lessons do not yet exist. Algebraic manipulation, calculus, literature,
general conversation, autonomous browsing, and source-code self-modification
are not implemented.

## Live views

Run the visible multi-tab launcher from PowerShell:

```powershell
.\scripts\start-live-pathways.ps1
```

It opens one Windows Terminal window with separate tabs for:

- the finite curriculum controller;
- model answers;
- active waves, candidate routes, intensities, and jump components;
- proposed route changes, regression checks, promotions, and archives;
- randomized protected and held-out grading; and
- pause, resume, stop, and status commands.

Every viewer reads one ignored local JSONL feed. Viewers never train the model.
The controller waits briefly so all feeds can attach, then completes or stops
at a declared gate. It does not remain as a background service.

The displayed numeric payload estimate counts explicit floating-point model
state only. It excludes Python objects, interpreter memory, terminal processes,
log files, archives, operating-system caching, and source files; it must not be
used as total memory consumption.
