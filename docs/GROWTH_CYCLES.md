# Growth and consolidation

Author: [Arnav123-s](https://github.com/Arnav123-s)

The [first structural trial](../experiments/2026-09-05-circuit-learning.md) expands a one-gate foundation into a five-gate transition and measures retention. The state-enabled search stage is scheduled by the curriculum; autonomous growth and repeated cross-task consolidation remain untested.

The learner may grow within a fixed device budget and later consolidate acquired structure. The budget includes persistent state, temporary learning memory, external storage and computation. Beginning another curriculum stage does not renew physical capacity.

## Acceptance criteria

1. Declare the new task and the behavior that must remain supported.
2. Measure the current model and its complete resource account.
3. Attempt a bounded repair or function-preserving capacity addition.
4. Learn using development data and test the proposed successor.
5. Search for equivalent shared structure after acquisition.
6. Measure the consolidated artifact and independently confirm retention and transfer.

Description length and execution cost are separate objectives. Quantization, deletion and imitation require measured output distortion; they do not establish equivalence. For a finite domain, exhaustive checking may be possible. For an unbounded domain, a universal claim requires a proof under specified semantics.

The existing verified-consolidation trial preserved all 196 selected guard answers but broke two earlier correct answers on final confirmation. Its result is documented in the [experiment record](../experiments/2026-09-04-verified-consolidation.md). General library compression remains unimplemented.
