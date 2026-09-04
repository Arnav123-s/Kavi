# Kavi model-first curriculum

Author: Arnav123-s

Status: six-stage unified circuit plus bounded regression cores and review-gated curriculum

## The project hierarchy

Kavi itself is the project: the model core that receives signals, forms compact
patterns, makes a prediction, changes only after verification, and carries a
small persistent state forward. The curriculum runner, evaluator, source gate,
and terminal trace are supporting equipment. They exist to teach and measure the
model honestly; they are not the intended final product.

The current project has one six-stage unified model and four earlier bounded regression cores:

1. The arithmetic pathway core receives quantity and relation signals, joins
   them through typed routes, and learns a three-scalar arithmetic readout.
2. The generated-symbol core receives one ASCII glyph, routes it through a
   normalized coordinate, and learns one centroid for letters and one centroid
   for digits. It does not retain a glyph-to-label table or source text.
3. The generated Unicode script-pathway core receives one preserved Unicode
   scalar, routes its exact code point through a bounded coordinate, and learns
   one centroid and support count for each of eleven declared pathways.
4. The reviewed textbook concept core receives a small algebra notation,
   stores two five-facet prototype centers and support counts, and distinguishes
   `expression` from `relation` only after fixed candidate gates pass.
5. The unified path-centric circuit carries the earlier routes forward, then
   learns six typed composition paths that execute unseen nested combinations
   while retesting every earlier stage.

A separate Unicode scalar contract is the ingress rule for the Unicode script core: it
preserves the original scalar and records normalization only as metadata. It
never rewrites the input. None of these cores is a language model or a general
intelligence. They are small, falsifiable pieces of the proposed Kavi model
architecture. See [UNICODE_SCRIPT_STAGE.md](UNICODE_SCRIPT_STAGE.md) for the
formula, test manifest, and strict scope boundary.

## The new symbol learning rule

For each class k, the core stores only a support count n_k and one centroid
mu_k. Given the normalized ASCII coordinate x of a verified glyph, a candidate
updates the appropriate pattern using:

    n_k(next) = n_k + 1
    mu_k(next) = mu_k + (x - mu_k) / n_k(next)

At inference, the glyph follows the only allowed route:

    glyph -> ordinal coordinate -> nearest verified prototype

The core abstains until it has evidence for both categories or when the two
prototype distances are too similar. It builds a child state from a finite
batch, measures that child on current, protected, and held-out symbols, and
promotes it only when error does not regress. The permanent state contains two
centroids and two support counts, not the presented symbols.

This is a deliberately small test of the requested idea that useful knowledge
should become compact structure rather than a growing pile of raw examples.
It does not prove that the same method can learn natural language, science, or
research mathematics.

## Teaching order

The order is based on prerequisites and fixed evaluation gates, not a claim that
people can be ranked by innate intelligence. The model cannot choose a later
stage because a work is famous or easy to obtain. A stage remains locked until
its declared earlier skills have passed their protected and held-out tests.

| Level | What Kavi learns | Current state |
| --- | --- | --- |
| Bootstrap | Generated lowercase ASCII letter/digit kinds | Implemented; fixed canonical lesson order. |
| Bootstrap | Generated quantities, addition before subtraction, and exact checks | Implemented; fixed canonical lesson ladder. |
| L0 | Exact one-scalar Unicode preservation and local metadata | Implemented source-free contract; no sequence or language claim. |
| L2 | Generated multiscript glyph pathways and confusable-character checks | Implemented bounded prototype core and fixed single-glyph evaluator; not script or language recognition. |
| L3 | One CC BY-SA local-only algebra lesson: expressions, relations, and exact variable-free checks | Implemented, finite, source fingerprinted, and bounded; not a text reader. |
| L3.5 | Typed path composition across existing glyph, script, arithmetic, comparison, and selection routes | Implemented source-free structural contracts with unseen nested programs and full earlier-skill retention; not natural language. |
| L3 | Numeral systems and exact quantities across more reviewed notation forms | Waiting for a separate reviewed lesson and evaluator. |
| L4-L5 | Language-specific word formation, definitions, and original/translation separation | Waiting for text-capable paths and qualified language review. |
| L5-L6 | Formal logic, counterexamples, and checked proofs | Waiting for typed symbolic language and an external verifier. |
| L5-L6 | Original-language works and carefully licensed textbooks | Waiting for language skill, rights, provenance, cultural protocol, extract, lesson, and test review. |

The full author-and-work hierarchy is in
[people-and-works.json](../curriculum/people-and-works.json). Its access URLs
and their current non-admission status are in
[access-records.json](../curriculum/access-records.json). The detailed
multilingual prerequisite graph is in
[multilingual-foundations.json](../curriculum/multilingual-foundations.json) and
explained in [MULTILINGUAL_FOUNDATIONS.md](MULTILINGUAL_FOUNDATIONS.md). The
public starred repository list is recorded separately as a methods-reference
catalog in
[methods-from-starred-repositories.json](../curriculum/methods-from-starred-repositories.json).

The curriculum graph and generated lesson schedules are deliberately not
randomized: eligibility is prerequisite-gated, generated early lessons follow a
canonical sequence, and any future varied practice must declare its reproducing
enumerator and held-out evaluation before it runs.

## Why source works are not automatically ingested

A famous title is not automatically a training permission. Exact editions,
translations, jurisdictions, and host terms can differ. For example, Project
Gutenberg distinguishes individual works unrestricted under U.S. copyright law
from works distributed with permission, says the individual eBook must be
checked, and notes that other countries have their own rules. See its
[license guidance](https://www.gutenberg.org/policy/license.html).

Accordingly, the catalog labels works as candidates, references, or quarantined
items. It never copies a book, paper, or PDF into this repository. An access
link is a review locator, not permission to crawl or ingest a host. Before a
source can enter Kavi's local lesson workspace, record all of the following:

1. Exact work, edition, language, creator, source URL, and applicable rights.
2. Local extract fingerprint and the permission basis for the intended use.
3. One concept, prerequisites, and a concise lesson claim.
4. A verifier that can independently check the claim.
5. Protected earlier-skill tests and held-out transfer tests.

The source-safety policy is enforced by
[DOCUMENT_CURRICULUM_GATE.md](DOCUMENT_CURRICULUM_GATE.md).

## External developmental teacher

The unified circuit now has an external corrective teacher and bounded
candidate search. It can repair supported script mistakes using the original
Unicode reference, retest older skills, and run fresh harder composition
questions against a 90% mastery gate. This leaves the inference model separate
from the teacher and its source table. See
[DEVELOPMENTAL_TEACHING.md](DEVELOPMENTAL_TEACHING.md). Words, sentence meaning,
multiplication/division, and broad source learning still lack model handlers.

## Automation behavior

Kavi now has a finite curriculum runner. It can automatically advance through
the declared runnable stages, checkpoint only after they pass their fixed
metrics, and stop at the first failed, missing-capability, or source-review
gate. It does not download books, access the network, alter itself, change
hardware settings, create a background service, or bypass pause and stop files.

Review commands that do not start training:

    python -m kavi.catalog_cli
    python -m kavi.school_cli --list

The owner-authorized local checkpoint completed the four generated foundations.
With the separately reviewed local lesson and its matching PDF/extract in the
ignored `private` workspace, the following command runs exactly the next
textbook-concept stage and then stops at the word-learning gate:

    python -u -m kavi.school_cli --max-stages 1 --interval-ms 750 --state-file runs\kavi-school-state.json

If that local lesson is missing or its fingerprint does not match, the source
stage reports a visible gate failure and does not run.

The unified six-stage run, including typed composition, is available through
`python -m kavi.pathway_cli run` or the multi-tab
`scripts/start-live-pathways.ps1` launcher. Its machine-readable order is in
[curriculum/pathway-curriculum.json](../curriculum/pathway-curriculum.json).
The state file is opt-in and local-only. It contains completed stage IDs, not
source text or model weights. A pause or stop file can be added to the command
exactly as documented in [OPERATIONS_AND_REPRODUCIBILITY.md](OPERATIONS_AND_REPRODUCIBILITY.md).

## Review boundary

The Unicode extension and the reviewed textbook-concept extension have isolated
unit tests. One owner-authorized local checkpoint completed the four generated
foundations. One owner-authorized local source intake admitted only the narrow
algebra lesson described in [TEXTBOOK_CONCEPT_STAGE.md](TEXTBOOK_CONCEPT_STAGE.md);
it did not add a source body to Git or create a persistent training process.
Review the catalog and authorize each new finite lesson separately. Changing the
people/works order or admitting a broader source remains a later decision.
