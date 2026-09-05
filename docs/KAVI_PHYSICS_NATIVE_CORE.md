# Physical dynamics research

Author: [Arnav123-s](https://github.com/Arnav123-s)

The working [discrete circuit learner](CIRCUIT_RUNTIME.md) performs Boolean operations and structural search. It has no physical energy dynamics. The framework below is a separate research hypothesis, not an account of the measured addition result.

Status: unimplemented hypothesis. Mathematical revision dated 5 September 2026.

The proposed core uses coupled state variables, sparse transport, dissipation and a learning signal. A useful physical interpretation requires a defined energy and a consistent relationship between the state dynamics and parameter updates.

## Energy balance

Gating the force in `q_dot = p/m`, `p_dot = -g grad(V) - gamma p` does not generally make kinetic energy plus V decrease. Its derivative contains `(1-g)(p/m) dot grad(V)`, whose sign is unrestricted.

Use a port-Hamiltonian form `s_dot = (J-R) grad(H) + Bu`, with skew-symmetric J and positive semidefinite R, as an analyzable starting point. A gate on a coupled position-momentum flow must be represented consistently in both coupling blocks. Changing masses, delays, input and noise need additional energy accounting.

## Learning

Equilibrium learning requires an energy-derived update and accurately settled free and nudged states. A fixed small number of steps has no general gradient guarantee. Derive parameter updates from the actual potential rather than substituting a correlation rule from a different energy.

First test a four- to eight-cell quadratic system with a known equilibrium and analytic gradient. Measure integration error, gradient error, settling cost and sensitivity to step size. Add nonlinear potentials only after those checks pass.

## Retention and memory

Importance-dependent inertia, state noise and structural splitting are hypotheses. None guarantees preserved answers. A unique equilibrium determined only by the current input also needs additional state to represent sequence history.

Section 9 of the [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md) contains the corrected derivations, noise convention, numerical stability conditions and comparison plan. [Port-Hamiltonian systems on graphs](https://arxiv.org/abs/1107.2006) and [equilibrium propagation](https://arxiv.org/html/1602.05179v5) are the principal research references.
