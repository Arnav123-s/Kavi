# Explanation-learning smoke test

Experiment ID: E1-2026-09-03-01
Date: 2026-09-03
Source revision: a9ee754
Author: Arnav123-s
Status: completed, limited-domain result

## Question

Does a verifier-gated pathway learner improve faster when a wrong arithmetic
answer receives a checked explanation of the transformation, rather than only a
target number?

## Method

Each event used the existing two-facet quantity/relation graph. The independent
arithmetic verifier supplied a trusted structured lesson:

- rule identifier;
- human-readable explanation;
- exact target;
- scoped target transformation parameters: left coefficient 1, signed-right
  coefficient 1, and bias 0.

The learner blended a local error proposal with those target transformation
parameters only in an isolated candidate. It promoted the candidate only after
protected and held-out manifests did not regress under the declared policy.

This is not free-form natural-language understanding. The explanation was
generated and checked in a deliberately tiny white-box arithmetic domain.

## Configuration

    python -u -m kavi.lesson_cli --steps 12 --seed 7 --workers 1 --max-active-routes 2 --conflict-every 0 --interval-ms 100 --ask 7 5 add

- finite lessons: 12;
- active facet-route cap: 2;
- independent evaluator workers: 1;
- external/network sources used during run: none;
- hardware setting changes: none;
- background persistence and source modification: none.

## Verification

The complete local test suite passed:

    python -m unittest discover -s tests -v

Result: 12 tests passed in 0.034 seconds.

The suite includes source-admission tests that reject a quarantined textbook
record from supplying a lesson.

## Result

| Measurement | Observed value |
|---|---:|
| Finite lessons completed | 12 |
| Explanation-guided candidates promoted | 5 |
| Correct answers before feedback | 7 |
| Abstentions | 0 |
| Final unseen query | 7 + 5 = 12 |
| Query confidence | 0.81 |
| Query uncertainty | 0.19 |

The first candidate reduced protected mean absolute error from 4.25 to 1.75 and
held-out mean absolute error from 14.00 to 6.25. Later candidates reached zero
mean absolute error on both small fixed manifests.

## Limits and failures to retain

1. The learner was taught one exact linear arithmetic rule in structured form.
   It did not read a textbook or research paper during this experiment.
2. Passing one unseen addition query is not evidence of broad generalisation,
   language understanding, scientific reasoning, or autonomy.
3. The source manifest contains metadata only. It does not contain book or
   paper bodies, and the document curriculum has not begun ingesting content.
4. A source's visible availability and a Creative Commons label do not override
   title-specific AI-use terms. Quarantined sources remain unused.
5. The live trace's route display still labels four active pipes against a
   two-route cap. That is a presentation issue to correct separately; the
   resource ledger itself reports pipes and routes separately.

## Decision

Keep E1 as evidence that verified structured explanations can accelerate this
toy pathway learner. The next experiment must use a separately reviewed,
admissible source extract, a source fingerprint, a concept-level verifier, and
withheld source-linked tests. Do not promote unreviewed documents, self-made
claims, or raw paper text into the learner.
