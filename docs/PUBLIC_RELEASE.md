# Kavi public-release policy

Author: Arnav123-s
Status: release policy

## Ownership and public scope

Kavi is authored by Arnav123-s. The public repository is intended to preserve
the project’s reviewed design, source code, tests, compact experiment records,
and reference links. It does not reconstruct private conversations, prior local
activity, or materials that were never intentionally included in the project.

The repository’s commit identity is limited to the project author’s GitHub
no-reply address. It contains no co-author trailers or tool attribution.

## What must never be committed

- Passwords, tokens, cookies, API keys, private certificates, or credential
  helper files.
- Personal records, private conversations, contact information, or browser data.
- Raw copyrighted textbooks, articles, PDF copies, datasets, model weights,
  checkpoints, caches, or generated runtime logs.
- Unreviewed source extracts or any data whose rights and provenance are not
  documented.
- Machine-specific configuration that exposes unnecessary system information.

The public curriculum gate stores source metadata, links, review notes, and
extract fingerprints only. It does not republish source bodies. See
[DOCUMENT_CURRICULUM_GATE.md](DOCUMENT_CURRICULUM_GATE.md).

## Naming and technical wording

The repository, Python package, command-line program, and design documents use
the name Kavi. Public materials should not use previous project names or
unnecessary vendor, assistant, or automation branding. Generic technical terms
remain where they are needed to state the design and source-use constraints
truthfully.

## Release verification

Before a public push, complete these checks from the repository root:

    git status --short
    git diff --check
    python -m unittest discover -s tests -v
    python -m kavi.source_cli

Then review the staged names and patch before committing:

    git diff --cached --name-status
    git diff --cached --check

Use explicit staging paths. Do not sweep in unrelated files merely because they
are nearby in a workspace. A user-requested full-project release still requires
a review of every staged item.

## Publication workflow

1. Create a public repository named Kavi under the author’s account.
2. Confirm the default branch and the remote URL before pushing.
3. Push the reviewed local main branch without rewriting published history.
4. Verify the public tree, documentation links, author attribution, and test
   instructions from the remote repository.
5. Do not publish a release tag until the author selects a software license.

No local policy can erase independent hosting, network, or account audit
records. The goal here is an accurate, clean project history and a deliberate
public source tree.

## After publication

Future changes should be small, reviewable commits with tests or an experiment
record when appropriate. A result may be published only with its limitations,
configuration, and failure cases. New learning mechanisms, curriculum sources,
or resource policies need documentation and evaluation before they are claimed
as improvements.
