# Kavi Hard-Pathway Core Plan

Author: Arnav123-s
Status: research specification and falsifiable test plan; not implemented, trained, or validated
Relationship: a candidate hard-routing and structural-plasticity refinement for the sparse graph inside the [Kavi Physics-Native Core](KAVI_PHYSICS_NATIVE_CORE.md). It does not replace the separate verification and task-workspace ideas in the [Machine-Native Intelligence Blueprint](MACHINE_NATIVE_INTELLIGENCE_BLUEPRINT.md).

## 1. The idea in plain language

Imagine Kavi as a small city of **pipes**, not as one giant room where every signal mixes with every other signal.

- A question enters through only a few pipes whose shapes fit that question.
- A well-practised base pipe handles common cases quickly.
- A very small side pipe, called an adapter, handles a closely related variation.
- A truly different or conflicting kind of problem gets a new scoped route instead of damaging an old route.
- Before a changed route replaces an old route, it must pass the tests that the old route already passed.

The intended result is:

> A learned answer emerges because the compatible pathway is triggered and settles, not because the system retrieves a transcript of an old answer or runs separate experts that vote.

A base route covering only 50% of a task family can be useful. It becomes safe only if the remaining 50% is recognised as outside its scope and sent to an adapter, a fallback, or an explicit “not yet known” result. A route that answers every case but is silently wrong 10% of the time is not the intended design.

## 2. Exact proposed model type

The candidate core is:

> **A hard-routed, capacity-limited, structurally plastic recurrent graph with typed pathways, local eligibility traces, calibrated uncertainty, and verifier-gated promotion.**

Short name: **Kavi Hard-Pathway Core (K-HPC)**.

Its research question is whether this combination improves the trade-off among learning, transfer, retention, confidence, and resource use:

1. hard compatibility rather than broad soft mixing;
2. small reusable base paths plus budgeted structural adapters;
3. local, recent-activity credit traces for corrections;
4. candidate-only restructuring with a tested fallback;
5. complete accounting for persistent and transient resources.

K-HPC is not:

| It is not | Why |
|---|---|
| a mixture of experts | Experts normally compute independently and are mixed or selected by a router. K-HPC uses one connected pathway fabric; a route is a constrained part of that fabric, not a separate opinion. |
| a raw-memory database | The core learns reusable transformations and pathway shapes. It does not treat a stored transcript as its main answer mechanism. |
| a literal simulation of a brain, galaxy, or atom | Physics and biology supply candidate control principles, not a claim that software weights are planets or neurons. |
| a promise of infinite memory | A fixed finite state cannot preserve unlimited unrelated facts exactly. It can support an open-ended number of compositions when it learns reusable rules. |
| permission for self-modifying source code | Any future structural change must be an isolated model candidate, not a live edit of code, evaluators, limits, or stop controls. |

## 3. What “memory” means here

The word memory needs three separate meanings.

| Kind | Where it lives | Purpose | Allowed in this proposal? |
|---|---|---|---|
| Current activation | temporary cell and edge activity while one input is settling | the present “triggering of pathways” | yes, but it is finite and expires |
| Procedural/semantic structure | route topology, parameters, capacities, and learned invariants | a compact rule such as how a quantity operation behaves | yes; this is the intended core memory |
| Raw episodic record | an old conversation, example, web page, or training sample | exact recall and auditing | not the core answer mechanism; external evaluation data and audit material must still be counted separately |

The desired behaviour is **implicit procedural memory**: after enough varied, verified examples, the pathway for an operation becomes easier to trigger and produces a result without replaying each example.

That does not make context literally infinite. A finite state has finite information capacity, a basic constraint formalised by information theory. Compression can retain a rule when many examples share structure; it cannot losslessly retain an unlimited set of arbitrary independent details at no storage cost. [Shannon's original paper](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x) is the source of the capacity-and-compression framework behind that distinction.

The practical target is:

> **Open-ended compositional context, not impossible unlimited exact recall.**

A finite grammar can create many unseen sentences. Likewise, a small learned operation can work on many unseen inputs. That is the kind of “infinite” behaviour the plan can investigate honestly.

## 4. The pathway object

A pathway is a sparse connected subgraph, not one neuron and not one stored fact. For pathway \(p\), keep:

\[
p=(\tau_p,\;E_p,\;W_p,\;b_p,\;m_p,\;h_p,\;\pi_p,\;\varepsilon_p,\;q_p).
\]

| Symbol | Name | Meaning |
|---|---|---|
| \(\tau_p\) | type signature | what representation patterns may enter and leave the route |
| \(E_p\) | permitted edges | the pipes through which this path may propagate |
| \(W_p\) | transformations | learned maps along those edges |
| \(b_p\) | capacity | maximum active width, rank, bandwidth, and internal steps for this path |
| \(m_p\) | stability or “mass” | verified support and resistance to casual rewriting |
| \(h_p\) | heat | surprise, uncertainty, and temporary permission to explore or change |
| \(\pi_p\) | plasticity | how rapidly its parameters may adapt |
| \(\varepsilon_p\) | eligibility trace | a fading record of which recently active edges could receive credit |
| \(q_p\) | quality record | calibration, coverage, retention, cost, and version-test results |

The physical words are engineering translations:

| Metaphor | Operational meaning | Must not mean |
|---|---|---|
| mass | evidence-weighted stability; heavily tested paths change slowly | literal gravity between parameters |
| heat | surprise and a bounded learning/exploration budget | laptop temperature or uncontrolled noise |
| gravity | learned affinity that makes compatible routes easier to enter | an inverse-square law applied blindly |
| orbit | a stable recurrent partial relation that can be reused | endless looping with no testable progress |
| time | a local update clock; active, surprising paths get more learning opportunities | real relativity inside ordinary code |
| fusion/coarse graining | replace redundant detailed routes by a smaller candidate that retains declared behaviour | deleting weights and assuming knowledge remains |

## 5. Hard compatibility and capacity-limited pipes

The central rule is:

> If an input does not fit a route's learned type and capacity, that route receives **zero** signal from that input.

For encoded input \(z\), a route can use a hard admission rule:

\[
C_p(z)=
\mathbf{1}\!\left[
d(z,\tau_p)\leq r_p
\;\land\;
\operatorname{demand}(z)\leq b_p
\;\land\;
\operatorname{scope}_p(z)=1
\right].
\]

Here \(d\) is a learned representation distance, \(r_p\) is the path's acceptance radius, and \(\operatorname{scope}_p\) is a learned structural compatibility test. The implementation may use masks and a sparse index, but the policy remains hard: a failed test means no partial activation leaking into an unrelated route.

For an admitted path:

\[
\operatorname{flow}_p(z)=C_p(z)\cdot F_p(z;W_p).
\]

Because \(C_p(z)\) is zero or one, a non-fitting input cannot be quietly mixed into that path.

Several compatible paths may share a small primitive or intersect at a declared interface. Intersection is not arbitrary mixing: each shared piece has its own input and output type. A learned quantity-comparison primitive could be used by arithmetic, physics, and word problems without making every language feature interact with every arithmetic feature.

### 5.1 Sparse recurrent settling

Within chosen routes, signals recur for a bounded number of microsteps:

\[
a^{k+1}
=(1-\lambda)a^k+
F_{\theta}\!\left(M_{R(z)}a^k,\;z\right),
\]

where:

- \(a^k\) is temporary activity;
- \(R(z)\) is the set of admitted routes;
- \(M_{R(z)}\) contains only edges belonging to those routes;
- \(\lambda\) is damping;
- the number of steps is limited by a declared compute budget.

This is serial-first causal processing: each microstep depends on the previous one. The device can still parallelise vector operations inside a microstep, but it does not need every parameter to run for every input.

### 5.2 Capacity is a real limit

Each route has:

\[
\operatorname{cost}(p)=P_p+A_p+S_p+O_p,
\]

where \(P_p\) is persistent parameters, \(A_p\) active activation memory, \(S_p\) optimiser/eligibility state, and \(O_p\) routing and bookkeeping overhead.

The total must remain within a hard active budget:

\[
\sum_{p\in\mathcal P_{\text{active}}}
\operatorname{cost}(p)
\leq B_{\text{device}}.
\]

An adapter is not free memory. It may share an existing base map or replace redundant state, but its parameters, state, and activation cost still enter this ledger.

## 6. Base path, adapter, rewrite, and branch

The system needs four different reactions to a correction. Treating all corrections as “change all weights” causes interference; treating all corrections as “add another expert” causes endless growth.

| Situation found by testing | Structural response | Why |
|---|---|---|
| Same rule, common form | strengthen the existing base path | improves the reusable primitive |
| Same rule, narrow alternate form | attach a small adapter | handles a local variation cheaply |
| Several routes implement the same underlying transformation | propose a refactor into a broader base path | turns repeated structure into one reusable operation |
| True conflict or incompatible rule | create a separate branch with an explicit scope boundary | prevents one context from corrupting another |
| Candidate has no measured advantage | reject it | more structure is not progress |

An adapter is a small residual transformation around a base path:

\[
y=P_{\text{base}}(z)+
C_{\text{adapter}}(z)\,
A_{\text{small}}(z).
\]

For a low-rank adapter:

\[
A_{\text{small}}(z)=UV^\top z,
\qquad
U\in\mathbb R^{d_{\text{out}}\times r},
\quad
V\in\mathbb R^{d_{\text{in}}\times r},
\quad
r\ll\min(d_{\text{in}},d_{\text{out}}).
\]

The rank \(r\) is the adapter's capacity. It must be paid for from the budget. A new adapter can be accepted only if it does one of the following:

1. shares a base transformation;
2. replaces redundant capacity elsewhere;
3. is later compiled into a smaller base path;
4. demonstrates enough verified gain per parameter, byte, and microstep to justify its place.

Turn “50% base plus small adapters reaches 90%” into a measurable claim:

\[
\text{adapter value}
=
\frac{
\Delta\text{verified coverage}
-\alpha\Delta\text{selective risk}
-\beta\Delta\text{forgetting}
}{
\Delta\text{persistent bytes}
+\gamma\Delta\text{active compute}
}.
\]

The weights \(\alpha,\beta,\gamma\) are fixed policy choices before comparison. They are not universal constants.

## 7. What happens after an answer is wrong

Suppose the model sees \(1+1\), sends activity through a quantity-and-addition pathway, and outputs 4. A trusted teaching signal says the answer is 2.

The intended sequence is:

1. Record the temporary active route and edge eligibility traces.
2. Obtain a trusted correction from a deterministic arithmetic verifier or curated lesson.
3. Mark the prediction as wrong; do not label the model's own next guess as truth.
4. Change only a candidate derived from the recently active compatible structure.
5. Test that candidate on varied sums, previously mastered cases, and withheld examples.
6. Promote it only if it improves the declared result without exceeding regressions or resource limits.

One correction does not reveal the entire addition rule. Generalisation requires a representation capable of quantities and operations plus varied verified examples. The goal is that repeated correction changes the pathway into a transformation that handles new compatible sums automatically.

### 7.1 Eligibility traces: local credit for recent pathways

An edge \(i\to j\) can maintain a fading eligibility trace:

\[
\varepsilon_{ij}^{t+1}
=\rho\varepsilon_{ij}^{t}
+\phi(a_i^t,a_j^t,W_{ij}),
\qquad 0\leq\rho<1.
\]

When a correction signal \(\delta_j\) arrives, a proposed local update is:

\[
\Delta W_{ij}
=-\eta\,
\pi_{ij}\,
\delta_j\,
\varepsilon_{ij}.
\]

Only recently relevant edges get substantial credit. Stability \(m\) lowers \(\pi\) for well-supported paths; surprise can raise plasticity on a new candidate, not on every old path.

This is related to e-prop's use of online synaptic eligibility traces and learning signals, but K-HPC must compare it with ordinary end-to-end gradients rather than assume it is better. [Bellec et al.](https://arxiv.org/abs/1901.09049) show an online approximation path for recurrent learning; they do not establish a general-purpose replacement for all backpropagation.

### 7.2 Backpropagation is a comparator, not a forbidden word

The plan does not ban backpropagation. It distinguishes:

- global gradient credit: a strong baseline for training fixed differentiable portions;
- local trace credit: a candidate method for online, sparse, recurrent adaptation;
- verifier feedback: a correctness signal separate from the model's own confidence;
- structural search: a discrete choice among adapter, refactor, branch, or rejection.

Removing an effective credit-assignment method merely because it is familiar would make the experiment less informative. The scientific question is whether hard paths, local traces, and safe structural change provide a better accuracy-retention-resource trade-off than equal-budget baselines.

## 8. Runtime algorithms

~~~text
ALGORITHM 1: HARD-PATH INFERENCE

Input: x, route graph P, fixed compute budget K
Output: prediction y, calibrated confidence c, route trace T

1. z <- encode(x)
2. candidates <- routes whose hard type/signature test passes on z
3. admitted <- candidates that fit their capacity and scope rules
4. active <- at most K admitted routes, chosen by a fixed sparse policy
5. If active is empty:
       return fallback_or_abstain(x), low confidence, empty trace
6. Run bounded recurrent settling only on edges owned by active routes.
7. Read an output and a confidence estimate from the settled state.
8. Return the result plus the exact temporary route trace.
~~~

The route trace is temporary internal state, not a permanent library of old user inputs. It may be retained briefly for a candidate update and then discarded, subject to the resource ledger.

~~~text
ALGORITHM 2: VERIFIED CORRECTION

Input: x, trusted target or verifier v, parent version M

1. Run HARD-PATH INFERENCE and obtain y, c, T.
2. Ask v whether y is correct; do not use c as proof.
3. If correct:
       increase evidence/support for the useful pathway only.
       update calibration statistics.
       stop.
4. If wrong:
       create a candidate from M; leave M unchanged.
       use T and recent eligibility traces to propose:
           a. local weight adjustment,
           b. small adapter,
           c. common-rule refactor, or
           d. scoped branch.
       test the candidate under the promotion rules below.
5. Promote only a passing candidate; otherwise keep M and log the failure.
~~~

~~~text
ALGORITHM 3: STRUCTURAL DECISION

Input: candidate failure cluster F, parent route p

1. Test whether F follows the same verified rule under a changed form.
   If yes, propose a small adapter to p.
2. Test whether two or more paths are behaviourally redundant on protected tests.
   If yes, propose a function-preserving refactor followed by restricted tuning.
3. Test whether the new evidence contradicts p inside p's valid scope.
   If yes, split scope or create a separate branch; do not average the conflict.
4. If the proposal cannot pay its state and compute budget, reject or queue it.
5. Evaluate candidate, parent, and fallback on the fixed suite.
6. Promote only if all non-negotiable gates pass.
~~~

## 9. The “cannot damage old knowledge” contract

Absolute no-forgetting is not honestly available for arbitrary future tasks without unlimited retained information. The project can instead make a strong, measurable contract:

> A candidate must not replace a protected parent route unless it passes the parent route's protected tests, its new-skill tests, calibration checks, and full resource accounting.

The safe answer-selection rule is:

\[
\operatorname{use}(p_{\text{new}},z)
\Longleftrightarrow
C_{p_{\text{new}}}(z)=1
\land
c_{\text{new}}(z)\geq\theta
\land
p_{\text{new}}\text{ is promoted}.
\]

Otherwise use the old route, a verified adapter, an explicit fallback, or abstain.

### 9.1 Coverage is not accuracy

| Statement | Meaning | Safe? |
|---|---|---|
| “The base route handles 50% of cases.” | It accepts 50% and sends the rest to a fallback or adapter. | potentially safe |
| “The new route answers 90% correctly.” | It may still give silent wrong answers on 10% of all accepted cases. | not enough |
| “At 90% coverage, accepted answers have at most a declared error bound on a held-out distribution.” | Coverage and conditional risk are measured separately. | the correct test target |

Measure:

\[
\operatorname{coverage}
=\Pr[\text{route accepts}],
\qquad
\operatorname{selective\ risk}
=\Pr[\text{wrong}\mid\text{route accepts}].
\]

For deterministic arithmetic, small formal systems, or executable programs, a verifier can establish correctness for an individual output. For broad language or scientific claims, confidence must remain a calibrated estimate, not “100% certain.”

### 9.2 Promotion gates

Before a candidate is promoted, all of these must pass:

1. **New-skill gain:** a predeclared improvement on a held-out task set.
2. **Retention:** no protected old-skill metric crosses its allowed regression limit.
3. **Selective safety:** confidence, coverage, and conditional error meet the predeclared target.
4. **Budget:** total persistent state, transient activation, eligibility/optimizer state, and latency remain within the device ceiling.
5. **Reproducibility:** the same candidate and test manifest reproduce the result.
6. **Fallback integrity:** the old parent remains available until the candidate passes; rejected candidates never overwrite it.

The evaluator, verifier, resource supervisor, and user stop control are outside the candidate's authority.

## 10. Growth, compression, and the fixed budget

The desired developmental pattern is:

\[
\text{stable base}
\rightarrow
\text{bounded local growth}
\rightarrow
\text{test}
\rightarrow
\text{merge or coarse-grain}
\rightarrow
\text{test again}.
\]

It is not:

\[
\text{always add adapters}
\rightarrow
\text{quietly use more memory forever}.
\]

### 10.1 Turning capacity down to zero

An inactive or dormant pathway can use zero *active compute*, but it cannot use zero persistent memory if the system intends to restore it exactly later. A dormant route still costs at least an address, metadata, and whatever compressed representation remains.

The defensible version is:

1. turn a low-value route's active capacity to zero;
2. create a smaller compressed candidate representation;
3. verify declared retained behaviour;
4. retain the compressed route or discard only the part shown redundant;
5. record the true before-and-after state cost.

This supports the intended “smaller neurons / coarser grains” idea without pretending that compression creates free information storage.

### 10.2 Safe consolidation rules

A group of adapters may be merged into a base route only when:

\[
\begin{aligned}
Q_{\text{new skill}}(M') &\geq Q_{\text{new skill}}(M)-\epsilon_{\text{new}},\\
Q_{\text{protected}}(M') &\geq Q_{\text{protected}}(M)-\epsilon_{\text{old}},\\
\operatorname{cost}(M') &< \operatorname{cost}(M),\\
\operatorname{risk}_{\text{selective}}(M') &\leq r_{\max}.
\end{aligned}
\]

The protected behaviours are declared before compression. If a behaviour was never represented in tests, the system cannot honestly promise it survived.

Function-preserving transformations are an important research comparison: [Net2Net](https://arxiv.org/abs/1511.05641) and [Network Morphism](https://arxiv.org/abs/1603.01670) show ways to change some neural structures while initially preserving their function. They support candidate refactoring as an engineering idea, but neither paper proves that arbitrary semantic pathways can be merged without loss.

## 11. Staged curriculum

School-like order is useful because it makes the experiment diagnosable. It is not itself an intelligence algorithm.

| Stage | Teach with | Verify with | What should become structural |
|---|---|---|---|
| 0. Representation primitives | symbols, equality/inequality, sequences, counts | generated exact tests | typed input and output routes |
| 1. Arithmetic operations | addition, subtraction, then multiplication/division | deterministic arithmetic verifier | quantity and operation pathways |
| 2. Formal composition | parentheses, variables, simple algebra | symbolic evaluator | reusable transformation chains |
| 3. Formal language | a small generated grammar and meanings | parser/interpreter | syntax and composition routes |
| 4. Cross-domain transfer | word problems tied to exact arithmetic or mechanics | deterministic generators | shared quantity/relation primitives |
| 5. Larger curated sources | only after lower stages have measured success | source-specific and held-out evaluations | broader abstractions, not raw source copying |

For each stage:

1. start with small, generated, checkable tasks;
2. evaluate on withheld combinations, not merely repeated examples;
3. record coverage, risk, retention, and resource use;
4. introduce adapters only after identifying a recurrent failure cluster;
5. attempt a refactor only after multiple adapters show a common rule;
6. revisit earlier tests after every consolidation.

“Starting the next grade at zero” should mean resetting the **progress counter for the new curriculum stage**, not resetting physical memory or pretending existing capacity vanished. Earlier pathways remain protected until a measured compression candidate proves adequate.

## 12. Research basis and what it actually supports

The following are primary papers inspected at the abstract/summary level for this plan. They are related mechanisms, not proof that their combination works. Full-method reading and reproduction should occur before implementation.

| Research | Established contribution | Use in K-HPC | What it does not prove |
|---|---|---|---|
| [Kirkpatrick et al., EWC](https://arxiv.org/abs/1612.00796) | slows changes to parameters important to earlier tasks | evidence-weighted stability or “mass” baseline | perfect retention or a structural pathway architecture |
| [Zenke, Poole, Ganguli, Synaptic Intelligence](https://arxiv.org/abs/1703.04200) | accumulates parameter importance during learning to reduce forgetting | another baseline for local importance accounting | that importance scores solve arbitrary task interference |
| [Li and Hoiem, Learning without Forgetting](https://arxiv.org/abs/1606.09282) | preserves old outputs while learning a new task without old-task data | comparison for no-raw-replay consolidation | exact retention when old outputs are incomplete or wrong |
| [Bellec et al., e-prop](https://arxiv.org/abs/1901.09049) | online eligibility traces plus learning signals approximate recurrent credit assignment | local recent-path correction candidate | a universal replacement for end-to-end gradients |
| [Miconi, Clune, Stanley, Differentiable Plasticity](https://arxiv.org/abs/1804.02464) | learns plastic recurrent connections with trainable Hebbian terms | fast/slow route plasticity baseline | safe lifelong learning or structural growth under a fixed budget |
| [Chen, Goodfellow, Shlens, Net2Net](https://arxiv.org/abs/1511.05641) | function-preserving transformations for some wider/deeper neural nets | safe initialisation for candidate refactors | semantic equivalence after later tuning |
| [Wei et al., Network Morphism](https://arxiv.org/abs/1603.01670) | generalises function-preserving network structural transformations | graph-refactor comparator | lossless arbitrary compression |
| [Rusu et al., Progressive Neural Networks](https://arxiv.org/abs/1606.04671) | avoids forgetting by freezing earlier columns and adding later ones | a retention baseline | fixed memory use; it grows with tasks |
| [Yoon et al., Dynamically Expandable Networks](https://arxiv.org/abs/1708.01547) | adds capacity for sequential tasks and encourages selective reuse | growth baseline | that expansion can remain inside a strict fixed device budget |
| [Rosenbaum et al., Routing Networks](https://arxiv.org/abs/1711.01239) | routes tasks through selected functions to reduce interference | routing comparator | the user’s single-fabric, non-expert pathway design |
| [Bengio, Léonard, Courville, Conditional Computation](https://arxiv.org/abs/1308.3432) | sparse stochastic units can activate only some computation | motivation for input-dependent compute | easy, stable training of hard discrete decisions |
| [Geifman and El-Yaniv, Selective Classification](https://arxiv.org/abs/1705.08500) | separates coverage from risk through a reject option | the mandatory acceptance/fallback measurement | correctness beyond the tested distribution |
| [Shannon, A Mathematical Theory of Communication](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x) | formal basis for information capacity and compression | honest limits on “infinite context” and zero-cost adapters | a particular neural architecture |

This research points to a useful conclusion: pieces of the idea exist separately—local plasticity, sparse routing, growth, morphism, importance protection, and abstention—but their trade-offs conflict. K-HPC exists as a research plan because the combination must be tested under one fixed budget and one fixed evaluator.

## 13. Required comparisons

The new core should never be compared with a weaker or larger uncontrolled system. Every candidate must be matched for:

- persistent parameter bytes;
- optimiser and eligibility state;
- peak activation bytes;
- routing index and metadata;
- number of microsteps;
- wall-clock latency;
- training examples and verifier calls;
- held-out test distribution;
- allowed fallback tools.

### 13.1 First controlled benchmark

Start with generated arithmetic and a tiny formal grammar, not broad web-scale language. These tasks have exact verifiers and make wrong answers unambiguous.

| ID | Equal-budget baseline/candidate | Purpose |
|---|---|---|
| B0 | fixed sparse recurrent graph | base quality and resource floor |
| B1 | B0 plus ordinary end-to-end gradient training | standard credit-assignment control |
| B2 | B1 plus parameter-importance protection | continual-learning control |
| H1 | hard paths with no adapters | isolate hard compatibility |
| H2 | H1 plus small adapters | test whether adapters improve coverage per cost |
| H3 | H2 plus candidate refactor/merge | test whether repeated adapters can compile into a smaller base |
| H4 | H3 plus local eligibility traces | test local correction against B1 at the same budget |

An H-series candidate is useful only if it occupies a better measured trade-off point than the baselines: better retained/generalised behaviour at equal or lower resource cost, or lower cost at equal protected behaviour.

### 13.2 Metrics

| Metric | Question it answers |
|---|---|
| exact accuracy | Are accepted answers correct on a known test? |
| coverage | How often does the path answer rather than defer? |
| selective risk | How often is it wrong when it chooses to answer? |
| calibration | Does a stated confidence match observed frequency? |
| old-skill retention | Did post-change performance regress on protected earlier tasks? |
| compositional transfer | Does a rule work on withheld combinations? |
| adapter efficiency | How much verified gain came per added persistent byte and active microstep? |
| route sparsity | How much of the graph actually ran? |
| peak resource cost | Could it run within the declared device ceiling? |
| candidate rejection rate | Is the proposal mechanism producing useful changes or random churn? |
| failure taxonomy | Did it fail from routing, representation, learning, consolidation, or confidence? |

## 14. Failure modes that must be expected

| Failure | What it looks like | Required response |
|---|---|---|
| brittle hard boundaries | a nearly matching input reaches no useful route | measure boundary cases; adjust representation or add a justified adapter |
| route collapse | one large route accepts everything | penalise over-broad scope and test selective risk |
| adapter bloat | coverage rises only because state grows without limit | enforce budget donation/replacement and merge tests |
| false confidence | system claims certainty on unsupported inputs | calibrate, require fallback, and use verifiers where possible |
| catastrophic interference | a local correction harms old tasks | keep parent frozen, test candidates, reject failures |
| memorisation instead of rule learning | training examples pass but combinations fail | use generated held-out compositions and minimal-description comparisons |
| harmful merge | compressed route loses a rare skill | retain parent until declared retention suite passes |
| endless unproductive mutation | many candidates with no useful gain | bounded experiment queue and stop after a predeclared negative result |
| evaluator gaming | candidate changes its target, test, or resource report | evaluator and ledger remain outside candidate authority |

## 15. Decision gates for implementation

No model training is authorised by this document. If the owner later unlocks implementation, use these gates in order.

1. **Specification gate:** choose one small domain, a fixed generator/verifier, a hard resource ledger, and a protected test manifest.
2. **Baseline gate:** reproduce B0 and B1 before adding pathway novelty.
3. **Hard-routing gate:** show H1's routing is sparse, stable, and no worse than B1 on declared quality at comparable resources.
4. **Adapter gate:** show H2 improves held-out coverage or selective risk without failing protected retention tests.
5. **Consolidation gate:** show H3 can reduce the true resource ledger while retaining declared behaviours.
6. **Local-learning gate:** show H4 matches or beats the global-gradient control on at least one predeclared continual-learning setting.
7. **Broader-curriculum gate:** only after earlier gates pass, expand from generated arithmetic/formal grammar to a carefully sourced educational domain.

Any failed gate is useful evidence. The proper result is to retain the simpler system or archive the negative result, not to redefine the score until it passes.

## 16. How this fits the existing Kavi designs

| Existing component | Role after this plan |
|---|---|
| Kavi Physical Dynamics Core | supplies sparse recurrent dynamics, local clocks, damping, bounded propagation, and resource-aware graph state |
| K-HPC | specifies strict typed route admission, base/adapter/refactor/branch choices, and the no-silent-damage promotion contract |
| Verified Search and Compilation Core | supplies the task contract, external tools, proof/checking boundary, versioning, and audit process for agentic work |
| Evaluation harness | stays independent; it is the source of success/failure evidence, not part of the learner's mutable “thought” |

The three layers should not be confused:

1. **K-HPC** learns and selects compact internal transformations.
2. **The agent harness** plans tasks, calls permitted tools, and schedules bounded experiments.
3. **The verifier/evaluator** decides whether an answer or candidate actually passed.

This separation is what allows a model to keep trying at difficult work without giving it authority to redefine truth, delete its stop control, or silently damage its own evaluator.

## 17. Final child-level summary

Kavi should be built like a careful growing map of useful roads:

- A road only opens for vehicles it fits.
- A small side road handles a nearby new kind of vehicle.
- If many side roads do the same job, engineers build one better main road.
- The old road stays open until the new road proves it works.
- The city has a fixed amount of land, so every new road must replace, share, or earn its space.
- A teacher checks answers. The city is not allowed to mark its own homework.

That is a concrete way to explore the requested “triggered pathways” idea while keeping it measurable, safe, device-bounded, and scientifically falsifiable.
