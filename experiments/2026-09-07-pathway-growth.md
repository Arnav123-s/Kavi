# Bounded acquisition and reuse of configurations

Author: [Arnav123-s](https://github.com/Arnav123-s)

## Protocol recorded before execution

Date: 7 September 2026. Baseline source commit: `fcacfed4bdd6571210ed5f29e9f3041135f3d5ca`. New experiment harness: `scripts/run_pathway_growth.py`. Existing learner and executor remain unchanged.

Hypothesis: retaining a relevant acquired computation can make later compositions discoverable within a fixed search budget. This is a selected demonstration curriculum, not an unbiased sample of learning problems.

The starting library is the dependency closure of multiplication from `experiments/library-20260907-compiled.json`: addition and compiled multiplication. The compilation of multiplication was engineered in the earlier experiment. Existing higher procedures, including square and power, are excluded from every starting arm.

| Arm | Additional information available during later search |
| --- | --- |
| Fixed | No retained new procedures |
| Unrelated | One procedure acquired from examples of doubling |
| Cumulative | Earlier successful square, fourth-power and eighth-power lessons |

All arms receive the same six teaching inputs, 0 through 5, with exact integer targets. The teacher supplies targets using ordinary arithmetic. Search receives input/output examples, not target expressions. Its call, repeat and range grammar, constants, types, search order and executor are supplied. The unrelated lesson adds teaching and search cost; that cost must be included in totals.

The final inputs are 6 through 12, 17 and 23, disjoint from training. Final evaluation begins only after all searches in all arms finish. A failed final test cannot trigger repair or a new search in this run. Each retained candidate is provisional. The main library is never modified.

Each search is limited to two expression nodes, 3,000 candidates, 40,000 candidate cases, 8,000 cache entries and five seconds. Execution is limited to 3,000 calls, 100,000 gates and 32 loop iterations. The single worker has a 120-second wall limit, including pauses, and a sampled 512 MiB process working-set limit. Memory observations include the process, not only retained programs. No reliable device-temperature telemetry is available. These are bounded software checks, not hard operating-system memory isolation.

After learning, retest addition and multiplication on all pairs from 0 through 9. Test acquired procedures on the final inputs. Compare the learned fourth-power expression with the explicitly engineer-supplied baseline `multiply(multiply(x,x),multiply(x,x))`. Count actual executor gates, iterations and calls. This comparison is not a learned rewrite demonstration. Report search and execution work separately: a shorter description can still invoke expensive subprocedures.

No randomization is used; search order is deterministic. Wall-clock measurements are descriptive single-run observations. The chosen task family and two-node budget deliberately probe compositional depth. Failure means failure under that budget, not inability of another model or an enlarged search to solve the task.

## Reproduction and controls

Run from the repository root:

```text
python -B scripts/run_pathway_growth.py live --config curriculum/pathway-growth.json --run-dir runs/pathway-growth-20260907-01
```

Use a new run directory. The visible window shows actual worker output and provides Pause, Resume and Stop controls. Closing it requests a stop. Use `run` instead of `live` for direct CLI execution. A pause counts against the total wall limit and the current search time limit.

The isolated run saves its configuration, component graphs, source digest, candidate counts, evaluation rows, process memory and elapsed/CPU time in `results.json`. Its `library.json` is for inspection and queries only. Passing finite tests is not a proof for all integers or evidence of open-ended comprehension.

## Correction follow-up: protocol recorded before execution

The second bounded experiment supplies square examples at inputs 0 and 1. Both the identity function and squaring fit this deliberately ambiguous lesson. Probe input 2, supply its correct target 4 as additional teaching evidence, and re-run the unchanged search with the original examples plus that correction. This is a numeric target correction, not understanding the English word "wrong".

Final test inputs are 3 through 12, 17 and 23. They are not used for either search. Compare both candidates on the same final inputs and check that the replacement retains the two original valid answers. Input 2 is correction/training data and is excluded from final evaluation. No retuning follows final tests. Search limits match the first experiment; total wall limit is 30 seconds. The run uses the fixed multiplication closure, not the cumulative result. It performs isolated re-synthesis; it does not learn a repair algorithm or modify a deployed component.

Reproduce with `python -B scripts/run_pathway_correction.py runs/pathway-growth-20260907-01/correction.json`. The output must not already exist. The same directory's Pause and Stop files are respected during execution.

## Measured results

Run: `pathway-growth-20260907-01`. The worker completed in 8.733 seconds, using 8.734 CPU seconds. Observed peak working set was 26,963,968 bytes (25.71 MiB). These measurements exclude implementation, testing and the separate display process. All 181 existing repository tests passed before execution. The learner and executor were unchanged.

| Arm | Square | Fourth power | Eighth power | Final library bytes |
| --- | --- | --- | --- | --- |
| Fixed | 9/9 | Not acquired | Not acquired | 608 |
| Unrelated doubling | 9/9 | Not acquired | Not acquired | 717 |
| Cumulative reuse | 9/9 | 9/9 | 8/9 | 962 |

The fixed arm exhausted the two-node search space after 1,182 candidates on each later task. The unrelated arm exhausted it after 1,199 candidates on each later task. The cumulative arm acquired square after one candidate, fourth power after 94, and eighth power after 98. Its learned expressions were `multiply(x,x)`, `square(square(x))`, and `fourth(square(x))`. These are acquired compositions of supplied operations, not invented arithmetic primitives. Recency ordering favors newly acquired procedures, so the measurements combine representation availability and this existing search prior.

Every arm preserved addition and multiplication on all 200 retention checks. The cumulative library grew by 354 bytes. The three target lessons used 193 candidates cumulatively, compared with 2,365 for the fixed arm and 2,402 for the unrelated arm; the unrelated doubling warm-up adds ten candidates. Candidate counts are not equal-cost work units. Detailed candidate-case counts, execution work and timings are retained in the evidence.

The failed eighth-power case was input 23. Its execution exceeded the fixed 32-iteration budget. A separate diagnostic with a 64-iteration limit returned 78,310,985,281 correctly, using 34 iterations, 1,260 gates and 21 calls. This is post-test diagnosis, not an additional held-out success. The original score remains 8/9. It illustrates why shorter stored compositions do not eliminate the cost of executing their dependencies.

Across the nine final fourth-power inputs, the supplied repeated-work baseline used 2,980 gates, 139 iterations and 94 calls. The learned composition used 2,270 gates, 103 iterations and 82 calls: 23.8% fewer gates on this workload. Both returned all nine answers correctly. This is an executor-work comparison, not a wall-clock speedup benchmark or a demonstration of autonomous whole-graph rewriting.

### Correction result

With only examples at 0 and 1, the search selected the identity function. At the correction input 2 it returned 2, while the teacher supplied 4. Re-synthesis with the three examples acquired `multiply(x,x)`. On the 12 final inputs, the old rule passed 0/12 and the replacement passed 12/12. Both original valid examples remained correct.

This shows correction of a reusable rule rather than storing only the corrected answer. The teacher chose the task and correction, supplied the target, and retained the existing search procedure. It does not demonstrate an internally learned error concept, autonomous choice of the correction, or a generally improving learning algorithm.

### Evidence and decision

See the [complete reuse results](2026-09-07-pathway-growth.json), [correction results](2026-09-07-pathway-correction.json), and [post-test execution-limit diagnosis](2026-09-07-pathway-limit-diagnosis.json). The isolated learned library remains available in the local run for queries. No candidate was promoted into the main library.

The evidence supports relevant compositional reuse and target-driven correction within the supplied arithmetic representation. It does not yet test learning component semantics, inferring mechanisms from prose, unrestricted restructuring, chemistry-inspired dynamics or open-ended intelligence. A future comparison should use varied task families and representation budgets, with total teaching and search costs included, before attributing a general learning advantage to this example.
