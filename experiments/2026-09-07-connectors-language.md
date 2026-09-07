# Shared multiplication and a first sentence-learning trial

Author: [Arnav123-s](https://github.com/Arnav123-s)

Date: 7 September 2026. Implementation: `5e803ac`. Run: `connector-language-20260907-01`.

## Result

The operand-order problem was reproduced and repaired. Both orientations of a multiplication request now enter one shared procedure with identical operand bindings and complete call traces. A checked compiler transformation also reduces multiplication's iteration count from the value of an operand to the bit length of the smaller operand.

The sentence learner acquired 18 frames from 36 annotated examples. It then interpreted new numbers and clause contents within those frames. Six short original-language passages supplied lexical exposure. These results establish a small arithmetic language interface and recorded vocabulary relationships; they do not establish philosophical comprehension, literary interpretation, open-ended reasoning or creativity.

The live worker completed in **2.653 seconds**, using **2.625 CPU seconds**. Its window displayed actual process events and stayed open with the transcript and saved-model query controls. This duration excludes research, implementation, testing, preparation and the subsequent evidence audit.

## The reproduced defect and repair

| Request | Previous retained library | Compiled library |
| --- | --- | --- |
| `multiply(3,100000)` | 300,000; 3 iterations | 300,000; 2 iterations |
| `multiply(100000,3)` | Iteration budget exhausted | 300,000; same complete trace as the swapped request |
| `multiply(3,1000000)` | 3,000,000; 3 iterations | 3,000,000; 2 iterations |
| `multiply(1000000,3)` | Iteration budget exhausted | 3,000,000; same complete trace as the swapped request |
| `multiply(1000000,1000000)` | Iteration budget exhausted | 1,000,000,000,000; 20 iterations |

The first part of the repair is an operation-specific connector. For multiplication, `(a,b)` and `(b,a)` belong to the same equivalence class. The connector chooses `(min(a,b),max(a,b))` before execution. No operand-specific procedures or answer records are added. Subtraction and directed sentence relations retain their order.

The second part is binary multiplication through the previously acquired addition circuit. Merely sorting the operands would leave a million-by-million request with a million-iteration loop. Binary scanning uses one count bit per iteration and invokes the addition circuit only for set bits. For a million squared, there are seven addition calls, 20 bit tests, 39 shifts and one connector comparison. The eight procedure calls include the outer multiplication call; the addition circuits execute 1,230 gates across 246 bit frames.

For either order of three times a million, the complete call trace is:

```text
add(0, 1000000)            -> 1000000
add(1000000, 2000000)      -> 3000000
multiply(3, 1000000)       -> 3000000
```

That execution uses two binary iterations, three calls, 43 bit frames and 215 gate evaluations. The input connector and binary control are supplied implementation. Kavi did not discover this optimization in the trial. The acquired addition gates are reused, and the compiler accepts the original repeated-addition body only after checking all eight local addition/carry cases. The [protocol](../docs/CONNECTORS_AND_LANGUAGE_PROTOCOL.md) gives the invariant and framing assumptions.

## Arithmetic evidence

| Check | Observed result | Boundary |
| --- | --- | --- |
| All seven-bit operand pairs | 16,384 / 16,384 correct | Exhaustive finite domain |
| Declared longer and boundary cases | 47 / 47 correct | Forty seeded pairs at 16–256 bits; seven explicit cases, including zero/one with a 4,096-bit value |
| Swap comparison | 47 / 47 identical complete executions | Both orientations compared with a 10,000-entry trace allowance; no truncated traces accepted |
| Retention | 516 prior successful cases; zero regressions | All 13 procedures; small declared valid domains |
| Historical `power(20,10)` trace | 221 completed calls | Default stores 128 with an explicit truncation flag; a larger allowance records all 221 |

The compiled artifact preserves every definition except multiplication. It does not alter the old file. The 4,096-bit value bound, gate/call fuel and total iteration limit still apply. Larger inputs or expensive dependent programs can still fail within those declared bounds; this is not unrestricted arithmetic.

A separate audit checked all **16,975 saved case rows**. It recomputed arithmetic references outside the procedure executor, checked the declared language expectations and source fingerprints, and confirmed that published exercises match the sealed local packet. Reloaded models also passed the 47 swap checks and all 28 language cases with the teaching reference and further source-file reads disabled. These are project-authored checks, not an external replication.

## What the language trial learned

The learner aligned annotated spans in pairs of teaching sentences, replacing varying values with typed slots. Two distinct examples supported each retained pattern. A saved rule routes the meaning of a recognized calculation to an existing operation. Other rules identify the roles in a reason, conditional, attribution, denied attribution or definition. The inference path does not consult the original teaching sentences.

```text
Sentence
  -> normalized tokens
  -> learned frame and slot bindings
  -> typed meaning
      calculation -> operation connector -> acquired gates/program -> result
      definition  -> source-specific stored sense
      relation    -> labeled roles; truth remains unassessed
```

“Subtract 3 from 1000000” binds the quantity after “from” to subtraction's first argument. Reversing the quantities produces an execution failure under the natural-number contract. A grammatical interpretation does not override the operation's input conditions.

| Evaluation group | Observed | What this means |
| --- | --- | --- |
| New numerical arguments in known frames | 12 / 12 correct | Instance transfer to acquired arithmetic |
| New clause contents in known relation frames | 7 / 7 correct | Role extraction, including direction and attribution |
| Two explicitly taught Hume definitions | 2 / 2 recalled | Source-linked lexical lookup |
| Unsupported capability probes | 5 / 5 declined | Unfamiliar wording, argument explanation, creative writing, cross-tradition comparison and an unknown word sense remained unsupported |
| Nested “because” ambiguity | 1 / 1 reported ambiguous | Multiple possible clause bindings |
| Invalid ordered subtraction | 1 / 1 rejected | Execution contract preserved |

All 28 checks met their declared expectations, but seven are boundary checks. Correctly declining to write a philosophical dialogue is not evidence of creative writing. Recognizing “the lamp glows because current flows” also does not establish the truth of the causal claim; the reversed claim receives a different role binding without being scientifically verified.

The 18 frames contain supplied meaning labels and acquired slot arrangements. Digit recognition, normalization, alignment rules and the available meaning types are supplied. New numbers within a known construction are a different challenge from new wording, nested compositional language or original-language interpretation. The model remains sensitive to phrasing.

## Original texts actually used

No Gutenberg source enters this new packet. The earlier arithmetic prerequisite retains its historical source provenance.

| Work | Language and source | Recorded lexical units |
| --- | --- | ---: |
| Hume, *Enquiry*, II.3 | English; [Hume Texts Online](https://davidhume.org/texts/e/2) | 56 |
| Kant, *Kritik der reinen Vernunft*, AA III 27 | German; [Akademie transcription](https://www.korpora.org/kant/aa03/027.html) | 78 |
| Plato, *Apology*, 17a | Ancient Greek; Burnet 1905 through [Perseus](https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0059/tlg002/tlg0059.tlg002.perseus-grc2.xml) | 34 |
| Newton, *Principia*, Laws I–III | Latin; 1713 [Newton Project transcription](https://www.newtonproject.ox.ac.uk/view/texts/normalized/NATP00081) | 56 |
| Vivekananda, *Raja-Yoga*, introductory paragraph | Original English; [Complete Works, volume 1](https://www.ramakrishnavivekananda.info/vivekananda/volume_1/raja-yoga/introductory.htm) | 58 |
| *Analects*, opening passage | Classical Chinese; [Stanford teaching transcription](https://chinesetexts.stanford.edu/2-lun-yu-%E8%AB%96%E8%AA%9E-the-analects/) | 32 |

The total is 314 lexical occurrences, 240 distinct nodes and 296 distinct adjacent pairs. Han characters are counted individually; these counts are not a uniform cross-language word metric. The model retains normalized units, counts, adjacency and source links. It does not derive the passages' meanings or translate them. Two Hume senses were separately supplied as annotated paraphrases.

The [source catalog](../curriculum/original-language-sources.json) records edition details, limitations and sources still outside the trial. This small selection is not representative of all countries, eras or philosophical traditions. Modern research and publisher dictionary pages were consulted during preparation but were not ingested; the research-reading exercises are separately authored. Full works, modern commentary and translations were not fed into this trial.

## Size and cost

| Item | Measurement |
| --- | ---: |
| Earlier acquired procedure library | 2,238 bytes |
| Compiled procedure library, still 13 procedures | 2,272 bytes |
| Additional arithmetic artifact size | 34 bytes |
| Language artifact, including frames, lexical memory and provenance | 26,810 bytes |
| Combined saved model artifacts | 29,082 bytes |
| Sealed source/annotation/evaluation packet | 25,023 bytes, stored separately |
| Complete run directory at audit | 735,897 bytes, including models and logs |
| Worker peak working set | 27,643,904 bytes (26.36 MiB) |
| Separate window process peak, observed after completion | 39,792,640 bytes (37.95 MiB) |
| Teaching work | 36 examples and 36 candidate span alignments |

The worker memory figure includes the interpreter, learning, compilation and final evaluation in that process. The window's peak is measured separately after completion; the two peaks need not have occurred simultaneously. Model bytes exclude Python, the implementation, input files, preparation and the audit. Run-directory size already includes the model files; these rows must not be added blindly. Lexical counts are persistent numeric statistics even though the arithmetic model has no learned numerical edge weights.

The 34-byte model increase does not include the source code implementing connectors and binary scanning. It demonstrates that many operand pairs can share one compact arithmetic description. It does not establish that arbitrary knowledge or graduate capability will require similarly small additions. No equal-capability comparison with a language model was performed.

## Interpretation and next engineering work

The review correctly identified operand orientation and unexplained trace truncation as implementation weaknesses. The connector resolves the first by preserving only distinctions relevant to the operation. The loop transformation repairs the remaining execution cost. Explicit trace accounting makes omitted records visible. The previous arithmetic idea survives these changes: numerical inputs still execute a shared procedure rather than retrieve stored answers.

For language, adding books now mostly grows lexical memory. Meaningful progress requires learning reusable compositions of typed meanings, entity references, quantifier and negation scope, and checked inferences. A later curriculum should pair selected primary passages with explicit interpretations, counterexamples and withheld constructions; it should compare source-guided teaching against matched exercises without those passages. This trial did not test whether the literary or philosophical sources improved transfer.

A statement being grammatical, attributed to an author or frequent in a text is not a reason to accept it as true. Argument learning must distinguish premises, conclusions, validity, evidence and uncertainty. Literature adds narrator perspective, figurative language and defensible alternative interpretations. Creativity needs its own held-out task and assessment of novelty and usefulness. These are engineering requirements still to implement and measure.

## Reproduction and artifacts

The [compiled arithmetic library](library-20260907-compiled.json), [machine-readable evidence](2026-09-07-connectors-language.json), [authored exercises](../curriculum/connector-language-exercises.json) and [protocol](../docs/CONNECTORS_AND_LANGUAGE_PROTOCOL.md) are reviewable in the repository. Original passages, the source-derived language artifact and full event/case logs remain local.

```powershell
python -B -m kavi library ask --library experiments/library-20260907-compiled.json multiply 1000000 3 --trace
python -B -m kavi.connector_language_cli ask --run-dir runs/connector-language-20260907-01 "what is 1000000 times 3?"
python -B -m kavi.connector_language_cli ask --run-dir runs/connector-language-20260907-01 "what does idea mean?"
```

All **181 tests passed** under Python 3.13.5 before the trial. The source manifest validated, original model hashes stayed unchanged, and the evidence audit passed. The optional earlier text-model tests use the existing PyTorch installation; this new trial itself uses the standard library and CPU only.
