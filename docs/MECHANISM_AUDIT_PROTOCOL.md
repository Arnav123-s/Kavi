# Mechanism and capability audit

Author: [Arnav123-s](https://github.com/Arnav123-s)

Recorded before the run, 7 September 2026. This follows the [recurrent experiment](../experiments/2026-09-07-recurrent-configuration.md). It tests specific remaining hypotheses; it is not an exhaustive test of every possible architecture.

## Questions

1. Do acquired connections matter causally, while arbitrary state names do not?
2. Can an additional notation acquire the same connections without an external alias replacement?
3. Can numerical feedback teach connections from the recurrent graph to previously acquired arithmetic?
4. Do temperature and error-path priority improve a small structural repair search?
5. Which existing capabilities survive direct checks, and which broader requests remain unsupported?

## Configuration and budgets

One visible worker, five minutes maximum including pauses, a 512 MiB observed working-set limit, and Pause/Resume/Stop controls. Check control files at intervals no longer than 50 ms between bounded computational steps. Alias learning permits at most 21,000 prefix states and 20,000 merge proposals per fit. These are model-search limits; hardware policy is unchanged.

Record complete local evidence and compact public results. Count model and dependency bytes, external evidence, all proposals, arithmetic executions, merge work, worker memory, CPU time and wall time. Visualization pacing is separate. No large source corpus is used. Final evaluation does not teach or select candidates.

## A. Causal structure and naming

Load the published eight-state graph. Redirect each of its 32 transitions to each of the other seven states: 224 interventions. Compare every mutant with the original using exact finite-state equivalence. Record distinguishing sequences. As a control, apply ten bijective state renamings that preserve the initial state. Add an unreachable state as a separate inactive-structure control. No intervention is installed as the main model.

Check whether the `a` and `b` transition functions commute on every state. Check that the selectors can fail to commute. These are properties of this acquired task, not claims that all information order is irrelevant. Minimal deterministic machines are expected to be sensitive to behavior-changing edge redirections; sensitivity is not a measure of intelligence.

## B. Learned notation sharing

Extend the alphabet with `α`. In this task only, it contributes an event to the same stream as `a`. Keep `?a` and `?b` as selectors. Generate old-alphabet labels from the old learned model and labels for sequences containing `α` from a separate teacher. Teach every sequence up to length six: 19,531 total, of which 5,461 belong to the original alphabet. Use merge-order seeds 7, 19 and 43.

The learner receives complete sequences and output labels, without an alias map. Freeze each model, then check 128 fresh streams of length 13–64, generated with seed 94001. Compare with a separately constructed reference and with the old graph on its alphabet. Inspect whether `a` and `α` have identical destinations at every learned state. This is task-specific notation sharing; it does not make the English article `a` a universal synonym for alpha.

## C. Learning the arithmetic connections

Use the new controller's output as an internal connection identifier. Supply the existing acquired `add`, `subtract` and `multiply` procedures as candidates. The bridge learner sees whole examples `(token stream, two integer values, final numerical answer)`. It executes candidates and retains only those consistent with each controller outcome. It receives no desired procedure name.

First teach `(empty stream, 2, 2) → 4` and `([a], 2, 2) → 4`; both addition and multiplication remain possible. Require an ambiguous result rather than guessing. Add `(empty stream, 2, 3) → 5` and `([a], 2, 3) → 6`. Freeze the uniquely selected connections, controller and library digest. Discard teaching records from the exported bridge.

Evaluate 128 new token/value combinations with seed 94002, stream lengths 13–64 and nonnegative operands from 0 through 1,000,000. Expected answers come from the independent event-count teacher followed by host addition or multiplication. Count the acquired arithmetic's calls, gates and iterations. This tests learned selection among supplied procedures. It does not test natural-language meaning, invention of arithmetic or learning the executor. Unknown tokens and unresolved connections must not produce a numerical answer.

### Additional supervised composition test

Added before execution in response to the request for new configurations inspired by old ones. Enumerate acyclic graphs with zero, one or two calls to acquired addition, subtraction and multiplication, with two input references and reuse of prior node outputs. Count every candidate, including inconsistent ones. The task label is opaque; the teacher supplies four numerical examples of a new relation, with no formula or desired graph. For this authored task the evaluator's relation is $(x+y)^2$.

Select a consistent graph by fewest nodes and canonical encoding; the representation and tie rule are supplied. A separate 48-case promotion bank with seed 94005 must pass before the graph is admitted as a new catalog entry. Names cannot overwrite earlier entries, and the base library digest is retained. Freeze the merged catalog, then evaluate 128 fresh inputs with seed 94006 and repeat earlier-operation checks. The merge adds a learned computation under supervision; it does not claim global compression of the entire catalog or unrestricted question understanding.

## D. Temperature and error-path priority

Create three faults in separate copies of the original graph by changing one selector transition: `(state 0, ?b)`, `(state 2, ?b)` and `(state 3, ?a)`. Replace its original destination by `(destination + 2) mod 8`. All starting models must preserve the old `a,b` task. The repair search receives each damaged graph and labeled examples, not the fault's location or the correct graph.

Use a fixed 128-example development bank over the original alphabet, lengths 5–12, seed 94003. A proposal changes one connection to one of seven different destinations. Compare four methods under the same maximum of 128 proposals: uniform greedy, error-path-priority greedy, uniform heated search, and heated search with error-path priority. Use paired search seeds 7, 19 and 43 for the three respective faults. This is three paired problem/seed cases, not a large benchmark.

Energy is the fraction of incorrect development outputs. Every candidate must preserve the old task exactly; temperature cannot override that requirement. Greedy methods accept non-increasing energy. Heated methods use $T_i=0.15(0.005/0.15)^{i/127}$ and

$$A(K,K')=\min\{1,\exp[(E(K)-E(K'))/T_i]\,q(K\mid K')/q(K'\mid K)\}.$$

Priority gives each connection weight one plus its occurrence count in failing development traces. The reverse-proposal ratio is included for that asymmetric proposal. Uniform proposals have ratio one. This is an engineered annealing comparison inspired by [Kirkpatrick et al.](https://hedibert.org/wp-content/uploads/2013/12/1983KirkpatrickGelattVecchi.pdf); the finite cooling schedule carries no asymptotic convergence claim. No physical heat, chemical reaction or quantum hardware is simulated.

Keep the best development candidate seen, stop early at zero development error, and freeze before evaluating a fresh 128-case bank, lengths 13–64, seed 94004, and exact full-task equivalence. If an arm fails, preserve it. Separately evaluate a complete 224-proposal one-edge repair search from each damaged starting graph, selecting on the same development bank. This closes a gap only within that explicitly enumerated neighborhood; it does not prove general repair is solved. Evaluation counts include candidates rejected by retention, and all additional trace work is recorded.

## E. Certificate and capability boundaries

Recheck the eight local addition identities and ten authored large/carry-boundary additions up to the runtime's 4,096-bit input limit. Check rejection above that limit. The theorem is an existing invariant argument; this audit does not claim discovery of a new addition theorem or a proof of Python.

Load the public foundation checkpoint and test known sentence calculations alongside six authored requests for an unfamiliar proof, calculus derivation, physical explanation, literary interpretation, philosophical comparison and creative prose. Report the actual interface outcomes. These probes demonstrate support boundaries; six questions are not a graduate examination or an intelligence score.

Previously deferred review recommendations remain deferred. Learned update rules, unrestricted semantic binding, internal event scheduling and quantum-inspired algorithms beyond this classical search comparison remain unimplemented. The final project report must distinguish experiments completed, ideas represented by a limited proxy, and ideas still untested.

Physical analogies are proposed as ways to construct and refine configurations. The hypothesis is that better configurations improve the overall learner. Complexity alone is not the endpoint: compare new-problem performance, preservation of earlier skills and the full cost of finding the configuration.
