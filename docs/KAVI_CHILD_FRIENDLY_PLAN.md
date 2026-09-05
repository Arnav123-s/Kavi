# Project overview

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi learns how to perform an operation by changing a small circuit. For addition, the goal is a pathway that combines new quantities correctly. It does not need to remember each equation used while teaching it.

When the pathway gives a wrong answer, the teacher supplies a counterexample. The learner searches for a corrected circuit and checks that earlier correct behavior is preserved. The same repaired pathway then processes other inputs.

The first implemented experiment learns a five-gate addition circuit. Three trials passed the declared unseen cases, exhaustive eight-bit additions and larger inputs up to 1,024 bits. The circuit's bit-processing loop and one temporary state register were supplied. Learning those structures and general language remains future work.

Run `python -m kavi circuit --help` to inspect the live interface. The [runtime guide](CIRCUIT_RUNTIME.md) explains the commands; the [experiment record](../experiments/2026-09-05-circuit-learning.md) gives the measurements and limits.
