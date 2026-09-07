# An expanding system of learned pathways

Author: [Arnav123-s](https://github.com/Arnav123-s)

## Intended system

Kavi's pathways are intended as a general representation of reusable computation. Chemistry, heat, energy, catalysts, physical systems and quantum descriptions are examples of possible structures, not a fixed inventory of mechanisms the system must imitate.

The motivating analogy is a miniature universe: an initially limited internal system acquires representations of additional relationships and processes, then uses them as components in further configurations. It need not contain those representations at initialization. Teaching should progressively expand what it can construct, interpret and revise. This is a computational analogy; the system is not claimed to simulate every physical process or inherit a physical system's computational resources.

The central learning problem is how experience becomes executable structure. A useful sequence is: infer a candidate relationship, represent its inputs and outputs, compose it with earlier structures, check its consequences, and retain or revise it. Learning the meaning of a description and learning an executable mechanism from it are separate achievements. A stored text or a component named after a physical phenomenon is insufficient evidence of either.

The representation may eventually include operations, relations, constraints, transformations and procedures that propose other procedures. A mechanism can be engineered initially, learned as a composition later, or replaced when a better representation is justified. Earlier valid behavior constrains replacements; earlier wiring need not remain fixed. Incorrect earlier answers should be corrected rather than preserved.

## What the next experiment can establish

The [bounded configuration-reuse experiment](../experiments/2026-09-07-pathway-growth.md) tests a small necessary capability: does a learned computation help acquire a later computation under the same per-task search limits? It uses the existing procedure learner and arithmetic executor. It does not add chemistry laws, learn new execution primitives, infer meaning from literature, or learn the search algorithm itself.

Three questions remain separate:

- Does retaining a configuration improve later acquisition compared with retaining nothing or an unrelated configuration?
- Does the resulting computation save execution work, after accounting for calls into shared components?
- Can the learner discover a new representation or update rule rather than select within a supplied grammar?

The experiment addresses the first two on a narrow arithmetic curriculum. The third remains a research goal. No external-review recommendation is adopted by this experiment.

## Correction and interpretability

Correction is useful when it changes a reusable computation and improves independent answers, while retaining earlier valid behavior. The [correction follow-up](../experiments/2026-09-07-pathway-growth.md) tests this on an intentionally ambiguous arithmetic lesson. A correction label is additional evidence; successful re-synthesis is not by itself learning what "wrong" means, identifying every cause of failure, or improving the learning algorithm.

As configurations grow, a complete low-level trace can become long and difficult to interpret. This is a possible consequence of scale, not a criterion for intelligence. Inspection should support component summaries, dependencies, changes between accepted versions, and expansion into execution details. A shorter or more abstract representation can sometimes become easier to inspect as capability improves.

## Learned internal roles

The intended system need not assign every acquired component a human-authored concept name. A component's role can emerge from how learning connects it to other components and which tasks it helps solve. One human concept may involve many components; one component may participate in several concepts. The owner describes this as Kavi deciding the meanings of its components. Operationally, that means learning their representations and uses, rather than receiving a fixed human taxonomy.

An execution trace reveals operations and dependencies, but does not automatically provide a complete semantic explanation. Human understanding may remain partial. Structural validity, behavioral tests and relevant invariants can still be checked without claiming that every internal role has been interpreted. Conversely, an opaque component is not evidence that it has a useful meaning or greater intelligence.

The current arithmetic experiments use supplied operation names, input types, execution semantics and search rules. Kavi acquires compositions within those constraints. Learning its own general representation, component boundaries and internal semantics remains beyond these experiments. Any claim of progress toward that goal should identify what was supplied, what was acquired, and which independent tasks the acquired representation enables.

## Relation to the earlier study

The [equations-as-components note](EQUATIONS_AS_PATHWAY_COMPONENTS.md) extends the same intent to mathematical models, including quantum state evolution. Their use would require appropriate representations and domain assumptions; none is implemented by the arithmetic experiments.

The [physical-pathway proposal](PHYSICAL_PATHWAY_RESEARCH.md) supplies examples within this broader direction. The [certificate and software study](CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md) records the preceding research and its limits. Their chemistry-specific mechanisms are optional experimental candidates, not the definition of Kavi.
