# Psychology teaching through earlier configurations

Author: [Arnav123-s](https://github.com/Arnav123-s)

## Question and scope

Can original psychology lessons learn useful routes through the recurrent English
configuration already acquired from arithmetic word problems? The proposed benefit
is shared computation across different forms of input. Sharing states alone is
not evidence that their meanings are equivalent.

The experiment compares two copies of the same 20-state earlier graph. The
transfer arm first attempts to join new routes to its states. The control retains
the earlier graph but forbids those joins. Both use the same lessons, literal
word encoding, output interface, seed, evaluation and work ceilings. A finite
simulation certificate must preserve every defined earlier execution. It does
not make an earlier wrong answer correct.

## Original material and partitions

Teaching uses OpenStax *Psychology 2e*, chapters 2, 6, 7, 8, 11 and 15, at source
revision `de7e40c91813dabdc2875df9d0709fc4f46080bb`. The authors are Rose M.
Spielman, William J. Jenkins and Marilyn D. Lovett. Each lesson consists of an
original review question, its four original alternatives and its original solution
letter. No generated questions, paraphrases, distractors or answer keys are used.

Group questions by source section and sort by SHA-256 of their source identifier.
For a group of four or more, reserve the last question for final evaluation and
the preceding one for development; teach the remainder. For a group of two or
three, reserve its last question for final evaluation. Teach singleton groups.
Exact normalized question duplicates must stay in one partition. No question is
discarded because a model answers it incorrectly.

Teaching proceeds cumulatively: research, learning and memory; then thinking,
language and intelligence; then personality and psychological disorders. Every
original learned constraint is checked after every replacement. This reuses the
earlier arithmetic graph and replays prior psychology constraints; it does not
yet infer a general lesson about how to learn or preserve every unseen psychology
answer from one stage to the next.

An independent final bank uses the original MIT 9.00 Spring 2009 Exam 2 and 9.00SC
Fall 2011 Exam 3. Keys come from the original answer sheet or blue answer markings.
The duplicated option label in 2009 question 4 is excluded. The first three 2011
questions were exposed during source discovery and are excluded. Exam inspection
is for extraction; no final answer is given to learning or model selection. Some
exam content lies beyond the taught chapters; report the full admitted denominator.
The separate 2011 Exam 2 has damaged embedded text and is not admitted.

The first run stopped before final evaluation when its overlap check found MIT
2009 question 42 in the OpenStax bank. The resumed course excludes exact question
duplicates across the entire OpenStax bank, records their identifiers and retains
the same teaching, candidate order and selection rule. The first run and its exact
protocol and runner remain in local evidence. No final score was observed before
this correction.

Full texts, examination keys, source questions and source figures remain in ignored
local storage. Preserve source hashes and exclusions. The source editions are
CC BY-NC-SA 4.0, subject to separately marked material. Psychology-derived model
artifacts distributed from this course carry the same licence and original-source
attribution. Noba readings on intelligence and psychopathy are research material;
they have no admitted keyed exercises in this course.

## Executable interface and learning

Each question-option pair follows one entry and the same graph, irrespective of
subject. Supplied boundaries distinguish the question, an offered answer, and
completed input. Literal stems form the event alphabet; a vocabulary collected
only from teaching partitions maps unknown tokens to one shared event. This
vocabulary preparation sees future teaching-stage words, but no development or
final text. Six earlier arithmetic output ports remain unchanged. Two additional
ports mean that an offered answer agrees or disagrees with the source key.

The source key supervises these relations. It is not available at inference. The
same graph processes all four alternatives, one at a time. A final answer requires
one supported alternative and three rejected alternatives after all four finish.
An undefined route is not treated as a rejection. This interface supplies the
multiple-choice task; it does not demonstrate unrestricted conversation.

Each candidate begins with an external prefix structure of the accumulated source
constraints. The supplied frontier-merging algorithm tests merges into acquired
states first, then new states. Every accepted merge preserves the source constraints
and an explicit mapping of old states and transitions. A control runs the same
procedure with acquired-state joins disabled. Seed 7 is fixed before either final
bank is opened. There is one candidate per arm and teaching stage. Reject a candidate
which fails to finish or loses any previously correct teaching answer. Within an
arm, prefer more correct accumulated teaching answers, then development answers,
then fewer encoded bytes. Record keeping the previous candidate as an outcome.

Direct execution and the existing provisional-connection constructor are measured
separately after freezing. The latter has 16 candidates and at most four provisional
links per question-option stream. It follows defined routes directly and opens
candidates only at missing links. Stable proposal order is supplied and is not
learned confidence. Neither final mode changes persistent connections. Fixed-first
and most-common-teaching-position controls expose scores obtainable without reading.

## Preservation claim

Let an earlier graph have transition function `delta`, output `o` and entry `0`.
A successor has `delta'`, `o'` and a mapping `h` such that:

```text
h(0) = 0
o'(h(s)) = o(s)
delta'(h(s), a) = h(delta(s, a)) whenever delta(s, a) is defined.
```

Induction on input length then preserves every earlier defined execution and its
output, including an unresolved output at a defined state. Additional transitions
can resolve previously undefined inputs. This is a standard simulation argument,
not a new general theorem about intelligence or perfect retention under arbitrary
repairs. Psychology teaching retention is checked on the finite teaching bank.

## Budgets and reporting

One visible worker, five minutes, 512 MiB working-set ceiling, Pause/Resume/Stop.
At most 18,000 initial states and 12,000 merge attempts per candidate; 35 million
counted work units per fit. Count copies, traversal, preservation checks, source
replay, evaluation, persistent serialized bytes, worker memory, CPU time, wall time
and external files. Interpretation code, original arithmetic dependencies and
teaching workspace are not included in the new artifact byte count.

Report teaching accuracy, old-skill preservation, both final banks, unresolved
answers, direct and adaptive execution, both controls, graph sizes, shared-state
visits and every failed candidate. Acquiring a definition of intelligence is not
equivalent to becoming intelligent. No research-grade psychology or clinical
assessment claim follows from this experiment.
