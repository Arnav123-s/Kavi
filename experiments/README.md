# Experiment records

The repository contains narrow, reproducible smoke-test records for the
implemented arithmetic prototypes. They verify code behavior under their exact
configuration; they are not evidence of general learning or broad capability.

When an experiment is explicitly authorized, create a reviewed text record containing:

- Experiment identifier, date, and source commit.
- Hypothesis and the exact mechanism being tested.
- Data provenance, permitted use, and training/evaluation separation.
- Fixed resource budget, numerical precision, and relevant configuration.
- Promotion criteria and protected earlier-skill tests, defined before execution.
- Reproduction steps, random seeds where applicable, and dependencies.
- Measured results, elapsed time, memory use, and available safety measurements.
- Failures, regressions, limitations, and the decision to retain or reject a change.

Publish compact, non-sensitive results, not raw private inputs, credentials, copyrighted source texts, or large binary artifacts. Report hypothetical examples as hypothetical; do not invent successful measurements.

Current records:

- [Stage-0 hard-pathway smoke test](2026-09-03-stage-0-smoke-test.md)
- [Explanation-learning smoke test](2026-09-03-explanation-learning-smoke-test.md)
