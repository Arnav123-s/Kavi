# Kavi growth and compression cycles

Author: Arnav123-s
Status: research specification; not implemented by the current arithmetic prototype

## The idea in plain language

Kavi is meant to learn in stages. At the beginning of a stage it has a compact
foundation. It may add a limited amount of temporary structure while learning a
new skill. Before moving to the next stage, it tries to keep the useful part in
a smaller foundation again. It may advance only if it still passes the old
tests, learns the new skill, and stays inside the device budget.

The word zero in a new stage means zero progress through that stage. It does
not mean that old knowledge was erased, that storage is infinite, or that one
number can contain arbitrary information.

## Fixed ceiling, changing allocation

There are three different quantities. They must not be confused.

| Quantity | Meaning | May change during a stage? |
| --- | --- | --- |
| Device ceiling | The absolute limit for memory, working memory, elapsed time, and permitted parallel work. | No, unless the owner explicitly changes it. |
| Foundation allocation | The compact persistent model carried from the previous stage. | Only after a successful promotion. |
| Expansion allocation | Temporary pathways, adapters, or local state used to learn the current stage. | Yes, but only inside the remaining ceiling. |

Every proposal must count persistent scalars, numerical precision, temporary
candidate state, optimizer or search state, replay or reference material,
working buffers, and evaluation copies. Counting parameters alone is not an
honest resource budget.

## Required promotion rule

A growth cycle must follow this order:

1. Declare the current foundation, the hard resource ceiling, a curriculum
   boundary, and fixed protected and held-out tests.
2. Allocate a bounded expansion budget before learning begins.
3. Learn only through a stated update rule and record every proposed change.
4. Test the expanded candidate on the current skill, earlier protected skills,
   and held-out transfer cases.
5. Produce one or more compact candidates without altering the frozen parent,
   test suite, or acceptance rule.
6. Promote only a candidate that meets the predeclared thresholds and fits the
   next-stage foundation allocation.
7. Otherwise retain the current parent, record the failure, and either reject
   the mechanism or start a separately declared experiment.

The current Kavi code implements a very small version of step 3 through step
6 for three arithmetic readout scalars. It does not implement architecture
growth, neural pruning, or permanent compression.

## What compression can and cannot mean

Compression is an engineering claim that needs measurements. Plausible
mechanisms include reusable rules replacing repeated instances, low-rank or
factorized parameterizations, quantization with an error bound, merging
redundant pathways, or a short verified program replacing a table of answers.

It cannot mean silently throwing away failures, moving information into an
unmeasured cache, renaming a large state as one weight, or relying on a wider
external library while claiming the model became smaller. A smaller model may
also take longer to compute; time and working memory remain part of the cost.

## Minimal accounting record

Each future cycle should write an experiment record containing the following
fields before the run begins.

| Field | Purpose |
| --- | --- |
| Parent commit and configuration | Identifies the exact starting point. |
| Foundation and expansion budgets | Makes the ceiling testable. |
| Precision and state ledger | Prevents hidden memory changes. |
| Source and rights record | Keeps curriculum content separately reviewed. |
| Protected, current, and held-out manifests | Prevents score changes after seeing results. |
| Candidate generator | States exactly how a compact candidate is formed. |
| Promotion thresholds | Defines success before the run. |
| Measurements | Includes accuracy, abstention, error, elapsed time, peak memory, and available thermal data. |
| Failure analysis | Records regressions, rejected candidates, and unresolved causes. |

## Pseudocode for a bounded cycle

    parent = load_frozen_foundation()
    budget = declare_fixed_budget()
    proposal = grow_within_budget(parent, budget.expansion)
    measure(proposal, current, protected, held_out, budget)

    compact_candidates = compress_without_mutating(parent, proposal, budget.foundation)
    accepted = [candidate for candidate in compact_candidates
                if passes_predeclared_tests(candidate, protected, held_out)
                and fits(candidate, budget.foundation)]

    if accepted:
        promote(best_by_declared_rule(accepted))
    else:
        retain(parent)
        record_rejection()

The pseudocode is a protocol, not an implementation or a guarantee that a
useful compact candidate exists.

## Safety and scientific boundaries

The cycle may not rewrite its evaluator, alter the device limits, change its
own source code, pull unreviewed documents, or continue in the background.
Those actions would make an apparent improvement impossible to audit. A failed
cycle is valuable evidence; it is not a reason to loosen acceptance criteria.

For the design that motivates this page, see [DESIGN.md](DESIGN.md),
[KAVI_COMPLETE_DESIGN.md](KAVI_COMPLETE_DESIGN.md), and
[EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md).
