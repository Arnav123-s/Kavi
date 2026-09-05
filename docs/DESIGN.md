# Architecture

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi investigates a learner whose acquired knowledge takes the form of reusable executable procedures. Learning changes typed program graphs; consolidation replaces redundant computation while preserving a specified behavioral contract.

The repository currently implements a symbolic pathway circuit and a separate complex recurrent text model. The symbolic circuit receives operation contracts from its curriculum. The text model learns numerical parameters through backpropagation. General program acquisition and library consolidation are the next research stage.

The [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md) defines the intended representation, current equations, evidence and development plan.

## Design decisions

- Use typed operations with explicit failure and execution-cost semantics.
- Begin with pure, exactly verifiable list, string and arithmetic tasks.
- Search for local repairs before expanding the grammar or capacity.
- Extract shared procedures only from acquired solutions.
- Distinguish behavior-changing repair from equivalent consolidation.
- Count model, optimizer, replay, search and archival storage separately.
- Compare new mechanisms with simple synthesis and recurrent baselines.

Backpropagation remains available. Local learning and physical dynamics are experimental alternatives whose value must be demonstrated under matched budgets. The [program-learning design](PATH_PROGRAM_LEARNING.md) is the primary implementation direction; the [physical dynamics note](KAVI_PHYSICS_NATIVE_CORE.md) defines a separate hypothesis.
