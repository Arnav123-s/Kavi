# Primary research

Author: [Arnav123-s](https://github.com/Arnav123-s)

The [certificate and software study](CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md) adds AbstractBeam and Minton's utility problem, audits the addition claim, and examines stabilizer/tensor simulation, dequantization, memory-aware computation and reaction-network dynamics. Its [physical-pathway proposal](PHYSICAL_PATHWAY_RESEARCH.md) separates engineered mechanisms from learned update procedures. External-review recommendations are recorded but deferred.

The implemented [structural learner](CIRCUIT_RUNTIME.md) searches two-state transducers represented by Boolean circuits. Its [procedure extension](PROCEDURE_LIBRARY_RUNTIME.md) performs bounded typed program induction over acquired operations. [Measured results](../experiments/2026-09-05-procedure-library.md) include useful call reuse and increasing search cost. Self-modifying graph systems remain relatives of the broader proposal; autonomous control semantics and general abstraction invention are not established by these trials.

The intended adaptive circuit has close relatives in self-modifying computational graphs, structural learning and program induction. The current text implementation belongs to complex recurrent neural models. The [adaptive dataflow circuit note](ADAPTIVE_DATAFLOW_CIRCUIT.md) gives the revised architectural comparison and additional primary sources.


### 5.1 Overall classification

The mathematical description of the clarified proposal is a dynamical system on computational graphs with feedback-dependent graph rewriting. Temporary execution changes and lasting structural learning must be distinguished. Self-modifying Cartesian genetic programming is a close operational precedent; the adaptive circuit note examines its evidence and limitations.

Incremental program induction over typed term graphs provides one concrete acquisition mechanism within this design. A term graph represents computation with shared subexpressions. Its operational semantics define what an instruction does, how state moves, and what counts as completion. Learned libraries allow a useful subgraph to become a reusable operation in subsequent searches.

[DreamCoder](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf) is a close architecture for this acquisition mechanism: it searches for programs, develops reusable abstractions, and learns to guide later search. Its initial language and representations are engineered, and its demonstrated domains and computational budgets differ from Kavi's. The relationship is a research lineage, not an implementation equivalence; it does not cover every aspect of a continuously reshaping circuit.

### 5.2 Structural compression

The closest specific relative of Kavi's proposed compression is library learning modulo an equational theory. [babble](https://arxiv.org/html/2212.04596v1) combines e-graphs and anti-unification to find reusable structure across programs whose syntax differs but whose expressions are equivalent under known equations. It starts with programs; it does not independently establish their correctness.

[Stitch](https://arxiv.org/html/2211.16605v2) provides a related top-down search for abstractions that compress a program corpus. Its compression objective is relevant to a bounded learner, but shorter program descriptions do not automatically execute faster or improve unseen tasks. Those require separate measurements.

The [E-Stitch workshop contribution](https://pldi26.sigplan.org/details/egraphs-2026-papers/7/E-Stitch-Top-Down-Library-Learning-for-E-Graphs), presented on 15 June 2026, directly combines top-down library learning with e-graphs. The official abstract describes preliminary results. It is a relevant recent direction; no design decision here depends on an unverified performance advantage from it.

### 5.3 Repair and verification

[Syntax-guided synthesis](https://www.cis.upenn.edu/~alur/SyGuS13.pdf) makes the learning problem concrete through a grammar, a background theory and a correctness specification. Counterexample-guided inductive synthesis alternates between proposing a program and obtaining a case that refutes it. This fits Kavi's correction-driven development when the verifier can supply meaningful counterexamples.

An example-based verifier checks observed behavior. A solver may establish a universal property only within its supported logic and assumptions. Timeout, unsupported arithmetic or an incomplete search must remain distinct from a proof that no solution exists.

[Stochastic superoptimization](https://theory.stanford.edu/~aiken/publications/papers/asplos13.pdf) is a useful relative for searching small program mutations under behavioral and execution costs. Its original work concerns loop-free machine code and uses separate validation. Kavi would need its own instruction semantics and mutation operators. The published errata must be used when reproducing its cost equations.

### 5.4 Compression objective

Minimum description length gives a precise form to the preference for small reusable structure. The objective accounts for the model description and whatever data it fails to explain. The encoding must be specified: counting nodes while ignoring large constants, hidden lookup tables or a learned proposal network is insufficient. [Grunwald's MDL introduction](https://arxiv.org/pdf/math/0406077).

### 5.5 Quantum diagrams and physical dynamics

[PyZX](https://arxiv.org/pdf/1904.04735) demonstrates automated rewriting of diagrams with quantum linear-map semantics. The transferable principle is that a structural rewrite should preserve a defined meaning. Kavi needs classical operational semantics for its programs. A quantum identity, particularly one valid only up to a global scalar, is not automatically valid for an exact classical numeric output.

The physical proposal has a different nearest relative: [port-Hamiltonian systems on graphs](https://arxiv.org/abs/1107.2006), which combine energy storage, transport, dissipation and external inputs. That framework offers useful stability structure. It does not establish that simulated gravity, chemical fields or phase interference improve learning.

| Kavi component | Closest mathematical family | Main distinction |
| --- | --- | --- |
| Adaptive circuit | Feedback-dependent rewriting of computational graphs | The update rule and transfer to new tasks must be established |
| Intended learned procedures | Typed program induction and library learning | Procedures must be acquired, rather than supplied |
| Structural consolidation | MDL and library learning modulo equations | Compression requires a defined encoding and valid identities |
| Behavioral repair | Counterexample-guided synthesis and program repair | Repair changes meaning and needs fresh correctness evidence |
| Equivalent-path optimization | Equality saturation | Optimizes represented alternatives, not all possible programs |
| Current text core | Complex nonlinear sparse recurrent network | Learns continuous coefficients and input/output maps |
| Fixed-size deployed circuit | Finite-state transducer under finite precision | Unbounded input families still require time and possibly workspace |
| Proposed physical core | Controlled dissipative graph dynamics | Stability and learning must be derived together |

## Bibliography

Sources were inspected on 5 September 2026. The scope column distinguishes full-paper access from abstracts and official summaries. Direct mathematical derivations in this specification concern the stated Kavi equations and assumptions; they are not attributed as experimental findings of the cited papers.

| Reference | Relevance and inspected scope |
| --- | --- |
| [Ellis et al 2021 DreamCoder](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf) | Program synthesis with learned libraries and search; full paper |
| [Lake et al 2015 Human-level concept learning through probabilistic program induction](https://www.cs.cmu.edu/~rsalakhu/papers/LakeEtAl2015Science.pdf) | Structured priors for concept acquisition; full paper |
| [Grunwald 2004 A Tutorial Introduction to the Minimum Description Length Principle](https://arxiv.org/pdf/math/0406077) | Description-length model selection; full tutorial |
| [Alur et al 2013 Syntax-Guided Synthesis](https://www.cis.upenn.edu/~alur/SyGuS13.pdf) | Grammar, specification and counterexample-guided search; full paper |
| [Willsey et al 2021 egg](https://arxiv.org/html/2004.03082v3) | Equality saturation and e-graph engineering; full paper |
| [Bowers et al 2023 Top-Down Synthesis for Library Learning](https://arxiv.org/html/2211.16605v2) | Stitch abstraction search; full paper |
| [Cao et al 2023 babble](https://arxiv.org/html/2212.04596v1) | Equational library learning and anti-unification; full paper |
| [Gupta et al 2026 E-Stitch](https://pldi26.sigplan.org/details/egraphs-2026-papers/7/E-Stitch-Top-Down-Library-Learning-for-E-Graphs) | Recent combination of top-down search and e-graphs; official workshop abstract only |
| [Schkufza et al 2013 Stochastic Superoptimization](https://theory.stanford.edu/~aiken/publications/papers/asplos13.pdf) | Search over executable mutations; full paper and [errata](https://theory.stanford.edu/~aiken/publications/papers/asplos_13_errata.txt) |
| [Kissinger and van de Wetering 2020 PyZX](https://arxiv.org/pdf/1904.04735) | Semantics-based diagram rewriting; full paper, QPL 2019 work |
| [van der Schaft and Maschke Port-Hamiltonian Systems on Graphs](https://arxiv.org/abs/1107.2006) | Energy balance in graph dynamics; preprint and published-work record |
| [Scellier and Bengio 2017 Equilibrium Propagation](https://arxiv.org/html/1602.05179v5) | Equilibrium gradient relation and assumptions; full paper |
| [Jaeger 2001 The Echo State Approach](https://publica.fraunhofer.de/entities/publication/7d4a7eec-a22c-4df0-903d-93f9cd5aca02) | Fixed recurrent reservoir and trained readout; institutional report record |
| [Trabelsi et al 2018 Deep Complex Networks](https://arxiv.org/html/1705.09792v3) | Complex neural components; full paper, 2017 preprint |
| [Orvieto et al 2023 Resurrecting Recurrent Neural Networks for Long Sequences](https://proceedings.mlr.press/v202/orvieto23a.html) | Linear recurrent unit baseline; proceedings and paper |
| [Chaudhry et al 2019 Efficient Lifelong Learning with A-GEM](https://arxiv.org/html/1812.00420v2) | Average episodic gradient constraint; full paper |
| [Chaudhry et al 2019 On Tiny Episodic Memories in Continual Learning](https://arxiv.org/abs/1902.10486) | Replay control; primary abstract and study record |
| [Mostafa and Wang 2019 Parameter Efficient Training of Deep Convolutional Neural Networks by Dynamic Sparse Reparameterization](https://proceedings.mlr.press/v97/mostafa19a.html) | Fixed-budget structural changes; proceedings and paper |
| [Chen et al 2016 Net2Net](https://arxiv.org/abs/1511.05641) | Function-preserving initialization; primary abstract and paper record |
| [Bellec et al 2019 A Solution to the Learning Dilemma for Recurrent Networks of Spiking Neurons](https://arxiv.org/html/1901.09049v2) | Eligibility traces and learning signals; full preprint |
| [Werner 1989 Quantum States with Einstein-Podolsky-Rosen Correlations](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.40.4277) | Separability distinction; abstract only |
| [Lindblad 1976 On the Generators of Quantum Dynamical Semigroups](https://link.springer.com/article/10.1007/BF01608499) | Physical channel constraints; abstract only |
| [Tishby et al The Information Bottleneck Method](https://arxiv.org/abs/physics/0004057) | Task-relevant compression; primary abstract, 1999 work uploaded in 2000 |
| [Vaswani et al 2017 Attention Is All You Need](https://arxiv.org/abs/1706.03762) | Attention baseline; primary paper record |
| [Guo et al 2017 On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html) | Confidence calibration; proceedings and paper record |
| [Liu and Zhu 2016 The Teaching Dimension of Linear Learners](https://jmlr.org/papers/v17/15-630.html) | Learner-dependent teaching requirements; journal record |
| [Agarwal et al 2021 Deep Reinforcement Learning at the Edge of the Statistical Precipice](https://proceedings.neurips.cc/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html) | Few-run evaluation reliability; proceedings record |
| [ARC-AGI-2 2025](https://arxiv.org/abs/2505.11831) | Independent abstraction-task design; primary paper record, revised 2026 |
| [ARC Prize 2025 Technical Report](https://arxiv.org/abs/2601.10904) | Competition evaluation and refinement evidence; January 2026 report record |
| [Jolicoeur-Martineau 2025 Less Is More](https://arxiv.org/abs/2510.04871) | Tiny recursive model research; primary paper record |
