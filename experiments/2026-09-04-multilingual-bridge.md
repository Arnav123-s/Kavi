# Multilingual bridge and mixed-quiz rollout

Date: 2026-09-04. Baseline teaching code: `ffb347e`.

## Owner-authorized scope

Add multiple-language foundations, increase teaching difficulty, and reduce
repetitive quizzes without replacing the model. A teacher restart was initially
blocked pending explicit authorization; no workaround was used. After the owner
approved, the old teacher saved its checkpoint and a new teacher resumed the
same learned core. Validation found a rehearsal omission; a subsequent
checkpointed continuation activated the correction.

The bridge is a narrow writing/symbol experiment. It does not implement complete
Hindi, Arabic or Spanish language courses, or certify the broader curriculum.

## Read-only evidence before switching

The same fixed assessment was given to two checkpoint copies, with no optimizer
updates. Both models were tested on the same 52 familiar letters and the same
64 previously unrecorded three-letter and 64 four-letter prompts:

| Checkpoint | Familiar single letters | Unseen three-letter cases | Unseen four-letter cases |
| --- | --- | --- | --- |
| Earlier, 6,454 updates | 3/52 | 0/64 | 0/64 |
| Later, 27,156 updates | 52/52 | 6/64 | 0/64 |

These measured results confirm limited learning, not readiness for unrestricted
language. They also explain why repeated 52/52 answers were insufficient
evidence for advancing a certified language-comprehension stage. The private
comparison report records exact checkpoint fingerprints and every answer.

## First live extension

The old active teacher stopped cleanly with 46,831 updates, 66,880 parameters,
and no completed language stage. The saved checkpoint hash was
`b19f8899521f11a79c704e8fb90d71b8cebbfe0dd9c1906b19ca7f156541d49f`.

The first extension cycle was accepted after the initial four Devanagari forms
passed and the earlier Latin letters remained correct. An early Arabic lesson
produced 2/4 correct familiar forms. Another observed Spanish lesson produced
4/4 familiar forms but regressed previously correct script characters, so the
candidate was rolled back rather than credited as retained learning.

Initial cycle outcomes were accepted, rollback, rollback, accepted, rollback,
rollback. Thus the first extension was not uniformly successful. Rehearsing only
Latin and the currently taught script was insufficient. The teacher was amended
to rehearse **all** previously correct script characters in each new cycle and
to attempt cross-script remediation before rollback. No retention standard or
model architecture was changed.

The first reserved three-letter assessment after a bridge cycle measured 25/64;
four-letter performance was 0/64. A later three-letter check was 20/64. These
fixed-bank results show that updates are not necessarily monotonic improvements.
They use a different bank from the earlier offline comparison and therefore
must not be presented as an exact 6-to-25 improvement on identical questions.

Early fresh mixed quizzes included results of 5/32 and 3/32. Those quizzes
included previously unsupported symbol-operation combinations and foreign
written forms; their scores are not directly comparable to the 52/52 familiar
Latin-letter score. Later results are recorded by the live run and must be read,
not predicted from this initial report.

## After the rehearsal correction

The resumed live teacher accepted six consecutive observed cycles (19 through
24) without changing the network size. At the measured checkpoint in the live
feed, the protected 52 Latin letters remained correct, and the selected script
subsets scored 8/8 Devanagari, 8/8 Arabic and 7/7 additional Latin written forms.
The four familiar written number words also scored 4/4. These are familiar-item
and retention results, not proof of language comprehension or new-word meaning.
The harder mixed and reserved tests remain independent gates, with no English
sequence stage marked complete at this observation.

## Data and measurement controls

The original Unicode character database and selected De Morgan number-name
table were checked against admitted fingerprints. Selected code points are
limited subsets, not complete scripts. New copy/join/first/last questions are
labeled teacher-defined exercises, never quotations by those sources' authors.

Fresh mixed prompts exclude previous prompts and training exposures. Reserved
assessment sequences are excluded across automatic exercise families. Practice,
retention, fresh mixed quizzes and repeated reserved assessments have distinct
labels. Grades are computed from actual generated answers with frozen weights.
No string-operation helper answers on the learner's behalf.

## Verification and resource boundary

`python -m unittest discover -s tests -q`: 101 tests passed after the rehearsal
correction. Added checks cover unseen-pool separation, deterministic generation,
operator balance, Unicode identity, exact grading, previous-script rehearsal,
checkpoint-publication guards and question-only inference. Mock tests establish
controller behavior, not model capability.

The network remains 66,880 parameters / 267,520 parameter bytes, with 535,072
recorded optimizer bytes, 64 mixing points and 256 available links. Two numerical
CPU threads and batches of at most four are retained. Total application RAM,
logs, books and archives exceed those tensor figures. No new thermal or peak
RAM measurement is claimed. No hardware safety threshold was modified.

The model has not demonstrated multilingual comprehension, word meanings,
general reasoning, master's-level skill, unlimited memory or quantum advantage.
The live session remains bounded and stoppable. Source texts, raw assessment
answers, checkpoints and conversation logs stay outside the public repository.
