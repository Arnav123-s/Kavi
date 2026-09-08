# PCL: independent continuations and the order barrier

Author: [Arnav123-s](https://github.com/Arnav123-s)

8 September 2026. Interpreter extension and read-only structural diagnostic.

## Result

PCL can now continue several questions independently from one active situation. Each continuation inherits the current phase state and the same immutable circuit, without retaining or replaying the original input. This is supplied execution machinery, not a learned world model.

The three successful [classification circuits](2026-09-08-pcl-classification.md) are insensitive to event order. Each reaches exactly one joint state across all 24 permutations containing one occurrence of each of its four event symbols. This is an appropriate property for those measurement inputs, but insufficient for interpreting ordered relationships. No new teaching, label inspection or final-bank tuning occurred.

| Saved circuit | Couplings | Permutations | Distinct final states | Artifact bytes |
| --- | ---: | ---: | ---: | ---: |
| regions-7 | 0 | 24 | 1 | 457 |
| regions-19 | 0 | 24 | 1 | 457 |
| regions-41 | 0 | 24 | 1 | 437 |

Artifact SHA-256 digests:

- Seeds 7 and 19: `1ae9b56a2fd8fc68b40cb149327773df9e2d8f4c7f247c362a2aed43c504a84f`.
- Seed 41: `9931db4971df21b87f59cfcf05b086f51617ff0a228011aa0cc6906d6aa9a6c4`.

## Why the order result is stronger than 24 examples

For a circuit with no couplings, let d(e) be the vector of summed impulses for a recognized event e. Its transition is coordinatewise modular addition:

$$T_e(z) = z + d(e) \pmod{\mathbf m}.$$

Therefore, for any two recognized events,

$$T_a(T_b(z)) = T_b(T_a(z)).$$

Any permutation of a recognized event sequence with the same multiplicities has the same final state and readout. This holds for all initial states, not just the permutations checked. The assumptions are no couplings, fixed event impulses and final-state-only readout. Unknown events instead fail the invocation. An upstream encoder could encode order into event identities, but then that encoder would be responsible for the distinction.

The existing coupled interpreter can distinguish event order in its regression fixtures. Having a grammar capable of ordered behavior does not establish that teaching has acquired useful ordered behavior. Nor would merely requiring a nonzero coupling count establish it: couplings can be inactive or behaviorally irrelevant.

## Independent continuations

Let a prefix p produce current state z under circuit K. For any suffix q, the implementation must satisfy:

$$\operatorname{finish}(\operatorname{continue}(\operatorname{fork}(z),q))
=\operatorname{predict}_K(pq).$$

This equality assumes unchanged K and sufficient execution budget. Branch execution must not change z or a sibling branch. Only a live, nonfailed invocation can branch. The parent remains open; each child releases an answer only when its caller finishes that child. A failed child cannot release an old answer.

```text
input prefix -> current phase state
                         |
                         +-> continuation A -> finish A
                         |
                         +-> continuation B -> finish B

The original state remains available. All paths share one work ceiling.
```

The implementation is `PhaseActivity.fork()`. It adds no parent pointer, transcript, example table or answer cache. Frozen configuration and phase tuples can be shared safely; processing another event replaces the child's phase tuple. This does not make working memory free: every live branch has a runtime object, and diverging branches retain their own current states. The caller owns branch lifetimes. This API does not add a branch scheduler, semantic bindings or a learned choice of which question to explore.

Forking charges one named operation per phase coordinate and shares the original Work instance. Repeated branching cannot obtain a fresh work budget. Exhaustion during fork leaves the parent's state intact; continued execution still observes the exhausted shared budget. Named operations are an accounting proxy, not CPU instructions.

## Verification and cost

All 298 repository tests passed in 9.762 seconds after this extension. Historical artifact, implementation and documentation checks also passed.

Four new regression methods cover independent questions, replay equivalence for all 31 suffixes of length zero through four over a two-symbol alphabet, isolated failure, closed-state rejection, absence of history fields and shared-budget interruption. These handcrafted fixtures test software semantics; they are not synthetic training data or evidence of learned language.

The read-only diagnostic charges 864 named operations per saved circuit, 2,592 in total. One local execution took approximately 0.0021 wall seconds; the process CPU timer reported zero at its resolution. This is not a performance benchmark. Peak memory was not measured. Saved circuits and their historical classification results are unchanged. Their original runtime source is recoverable at publication commit `8f07b7b11e7979c687b277692b5beae5f06f1b36`; the present runtime adds branching.

```powershell
python -B -m unittest tests.test_phase_branching tests.test_phase_configuration
python -B -m scripts.check_pcl_state_branching --run-dir runs/pcl-classification-20260908
```

The diagnostic requires the ignored local checkpoints. It does not acquire data, fit candidates or restart a curriculum.

## Next learning requirement

The next source-based course must require relationships whose answers depend on roles or order, rather than reward only unordered measurement grouping. Its separately reviewed packet must distinguish original source content from supplied annotation and output encoding. Split related variants together to prevent leakage. Select candidates using teaching and development only, then measure unfamiliar combinations once on a frozen final bank.

Required comparisons are uncoupled versus coupled circuits, equal total search budgets, replay versus independent continuation, and correction with earlier valid outcomes protected. Use the same situation for several source-supported questions. Do not label a continuation a counterfactual unless the circuit actually supports replacing the relevant premise; appending another event alone does not guarantee that semantics.

This revision closes the independent-continuation execution gap. Learned bindings, relational transformations, correction scope, natural-language interpretation and a persistent learned world remain open. No advance to a higher educational level is claimed.
