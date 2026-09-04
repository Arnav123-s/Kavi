# Kavi multilingual foundations

Author: Arnav123-s

Status: curriculum proposal for owner review; no multilingual training has begun

## The simple idea

Kavi should not begin as an English-only reader and then treat every other
language as an add-on. It should first learn how to preserve a written signal,
then distinguish writing systems, then learn exact quantities, then learn the
rules of each language it is actually approved to study. Only after those
pieces pass their tests should it approach an original work.

This is a **prerequisite graph**, not a randomized pile of books and not a
ranking of people or cultures. A node unlocks only after its listed earlier
nodes pass fixed protected and held-out checks. Several language lanes can be
at the same level because none is a default or a lesser version of another;
the device still schedules them serially unless a later measurement proves a
safe resource budget for more work.

The machine-readable plan is
[multilingual-foundations.json](../curriculum/multilingual-foundations.json).
The companion catalog of people, traditions, and original works is
[people-and-works.json](../curriculum/people-and-works.json).

## What Kavi can really do today

The current generated symbol core can only distinguish lowercase ASCII letters
from decimal digits. Its arithmetic core can learn a small generated addition
and subtraction rule. Neither one reads a word, understands a language, or
handles Unicode scripts. This is a hard boundary, not a temporary label.

So the first actual code is only a source-free bootstrap. It must not be called
Arabic, Bengali, Chinese, Devanagari, Hangul, Tamil, or multilingual learning.
Those capabilities require a new tested model core before any training run is
authorized.

## Teaching order

| Level | Kavi learns | It must already know | Gate before moving on |
| --- | --- | --- | --- |
| L0 | How to preserve a signal: bytes, Unicode scalars, direction, and normalization metadata | Nothing | Exact round-trip of every supported token; abstain on unsupported input. |
| L1 | Tiny generated ASCII letter/digit categories | Nothing | Fixed protected and held-out glyph tests. |
| L2 | Script identity and glyph differences | L0 and L1 | Generated, balanced, script-aware held-out tests. |
| L3 | Numeral systems and exact quantities | L2 | Exact conversion/arithmetic tests on unseen written forms. |
| L4 | Language-specific word formation and grammar | L2 and L3 | Qualified language review plus held-out composition tests. |
| L5 | Definitions, arguments, source location, and approved original/translation alignment | L4 | Rights, provenance, cultural protocol, verifier, retention, and transfer gates. |
| L6 | Mathematics, science, logic, and research works | L5 | Domain verifier plus retained earlier-script and language ability. |

This means Kavi cannot jump from recognizing a character to reading an ancient
text, and it cannot jump from a translation to a claim about the original.

## What “not randomized” means

There are two different things that are easy to mix up:

1. **The learning route:** fixed. A later node cannot be selected until every
   prerequisite has passed. No famous book or difficult problem gets to skip
   the foundations.
2. **Generated practice within one unlocked node:** reproducible and declared.
   It may enumerate varied examples to test generalization, but its identifier,
   seed or enumerator, source status, and evaluation split must be recorded.
   It may never silently introduce an unearned concept.

For source-based lessons, the order is even stricter: source review comes
before local extraction; a named concept comes before a lesson; a verifier and
held-out test are fixed before learning is measured.

## Script is not language

One script can write many languages, and one language can be written in more
than one script. For example, Latin is used by many languages; Arabic-derived
writing is used by Arabic, Persian, Urdu, and several Ajami traditions; Han
characters have different relationships to Chinese, Japanese, and Korean.
Kavi therefore stores **script**, **language**, **direction**, **edition or
manuscript witness**, and **source location** as different facts. It must not
guess that shared letters mean shared grammar or meaning.

The starting lanes intentionally include Latin/IPA, Greek/Cyrillic,
Arabic-derived scripts, South Asian scripts, East Asian scripts, African
scripts and language traditions, Indigenous Americas/Oceania, and an
expandable group for other regional and historic scripts. This is broad by
design, but it does not pretend to cover every living or historical language.
Each additional lane needs a qualified reviewer and a script-aware evaluator.

## Original-language works: what “use the original” safely means

For every work in the catalog, the original-language title and script are kept
as metadata. That makes the original the reference point instead of making a
translation look like the work itself. It does **not** authorize copying,
scraping, or training on the work.

Before any extract can enter a local lesson workspace, Kavi needs all of these:

1. The exact edition or manuscript witness, original language and script,
   creator or tradition, source location, provenance, and rights basis.
2. A record of textual variants, editorial layers, or translation layers when
   they matter.
3. Any cultural or community protocol that applies. Indigenous, oral, sacred,
   ceremonial, and community-governed knowledge is never automatically
   collected.
4. A small, stated concept with prerequisite nodes and an independent verifier.
5. A local extract fingerprint, kept outside this public repository, plus
   protected retention and held-out transfer tests.

Some collections must remain catalog-only even when they are readable on the
web. The Chinese Text Project, for example, says that its content is protected,
forbids automated large downloads, and requires permission for republication;
it is a source locator, not a corpus to scrape. See its
[FAQ](https://ctext.org/faq/ens). UNESCO describes the Timbuktu collections as
handwritten cultural heritage held in public and private collections, so the
catalog keeps those as provenance-and-community-review entries rather than
automatic data. See [UNESCO's overview](https://www.unesco.org/en/articles/mali-timbuktu-manuscripts).

The catalog also identifies the *Hunminjeongeum* manuscript in its original
Korean/Hanja setting; UNESCO records it as the 1446 work that promulgated the
Korean alphabet and includes explanatory material. That makes it a useful
metadata reference for a future Korean-script lane, not an automatically
ingested lesson. See [UNESCO's record](https://www.unesco.org/en/memory-world/hunminjeongeum-manuscript?hub=1081).

## How a future language lane would run

Here is the required sequence for one language/script lane, in child-simple
terms:

1. **Keep the marks unchanged.** Kavi proves it can receive and return the
   characters without silently changing them.
2. **Tell marks apart.** It learns generated glyph identity and direction;
   confusingly similar marks are held out for testing.
3. **Learn the writing rules.** It learns only the approved facts about joining,
   grapheme boundaries, or character composition for that lane.
4. **Learn tiny meaningful pieces.** It learns reviewed morphology and simple
   word formation before sentences.
5. **Learn checked statements.** It reads one approved definition, claim, or
   worked example with a verifier and source location.
6. **Keep what it learned.** It must still pass earlier glyph, number, and
   language tests before the next topic unlocks.

If any gate fails, the next level stays locked. The response is a recorded
failure, more review, or an abstention—not a claim that Kavi has understood the
source.

## Why the catalog is arranged by prerequisites rather than “greatest people”

The catalog has shared generated foundations first, then source lanes whose
conceptual entry conditions are explicit. Within later mathematics, logic,
science, and computation work, the order is driven by needs such as
symbol handling -> quantity -> definitions -> proof -> measurement -> research,
not by nationality or a claim that one person is more intelligent than another.

Original works from South Asia, East Asia, West Asia and North Africa, Africa,
the Americas and Oceania, Europe, and cross-regional modern fields appear as
parallel catalog lanes after the shared prerequisites. A lane is allowed to
advance only when its own language competence, source review, and domain
verifier exist.

## Next boundary

This revision is ready for the owner to review as a curriculum and source list.
It does not start a run, download a work, create a checkpoint, or extend the
model with a Unicode/text core. After review, the next safe engineering task
would be a small generated multiscript glyph core with a fixed script-balanced
evaluation manifest—not source-text training.
