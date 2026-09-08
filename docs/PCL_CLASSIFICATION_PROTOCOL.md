# PCL phase-region classification protocol

Author: [Arnav123-s](https://github.com/Arnav123-s)

8 September 2026. Defined before the final classification bank is evaluated.

## Question

Does learning rules over ranges of current phase values improve classification of unseen original measurements relative to the exact-state readout? This is a first classification test. It does not test English interpretation, an acquired internal world, conscious experience, or general scientific understanding.

The current readout requires an exact joint phase match. The extension learns axis-aligned interval conjunctions over joint phases. It starts from teaching executions and greedily expands a same-class region only when no supplied opposite-class state lies inside. At inference, conflicting matching regions yield unresolved; there is no nearest-example lookup. Interval bounds and labels are learned; the interval grammar, covering algorithm and proposal distribution are supplied. The closest conventional interpretation is supervised rule covering over recurrent state.

## Source and partition

Use the unchanged `bezdekIris.data` edition in the [official UCI Iris archive](https://archive.ics.uci.edu/dataset/53/iris), cited as Fisher (1936), DOI 10.24432/C56C76, CC BY 4.0. Record archive and member hashes. The UCI page documents differences between distributed data and the historical paper; do not silently repair either edition or claim an archival reconstruction of the paper. The 150 records contain four measured flower dimensions and original species labels. Source bodies remain private. No invented measurements, questions or labels are admitted.

Group identical four-feature records before partitioning, rejecting conflicting labels. Within each species, sort groups by SHA-256 of their canonical measurement strings. Allocate the first 60 percent of groups to teaching, the next 20 percent to development, and the rest to final evaluation. Duplicate groups never cross a boundary. The first teaching stage takes the first half of teaching groups within each species; the second adds the remainder. Development is measured but does not alter proposals, select seeds or change the protocol. Final records are evaluated only after every fit is finished and each arm is frozen.

## Encoding and supplied template

Multiply the source centimetre values by ten exactly, preserving the source's decimal precision. Emit that many copies of the corresponding field event, in source field order. Four phase counters, each modulo 256, initially count those events. Their initial impulses map the four measurement fields to four current phases. The zero state is reset for every specimen. This numeric representation is supplied; it is not learned language or discovery of what a sepal means. All admitted original values must be positive integral tenths below 256.

The template has one propagation tick per event and at most two couplings. It remains unchanged across both stages. Whole-circuit reconstruction proposes twelve complete definitions per stage, with the existing dynamics first and inherited/new dynamics afterward. Use fixed seeds 7, 19 and 41 for both exact and region arms. Each second stage inherits its own first-stage generation. Protect all first-stage teaching outcomes while fitting the cumulative bank. Never use final examples as preservation obligations.

Selection minimizes teaching error and then encoded circuit bytes, subject to the protected bank. Rejected candidates leave the old generation active. A candidate can fit every teaching point while still encoding narrow regions; success on the teaching bank is insufficient. Explicitly report whether the dynamics changed or only the readout changed.

## Controls and measurements

Compare exact and region readouts with the same template, candidate count, partitions and seeds. Include a majority-class control and a learned single-threshold decision stump fitted only on the teaching measurements. The stump selects a measurement field and threshold between observed values, choosing the most common class on each side by training accuracy; report this ordinary classifier's final performance.

For each arm and stage, report correct, wrong and unresolved outputs, teaching retention, development results, acceptance, proposal counts, output-rule counts, serialized bytes, whole-generation hashes and work counts. Record structural inheritance and coupling counts. Evaluate final data once after freezing. Retain failures and interrupted fits. Report total wall and CPU time, display pacing, available memory telemetry and local source/checkpoint/log storage separately.

One visible worker uses the existing Pause/Resume/Stop controller, a five-minute wall budget and a 512 MiB working-set ceiling. Each reconstruction has a 30-million-unit named-operation budget. Whole-candidate enumeration and rule-region constraints are counted. These counters do not replace host-level timing or memory measurements. No background restart is installed.

## Boundaries

Region inference changes readout semantics, so old exact patterns remain valid and overlapping contradictory regions must be unresolved. Test these properties before the course. This new representation does not establish the earlier exact finite-state simulation certificate for arbitrary phase reconstructions; retention here is finite-bank retention.

Passing this small classical dataset would show that acquired phase rules can classify some new measurements. It would not show that pendulum interactions are necessary, that the internal-world target is achieved, or that PCL improves on established classifiers. If the supplied counter dynamics survive and only intervals change, report the result as learned readout classification.
