# Learning phase-region rules

Author: [Arnav123-s](https://github.com/Arnav123-s)

8 September 2026. Implemented readout extension; source-based results are recorded separately.

## Problem

The first PCL readout assigns output ports to exact joint phase states. A changed measurement can reach a new state and receive no answer even when a broader distinction could apply. This is an expressivity limitation in the readout, not evidence that any particular generalization is correct.

The extension permits a rule to constrain each phase to an inclusive interval. For rule r, bounds l_ri and u_ri and output c_r:

$$R_r(p)=\bigwedge_i(l_{ri}\leq p_i\leq u_{ri}).$$

An exact phase is the special case l_ri=u_ri. The intervals use the numbered phase coordinate; they are not circular intervals spanning the modulus boundary. Representing such a set requires multiple rules. The choice of interval geometry is supplied by the implementation.

## Acquisition

Execute the teaching and protected sequences through a complete candidate circuit. If two final states are identical but require different outputs, reject the candidate. Otherwise collect their distinct final states in temporary teaching workspace.

Process these states in sorted order. For a state with label c, try extending an existing c-labelled region by its coordinate-wise bounding box. Admit that extension only if no supplied state with another label is contained within it. If no compatible extension exists, create a point region. The retained model contains the resulting bounds and output ports; it contains no sequences or source-row identifiers.

Bounds are learned from evidence, but the covering algorithm is engineered. Its order affects the chosen covering. This is supervised rule covering over recurrent states, not a novel proof of abstraction, learned causal semantics, or a complete internal-world model. Regions can still retain overly specific examples.

## Inference and ambiguity

An invocation consumes its complete input, then checks all readout rules against its current phases. One or more matching rules with the same output release that port. No matching rule is unresolved. Matching rules with different outputs are also unresolved. Rule list order cannot choose the answer.

Although every admitted region excludes opposite labels at the teaching points, regions of different classes may overlap elsewhere. The final ambiguity rule handles those unseen intersections without guessing. Finite teaching consistency does not certify the rest of the state space.

Inference performs conjunction checks, not a nearest-example search. The source table is outside deployed inference. This distinction does not imply zero memory: rules, phase values, circuit definitions and the interpreter occupy storage.

## Whole-circuit learning

`reconstruct(..., readout='regions')` uses the same stable template and complete candidate assembly as the exact-state comparison. Each candidate receives a newly acquired readout. Selection still uses the declared correction and protected banks. No connection is patched into the active generation during inference, and an interrupted reconstruction leaves that generation available.

The original exact readout remains the default. Existing exact patterns remain valid. The [implementation](../kavi/phase/regions.py), [runtime](../kavi/phase/runtime.py), and [regressions](../tests/test_phase_regions.py) separate covering, execution and verification.

## What the checks establish

Four new regression methods check interpolation to an unshown phase, contradictory overlapping regions, an opposite-class state blocking expansion, serialization, invalid bounds and interruption. Their small authored fixtures are not curriculum data or capability results.

The [classification protocol](PCL_CLASSIFICATION_PROTOCOL.md) measures both readout forms on original Iris measurements with the same initial counter circuit, partitions and candidate counts. A successful result must identify whether the learned dynamics changed. If only output regions improved, the justified claim is readout classification; the experiment would not show that coupled pendulums or a learned internal world caused the improvement.
