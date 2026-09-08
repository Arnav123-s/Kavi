# Published English questions, reuse and structural sharing

Author: [Arnav123-s](https://github.com/Arnav123-s)

Later [incremental, questioning and direct-state experiments](2026-09-07-incremental-inquiry-transfer.md) extend this record. The results below retain their original measured configurations and denominators.

7 September 2026. Two completed teaching courses and one subsequent representation check. The acquired English configurations compute proposed answers without retrieving teaching questions, answers, dictionaries or source passages. They remain weak mathematical-language prototypes.

The first course learned useful routing for elementary arithmetic. The larger course improved on a separate source but damaged earlier English answers. Exact sharing then reduced the larger artifact's size without changing its acquired decisions. None of these results establishes general English comprehension, autonomous intent formation or graduate-level competence.

## Results

| Measurement | Initial configuration | Expanded configuration |
| --- | ---: | ---: |
| Teaching questions | 389 | 1,822 |
| Development questions | 136 | 476 |
| Selected development result | 86/136 | 138/476 |
| Original 150-question ASDiv bank | 100/150 | 87/150, follow-up |
| Expanded ASDiv follow-up bank | Outside initial admission | 91/175 |
| Official GSM8K test, 303 admitted problems | 17/303 | 30/303 |
| Official GSM8K test, all 1,319 problems | Not evaluated beyond the 303 selected problems | 30/1,319 |
| Serialized English configuration | 5,201 bytes | 149,917 bytes |

The initial ASDiv score is 66.7% on the supported subset. Its complete admitted-source test partition contains another 187 unsupported questions, giving 100/337, or 29.7%. The expanded GSM8K score is 9.9% on the supported subset and 2.3% with all original test questions included. These denominators prevent the annotation reader's exclusions from disappearing from the assessment.

On the common ASDiv bank, 68 initially correct answers stayed correct, 32 became wrong, and 19 initially wrong answers became correct. All 150 earlier questions were present. The expanded model is therefore retained as an experimental candidate and does not automatically replace the initial model. The 175-question follow-up adds 25 newly admitted questions; it is not a new independent examination.

~~~mermaid
flowchart LR
    A[100 earlier correct answers] --> B[68 retained]
    A --> C[32 regressions]
    D[50 earlier wrong answers] --> E[19 improvements]
    D --> F[31 still wrong]
    B --> G[87 correct after rebuilding]
    E --> G
~~~

## Sources and separation

ASDiv V1.0 contains 2,305 published elementary word problems with human annotations. The source is Miao, Liang and Su's [paper](https://aclanthology.org/2020.acl-main.92/) and [author repository](https://github.com/chaochun/nlu-asdiv-dataset). Its dataset license is CC BY-NC 4.0. The course excludes 752 problems attributed to CommonCoreSheets, DadsWorksheets, Math-Aids and MathWorksheets4Kids. The remaining 1,553 source problems are separated by a normalized-input signature hash before teaching. The initial reader admits 675 and rejects 878 as outside its grammar. The expanded reader admits 806 and rejects 747.

The second source is the human-written **base** GSM8K dataset described by [Cobbe et al.](https://arxiv.org/abs/2110.14168) and distributed in the [OpenAI author repository](https://github.com/openai/grade-school-math). Only the base training and test files are used. Automatically generated Socratic files and model-produced solutions are excluded. The MIT license accompanying that repository remains with the local data. This is data-source attribution.

The GSM8K training file contains 7,473 questions. The expanded reader admits 1,667 and rejects 5,806. Its normalized signatures define training and development partitions. No exact normalized-signature overlap was found between admitted GSM8K training questions and ASDiv's final partition, or between the admitted official GSM8K test and the teaching partition. Exact signature separation does not rule out every paraphrase or similar problem template.

The original test file was downloaded before the run and parsed only after development selected and saved the expanded model. Admission uses the published worked answer to determine whether a test problem belongs to the supported grammar. Answer inference receives only the question text; it cannot use that annotation or the final answer. Consequently, the supported score is conditional on this answer-informed admission process. The full-source denominator remains essential.

| Unmodified source file | Bytes | SHA-256 |
| --- | ---: | --- |
| ASDiv.xml | 947,401 | ef8904068482919ac48c8eeaaf6df344b8a308ba66d048c2d4d87eab82dc4929 |
| GSM8K train.jsonl | 4,166,206 | 17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465 |
| GSM8K test.jsonl | 749,738 | 3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14 |

Source bodies and full transcripts remain local. No invented teaching question, altered-number lesson or generated explanation was added in these courses. Numerical fixtures in interpreter tests are execution checks, not teaching data. The earlier science experiments retain their separate, historically generated-data provenance.

## What was learned

The initial learner receives annotated operation relationships between quantities. It learns predicate branches that rank addition, subtraction, multiplication and division, including argument direction. A supplied search procedure combines those preferences into a variable-input expression. A 125-node tree remains after teaching; lesson texts and frequency tables are discarded from the deployed artifact.

The expanded learner adds two acquired decision structures: quantity relevance and routing into an existing multi-operation program. Its retained structure has 225 relevance nodes, 1,527 operation nodes, 455 program-routing nodes and 588 distinct program definitions. The worked-solution annotations supply those program arrangements. The learned routing decides when to use them. These counts are not numbers of understood concepts.

Each training pass identifies an identical existing program before adding a new definition. At inference, a single learned program choice with compatible arity executes directly. Otherwise, the supplied search combines existing operations. A unique choice at a training leaf does not certify a correct interpretation of unfamiliar prose.

~~~mermaid
flowchart TD
    Q[Completed question text] --> I[Supplied token and quantity encoding]
    I --> R[Acquired relevance decisions]
    R --> P[Acquired program route]
    P --> U[Execute an existing compatible program]
    P --> C[Compose alternatives if the route is unresolved]
    C --> O[Acquired operation preferences]
    O --> E[Execute the selected arrangement]
    U --> A[One proposed answer]
    E --> A
~~~

The four numerical operation interfaces, token features, Gini split criterion, finite expression grammar, equation-isolation procedure and candidate-ranking rule are supplied. This experiment is related to arithmetic semantic parsing, including Roy and Roth's [Solving General Arithmetic Word Problems](https://aclanthology.org/D15-1202/); it is not a replication of that system or a new universal language-learning method.

The newer [interacting-configuration runtime](../docs/INTERACTING_CONFIGURATIONS.md) is a separate execution mechanism. The two English learners measured here use predicate routes. The later direct-state course acquires recurrent word transitions and reports their weak generalization separately.

## Controls and failures

The initial language-blind control scores 43/150, compared with 100/150 for learned routing. Removing its wider candidate beam retains 100/150 while reducing candidate constructions from 13,638 to 2,898. This is evidence about the declared search conditions; the two sizes were not selected using a new final set.

Only 12 initial test problems have program shapes absent from teaching, and only two are answered correctly. The stronger aggregate result therefore should not be described as broad invention of unfamiliar multi-step programs.

On the 303 admitted GSM8K test problems, reuse-first execution answers 30 correctly, compared with 26 for composition on every problem under the same expanded relevance and operation decisions. It directly reuses a program on 21 questions. Candidate constructions fall from 3,418,338 to 3,279,504, a 4.1% reduction. These are candidate-work counts, not a measured wall-clock speedup or a statistical significance claim.

The expanded model answers 4/95 GSM8K problems containing irrelevant explicit quantities and 1/31 with more than five active quantities. On the ASDiv follow-up it answers 0/5 admitted algebra questions and 4/20 with irrelevant quantities. No admitted GSM8K test problem exercises the separate linear-equation annotation path. Increasing the grammar bound did not solve these interpretation problems.

Unsupported cases include implicit constants, quantities used repeatedly, unsupported equation forms, multiple answers, nonlinear equations and worked solutions that cannot be reconstructed uniquely. Failures and work-budget exhaustion count as wrong. The preserved 17/17 scientific checks exercise a separate numerical registry; they do not cancel the English regressions.

## Sharing repeated structures

The subsequent transformation groups **identical ordered computational substructures**. It shares predicate suffixes and expression subtrees while retaining every program entry and its argument positions. It does not group words by meaning, merge temporary activations, change operator order or discover intent.

| Representation | Predicate nodes | Program nodes | Serialized bytes |
| --- | ---: | ---: | ---: |
| Original artifact | 2,207 | 4,498 occurrences when expanded | 149,917 |
| Shared format with sharing disabled | 2,207 | 4,498 | 196,360 |
| Shared format with sharing enabled | 1,411 | 975 | 109,826 |

The final artifact is 26.7% smaller than the original. The same-format control shows a 44.1% reduction from sharing itself; changing the encoding without sharing would have made the artifact larger.

The checker compares every original ordered predicate structure and all 588 program expressions against their shared representation. Exact structural equality preserves predicate outputs and arithmetic evaluation order under the unchanged interpreter. The new runtime loads the shared representation directly; it does not load the original model or training material. Only the selected program is expanded temporarily when execution needs it.

The check establishes representational preservation, including the original mistakes. It establishes no new correctness result about English and no guarantee for future behavior-changing repairs. Each invocation still owns its own temporary values. Two uses of the same definition must remain separate when their states or input histories differ.

The transformation and full structural verification take 0.0324 seconds wall time and 0.03125 seconds CPU time in this run. The recorded work includes 13,410 node visits across the shared and unshared transformations, 4,319 repeated-node matches, 2,207 predicate comparisons and 588 program comparisons. Peak memory was not measured for this short transformation.

## Resources and artifacts

| Resource | Initial course | Expanded course |
| --- | ---: | ---: |
| Wall time | 18.413 s | 272.156 s |
| CPU time | 3.344 s | 256.188 s |
| Included display pacing | 15.224 s | 15.240 s |
| Peak worker memory | 68,403,200 bytes | 423,108,608 bytes |
| Local run records, excluding the census file | 794,077 bytes | 1,411,934 bytes |

Both courses use one visible worker, Pause/Resume/Stop, a five-minute limit and a 512 MiB observed worker-memory ceiling. The expanded course also declares a 100-million-unit learning allowance per candidate and a one-million-unit per-question allowance. Reliable CPU-temperature telemetry is unavailable. No later background teaching is installed.

The three source files occupy 5,863,345 bytes. Acquisition metadata, licenses, the interpreter, the acquired arithmetic/science dependency, temporary feature sets, candidate lists, verification work and Python are additional resources. A five-kilobyte routing artifact is not a five-kilobyte complete intelligent system. No matched comparison with a large language model was performed.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [Initial English configuration](english-20260907-initial-model.json) | 5,201 | 0c5626f9aad0e0055baa1cbf1cf0f153daa81fb188293bce104a98f8e197096f |
| [Expanded English configuration](english-20260907-expanded-model.json) | 149,917 | 754f45e15b0be03626f5c044398c51beee75403ca6aa991803a4afdb66d52978 |
| [Shared expanded configuration](english-20260907-shared-model.json) | 109,826 | edc06bbb81611ed74d9de9c8dc952113ae416d1f253dab587feb61695d10ab2a |

The initial implementation is preserved at revision 70c4cb7. A later optional quantity-limit argument leaves its default behavior unchanged; historical source hashes refer to the actual measured version. The [first protocol](../docs/ENGLISH_CONFIGURATION_PROTOCOL.md), [expanded protocol](../docs/PUBLISHED_ENGLISH_REPAIR_PROTOCOL.md), [measurements](2026-09-07-published-english.json), [sharing check](2026-09-07-english-sharing.json) and [data attribution](../docs/ENGLISH_DATA_ATTRIBUTION.md) preserve the conditions and provenance.

## Consequence for the design

There is evidence for compact acquired rules, limited transfer from English to arithmetic, direct reuse and exact representational consolidation. The larger course demonstrates that additional teaching and whole reconstruction can still lose earlier useful distinctions. Exact consolidation reduces that model's size; it cannot repair its missing semantics.

The remaining target is to learn context-dependent interaction patterns, component boundaries and correction procedures, then show transfer and retention in a unified runtime. Broad conversation, philosophy, advanced mathematics, machine learning, chemistry and biology have not been acquired by these courses. The current evidence does not justify a graduate-level or general-intelligence claim.
