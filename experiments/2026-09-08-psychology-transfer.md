# Psychology teaching and earlier-circuit transfer

Author: [Arnav123-s](https://github.com/Arnav123-s)

The completed event-graph course retained all 68 teaching answers but did not generalize usefully. Both arms answered zero unseen questions correctly by direct execution. Allowing provisional connections produced a few correct answers and many unresolved or wrong answers, below the supplied answer-position controls. This result does not establish psychology understanding or useful transfer from the earlier arithmetic graph.

This course predates the [PCL design](../docs/PCL_DESIGN.md). It tests `event_transfer.py` and `text_choice_events.py`, not the new phase-circuit package. No PCL language or psychology course has been run.

## Protocol and sources

The [protocol](../docs/PSYCHOLOGY_TRANSFER_PROTOCOL.md) fixes three cumulative teaching stages, seed 7, candidate budgets and separate teaching, development and final banks. The [aggregate measurements](2026-09-08-psychology-transfer.json) retain stages, work counts, hashes, exclusions, controls and the earlier failed run. Source bodies, answer keys, per-question outputs and derived checkpoints remain in ignored local folders.

Teaching uses original review questions and their original four options from OpenStax *Psychology 2e*, by Rose M. Spielman, William J. Jenkins and Marilyn D. Lovett. The [official source collection](https://github.com/openstax/osbooks-psychology/tree/de7e40c91813dabdc2875df9d0709fc4f46080bb) is pinned to revision `de7e40c91813dabdc2875df9d0709fc4f46080bb`. Chapters cover research, learning, memory, thinking/intelligence, personality and psychological disorders. There are 68 teaching questions, 17 development questions and 36 final questions.

The independent final bank uses original examinations from John D. E. Gabrieli's [MIT Introduction to Psychology course](https://ocw.mit.edu/courses/9-00sc-introduction-to-psychology-fall-2011/): the archived 2009 second examination and the 2011 third examination. Original answer-sheet letters or the PDF's marked correct options provide evaluation keys. There are 90 admitted independent questions after exclusions. No new distractors or explanatory answers were invented.

The acquired OpenStax collection and MIT course materials carry CC BY-NC-SA terms. Consult the collection's [licence](https://github.com/openstax/osbooks-psychology/blob/de7e40c91813dabdc2875df9d0709fc4f46080bb/LICENSE) and [MIT terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/) before redistributing source derivatives. Public project authorship does not replace third-party attribution. The source-derived circuit artifacts are measured locally and are not redistributed in this revision.

Patrick's [Psychopathy](https://nobaproject.com/modules/psychopathy) and Biswas-Diener's [Intelligence](https://nobaproject.com/modules/intelligence) modules were collected for research. They were not admitted as keyed lessons in this course. The notebook catalogue also remains untrained.

## What was actually transferred

Both arms start with the earlier 20-state event graph, whose saved artifact is 10,590 bytes. The reuse arm tries to merge new routes into acquired states before merging new states with one another. The separate arm uses the same procedure but disallows joins into the acquired states.

A finite simulation certificate preserves every defined old execution through a mapping into the successor. This retains old outputs, including old wrong answers. It does not establish that new routes have the same meaning as the states they join. Finite new teaching constraints are checked separately.

The new interface streams the original question and each original option through one graph. A final answer requires one support port and three rejection ports. Missing execution is not counted as rejection. This is a supplied multiple-choice interface; it does not demonstrate free-form reading or conversation.

Each stage reconstructs from the earlier arithmetic graph plus accumulated psychology constraints. It does not inherit the preceding psychology graph itself. The full teaching-partition vocabulary of 782 word forms is available from the start, including words from later teaching stages. Neither final bank contributes vocabulary or candidate selection evidence.

## Results

| Measurement | Reuse acquired states | Separate new states |
| --- | ---: | ---: |
| Final teaching | 68/68 | 68/68 |
| Development | 0/17 | 0/17 |
| Direct OpenStax final | 0/36 | 0/36 |
| Adaptive OpenStax final | 1/36 | 0/36 |
| Direct independent MIT final | 0/90 | 0/90 |
| Adaptive independent MIT final | 0/90 | 3/90 |
| Direct unresolved, OpenStax / MIT | 36 / 90 | 36 / 90 |
| Adaptive unresolved, OpenStax / MIT | 25 / 79 | 29 / 83 |
| Retained states | 22 | 25 |
| Retained edges | 2,340 | 2,097 |
| Serialized artifact bytes | 33,400 | 29,934 |
| Exact earlier defined execution preserved | Yes | Yes |
| Persistent model unchanged during final evaluation | Yes | Yes |

The reuse arm made 702, 856 and 1,347 joins into old states across its three fits. That is actual structural sharing. It nevertheless produced the larger artifact and no established generalization advantage.

The adaptive mode uses at most 16 candidates and four provisional links per question-option stream. Its stable proposal order is supplied, not learned confidence. A direct invocation carries one current graph state; adaptive execution can carry multiple candidates and additional temporary structure. Those costs must not be hidden behind the direct state count.

A fixed-first-option control scores 16/36 on OpenStax and 18/90 on MIT. The most common teaching answer position scores 9/36 and 20/90 respectively. These controls are not language models; they show that the acquired routes do not yet yield useful performance even against simple answer-position behavior.

## Failed run and extraction limits

The first run completed teaching but stopped before final evaluation after discovering an exact duplicate question across the two source collections. No final scores had been produced. The repaired run excludes MIT 2009 examination 2, question 42, then repeats the same training and selection procedure. Both run records remain in the evidence file.

Other exclusions are an ambiguously labelled original question, three examination questions exposed during source discovery, and the 2011 second-examination PDF whose glyph extraction damaged words. The extractor did not invent repaired text. Exact string exclusion does not guarantee the absence of paraphrases or shared educational content; cross-source independence is limited accordingly.

The first run took 28.85 wall seconds and 17.95 CPU seconds. The completed rerun took 34.85 wall seconds and 20.05 CPU seconds, including 15.06 seconds of display pacing. Its reported peak working set was 34,619,392 bytes. The source download set, original graphs, interpreter, transient strings, candidate copies and teacher workspace are additional to the artifact byte counts. CPU temperature was unavailable.

The repeated fits presented 1,136 binary teaching pairs in total across stages and arms. This is not 1,136 independent source questions. The aggregate evidence retains operation counts for fitting, copying, verification and evaluation.

## Implication for the next learner

Remembering a source lesson as a successful circuit route is insufficient. The next learner must acquire distinctions and reusable operations that work on unfamiliar inputs. PCL's two-layer reconstruction, coupled activity, representation learning and internal world-model targets are attempts to address this gap. Their success must be measured independently; this negative result does not prove or disprove the whole proposal.

The source acquisition and course scripts are retained for reproduction. A fresh curriculum run is separate from read-only inspection and must use an explicit run configuration and visible controls. No additional broad course was launched for this documentation revision.
