# Adaptive connections and local repair

Author: [Arnav123-s](https://github.com/Arnav123-s)

A connection can carry a state-dependent response rather than a single constant gain. Candidate mechanisms include a decaying state, a gated residual, a frequency-selective recurrence or a typed executable operation. Each introduces different state and learning costs.

The implemented repair connection is a small context-dependent residual with a learned amplitude and phase. Eight connectors add 56 parameters. Its zero-amplitude initialization preserves the initial function; subsequent learning can change old answers.

The [small-repair experiment](../experiments/2026-09-04-small-repair-connections.md) found modest improvements alongside forgetting. The [forward-repair experiment](../experiments/2026-09-04-forward-repair.md) found identical final correctness for paired eight- and nine-connector variants. Neither result supports a general retention guarantee.

For structural repair, identify the failing executed path, enumerate well-typed local changes and verify their effect on callers. Locality in a graph does not guarantee locality in behavior when a component is shared. See sections 6 and 8 of the [specification](KAVI_ENGINEERING_SPECIFICATION.md).
