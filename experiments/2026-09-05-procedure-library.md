# Procedure acquisition, reuse and execution cost

Author: [Arnav123-s](https://github.com/Arnav123-s)

Date: 5 September 2026

Two finite live trials acquired and evaluated small arithmetic programs. A later packaging step retained compatible procedures from both trials. The complete compact record is [available as JSON](2026-09-05-procedure-library.json). These results concern an elementary program-learning mechanism; they do not establish university or master's-level subject capability.

## Protocol and provenance

| Item | Initial library trial | Scaling follow-up |
| --- | --- | --- |
| Local run | `library-20260905-01` | `library-20260905-02` |
| Source revision | `a54d196` | `0453052` |
| Seeds | 7, 19, 31 | 43, 59, 73 |
| Configuration | [Initial](../curriculum/library-run.json) | [Scaling](../curriculum/library-scaling-run.json) |
| New program lessons | 10 | 11 |
| Wall time | 45.868 seconds | 56.349 seconds |
| CPU time | 45.453 seconds | 55.984 seconds |
| Peak process memory | 48,963,584 bytes | 50,249,728 bytes |
| Run files at audit | 20,074,510 bytes | 20,696,175 bytes |
| Evaluation rows independently audited | 358,575 | 365,093 |

Both runs used Python 3.13.5 on one CPU process. Their ceilings were 900 seconds, 512 MiB sampled process memory and 128 MiB of run files. Each program search had three instructions, 20,000 candidates, 1,000,000 candidate cases and ten seconds. Search execution allowed 512 iterations; inference allowed 4,096, with separate call, gate and depth limits. Preparation, visible-window overhead and the original addition acquisition are outside these worker timings. Energy and reliable CPU temperature were unavailable.

The teacher formalized selected ideas from the admitted 1858 English witness of De Morgan's *Elements of Arithmetic*: paragraphs 28–30, 35–38, 39–41, 47–49 and 206–207. Source SHA-256 is `c7dc1494dc3172531d79f11108c231377a4c17be0dbf9eb1ccce1a163e9ffd2f`. Extract hashes are in the JSON record. Scaling, powers, triangular sums and sums of squares are separately authored composition probes. The learner received formal examples; it did not interpret prose. Raw source text remains private.

Each seed imported the [previously acquired addition circuit](circuit-20260905-model.json), acquired a separate subtraction transition from 48 examples, then searched programs. Input types, operation names, teaching order, zero/one constants, the grammar and loop semantics were supplied. Gate choices, wiring and program arrangements were selected through learning. Inference executes saved structure without the teacher or a teaching-record lookup.

All task selections ended before each seed's final evaluation. The whole library was sealed by its canonical hash. Same-domain withheld cases, finite audits and larger-input probes were recorded separately. Audits overlap teaching. Search never received the final banks. The follow-up was designed after observing the first trial's failures, so it is a diagnostic extension, not a blind replication. It uses new seeds and larger, distinct power and factorial transfer inputs; the task families remain the same.

## Initial result

Seeds 7 and 19 retained 11 procedures in 2,004 bytes. Seed 31 retained 12 in 2,131 bytes because it also acquired power. Subtraction used five gates and 321 bytes in every seed, passed 88 withheld cases, all 32,896 ordered eight-bit pairs and all 32 length-transfer cases. Its post-selection borrow identity held in all eight local rows.

The final tests exposed operational limits:

| Task | Initial result per seed | Interpretation |
| --- | --- | --- |
| Add, subtract, double, sum3, triple, adjusted difference, square, triangular sum and sum of squares | Every declared case passed | Exact behavior within the tested domains |
| Multiply | 208/208 withheld; 1,024/1,024 audit; 12/24 transfer | Large first operands exceeded the iteration limit |
| Power, seeds 7 and 19 | Not acquired within 20,000 candidates | All final queries reported an unavailable procedure |
| Power, seed 31 | 18/18 withheld; 87/117 audit; 0/16 transfer | The acquired algorithm exceeded fuel on larger inputs |
| Factorial | 2/3 withheld; 8/11 audit; 0/4 transfer | Values from 8! onward exceeded the iteration limit |

Multiplication was `repeat[add](x0, 0, x1)`: start at zero and add the second operand once for every unit of the first. Powers and factorials then put their growing accumulator in that costly first position. The selected programs were mathematically meaningful, but resource-bounded execution made some valid inputs unavailable. There were no incorrect numerical returns among completed evaluations; failures were explicit errors or missing procedures.

## Scaling lesson and follow-up

The [follow-up protocol](../docs/SCALING_LESSON_PROTOCOL.md) inserted 24 examples of a large quantity multiplied by a small count. Its teaching anchor `(1024, 2)` could not finish through the original argument order under the existing search limit. The learner selected `scale(x0, x1) = multiply(x1, x0)` after nine candidates in every seed. This added 113 canonical bytes. No new interpreter instruction or host arithmetic primitive was introduced.

All three follow-up seeds acquired the same 12-procedure, 2,094-byte library:

| Task | Follow-up result per seed | Change and remaining limit |
| --- | --- | --- |
| Scale | 40/40 withheld; 1,024/1,024 audit; 12/24 transfer | Large quantity with small count works; reversing that order still exhausts fuel |
| Power | 18/18 withheld; 117/117 audit; 16/16 transfer | Acquired `repeat[scale](x1, 1, x0)`; transfer covers bases 17–20 and exponents 7–10 |
| Factorial | 3/3 withheld; 11/11 audit; 4/4 transfer | Acquired `range[scale](x0, 1)`; transfer covers 15!–18! |
| Original multiply | 208/208 withheld; 1,024/1,024 audit; 12/24 transfer | Its definition and order sensitivity remain unchanged |
| Sum of squares | Not acquired within ten seconds | The larger library made search too costly; all final queries were retained as failures |
| Remaining acquired operations | Every declared case passed | Original finite domains and new seeded length probes |

The extra lesson helped downstream computation, while expanding the search vocabulary had a cost. Sum-of-squares search timed out after 15,702, 14,873 and 15,494 candidates. The base-only condition acquired that task after 2,337 candidates in each seed. A larger useful library did not guarantee cheaper acquisition.

This follow-up repeated learning from the declared addition prerequisite. Failure to reacquire sum of squares in those fresh trials is not a deletion of a procedure from the first trial. Both original artifacts remain preserved.

## Reuse comparison

Every program task was also searched with only acquired addition and subtraction available. Both conditions received the same task examples and budgets within a trial. Their bounded hypothesis classes differ because a named acquired procedure compresses what can fit in three instructions. The comparison measures access to that vocabulary, not superiority over every program learner or numerical model.

Tripling took one candidate with access to `sum3`, versus 145 with only the two base circuits. Squaring took one versus 49. The scaling follow-up took nine candidates versus 121. These are task-specific candidate counts; all call execution and cache work are separately recorded.

The library condition was slower in several other tasks. In the initial run, sum-of-squares search took 9,929–14,031 candidates versus 2,337. In the follow-up it timed out. Base-only power and factorial were not acquired under the declared grammar and budgets. These results support selective reuse, and identify proposal ranking and vocabulary selection as unresolved engineering problems.

## Persistent size and retention

The following is the measured follow-up growth curve. It includes procedure names, signatures and JSON structure. The imported addition circuit alone is 321 bytes; its enclosing one-procedure library is 449 bytes.

| Accepted stage | Shared library bytes | Added bytes |
| --- | --- | --- |
| Imported addition | 449 | 449 |
| Subtraction | 853 | 404 |
| Double | 962 | 109 |
| Three-input sum | 1,094 | 132 |
| Triple | 1,214 | 120 |
| Adjusted difference | 1,385 | 171 |
| Multiply | 1,510 | 125 |
| Square | 1,624 | 114 |
| Scale | 1,737 | 113 |
| Power | 1,861 | 124 |
| Triangular sum | 1,977 | 116 |
| Factorial | 2,094 | 117 |

Later related operations added 109–171 bytes each. The increments did not converge to zero or decrease monotonically. Independently packaging every follow-up procedure with its complete dependencies would occupy 8,032 bytes. Shared storage was 73.9% smaller than that packaging control. This is not a comparison with optimally compressed flat code, the full executor or a trained neural model.

Protected checks found zero regressions across 4,506 case checks in the initial run and 5,184 in the follow-up. These totals count checks across stages, not distinct inputs. Earlier definitions were immutable. This establishes retention under append-only extension, not safe mutation of shared procedures.

## Retained artifact

The [retained library](library-20260905-retained.json) contains 13 acquired procedures in **2,238 bytes**. It starts with the follow-up's seed-73 library and imports `sum_squares` from initial seed 7. Its required `add`, `multiply` and `square` definitions match exactly in both libraries. Every existing follow-up definition is unchanged.

This deterministic packaging step is supplied engineering, not another learning run or learned consolidation. Eleven recorded queries and an additional 1,089-case sum-of-squares audit passed after combination. The JSON record includes the source hashes, matching dependencies and actual call traces. Separate dependency packages would occupy 8,864 bytes; the shared retained artifact is 74.8% smaller under that specific control.

| Retained procedure | Executed arrangement |
| --- | --- |
| `add`, `subtract` | Separately acquired five-gate transition circuits |
| `double(x)` | `add(x, x)` |
| `sum3(a, b, c)` | `add(a, add(b, c))` |
| `triple(x)` | `sum3(x, x, x)` |
| `adjusted_difference(a, b, c)` | `sum3(c, 0, subtract(a, b))`, with `a >= b` |
| `multiply(a, b)` | Add `b` to zero `a` times |
| `square(x)` | `multiply(x, x)` |
| `scale(a, b)` | `multiply(b, a)` |
| `power(a, b)` | Start at one; apply `scale(accumulator, a)` `b` times |
| `triangular(n)` | Fold acquired addition over `1..n` starting at zero |
| `factorial(n)` | Fold acquired scale over `1..n` starting at one |
| `sum_squares(a, b)` | Start at `square(b)`; add `a` another `a` times |

The complete artifact hash is `0a089a0b26fa2b453ed3f896637f47684920d1dfe9568edb6515bd6775285ec6`. The [first](library-20260905-first.json) and [follow-up](library-20260905-scaling.json) source libraries are also published. Neither original run was overwritten.

## Reproduction and interpretation

The public models support source-free inference:

```powershell
python -m kavi library inspect --library experiments/library-20260905-retained.json
python -m kavi library ask --library experiments/library-20260905-retained.json power 20 10 --trace
python -m kavi library ask --library experiments/library-20260905-retained.json factorial 18
python -m kavi library ask --library experiments/library-20260905-retained.json sum_squares 72 83
```

These queries return `10240000000000`, `6402373705728000` and `12073`. Running the teaching protocol also needs the admitted local source witness. The [runtime reference](../docs/PROCEDURE_LIBRARY_RUNTIME.md) describes live launch, pause, stop, evidence and reproduction. All 169 regression tests passed under Python 3.13.5; the two full trial files were independently audited against arithmetic references, aggregate counts and sealed hashes.

The useful result is that a 113-byte acquired arrangement enabled more effective use of earlier operations. The unresolved cost is that a growing vocabulary can make search worse. Efficient two-large-operand multiplication, automatic choice of call order, discovered abstractions, safe shared repair, prose interpretation and advanced subject reasoning remain separate work. The [advanced capability protocol](../docs/ADVANCED_CAPABILITY_PROTOCOL.md) specifies the evidence needed for those claims.
