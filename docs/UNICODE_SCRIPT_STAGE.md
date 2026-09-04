# Kavi Unicode scalar and script-pathway stage

Author: Arnav123-s

Status: implemented source-free model extension; no document or language training

## What this adds

This is the first Kavi core that can receive a non-ASCII character without
silently replacing it. It has two deliberately separate parts:

1. The **Unicode scalar contract** accepts exactly one Unicode scalar, keeps
   that exact character and code point, and reports only local metadata.
2. The **script-pathway core** learns a tiny compressed prototype for each of
   eleven declared generated pathways. It routes one scalar through a fixed
   hard path and tests the candidate before changing the parent state.

It does not read words, recognize arbitrary writing systems, translate,
identify a person's language, or ingest a document. It is not an
implementation of the Unicode Script property and it is not multilingual
training.

## Exact signal rule

For an input scalar `g`, Kavi retains `g` unchanged and records its code point
`p = ord(g)`. It computes an optional observation only:

    nfc_matches_input = NFC(g) == g

It never substitutes the NFC form for the input. That matters because a
normalization view can differ from an original scalar. The contract rejects an
empty string, a multi-scalar string, and surrogate code points; it accepts a
single combining mark as a scalar but does not claim to understand it.

The design follows Unicode's distinction between code points and normalized
text, while intentionally keeping normalization as metadata at this early
single-scalar stage. See [Unicode Standard Annex #15](https://unicode.org/reports/tr15/)
and [Unicode Standard core specification, Chapter 3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/).
The metadata comes from the local Python Unicode database, so this prototype
does not claim conformance to a particular full Unicode release.

## The small learning core

The model maps the exact code point to a bounded coordinate:

    x = p / 0x10FFFF

For each declared pathway `k`, its only learned values are support `n_k` and
centroid `mu_k`. A verified lesson proposes:

    n_k(next) = n_k + 1
    mu_k(next) = mu_k + (x - mu_k) / n_k(next)

At readout, the scalar follows exactly one route:

    scalar -> exact code point -> bounded coordinate -> nearest verified prototype

Kavi abstains until every declared pathway has at least one verified lesson,
and it abstains when the nearest two prototypes are too close. A batch becomes
a candidate state first. The frozen parent is replaced only if the candidate
adds verified support without worsening current, protected, or held-out error.

The persistent model ledger is deliberately explicit: 11 centroids, 11 support
counts, and one promotion counter—23 scalar values in this prototype. It does
not include Python, the operating system, terminal, graphics hardware, or
other host memory.

## Bounded generated pathways

All values below are individual Unicode scalars declared in code. They are not
words, quotations, source excerpts, a downloaded Unicode table, or training
data from the people-and-works catalog.

| Pathway | Generated training scalars | Protected scalar | Held-out scalar |
| --- | --- | --- | --- |
| Latin | b, c, d | A | o |
| Greek | β, γ, δ | Α | ο |
| Cyrillic | б, в, г | А | о |
| Arabic | ب, ث, ج | ت | د |
| Devanagari | अ, इ, उ | आ | ए |
| Bengali | অ, ই, উ | আ | এ |
| Tamil | அ, இ, உ | ஆ | ஏ |
| Hiragana | あ, う, え | い | お |
| Katakana | ア, ウ, エ | イ | オ |
| Han | 一, 二, 三 | 中 | 字 |
| Hangul | 가, 다, 라 | 나 | 마 |

The Latin, Greek, and Cyrillic protected/held-out checks intentionally keep
separate code points that can appear visually similar (`A`, `Α`, `А`; and
`o`, `ο`, `о`). This is a narrow exact-scalar test, not a claim of broad
confusable detection. Unicode's wider confusable-security guidance is in
[UTS #39](https://unicode.org/reports/tr39/); Kavi does not implement that
standard. Likewise, Unicode's Script and Script_Extensions properties are
defined in [UAX #24](https://unicode.org/reports/tr24/); Kavi uses only its
small declared experimental pathways rather than those complete properties.

## What the visible trace shows

The school emits, for every generated lesson:

- the literal scalar and `U+` code point;
- the three active pipe identifiers;
- the bounded coordinate, answer or abstention, and confidence;
- the parent-versus-candidate current, protected, and held-out errors;
- the compact model ledger; and
- any pause or stop action.

The trace is a visible record of program decisions, not hidden model reasoning
or a claim that the model has read a language.

## Curriculum boundary

`unicode-signal-contract` and `multiscript-glyph-foundations` are now finite,
source-free runnable stages in `curriculum/model-curriculum.json`. The next
stage, `word-forms-and-definitions`, remains locked. It requires a text model,
language-specific evaluation, qualified review, and source admission; neither
is bypassed by this code.

To inspect without running anything:

    python -m kavi.school_cli --list

After an owner explicitly authorizes a finite continuation from a checkpoint
that already contains the two completed bootstrap stages, this command runs at
most the two Unicode stages and then stops at the word-learning gate:

    python -u -m kavi.school_cli --max-stages 2 --lessons-per-stage 24 --symbol-batch-size 11 --interval-ms 80 --state-file runs\kavi-school-state.json

The checkpoint stores only completed stage identifiers. It does not store raw
glyph lessons, source text, or model weights.
