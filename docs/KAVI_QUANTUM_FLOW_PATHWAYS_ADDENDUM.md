# Complex flow and typed transport

Author: [Arnav123-s](https://github.com/Arnav123-s)

The [structural sharing and quantum study](STRUCTURAL_SHARING_AND_QUANTUM_RESEARCH.md) develops these constraints in detail, compares DreamCoder and Babble, and specifies spectroscopy-inspired probes and conditional quantum backends. Its algebra checks are separate from learning experiments.

The [implemented circuit](CIRCUIT_RUNTIME.md) is classical and uses no amplitude or quantum simulation. Multiple candidates are ordinary explicitly counted search alternatives. The complex-flow mechanisms below remain a separate proposal.

Status: proposed classical numerical experiment.

Complex amplitudes can represent magnitude and relative phase. Interference then follows the chosen algebra. A learned or verified rule must connect that algebra to task correctness; cancellation alone is not a truth test.

## Stable evolution

The continuous system `psi_dot = (-Gamma - iH) psi` is nonexpansive when H is Hermitian and Gamma is positive semidefinite Hermitian. Explicit Euler does not inherit that guarantee for arbitrary steps. In the undamped case, a nonzero-frequency mode grows under every positive Euler step.

A Cayley step preserves norm for Hermitian H, and a split damping operator can produce a contraction. Matrix solves and exponentials have costs that must be measured. Post-step normalization changes the trajectory and can hide integration error.

## Type constraints

Applying a directional type mask to a Hermitian matrix can destroy Hermiticity. Symmetrizing it can reopen a prohibited reverse edge. Keep reciprocal mixing within compatible blocks and represent directional typed transport separately.

A pairwise outer product describes coherence in the selected representation. Calling it entanglement requires a tensor-product subsystem model and a nonseparability criterion. The initial experiment needs only classical complex computation.

Compare learned phases with zero, fixed random and real-valued controls under equal budgets. Section 9 of the [specification](KAVI_ENGINEERING_SPECIFICATION.md) gives the equations and assumptions.
