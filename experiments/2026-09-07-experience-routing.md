# Learning which components to try

Author: [Arnav123-s](https://github.com/Arnav123-s)

## Protocol recorded before execution

Starting revision: `b4b5ec3`. This trial addresses the supplied-operation-hint gap from the foundation curriculum. It tests the owner's proposal that past successful configurations should help connectors direct later learning. It combines discrete behavior probes, acquired routing branches and bounded fallback. It does not implement physical heat, quantum evolution, general self-modification or the deferred external-review recommendations.

Eight earlier fixed-library successes from seed 17 supply labels by extracting the component names actually called in their acquired expressions. The earlier runs used teacher hints, so the selector inherits teacher-assisted historical experience. It does not read those hint fields or receive task-specific hints for the new tasks. Fresh authored probes of the eight earlier task oracles supply additional outer-level training information.

For each input axis, the supplied probe scheme varies that input from zero through four while other inputs equal one. Pairwise probes vary two inputs to two, and an all-zero probe checks the intercept. The signature records arity, three sorted padded apparent degrees, the count of nonzero pairwise mixed differences and whether the zero-input output is nonzero. The degree is the greatest nonzero forward-difference order observed, capped at four. Finite probes neither prove polynomial degree nor uniquely identify a function.

A discrete decision tree is fitted to eight signature/component-set pairs. Its induction rule minimizes conflicting-label pairs at each split; ties use feature order. Leaves contain the union of labels where evidence cannot distinguish a smaller set. An unseen branch uses the union available at that node. Input-axis degree sorting is a supplied permutation invariant, not a discovered identity. Tree topology and leaves are acquired; probe features, induction, execution semantics and fallback are supplied.

The comparison uses the same five-component base library and exactly the same task teaching observations in three conditions: ordinary call-only search, learned routing, and routing trained with cyclically mismatched historical labels. Each task receives all signature probes plus up to eight sampled teaching inputs from zero through five. Both selectors are frozen before new-task teaching begins. No task names or target implementations are given to the selector; implementations remain teacher/evaluator oracles.

New tasks are `x^3+1`, `x^2+1`, `(a+b+1)^2`, `a^2+b`, `ab+1`, `a^2 b`, `(x+1)^4`, `a^4+b^4`, `ab+c+1` and `(a+b)^4+1`. These are related polynomial compositions, including one input-permuted earlier function, not a cross-domain benchmark. Teaching-bank seeds are 101 and 203. Arm order rotates by task.

Every task has two seconds, 4,000 candidate programs, 80,000 candidate cases and three expression nodes. A focused route receives at most half a second, 1,000 candidates and 20,000 cases. Failure widens to the complete component library using only the remaining total allowance. Restarted search work is counted; narrowing does not receive a free second budget. Each execution permits 5,000 calls, 200,000 gates and 256 iterations. The whole worker has a 300-second wall limit and sampled 512 MiB working-set guard. Pause time counts against wall limits. Existing arithmetic is never replaced.

After all acquisition finishes, final inputs are drawn from 30 through 36: seven unary cases or twelve cases otherwise. Every missing candidate counts as failed final coverage. New final answers never train the selector or guide a repair in this version. The 254-case earlier arithmetic bank is retested. Report accuracy, all candidate work, time, probe costs, selector storage, base storage and process memory, including preparation and failed attempts. Success means evidence of useful routing on these tasks; an inconclusive result is retained.

Run `python -B -m scripts.run_experience_routing live --run-dir runs/experience-routing-20260907-01` for the readable window with Pause, Resume and Stop controls. Use a new directory for any replay. The runner uses public earlier artifacts and authored exercises; no literary source ingestion occurs.

## Relation to earlier ideas and research

The [expanding pathway design](../docs/OPEN_ENDED_PATHWAY_LEARNING.md) motivates roles learned from use. The [physical-pathway proposal](../docs/PHYSICAL_PATHWAY_RESEARCH.md) separates learned selection from engineered dynamics: a focused component set is a limited context-dependent acceleration mechanism. Search widening is an engineered response to failure, not literal temperature or an annealing algorithm. The [XRF/LIBS study](../docs/STRUCTURAL_SHARING_AND_QUANTUM_RESEARCH.md) motivates calibrated probing; integer differences here are behavioral measurements, not spectra or quantum measurements.

[Olausson and Solar-Lezama's component-discovery lecture](https://people.csail.mit.edu/asolar/SynthesisCourse/Lecture9.htm) explains why a growing library can increase branching and why previous solutions can guide future synthesis. That is relevant prior art, not a novelty claim or an implementation of DreamCoder, Babble or Stitch. [Cornell's synthesis lesson](https://www.cs.cornell.edu/courses/cs6120/2022sp/lesson/13/) gives the broader search-for-a-program formulation. These sources were reviewed for scope; no proposed external-review algorithm was adopted.

## Route-first follow-up protocol

Status: implemented as an isolated prototype and unit-tested, but **not run**. The owner's subsequent clarification replaced explicit context-and-route memory with input-driven shared interpretation as the next experiment; see the [incremental pathway protocol](2026-09-07-incremental-paths.md). The protocol below remains a record of the alternative, not a measured result.

The owner subsequently proposed reusing a chosen pathway directly, searching alternatives only when that route is absent or fails, and permitting learning during evaluation. The frozen comparison above remains unchanged. A separate follow-up starts with its learned selector and an empty executable route memory. It runs two passes over the ten task functions, with common probes and different extra teaching inputs. The newest route with a matching signature is checked first against the supplied teaching evidence. Only failure or absence permits trying other stored routes; only failure to find a fitting stored route invokes synthesis. A matching route returns immediately without candidate search. Route checking is real work and is counted separately.

Each acquisition has four seconds, at most 8,000 candidates and 160,000 candidate cases, shared across validation and both search phases. The focused phase uses at most one second, 2,000 candidates and 40,000 candidate cases. The search grammar stays at three nodes. The memory can retain at most 64 executable configurations and stores feature contexts and expressions, not example answers. The four-second allowance differs from the preceding comparison, so its timings are not an equal-budget comparison with that study. Three additional prediction inputs per task and pass are 50/53/57 and 60/63/67 respectively, offset by input index for higher arities. These prediction answers do not update the route memory in the reuse test.

A separate correction stream starts with only `0 -> 0` and `1 -> 1`, which permit an incorrect identity or square hypothesis for the intended cube operation. It records predictions for inputs 2, 3 and 4 before revealing each target. A wrong prediction becomes additional teaching evidence and triggers bounded repair before the next input. The original prediction remains scored as wrong. Its context is supplied and held constant; it does not claim task-intent recognition from an unlabelled input. The model may retain the old route while rejecting it for the corrected lesson. This is online adaptation within a supplied update mechanism, not learning an update algorithm.

The follow-up keeps the same 300-second worker limit, sampled 512 MiB guard and visible controls. Run `python -B -m scripts.run_route_memory live --run-dir runs/route-memory-20260907-01`. It requires the first trial's local results. No final results from that trial choose a winning selector: its learned arm is the declared follow-up mechanism, including its failures.

## Focus-budget repair protocol

The completed comparison left `ab+c+1` unacquired in both learned-routing trials. Inspection showed that the selector correctly chose addition and multiplication, but its focused phase hit the 20,000-case sublimit after roughly 0.3 seconds. The controller then abandoned that useful restriction and spent the remainder on broad search. This is a controller-budget defect rather than a demonstrated wrong component choice.

A targeted follow-up retains the learned component set for the full existing two-second, 4,000-candidate, 80,000-case task allowance. It adds no new operation hint or total budget. It repeats only those two failed acquisitions and uses twelve fresh cases per seed from inputs 80 through 86. It does not re-score the original final bank. The worker has a 60-second cap, finite data and visible controls; it does not implement a process-memory guard. Run `python -B -m scripts.run_routing_budget_repair live --run-dir runs/routing-budget-repair-20260907-01`. This is a local repair responding to observed failures; it does not establish that permanently narrow search is always preferable.

## Measured results

| Condition | Acquired task instances | Fresh correct / all cases | Candidate programs | Summed task seconds |
| --- | --- | --- | --- | --- |
| Ordinary call-only search | 13/20 | 126/210 | 7,329 | 22.36 |
| Learned routing | 18/20 | 186/210 | 6,440 | 11.26 |
| Mismatched routing | 12/20 | 119/210 | 9,173 | 20.24 |

The two seeds change task teaching samples; they are not independent learned-selector seeds. Every acquired program passed its final cases. Missing programs count as unsuccessful coverage. The full comparison took 55.527 seconds, including 0.026 seconds of preparation; sampled peak process working set was 28,401,664 bytes. Earlier arithmetic passed 254/254 and the base library digest was unchanged.

The learned tree occupies 548 canonical bytes, added to the 962-byte base arithmetic library. Historical artifacts, additional probe answers, new candidate expressions, transient search caches and Python are additional state or work. The tree's small size does not represent the entire experiment. The supplied probe scheme queries task oracles and favors polynomial behavior; this result does not establish unlabelled-input understanding or general cross-domain learning.

Both remaining learned-routing failures were `ab+c+1`. The focus-budget repair acquired `add(x2, add(1, multiply(x0, x1)))` for both seeds, in 1,518 candidates each. It took approximately 0.65 and 0.68 seconds of search and passed 12/12 new cases per seed. The original 18/20 score stays unchanged. The repair supports avoiding premature widening on this failure; a complete rerun of all conditions under the revised controller has not been performed.

Evidence: [full comparison](2026-09-07-experience-routing.json) and [targeted budget repair](2026-09-07-routing-budget-repair.json). The [input-driven design](../docs/INPUT_DRIVEN_PATHWAYS.md) connects these results to the owner's subsequent clarification about information flowing through shared configurations.
