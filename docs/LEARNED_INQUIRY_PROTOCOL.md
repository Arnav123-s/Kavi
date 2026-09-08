# Learning to ask during correction

Author: [Arnav123-s](https://github.com/Arnav123-s)

7 September 2026. Recorded before the questioning course.

## Behavior to learn

Learn whether to ask a teacher about a relationship that the current arithmetic interpretation may have misunderstood. The learned object contains predicate connections leading to `ask` or `answer`. It contains no saved questions, reference answers, correction episodes or class frequencies. This is an operational decision under uncertainty; it is not a claim of a subjective feeling of doubt.

Use the configuration selected by the incremental English course as the fixed language component. Preserve that component during this experiment so changes in questioning can be measured separately from changes in arithmetic interpretation. The incremental course already tested persistent corrections to the language configuration. A reply during the present evaluation changes only the current calculation, not the deployed model.

## Teaching evidence

Use the 554 original human-authored teaching questions admitted by the incremental course. Add the next 240 eligible three-quantity GSM8K training questions in the same fixed signature order, excluding every existing training, development and final signature. These are additional genuine source questions. Do not fabricate lessons, substitute numerical variants, or use generated solutions.

For each question, first compute a prediction without its worked answer. Only afterward use the original reference answer and formula to identify an actual mistake. If the final prediction is wrong and a quantity pair has the wrong operation relative to the published derivation, teach `ask` for that pair. Otherwise teach `answer`. A source derivation supplies one valid interpretation; another derivation can also be valid. This label rule does not claim that every differing intermediate expression is an error.

Policy inputs are existing input predicates, the proposed pair relation, the preferred route, and any alternative relation in the bounded candidate set. Correct answers, teacher replies, question identifiers and source formulas are not policy inputs. During teaching, the ordinary input predicates are computed from the source question. In deployment, only predicates acquired by the two configurations are retained in current input activity.

Candidate question policies use predicate trees of depths 4, 8 and 12, with minimum leaf size three. The Gini splitting procedure, features and interface remain supplied. Each leaf retains only its ordering of action ports. Include the original policy that never asks. Selection uses the incremental course's 216 development questions: maximize correct answers after a reply minus 0.1 times questions asked; break ties by fewer questions and smaller configuration. Record all candidates, including any failure to learn a useful policy.

## Question and reply interface

A question asks which of six oriented arithmetic relations connects the branches containing a selected pair of explicit quantities. Relations are addition, subtraction, reversed subtraction, multiplication, division and reversed division. This refers to the operation where the two branches meet; it does not necessarily mean applying an operation directly to the two literal numbers.

The acquired policy decides which pairs warrant a question. If several pairs activate `ask`, use the first pair in input order. Allow one question per problem. Question wording, this tie rule and the six response ports are supplied interface behavior, not learned English generation.

The teaching process answers only the requested relationship, using the published worked derivation. It does not supply the final numerical answer to the learner. The current search must comply with that relation before the resulting calculation can execute. A failed or unhelpful clarification remains a failure; do not ask unlimited questions until the reference answer appears. A teacher reply is additional information, so assisted results are always reported separately from independent answers.

## Follow-up and controls

Freeze the policy before revisiting ASDiv's original 150 questions and the eligible two- or three-quantity GSM8K official test questions. The latter must use every explicit quantity once, matching the admitted grammar. Report excluded questions and denominators. These banks have appeared in earlier project experiments and are follow-up checks, not newly independent exams.

Compare no questions, the learned question decision, and always asking about the first pair. Report independent accuracy, assisted accuracy, questions asked, useful corrections, harmful changes, unchanged answers, the accuracy of answers issued without clarification, and teacher-dependent work. Do not report answers after teacher help as autonomous intelligence. Hash the frozen artifact before and after evaluation to detect persistent updates.

## Controls and scope

Use the visible learning window with Pause, Resume and Stop, a five-minute wall limit and the existing observed 512 MiB worker ceiling. Allow at most 60 million work units per policy reconstruction and one million per problem. Count preparation, all development candidates, final controls, replay, dependency verification and display time. Save full evidence privately and publish filtered counts and identifiers without source bodies.

This experiment teaches a narrow questioning decision from genuine correction feedback. It does not teach general conversation, philosophical doubt, open-ended question writing, or research-level reasoning. Genuine source provenance and restrictions follow [the English data attribution record](ENGLISH_DATA_ATTRIBUTION.md).
