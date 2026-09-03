# Kavi model-first curriculum

Author: Arnav123-s

Status: implemented early-core extension plus review-gated curriculum plan

## The project hierarchy

Kavi itself is the project: the model core that receives signals, forms compact
patterns, makes a prediction, changes only after verification, and carries a
small persistent state forward. The curriculum runner, evaluator, source gate,
and terminal trace are supporting equipment. They exist to teach and measure the
model honestly; they are not the intended final product.

The current model has two real but tiny cores:

1. The arithmetic pathway core receives quantity and relation signals, joins
   them through typed routes, and learns a three-scalar arithmetic readout.
2. The new generated-symbol core receives one ASCII glyph, routes it through a
   normalized coordinate, and learns one centroid for letters and one centroid
   for digits. It does not retain a glyph-to-label table or source text.

Neither core is a language model or a general intelligence. They are the first
small, falsifiable pieces of the proposed Kavi model architecture.

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

The order is based on prerequisites and the availability of exact verifiers,
not a claim that people can be ranked by innate intelligence.

| Order | What Kavi learns | Current state |
| --- | --- | --- |
| 0 | Generated glyph kinds: lowercase letters and decimal digits | Implemented, review-gated before a real run. |
| 1 | Generated quantities, addition, and subtraction | Implemented, review-gated before a real run. |
| 2 | Words, definitions, and compositional language | Waiting for a text-capable Kavi core and evaluation suite. |
| 3 | Formal logic, counterexamples, and checked proofs | Waiting for typed symbolic language and an external verifier. |
| 4 | Primary works and carefully licensed textbooks | Waiting for rights, provenance, extract, lesson, and test review. |

The full author-and-work hierarchy is in
[people-and-works.json](../curriculum/people-and-works.json). The public starred
repository list is recorded separately as a methods-reference catalog in
[methods-from-starred-repositories.json](../curriculum/methods-from-starred-repositories.json).

## Why source works are not automatically ingested

A famous title is not automatically a training permission. Exact editions,
translations, jurisdictions, and host terms can differ. For example, Project
Gutenberg distinguishes individual works unrestricted under U.S. copyright law
from works distributed with permission, says the individual eBook must be
checked, and notes that other countries have their own rules. See its
[license guidance](https://www.gutenberg.org/policy/license.html).

Accordingly, the catalog labels works as candidates, references, or quarantined
items. It never copies a book, paper, or PDF into this repository. Before a
source can enter Kavi's local lesson workspace, record all of the following:

1. Exact work, edition, language, creator, source URL, and applicable rights.
2. Local extract fingerprint and the permission basis for the intended use.
3. One concept, prerequisites, and a concise lesson claim.
4. A verifier that can independently check the claim.
5. Protected earlier-skill tests and held-out transfer tests.

The source-safety policy is enforced by
[DOCUMENT_CURRICULUM_GATE.md](DOCUMENT_CURRICULUM_GATE.md).

## Automation behavior

Kavi now has a finite curriculum runner. It can automatically advance through
the declared runnable stages, checkpoint only after they pass their fixed
metrics, and stop at the first failed, missing-capability, or source-review
gate. It does not download books, access the network, alter itself, change
hardware settings, create a background service, or bypass pause and stop files.

Review commands that do not start training:

    python -m kavi.catalog_cli
    python -m kavi.school_cli --list

After the owner approves the catalog and explicitly authorizes a finite first
run, the command will be:

    python -u -m kavi.school_cli --max-stages 2 --lessons-per-stage 24 --state-file runs\kavi-school-state.json

The state file is opt-in and local-only. It contains completed stage IDs, not
source text or model weights. A pause or stop file can be added to the command
exactly as documented in [OPERATIONS_AND_REPRODUCIBILITY.md](OPERATIONS_AND_REPRODUCIBILITY.md).

## Review boundary

The code has passed isolated generated unit tests only. No real Kavi curriculum
run, source ingestion, or persistent training process has been started from
this plan. Review the catalog first; then choose whether to authorize only the
generated foundations, change the people/works order, or admit a reviewed
source for a later stage.
