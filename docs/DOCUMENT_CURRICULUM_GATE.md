# Kritjnah document curriculum gate

Author: Arnav123-s

## Decision

Kritjnah should learn from real educational and research sources only through a
reviewed curriculum pipeline. A book, paper, web page, or PDF is not admitted
merely because it is readable online.

The public repository stores source metadata, citation links, curriculum order,
lesson claims, verifier identity, and fingerprints of approved local extracts.
It does not store full textbooks, papers, copied passages, private caches, or
large datasets.

## Why raw documents are not enough

Reading a whole paper does not itself create a checked understanding. A useful
lesson needs all of the following:

1. a source with recorded provenance and rights;
2. one declared concept and its prerequisites;
3. a concise explanation or derivation;
4. a source location and extract fingerprint;
5. an independent way to check the learned claim;
6. a held-out transfer or retention test.

The source supplies evidence. It does not change the evaluator, source code,
hardware budget, or stop control.

## Admission rule

The machine reads curriculum content only when all conditions are met:

1. the original source URL and creator are recorded;
2. the exact work has an admissible reuse status, not just an open web page;
3. its metadata and license are reviewed again at ingestion time;
4. the extract is stored outside the public repository and fingerprinted;
5. a lesson has a concept, prerequisites, explanation, and verifier;
6. the source is marked approved in curriculum/source-manifest.json.

Sources with unclear terms stay quarantined. They are not downloaded, trained
on, or used as an implied instruction set.

## Initial source review

| Source class | Current status | Reason |
|---|---|---|
| NASA NTRS record 19830024400 | metadata admitted | The record identifies the work as a US Government work with public use permitted. Each selected extract still needs a fresh per-document review. |
| OpenStax Physics | quarantined | Its license and current title-specific AI-use terms must be checked before any ingestion. |
| arXiv papers | quarantined by default | Licenses are selected per paper; an arXiv host page is not a blanket reuse authorization. |

NASA NTRS exposes public scientific and technical records, including documents
whose record identifies US Government work and public use permission. See the
official record at https://ntrs.nasa.gov/citations/19830024400.

OpenStax has open educational resources, but title-level pages and current terms
must be reviewed rather than assumed to permit model training. Its official
licensing information is at
https://help.openstax.org/s/article/Licensing-information-of-OpenStax-textbooks.

arXiv licensing is item-specific and needs an exact-paper review before use.
See https://info.arxiv.org/help/license.html.

## Curriculum order

The sequence file deliberately starts with symbols, quantities, equality, and
arithmetic. It then adds language and logic, science foundations, and finally
primary research. A higher stage is not allowed to substitute for its
prerequisites.

The first live explanation experiment remains a generated arithmetic verifier
because it has exact answers. It is a harness test, not a substitute for the
document curriculum. The document pipeline should be added only after the
source gate and lesson verifier are both satisfied.
