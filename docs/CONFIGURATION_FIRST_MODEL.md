# A mostly stable network with changing configurations

Author: Arnav123-s

Status: clarified design target; partly implemented

## The owner's intended learner

The network's physical budget should change rarely. Learning should mostly
change local settings, which connections conduct, and how existing components
combine. A pathway is the flow created by a configuration; it need not be a
permanent separately allocated object for every skill.

The small neuron-like components act as switches, adapters, joins, loops, and
jumps. They control information flow. A question may use several overlapping
paths, leave one partway through, and enter another through a compatible
connection. An advanced task can reuse configurations already useful for
language, arithmetic, and other skills.

A new skill should first try a new arrangement of existing resources. If a
smaller shared arrangement performs well on both the new and older tasks,
use it. A small context-specific adapter may preserve an older behavior while
the common part becomes simpler. Add physical capacity only when tested
reconfiguration and small adjustments cannot meet the required scores.

Algebra is an example of this general behavior, not a dedicated architecture.
Using a letter in algebra must not damage language use of that letter. Tests
must check both contexts. Merging or splitting a pathway refers to changing
the active shared computation; it does not require keeping both previous
whole networks active.

## Development objective

Let the model have a component pool B, reusable connections E, local settings
theta, and an input-dependent activation configuration a(x). Its answer is:

```text
y = execute(B, E, theta, a(x), x)
```

Search over E, theta, and a before expanding B. For a candidate configuration,
first require the new-task mastery threshold and protected old-task retention.
Then prefer lower added capacity, lower active computation, and simpler
connections. A proposed cost for future measured experiments is:

```text
cost = alpha * added_component_bytes
     + beta  * active_connection_count
     + gamma * measured_execution_work
     + delta * stored_configuration_bytes
```

The terms and coefficients must be fixed before comparison. A complicated
configuration that loops excessively or activates unnecessary paths should
lose to an equally accurate simpler one. Parameter count alone is insufficient:
temporary state, traversal steps, source tables, and execution time also cost
resources. Rare growth remains possible within an explicit budget.

## What the code currently demonstrates

- Configuration-only correction of an existing categorical route.
- Reuse of existing glyph, script, and arithmetic routes by supplied typed
  composition connections.
- External candidate evaluation and protected earlier-skill checks.
- Preference for passing updates with no newly allocated route or adapter.
- Replacement of the active state, with old parents kept outside inference.

The live corrective experiment retained 23 routes and 61 adapters before and
after the correction. One Han route and its existing connection settings
changed; no new route or adapter was required.

## What still needs implementation

The present state explicitly allocates routes and adapters. It is not yet a
general fixed component pool with discovered transient paths. Most input
features and typed operator contracts are supplied. It cannot autonomously
learn arbitrary cross-path jumps, merge and split shared subcomputations,
discover a better architecture, or preserve language understanding while
learning algebra, because language understanding is not implemented.

The next core experiment should therefore test learned configuration changes
over shared components, including a compact common subpath plus a small
context adapter. It needs two independently specified tasks, protected cases
for both, new combinations, and a direct comparison against keeping separate
paths. Success requires measured correctness and lower total cost, not merely
renaming parameter updates as a new pathway.

Complex phase calculations may be one routing mechanism to test. They run on
classical hardware; they do not provide physical quantum parallelism or
unlimited memory. A finite configuration can capture useful rules and
regularities, but cannot retain arbitrary unlimited information losslessly.

See [DEVELOPMENTAL_TEACHING.md](DEVELOPMENTAL_TEACHING.md) for the external
teacher and [TYPED_COMPOSITION_STAGE.md](TYPED_COMPOSITION_STAGE.md) for the
currently implemented computation.

## Mathematical shortcuts worth studying

Two primary research records illustrate that quantum-inspired mathematics can
lead to efficient classical computation under specific conditions:

- [Vidal, Efficient classical simulation of slightly entangled quantum computations](https://arxiv.org/abs/quant-ph/0301063): restricted entanglement permits compact representations and efficient classical simulation. The cost still depends on the amount of entanglement; this is not a universal shortcut for arbitrary quantum computation.
- [Tang, A quantum-inspired classical algorithm for recommendation systems](https://arxiv.org/abs/1807.04271): under stated matrix and sampling-access assumptions, classical sampling reproduces a recommendation task previously associated with a proposed exponential quantum advantage. Input access and representation costs are part of the conditions.

The primary abstracts were inspected for these narrow claims; this entry does
not claim a full-paper reproduction. They are research references, not admitted
training text.

For Kavi, possible experiments include shared subexpression reuse, sparse
activation, compact factorized transformations, and phase-based joins. Each
must compete with a simpler classical baseline using the same tasks and
resource accounting. A mathematically equivalent shortcut is preferable when
it preserves the required outputs at lower cost. An approximation must expose
its error. No such result has yet established a quantum-inspired advantage
for the current Kavi core.
