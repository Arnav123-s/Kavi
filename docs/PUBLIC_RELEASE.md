# Publication and attribution

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi is authored by [Arnav123-s](https://github.com/Arnav123-s). The public repository contains source code, tests, technical documentation, source metadata and compact experiment records. Cited research retains its original authorship.

Private conversations, credentials, source bodies, datasets, model checkpoints and runtime logs remain outside the public tree. Source manifests record bibliographic information, admitted scope and fingerprints without redistributing the source material.

## Release procedure

Review the working diff, relevant checks and explicitly staged file list. Confirm that reported results identify the code revision, configuration, evaluation scope and regressions. Use the repository-local author identity and preserve published history.

```powershell
git status --short
git diff --check
git diff --cached --name-status
git diff --cached --check
```

Publishing to the remote repository is a separate release action. A software license has not yet been selected. See [contribution standards](../CONTRIBUTING.md) and the [source admission policy](DOCUMENT_CURRICULUM_GATE.md).
