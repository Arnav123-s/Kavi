# Unified pathway-circuit live run

Experiment ID: PC-2026-09-04-01

Date: 2026-09-04

Source commit: `7f24506`

Author: Arnav123-s

Status: completed bounded experiment

## Question

Can one persistent, path-centric circuit learn several prerequisite-ordered
tasks while reusing earlier paths, limiting each activation wave to four paths,
and promoting a candidate only when protected and held-out checks do not
regress?

The notation task is one test of contextual path reuse. It is not a claim that
the architecture is only for algebra, nor evidence that it already supports
arbitrary domains.

## Mechanism tested

- Learned routes and transforms are the persistent active model.
- Detectors, resistors, switches, capacitors, junctions, loops, jumps, and
  transformers are local circuit roles that control flow; they are not treated
  as independent thinking agents.
- Several compatible paths can activate in bounded waves. Classical complex
  amplitudes and squared magnitude provide a deterministic, quantum-inspired
  interference score; no quantum hardware or physical quantum effect is used.
- Hard task identifiers prevent one symbol from silently changing meaning in a
  different task. Jump adapters connect compatible earlier paths to a later
  route.
- Every update is made in an isolated candidate. The parent remains frozen
  during evaluation. A passing candidate becomes the only active state, and
  the parent is serialized outside inference for external recovery only.

## Provenance and evaluation separation

The glyph, arithmetic, Unicode-scalar, and multilingual-script lessons were
generated locally from fixed code and seed 31. The final notation stage used a
previously reviewed private lesson derived from the source record
`basic-algebra-with-applications-6e` in `curriculum/source-manifest.json`.
Private source text, raw prompts, manifests, logs, and archives were not
committed. Protected and held-out partitions were fixed before execution.

The run did not fetch from the network, modify its source code, schedule
background work, change hardware or thermal settings, or read archived parents
during inference.

## Configuration

```text
Command: scripts\start-live-pathways.ps1 -IntervalMs 350 -StartDelaySeconds 10 -MaxParallelPaths 4
Interpreter: Python 3.13.5
Seed: 31 (runtime default)
Live feeds: answers, pathways, learning, grading
Run directory: runs\pathway-live-20260904-111436 (ignored local artifact)
```

## Promotion rule

A candidate was retained only when its targeted update increased support and
did not reduce the declared current, protected, or held-out accuracy. Stage
promotion required the predeclared accuracy threshold. Randomized test order
changed presentation order, not partition membership or expected answers.

## Observed result

| Measurement | Observed value |
| --- | ---: |
| Implemented stages completed | 5 |
| Stage grades passing | 5 / 5 |
| Final protected accuracy at each stage | 1.00 |
| Final held-out accuracy at each stage | 1.00 |
| Candidate promotions | 23 |
| Frozen parent archives | 23 |
| Active categorical routes | 15 |
| Active arithmetic transforms | 2 |
| Active jump adapters | 42 |
| Maximum paths per activation wave | 4 |
| Final numeric-payload estimate | 2,168 bytes |
| Serialized JSON state size | 20,979 bytes |
| Approximate wall time including display delay | 38.83 s |
| Kavi Python processes after completion | 0 |

The final notation routes reused the existing digit and addition paths through
jump adapters. The compact active state did not contain sampled prompt strings.
All 23 archived parents were marked `active_during_inference: false`.

## Limits and decision

This is a white-box toy experiment over five small, fixed stages. Perfect
scores on these manifests do not establish language understanding, calculus,
scientific reasoning, infinite context, frontier intelligence, or superiority
to neural networks. The numerical payload estimate counts model scalars only;
it excludes Python, terminal, JSON, and operating-system overhead. The
serialized state size is reported separately. No GPU, temperature, energy, or
whole-process memory measurement was collected.

The run stopped at `word-forms-and-definitions` because that stage still needs
an explicit representation, reviewed lessons, an independent verifier, and
held-out tests. Decision: retain the domain-independent routing mechanism and
its bounded evidence; do not claim unimplemented capabilities.
