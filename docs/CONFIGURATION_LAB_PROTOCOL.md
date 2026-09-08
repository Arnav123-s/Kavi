# Compositional learning and equation experiments

Author: [Arnav123-s](https://github.com/Arnav123-s)

7 September 2026. Recorded before the live experiment. This protocol tests part of the [relational configuration design](REUSABLE_RELATIONAL_CONFIGURATIONS.md).

## Configuration and controls

Use one visible worker with Pause, Resume and Stop. The worker has a five-minute wall-clock limit, including pauses, a 512 MiB observed working-set ceiling and a five-million-unit counter ceiling per measured phase. The counter combines operation counts and processed metadata bytes as a conservative stopping rule; it is not a physical performance unit. Count its constituent fields separately. The graphical display has a separate process and is outside the worker-memory measurement.

Keep complete examples, execution records and logs in a fresh ignored run folder. Publish compact results, acquired configuration definitions, dependency fingerprints and this protocol. Record source hashes, Python version, wall time, CPU time, display pacing, process memory and local evidence size. Do not train on the final bank or use its outcomes to choose a candidate.

## Shared representation and local learning

Primitive kernels, identity connections and composed pathways use one configuration interface. A composed configuration may call another composed configuration. Definitions share structure; calls hold their own temporary values. The implemented graphs are acyclic and have one output. General relational feedback, learned scheduling and learned applicability conditions remain outside this experiment.

Load the earlier acquired arithmetic library. Supply an outer graph that adds two inputs, passes that intermediate and a third input to one missing configuration, and adds a fourth input to its result. The missing configuration is learned from final numerical answers. The boundary of the unknown part is supplied; automatic fault localization is not claimed.

Enumerate the same 338 zero-, one- or two-call graphs over acquired addition, subtraction and multiplication in both arms. Compare recomputing the complete outer graph for each candidate with retaining the known prefix values during that teaching transaction. Use four authored lessons with target `(x+y+z)^2+w`, followed by 48 promotion examples and 128 final examples. Seeds are 95001 and 95002 respectively. Final integer inputs are outside the teaching range. Count all candidates, failed candidates, prefix preparation, executions and acquired-arithmetic work. The local cache is discarded after teaching.

After promotion, retain the inferred subconfiguration and expand the hierarchy into a flat execution schedule. Bind the expansion to every contributing definition and the supplied substrate. Count expansion and guard work. A known path executes with no candidate search. Check all 256 input pairs from zero through fifteen for each of the earlier add and multiply operations.

## Correction and invalidation

Begin a separate provisional rule with the ambiguous lesson `(2,2) -> 4`. Record its multiple consistent candidates and the deterministic tie choice. This intentionally permits a provisional answer so that the correction mechanism can be tested; ambiguity must remain visible in the report. Attach a wrapper and retain its expanded execution schedule.

Use `(2,3) -> 6`, `(3,4) -> 12` and `(1,5) -> 5` as correction evidence, retaining the first valid lesson. Learn a successor under the same 338-candidate grammar. The earlier schedule must reject its changed dependency. As a negative control, bypass that check and record the resulting errors. Re-expand the corrected wrapper and evaluate 128 new pairs with seed 95003. Check that unrelated acquired addition and multiplication still work.

## Configurations can produce configurations

Apply a supplied chain/product-rule transformer to the learned squared-sum configuration. The output is another executable configuration in the same format. Test its derivative on 128 new input pairs with seed 95004 against the independent polynomial identity `2(x+y)`. Count transformation, expansion and execution work. The transformer is engineered; this trial does not show Kavi inventing calculus or learning differentiation rules from prose.

## Equations as internal operations

Supply two explicit finite evolution kernels:

* Three coupled temperatures with unit conductance and capacity: `dT_i/dt = sum_j(T_j-T_i)`. For three cells, `T_i(t) = mean(T(0)) + exp(-3t)(T_i(0)-mean(T(0)))`. All three temperatures affect each result. This is a small graph heat equation, not a continuum simulation.
* A two-amplitude quantum state with `hbar=1` and a fixed Hamiltonian `H=X`: `U(t) = cos(t)I - i sin(t)X`. This is an exact closed-form software evolution, not quantum hardware or a many-body solver.

For each kernel, teach final outputs after two equal evolution intervals without supplying the desired composed graph. Enumerate all 154 two-input graphs of at most two calls over that evolution kernel and real addition. Rank consistent graphs by a declared heuristic cost: twelve units for an evolution call, one for addition, then node count and canonical representation. These units express a selection preference, not measured CPU speed.

Use four authored lessons, 48 promotion inputs and 128 frozen final inputs per kernel; seeds 95005/95006 for heat and 95007/95008 for quantum evolution. Compare the selected configuration with the direct two-step calculation. Record evolution calls, full operation counts, actual execution timing and maximum discrepancy. Check heat conservation/range and quantum normalization. Count the cost of discovery separately from later execution. Any claimed break-even point must name the cost measure used.

Use two normalized states with equal populations and opposite relative phases at `t=pi/4`. Compare full amplitude evolution with an ablation that discards relative phase. This tests whether interference contributes to these physical outputs; it is not an intelligence benchmark.

## Source-based curriculum extension

The owner also requested original scientific works followed by textbook practice, correction and a separate unseen textbook. Record this as a separate live curriculum and protocol before its execution. Historical works must be inspected in their original language and identified by edition and section. Authored numerical lessons derived from those works are structured supervision. Do not describe that process as independent reading comprehension by Kavi.

Practice questions and corrections may enter learning. Freeze the resulting configurations before opening the final question bank. Use a different textbook author/source with the same subject chapters, check for duplicate questions, and publish failures as well as successes. Final questions must not be recycled into training while still counted as unseen evaluation. Broader unsupported questions remain in the report rather than being answered by the surrounding assistant and attributed to Kavi.
