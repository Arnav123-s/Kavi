# Kritjnah Component Catalog

Author: Arnav123-s

Status: naming and architecture specification; not yet implemented or trained

## 1. What kind of model is Kritjnah?

The complete system is named **Kritjnah**.

Its precise type is:

> **A bounded developmental research agent built around a sparse modular recurrent sequence model.**

That sentence has five parts:

- **Bounded** means a guardian controls resources, permissions, recovery, and stopping.
- **Developmental** means capacity may grow, specialize, consolidate, and compress through measured stages.
- **Research agent** means it can retrieve information, use tools, test ideas, remember results, and later propose bounded improvements.
- **Sparse modular** means only the core and a small number of relevant specialists run for a task.
- **Recurrent sequence model** means it processes ordered information step by step while carrying a compact internal state.

The neural model itself is called **Kritjnah Core**. Its type is:

> **A causal, serial-first, sparse modular recurrent state-space model with limited local attention, adaptive internal steps, and external retrieval.**

The outer system is not part of the neural weights. It contains the evaluator, memory database, research loop, proof checker, resource controller, checkpoints, and audit history.

## 2. The complete family

| Name | Meaning | Intended size or role |
|---|---|---|
| **Kritjnah Seed** | Small plumbing and learning prototype | about 8-15 million parameters |
| **Kritjnah Core** | Stable reference neural model | experimentally chosen within about 30-60 million parameters |
| **Kritjnah Branch** | Temporary specialist added around a cluster of errors | small low-rank module |
| **Kritjnah Candidate** | One experimental child system | one live candidate at a time |
| **Kritjnah Consolidate** | Candidate produced after growth and compression | must pass every retention gate |
| **Kritjnah Archive** | Disk-backed family of verified and rejected lineages | stores artifacts, measurements, and reasons |
| **Kritjnah** | Entire agent, including the core and surrounding systems | one bounded local research system |

These are roles, not claims of quality. A model becomes the reference only after measurement.

## 3. Architecture tree

```text
KritjnahSystem
|
+-- BoundaryPlane
|   +-- K-Guard        BoundarySupervisor
|   +-- K-Ruler        FixedEvaluator
|   +-- K-Ledger       EventLedger
|   +-- K-Stop         StopController
|   +-- K-Proof        TrustedProofKernel
|
+-- AgentPlane
|   +-- K-Executive    TaskExecutive
|   +-- K-Core         RecurrentCore
|   +-- K-Field        SparseRelevanceRouter
|   +-- K-Clock        DeliberationController
|   +-- K-Tools        ToolBroker
|
+-- MemoryPlane
|   +-- K-State        WorkingState
|   +-- K-Cache        RecentExperienceCache
|   +-- K-Library      ProvenanceMemoryIndex
|   +-- K-Sources      SourceDependencyGraph
|   +-- K-Debate       HypothesisBank
|   +-- K-Consolidate  SemanticConsolidator
|
+-- LearningPlane
|   +-- K-Global       GlobalCreditLearner
|   +-- K-Local        LocalPredictionLearner
|   +-- K-Trace        EligibilityTraceBank
|   +-- K-Balance      HomeostaticGainController
|   +-- K-Inertia      StructuralInertiaStore
|   +-- K-Release      ContradictionReleaseGate
|
+-- DevelopmentPlane
|   +-- K-Residual     ResidualClusterer
|   +-- K-Gate         GrowthGate
|   +-- K-Builder      BranchBuilder
|   +-- K-Practice     SpecializationTrainer
|   +-- K-Fold         CompressionEngine
|   +-- K-Retention    RetentionGate
|   +-- K-Lineage      LineageRegistry
|
+-- ResearchPlane
    +-- K-Scientist    ProposalGenerator
    +-- K-Fence        EditableSurfaceGuard
    +-- K-Sandbox      CandidateSandbox
    +-- K-Trial        FixedBudgetTrialRunner
    +-- K-Measure      EffectEstimator
    +-- K-Map          ParetoArchive
    +-- K-Parent       ParentSelector
    +-- K-Queue        ExperimentQueue
```

## 4. Boundary components

Boundary components are ordinary trusted software, not learned neural modules. Candidate code cannot edit them.

| Project name | Code name | Component type | Child explanation |
|---|---|---|---|
| **K-Guard** | `BoundarySupervisor` | immutable control service | The guardian that enforces every important rule. |
| **K-Ruler** | `FixedEvaluator` | immutable evaluation harness | The teacher and answer key that measure whether a change helped. |
| **K-Ledger** | `EventLedger` | append-only audit log | The diary that records what happened and in what order. |
| **K-Stop** | `StopController` | process-control boundary | The stop button that saves work and ends every child process. |
| **K-Proof** | `TrustedProofKernel` | independent formal verifier | The strict checker that accepts a proof object only when every formal step is valid. |
| **K-Policy** | `ImmutablePolicySet` | signed configuration | The written rules describing permissions, sources, limits, and editable files. |
| **K-Manifest** | `RunManifestStore` | reproducibility record | The label listing the exact recipe used for one run. |

### K-Guard contains these smaller parts

| Project name | Code name | Type | Job |
|---|---|---|---|
| **K-Sensors** | `TelemetryCollector` | monitoring service | Reads temperature, memory, utilization, latency, errors, and progress. |
| **K-Budget** | `BudgetController` | constrained controller | Chooses batch, context, inner steps, workers, and trial length. |
| **K-Thermal** | `ThermalMarginController` | safety controller | Maintains a conservative margin below an emergency boundary. |
| **K-Save** | `CheckpointStore` | atomic artifact store | Writes checksummed parent and child checkpoints. |
| **K-Recover** | `RecoveryManager` | state machine | Restores the last verified parent after interruption or corruption. |
| **K-Reaper** | `ProcessReaper` | operating-system helper | Ensures stopped or failed trials leave no child processes behind. |
| **K-Watch** | `FailureCircuitBreaker` | failure controller | Backs off after repeated failures instead of entering a crash loop. |

## 5. Neural core components

These components form the trainable sequence model.

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-Bytes** | `ByteSafeEncoder` | deterministic input encoder | Represents every UTF-8 byte even when no learned token exists. |
| **K-Tokens** | `LearnedTokenLayer` | optional learned tokenizer | Combines common byte sequences to reduce work without losing byte coverage. |
| **K-Embed** | `SharedEmbeddingTable` | trainable neural layer | Changes token identifiers into vectors and shares parameters with the output vocabulary. |
| **K-Core** | `RecurrentCore` | trainable causal sequence model | The main student that carries a compact state from one step to the next. |
| **K-Stream** | `RecurrentStateMixer` | state-space token mixer | Moves useful information through time without storing a huge live context cache. |
| **K-Window** | `LocalAttentionBridge` | bounded attention layer | Lets nearby tokens compare directly inside a small fixed window. |
| **K-Features** | `GatedFeatureMixer` | gated feed-forward layer | Creates and combines features inside each residual block. |
| **K-Norm** | `StateNormalizer` | normalization layer | Keeps numerical scale stable. |
| **K-Field** | `SparseRelevanceRouter` | graph-guided top-1 router | Chooses which specialist should wake up. |
| **K-Branch** | `LowRankSkillBranch` | trainable specialist | Learns one recurring residual pattern using few additional parameters. |
| **K-Predict** | `SequencePredictionHead` | neural output head | Predicts the next token or structured sequence item. |
| **K-Action** | `ActionProposalHead` | constrained output head | Proposes a tool action for the executive; it does not execute it directly. |
| **K-Value** | `MarginalGainEstimator` | learned or calibrated estimator | Predicts whether another internal step is worth its cost. |

### What makes K-Core different from an ordinary model?

K-Core combines four properties:

1. **Recurrent state:** it carries a compact memory forward.
2. **Small attention windows:** it can inspect nearby details without a massive memory cache.
3. **Sparse specialists:** normally one specialist runs instead of all specialists.
4. **Adaptive recurrent depth:** hard inputs may receive a few extra bounded correction steps.

Its first baseline deliberately omits properties 3 and 4. They are added only after the simple core is measured.

## 6. Agent and reasoning components

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-Executive** | `TaskExecutive` | deterministic agent state machine | Breaks a task into observe, retrieve, think, act, check, and record states. |
| **K-Clock** | `DeliberationController` | adaptive-compute scheduler | Grants another internal step only when expected gain exceeds cost. |
| **K-Refine** | `PredictiveStateRefiner` | iterative neural inference | Revises hidden states to reduce prediction residuals. |
| **K-Uncertainty** | `UncertaintyMonitor` | calibration component | Measures entropy, surprise, disagreement, and historical calibration. |
| **K-Intent** | `GoalState` | explicit structured record | Stores the current task, success conditions, constraints, and remaining budget. |
| **K-Plan** | `PlanGraph` | mutable task graph | Stores steps, dependencies, results, and unresolved branches. |
| **K-Tools** | `ToolBroker` | permission-checked interface | Offers approved tools without giving the neural model direct system authority. |
| **K-Verify** | `ResultVerifier` | tool-output checker | Confirms that an action actually produced its claimed result. |
| **K-Answer** | `ResponseComposer` | constrained output assembler | Builds the final answer from model output, evidence, checks, and uncertainty. |

K-Executive is not a second intelligent model. It is a clear state machine surrounding K-Core so failures and retries can be inspected.

## 7. Memory and evidence components

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-State** | `WorkingState` | accelerator-resident recurrent memory | Holds the smallest currently active state. |
| **K-Cache** | `RecentExperienceCache` | bounded system-memory store | Holds recent events that may soon be reused. |
| **K-Library** | `ProvenanceMemoryIndex` | disk-backed retrieval database | Stores long-term episodes, vectors, text, outcomes, and exact source links. |
| **K-Sources** | `SourceDependencyGraph` | provenance graph | Marks shared authors, datasets, citations, copies, and derived notes. |
| **K-Debate** | `HypothesisBank` | bounded Bayesian mixture | Keeps several explanations alive until evidence separates them. |
| **K-Evidence** | `EvidenceUpdater` | dependence-aware Bayesian updater | Changes hypothesis weights without counting duplicates as independent support. |
| **K-Surprise** | `SurpriseMonitor` | prediction diagnostic | Finds observations that every active hypothesis explains poorly. |
| **K-Check** | `ClaimProofreader` | two-stage validation pipeline | Runs a cheap check and then a genuinely different stronger check. |
| **K-Consolidate** | `SemanticConsolidator` | slow-memory learner | Converts repeated verified episodes into reusable structure. |
| **K-Failures** | `NegativeResultIndex` | failed-attempt memory | Preserves disproved ideas and failure causes so they are not silently repeated. |
| **K-Retrieve** | `DiverseRetriever` | budgeted retrieval algorithm | Chooses relevant, reliable, diverse evidence that fits the context budget. |

## 8. Learning components

The complete update system is called **K-Learn** (`HybridLearningEngine`). It combines several candidate learners. Each can be turned off for controlled experiments.

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-Global** | `GlobalCreditLearner` | end-to-end gradient learner | Assigns final task error to earlier parameters. |
| **K-Local** | `LocalPredictionLearner` | auxiliary local learner | Trains each layer to reduce a nearby predictive residual. |
| **K-Trace** | `EligibilityTraceBank` | delayed-credit memory | Temporarily marks recent parameter activity for a later outcome signal. |
| **K-Outcome** | `OutcomeModulator` | third-factor signal | Scales trace updates using measured improvement or failure. |
| **K-Balance** | `HomeostaticGainController` | negative-feedback controller | Prevents useful activity from saturating or disappearing. |
| **K-Inertia** | `StructuralInertiaStore` | continual-learning regularizer | Makes important, independently supported parameters harder to overwrite. |
| **K-Release** | `ContradictionReleaseGate` | correction mechanism | Temporarily reduces inertia when strong contrary evidence appears. |
| **K-Stability** | `NumericalStabilityGuard` | optimizer safety layer | Clips invalid updates and catches non-finite values. |
| **K-Optimizer** | `ParameterOptimizer` | numerical optimizer | Applies the accepted combined parameter update. |

Backpropagation is a component of K-Learn, not the identity of Kritjnah. It remains the reference credit-assignment method until experiments justify reducing it.

## 9. Development components

The developmental system is named **K-Grow** (`DevelopmentController`). It changes structure much more slowly than ordinary learning changes weights.

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-Residual** | `ResidualClusterer` | error-analysis algorithm | Finds stable groups of related mistakes. |
| **K-Gate** | `GrowthGate` | structural decision rule | Allows growth only when predicted gain per byte and resource margins pass. |
| **K-Builder** | `BranchBuilder` | function-preserving constructor | Adds a zero-output or duplicated branch without changing initial behavior. |
| **K-Practice** | `SpecializationTrainer` | focused learner | Trains the new branch on its residual cluster and boundary cases. |
| **K-Merge** | `ModuleMerger` | consolidation algorithm | Combines specialists that learned sufficiently overlapping functions. |
| **K-Fold** | `CompressionEngine` | candidate transformation pipeline | Tries distillation, low-rank factorization, structured sparsity, or quantization. |
| **K-Retention** | `RetentionGate` | protected evaluation gate | Rejects compression if an important old or new ability falls too far. |
| **K-Lineage** | `LineageRegistry` | ancestry database | Links every branch and compressed child to its exact parents and tests. |
| **K-Ceiling** | `CapacityCeiling` | immutable resource constraint | Limits temporary and final memory use on the target device. |

K-Fold does not delete the verified parent. It creates a child, tests it, and promotes it only after K-Retention passes.

## 10. Research and evolution components

The outer research system is named **K-Lab** (`ResearchDirector`). It is a bounded experimental optimizer, not a second uncontrolled agent.

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-Scientist** | `ProposalGenerator` | hypothesis-generation component | Proposes one change and a prediction that could be wrong. |
| **K-Fence** | `EditableSurfaceGuard` | immutable file boundary | Rejects changes outside the explicitly allowed files or parameters. |
| **K-Sandbox** | `CandidateSandbox` | isolated execution environment | Runs the child without granting it authority over the host or boundaries. |
| **K-Smoke** | `SmokeTestRunner` | cheap failure filter | Catches crashes and obvious invalid behavior before a full trial. |
| **K-Trial** | `FixedBudgetTrialRunner` | experiment executor | Gives every comparable candidate a declared time and resource budget. |
| **K-Measure** | `EffectEstimator` | statistical evaluator | Estimates improvement, uncertainty, and regression rather than trusting one run. |
| **K-Map** | `ParetoArchive` | disk-backed quality-diversity archive | Stores best verified candidates for different tradeoff regions. |
| **K-Parent** | `ParentSelector` | exploration/exploitation selector | Chooses a useful but not overused parent. |
| **K-Queue** | `ExperimentQueue` | durable scheduler | Stores the next bounded job and resumes after ordinary interruption. |
| **K-Rollback** | `CandidateRollback` | recovery operation | Removes a failed live child and restores the verified parent. |

K-Lab may eventually change a small part of K-Learn or K-Core. It never changes K-Guard, K-Ruler, K-Proof, K-Ledger, K-Stop, or K-Policy.

## 11. Curriculum and data components

The education system is called **K-School** (`CurriculumManager`).

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-Curator** | `SourceCurator` | deterministic ingestion pipeline | Accepts only correctly identified and permitted material. |
| **K-Catalog** | `SourceCatalog` | metadata database | Records authorship, origin, license, level, field, and dependencies. |
| **K-Graph** | `PrerequisiteGraph` | curriculum dependency graph | States which ideas should normally come before others. |
| **K-Spiral** | `SpiralCurriculumSampler` | stage-aware sampler | Revisits old ideas at greater depth instead of abandoning them. |
| **K-Replay** | `RetentionReplaySampler` | anti-forgetting sampler | Rehearses rare, old, failed, and boundary examples. |
| **K-Counter** | `CounterexampleGenerator` | adversarial teaching component | Searches for cases that break an attractive rule or proof. |
| **K-Holdout** | `SealedEvaluationSet` | never-trained test collection | Detects whether research has overfit visible tests. |
| **K-DataManifest** | `DatasetManifest` | reproducibility artifact | Freezes the exact training examples and transformations for a run. |

## 12. Formal mathematics components

The formal research pipeline is named **K-Theorem** (`FormalResearchPipeline`).

| Project name | Code name | Component type | Job |
|---|---|---|---|
| **K-Statement** | `StatementNormalizer` | formalization tool | Converts a claim into exact definitions, variables, and assumptions. |
| **K-Lemmas** | `LemmaRetriever` | proof-aware retrieval | Finds relevant checked lemmas without treating unverified prose as proof. |
| **K-Counterexample** | `CounterexampleSearch` | falsification engine | Tries to find a case that makes the claim false. |
| **K-ProofBuilder** | `ProofObjectBuilder` | formal construction interface | Builds a machine-readable proof candidate. |
| **K-Proof** | `TrustedProofKernel` | independent immutable checker | Accepts or rejects the formal proof object. |
| **K-Dependencies** | `ProofDependencyLedger` | formal provenance graph | Stores exactly which definitions and lemmas a result uses. |
| **K-Conjectures** | `ConjectureRegistry` | research database | Separates open, disproved, partially proved, and fully checked statements. |

K-Proof appears in both the boundary and mathematics lists because the pipeline uses it, but does not own or modify it.

## 13. What is neural and what is ordinary code?

| Category | Components |
|---|---|
| **Trainable neural components** | K-Embed, K-Core, K-Stream, K-Window, K-Features, K-Field candidate, K-Branch, K-Predict, K-Action, K-Value |
| **Trainable learning state** | K-Trace, K-Balance, K-Inertia, optimizer moments, hypothesis probabilities |
| **Deterministic algorithms** | K-Executive, K-Retrieve, K-Residual, K-Gate, K-Builder, K-Fold, K-Parent, K-Spiral |
| **Databases and artifacts** | K-Library, K-Sources, K-Failures, K-Map, K-Lineage, K-Ledger, manifests, checkpoints |
| **Immutable trusted boundaries** | K-Guard, K-Ruler, K-Proof, K-Stop, K-Policy, K-Fence |
| **External tools** | approved source retriever, calculator, code sandbox, theorem prover, profiler, and hardware sensors |

This separation is important. Making every part neural would make the system difficult to inspect and would allow learned errors to corrupt the measuring instruments.

## 14. One complete trip through the system

For one task:

1. **K-Executive** reads the goal and constraints from **K-Intent**.
2. **K-Guard** grants a bounded resource allowance.
3. **K-Retrieve** asks **K-Library** for a small diverse evidence set.
4. **K-Sources** discounts evidence that came from the same original source.
5. **K-Debate** keeps several possible explanations.
6. **K-Bytes**, **K-Embed**, and **K-Core** process the sequence.
7. **K-Field** wakes at most one **K-Branch**.
8. **K-Clock** decides whether another **K-Refine** step is worth its cost.
9. **K-Action** may propose a tool request through **K-Tools**.
10. **K-Verify** checks the tool result.
11. **K-Check** or **K-Proof** verifies an important claim.
12. **K-Learn** calculates a candidate parameter update.
13. **K-Balance**, **K-Inertia**, and **K-Release** control stability and correction.
14. **K-Ledger** records the complete event.
15. **K-Consolidate** may later move verified repeated experience into slow memory.
16. **K-Residual** records persistent error clusters for possible future growth.
17. On a slower schedule, **K-Lab** may test one controlled system improvement.

## 15. The shortest correct description

Kritjnah is not just a language model and not just an evolutionary algorithm.

It is:

> **A resource-bounded, retrieval-augmented, continual-learning research agent whose neural center is a sparse modular recurrent state-space sequence model, whose structure can undergo retention-tested development, and whose later improvements are selected by an external fixed evaluator and quality-diversity archive.**

In child-sized words:

> **Kritjnah is a small student with a library, a few helpers, a strict teacher, a careful scientist, and a guardian that the student cannot rewrite.**
