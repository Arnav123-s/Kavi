# Shared connectors and grounded sentence learning

Author: [Arnav123-s](https://github.com/Arnav123-s)

Revision: 7 September 2026

## The change

Multiplication has one shared entry point. Its connector places interchangeable operands in a canonical order before executing the procedure. Requests `(3, 1000000)` and `(1000000, 3)` therefore enter the same computation with the same bindings. This connector is operation-specific: subtraction, directed relations, and sentence roles retain their input order.

Mathematically, the connector selects a representative of the equivalence class `(a,b) ~ (b,a)`. Multiplication is constant on that class, so both requests can share a computation. This is canonicalization under permutation symmetry. It must be justified for each operation: identifying “A supports B” with “B supports A” would discard meaning.

Normalization alone does not repair value-linear multiplication when both operands are large. A checked compiler transformation replaces the acquired repeated-addition loop with binary scanning and conditional addition. The final computation continues to execute the acquired addition gates. It does not call the teacher or a host multiplication primitive. The shifts, comparisons, loop and compiler are supplied engineering; this trial does not claim that Kavi discovered binary multiplication.

The compiler accepts only the exact repeated-addition form with a zero accumulator and the two argument references. It checks every local input/carry row of the referenced circuit against the identity `output + 2 * next_carry = left + right + carry`. The original executor specifies zero initial carry and final zero padding. The resulting whole-operation argument establishes addition under those assumptions. The binary loop preserves `accumulator + count * step = initial_left * initial_right`, consumes one count bit per iteration, and terminates when the count is zero. This is a mathematical argument with executable local checks, not a machine-checked proof of the Python implementation.

The iteration count becomes the bit length of the smaller operand. Gate work still grows with operand length and with the number of additions. Integer shifts and connector comparisons are counted separately; their host implementation cost is not zero. The natural-number limit remains 4,096 bits, with finite gate, call and iteration budgets. A result can still be unavailable when these limits are exceeded.

Only the multiplication definition changes in the newly compiled library. Existing callers, including `scale`, reach this same procedure. Earlier artifacts and their historical results remain unchanged. Correctness preservation is checked on dependent operations as well as multiplication itself.

## Traces

Execution now reports the number of completed call events and whether trace entries were omitted. The default remains 128 records. The query interface accepts `--trace-limit` up to 100,000. For the earlier `power(20,10)` example, this permits a complete 221-call trace instead of an unexplained 128-record prefix.

A complete call trace is not a complete instruction log or a natural-language derivation. The counter distinguishes trace recording from execution work. Failed execution retains partial resource information; a successful arithmetic result does not imply that a physical explanation or proof has been generated.

## What language learning means in this trial

The learner starts without sentence rules. A teacher supplies 36 utterances paired with typed meanings: operation/argument records, claim/reason roles, conditional roles, attribution, denied attribution, definitions, and lexical queries. The learner aligns annotated spans and retains a generalized frame only when supported by at least two distinct teaching sentences. Digit parsing, Unicode normalization, the alignment method and the available meaning types are supplied.

Thus a learned frame can route “what is 1000000 times 3?” to the shared multiplication procedure without the user entering a procedure name. A different learned frame reverses the grammatical arguments of “subtract 3 from 1000000” while preserving the subtraction procedure's order. Clause frames preserve who said what, which clause is offered as a reason, and whether an attribution was denied. These are narrow structural interpretations, not judgments of truth or argument validity.

The runtime rejects unrecognized wording and reports multiple interpretations as ambiguous. No embedding model, external language model, translation engine, full syntactic parser, or general reasoning engine is present. A new number in a learned frame is instance transfer; a completely new construction is a separate test. This distinction follows the evaluation issue studied in [compositional semantic parsing](https://aclanthology.org/2021.acl-long.75/).

Two source-specific word senses are retained as explicitly supplied lexical entries from Hume's terminology: `idea` and `impression`. Returning their definitions is source-linked recall, not invention of a definition or proof of general word understanding. The saved lexical entries and their sources count toward persistent size.

## Original sources

No Project Gutenberg passage enters this new packet. The previous arithmetic artifact remains a historical prerequisite; its original provenance is preserved. The [source catalog](../curriculum/original-language-sources.json) identifies each selected witness, language, scope and fingerprint.

| Source | Language and witness | Actual use |
| --- | --- | --- |
| Plato, *Apology* 17a | Greek; Burnet's 1905 edition through the [Perseus Project](https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0059/tlg002/tlg0059.tlg002.perseus-grc2.xml) | Opening passage, lexical exposure |
| Hume, *Enquiry*, II.3 | Original English through [Hume Texts Online](https://davidhume.org/texts/e/2) | Selected passage, lexical exposure and two explicitly annotated senses |
| Kant, *Kritik der reinen Vernunft*, AA III 27 | German, second-edition introduction through the [Akademie electronic text](https://www.korpora.org/kant/aa03/027.html) | Lines 14–21, lexical exposure |
| Newton, *Principia*, 1713 | Latin, normalized scholarly transcription through the [Newton Project](https://www.newtonproject.ox.ac.uk/view/texts/normalized/NATP00081) | Statements of Laws I–III, lexical exposure |
| Vivekananda, *Raja-Yoga*, introductory chapter | Original English, *Complete Works* volume 1 [digital transcription](https://www.ramakrishnavivekananda.info/vivekananda/volume_1/raja-yoga/introductory.htm) | Opening paragraph, lexical exposure; print impression unspecified on the page |
| *Analects*, opening passage | Classical Chinese, [Stanford Chinese Philosophical Texts](https://chinesetexts.stanford.edu/2-lun-yu-%E8%AB%96%E8%AA%9E-the-analects/), lesson 2, extract A | Ancient passage only, character adjacency; modern glosses and translations excluded |

“Original” here means the author's language in a documented textual witness; it does not mean possession of an autograph manuscript. Ancient authors survive through transmitted editions. Modern editorial notes and translations are not substituted for the selected text. Passages are stored only in the ignored local packet, with whitespace normalization documented and SHA-256 fingerprints.

Reading these passages adds lexical units, adjacency counts and source edges to a separate memory. That can support later lexical work, but it does not interpret their philosophical or scientific content. English sentence exercises are separately authored annotations and paraphrases; the system did not translate the Greek, German or Latin into them. The language artifact includes this source-derived memory and remains local.

The six-source selection spans ancient China and Greece, eighteenth-century European works and nineteenth-century Indian philosophy. It is a starting selection, not a survey of global philosophy. The Vivekananda archive [credits support from Advaita Ashrama](https://www.ramakrishnavivekananda.info/) and is [catalogued by the University of Pennsylvania](https://onlinebooks.library.upenn.edu/webbin/book/lookupname?key=Vivekananda%2C+Swami%2C+1863-1902). The Stanford extract is an identified teaching transcription, not a critical edition. The tokenizer treats Han characters as individual lexical units; that does not establish Chinese word segmentation or language competence.

A Sanskrit *Nyāyasūtra* witness at [GRETIL](https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/sa_gautama-nyAyasUtra.htm) was inspected, but its notice says it is not proof-read and its terms are noncommercial share-alike. It remains outside this trial pending a suitable edition and scope review. The Chinese Text Project's direct retrieval returned 403; that copy was not used. Arabic, further South Asian, East Asian, African and other traditions require their own editions, language handling and assessment; they are not marked complete.

Research-reading exercises use separately authored sentences about programs and reuse, informed by the [DreamCoder paper](https://arxiv.org/abs/2006.08381). The article itself is not ingested. A [publisher dictionary entry](https://www.merriam-webster.com/dictionary/hypothesis) was inspected as a reference; no dictionary page is ingested. Future dictionary admission needs a stated edition and sense-selection task, not an assumption that copying definitions confers understanding.

## Run and evaluation

The configuration is [connector-language-run.json](../curriculum/connector-language-run.json). It fixes a packet hash, seed 83, a 180-second wall limit, a sampled 256 MiB process-memory ceiling and 32 MiB of run files. The window displays actual child-process events and retains pause and stop controls. No background scheduler is installed.

The [authored exercises](../curriculum/connector-language-exercises.json) publish the teaching annotations and declared evaluations for inspection. Source bodies remain in the local sealed packet. The saved arithmetic library supports inference without that packet; replaying source exposure requires the six reviewed excerpts with matching hashes.

```powershell
python -B -m kavi.learning_window --runner kavi.connector_language_cli --config curriculum/connector-language-run.json --run-dir runs/connector-language-trial --start
python -B -m kavi.connector_language_cli ask --run-dir runs/connector-language-trial "what is 1000000 times 3?"
python -B -m kavi library ask --library experiments/library-20260905-retained.json power 20 10 --trace --trace-limit 1000
```

The run seals the compiled library and acquired language model before final evaluation. Arithmetic assessment covers all 16,384 seven-bit multiplication pairs plus declared longer cases, exact swapped-execution equality and earlier correct dependent results. It also demonstrates the historical trace truncation case with the repaired reporter.

The 28 language checks are reported by group: 12 calculations with new arguments in known frames, seven new clause contents in known relation frames, two taught-definition recalls, five unsupported capability probes, one ambiguous sentence and one invalid ordered arithmetic request. Correctly declining a creative-writing request is recorded as correct boundary handling; it is not a creative-writing capability. New wording and original-language argument interpretation remain unsupported.

These are developer-authored partitions for a first integration trial, not an independently designed language benchmark or evidence of graduate proficiency. No source passage, final answer, teacher function or annotation file is consulted by saved-model arithmetic inference. Source-specific lexical recall is explicitly a lookup in retained memory. All numerical work, source exposure and language-frame learning have separate result fields.

The [completed 7 September trial](../experiments/2026-09-07-connectors-language.md) records the actual results, model sizes, source exposure, limitations and independent evidence audit.

## Next requirements

The next substantive learning mechanism is compositional parsing with reusable typed meanings, explicit entities, scope and negation, followed by checked inference over those meanings. Literature requires speaker and narrator distinctions, metaphor, ambiguity and interpretation tied to passages. Research reading requires assumptions, methods, evidence and limitations. Creativity needs an independently assessed task with novelty and usefulness criteria. None follows automatically from adding more books or counting more words.
