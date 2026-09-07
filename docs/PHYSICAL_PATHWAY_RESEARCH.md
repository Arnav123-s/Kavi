# Physical pathway mechanisms: engineered and learned

Author: [Arnav123-s](https://github.com/Arnav123-s)

7 September 2026. Research proposal; not implemented. Extracted from the [certificate and software study](CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md). Earlier external-review recommendations remain deferred.




The proposed goal is to make the program's internal dynamics more expressive and useful for learning. It is not to make the laptop equal a quantum computer or supercomputer in raw hardware capacity. Heat, cooling, catalysis and a periodic-table-like organization can have precise software meanings. Their value depends on the rules chosen and their measured effect on acquisition, transfer and retention.

The closest mathematical relatives are typed reaction networks, multiset rewriting, stochastic search and energy-based dynamics. These are different models with different guarantees. Combining their vocabulary is not yet a combined algorithm.

![Typed pathways with thermal exploration and catalytic context](figures/physical-pathway-model.svg)

### 10.1 A table of computational elements

The periodic table is a useful organizational analogy: a small set of components with systematic composition properties can produce many compounds. A software version should classify components by verified behavior, not assign literal chemical elements or assume electron-shell laws apply to programs.

| Property | Computational meaning | Example boundary |
| --- | --- | --- |
| Species or family | Input and output types | Integer, proposition, sequence and physical quantity are distinct |
| Bonding sites | Arity, binding and composition rules | A binary operation needs two compatible arguments |
| Reaction laws | Verified algebraic identities | Integer addition is commutative; subtraction is not |
| Conserved quantity | Invariant preserved by a transformation | Value, unit, resource token or proof obligation |
| Activation condition | Context in which a rule is valid | Nonzero divisor, available lemma, matched grammar |
| Catalytic effect | Change in proposal or execution rate | A valid reusable rule accelerates a known transformation |
| Stability class | Conditions for valid settling behavior | Fixed energy and admissible dynamics |

This table is a proposed representation, not a new chemistry implementation. A component's properties may need proofs or qualified evidence. Learning an unknown property is part of the problem; it cannot be supplied by an attractive label. The table also need not have 118 entries or imitate the real periodic ordering.

### 10.2 Reaction rules as pathways

Let a count vector n describe available typed objects. A reaction consumes a multiset alpha and produces beta:

$$r:\alpha_r\longrightarrow\beta_r,\qquad n'=n+\nu_r,\quad\nu_r=\beta_r-\alpha_r.$$

The reaction is enabled only when n is componentwise at least alpha and all type and context guards hold. If N collects the reaction vectors, a linear invariant is certified by:

$$\ell^TN=0\quad\Longrightarrow\quad\ell^Tn'=\ell^Tn.$$

For example, reactions A to Y and B to Y preserve A+B+Y. Starting with counts (a,b,0), eventual exhaustion of both inputs yields Y=a+b. Explicitly firing one event per unit takes a+b events, however. It is much less efficient for large integers than Kavi's binary representation. Emulation should preserve useful logic without mechanically copying a costly molecular encoding.

[Chen, Doty and Soloveichik](https://web.cs.ucdavis.edu/~doty/papers/dfccrn-journal.pdf) characterize deterministic stable count-output computation by finite chemical reaction networks as semilinear under their model. Their work distinguishes that model from probabilistic computational universality. “Chemical networks can compute” is not a guarantee that every chosen reaction system learns general intelligence.

### 10.3 Rates and concentrations

A continuous mass-action model uses concentrations x and reaction rates v:

$$\dot x=Nv(x),\qquad v_r(x)=k_r\prod_i x_i^{\alpha_{ir}}.$$

Rate constants depend on the concentration and time units. If concentration has unit C, a reaction of total order m requires k with units C to the power 1-m per time. Discrete molecule counts require combinatorial propensities instead of blindly reusing the continuous rate law. In a software-only analogue, these may instead be dimensionless activation variables and computational update rates; that choice must be stated.

If a connector changes a rate based on incoming information, the program has a context-dependent dynamical system. This could encourage some transitions and suppress others. It does not determine whether the resulting output is correct. That remains a separate task contract.

### 10.4 Heat and cooling as exploration controls

For a finite feasible set of candidate configurations G, assign a declared score E(G) and positive temperature T in matching score units:

$$\pi_T(G)=\frac{e^{-E(G)/T}}{Z_T}.$$

Higher temperature makes unfavorable alternatives less suppressed. Lower temperature concentrates probability on lower-score alternatives. [Simulated annealing](https://hedibert.org/wp-content/uploads/2013/12/1983KirkpatrickGelattVecchi.pdf) gives an established computational use of this idea. Each proposed state still has to be constructed and evaluated; temperature does not evaluate all branches simultaneously.

A proposed connector-level heat signal could respond to a bounded diagnostic mismatch r, then cool between events:

$$h_{t+1}=\operatorname{clip}_{[0,h_{\max}]}\big((1-\lambda)h_t+\alpha r_t\big),\quad T_t=T_{\min}+(T_{\max}-T_{\min})h_t/h_{\max}.$$

Here 0<lambda<=1, alpha is nonnegative, h_max is positive, and 0<T_min<=T_max. This is a candidate control rule devised for the study, not an implemented learner or a physical heat equation. A mismatch could increase exploration locally; success or inactivity could permit cooling. The signal must not be derived from withheld evaluation answers.

For proposal q, a fixed-temperature Metropolis-Hastings step accepts with:

$$A(G,G')=\min\left(1,e^{-[E(G')-E(G)]/T}\frac{q(G\mid G')}{q(G'\mid G)}\right).$$

The ratio matters when catalysts bias proposals asymmetrically. Invalid types and invalid proofs are outside the feasible set, so heating never makes them acceptable. Correctness is not a finite energy penalty that sufficiently high temperature may override.

[Hajek's cooling theorem](https://web.mit.edu/6.435/www/Hajek88.pdf) concerns a fixed finite landscape under explicit connectivity and cooling conditions. For its deepest nonglobal barrier d*, the relevant infinite-series condition is:

$$\sum_{k=1}^{\infty}e^{-d^*/T_k}=\infty.$$

The familiar logarithmic schedule can satisfy this condition, but it is an asymptotic convergence result, not a practical runtime promise. A changing learned graph, changing energy or local reheating cannot simply inherit it.

### 10.5 Catalysts and controlled settling

A reaction C+X to C+Y leaves the catalyst present. In software, C might represent an available lemma, a typed context or an already validated conversion. Its presence can enable a route or alter proposal rates. It does not make a false statement true.

Another precise classical analogue is a mobility matrix that changes how an internal state z moves down a fixed energy:

$$\dot z=-M(z,c)\nabla E(z),\qquad M=M^T\succeq0.$$

Then direct differentiation gives:

$$\dot E=-\nabla E^TM\nabla E\le0.$$

A positive scalar multiplier changes continuous-time speed along the same trajectory. A positive-definite matrix can change the trajectory while preserving descent; a singular one can introduce stuck states. This is a computational analogy to catalysis. Numerical integration still costs work and requires stability checks.

For actual fixed complex-balanced mass-action networks with positive equilibrium x*, an established Lyapunov function is:

$$V(x)=\sum_i\left[x_i\log(x_i/x_i^*)-x_i+x_i^*\right].$$

[Anderson's proof](https://people.math.wisc.edu/~dfanderson/CRNT_Lyapunov.pdf) establishes decrease in the positive stoichiometric class under the stated assumptions. It does not apply automatically to an arbitrary adaptive graph, driven input stream or changing reaction table. Likewise, when learning makes E time-dependent:

$$\frac{dE(z,t)}{dt}=\nabla E^T\dot z+\partial_tE.$$

The extra term can be positive. Fixed-configuration settling and structural learning therefore need separate analysis. A low-energy state is also not necessarily a correct answer; the chosen energy must represent the actual objective adequately.

### 10.6 More outputs from one pathway

A shared pathway can produce a structured result, a distribution over alternatives, or a bounded set of candidates. Connectors can expose different outputs based on types and context. This is compatible with reusable computation, but a branching implementation must count every evaluated branch and its stored state.

If B alternatives are maintained, their aggregate state and work generally grow with B unless a demonstrated shared representation reduces them. Sampling one branch, returning all B outputs and calculating an interference amplitude are distinct operations. Chemical concentrations are nonnegative populations; complex amplitudes have phases and interference. One cannot substitute one model for another while keeping all of its guarantees.

### 10.7 A falsifiable research question

The useful hypothesis is: do typed components, context-sensitive reaction rules and temperature-controlled exploration improve acquisition or transfer at a fixed total compute and storage budget? Compare thermal routing against fixed-temperature routing, catalytic context against an equally informed ordinary selector, and the component table against the same properties represented without chemistry terminology.

Track withheld compositional success, retention, number of candidates, time, peak memory and persistent state. Include failures such as runaway activation, cycling, overconfident settling and incorrect rule reuse. Rates, barriers, heat variables and durable graph choices all count as state; changing their names does not eliminate parameters.

No physical-pathway mechanism is implemented in this update. It is recorded as a separate user-proposed direction, alongside the software survey. The external review's recommendations remain deferred. A later bounded experiment can decide whether the new dynamics add useful computation beyond the existing baseline.


### 10.8 Two tracks: engineered rules and learned rules

The research direction has two distinct tracks. In the first, an engineer designs the component taxonomy, connector rules, thermal response and catalytic effects. The learner uses those supplied mechanisms. In the second, the learner acquires improvements to configurations or to the rules that generate and modify configurations. Success in the first track does not establish success in the second.

![Engineered and learned mechanism tracks](figures/two-learning-tracks.svg)

| Track | What is supplied | What may be learned | Evidence required |
| --- | --- | --- | --- |
| A. Engineered mechanism | Update rules, component contracts, thermal law, catalyst behavior | Task-specific pathways within that system | Benefit over the same task learner without the mechanism |
| B1. Learned selection | A menu of engineered mechanisms | Which mechanism to use and its settings | Transfer of the selector to new tasks |
| B2. Learned composition | Lower-level operations and a bounded composition language | New configurations and control programs | Held-out success from compositions not supplied as complete solutions |
| B3. Learned adaptation | A bounded language for proposing graph and rule changes | A reusable update procedure that improves later learning | Improvement across independent task sequences, with retained skills and full resource accounting |

Learning an update procedure has precedents such as [Andrychowicz et al. (2016)](https://arxiv.org/abs/1606.04474), which studies learned numerical optimizers. That is relevant prior art, not an implementation match for Kavi. B1 is useful but should not be reported as inventing a mechanism. B2 and B3 are stronger claims. Even those tracks require a supplied execution substrate, admissible representation and evaluation contract. What the learner is permitted to change must be explicit.

Let K be the persistent configuration and D new teaching evidence. A learned update procedure M with parameters or structural description phi proposes:

$$K'=M_\phi(K,D).$$

Here phi may itself be an executable graph rather than a dense weight array. Its description and training workspace still count as stored information. A proposed cross-task objective is:

$$J(\phi)=\sum_{\tau\in\mathcal T_{\rm train}}\left[\mathcal E_\tau\!\left(M_\phi(K_\tau,D_\tau),V_\tau\right)+\lambda C_\tau+\mu\ell(K'_\tau)\right].$$

D contains task-specific teaching examples; V contains feedback used to train the update procedure; C counts adaptation and execution cost; and length uses a fixed encoding. Because V influences phi, V is training data at the outer learning level. Final evaluation needs independent tasks and examples that influenced neither the update rule nor selection of its reported version.

Before accepting a proposal, check type validity, configured resource limits, relevant correctness certificates and the retained bank. Store changes as versioned model data with a reversible promotion step. The research proposal does not authorize arbitrary source-code editing or removal of these checks. The current update adds documentation only; it does not run an adaptive rule learner.

The hypothesis is that increasing experience yields more useful configurations and eventually a better adaptation mechanism. More complex configurations are not automatically better: complexity must earn its cost through new capability, cheaper acquisition or stronger reuse. Progress should be measured against experience while separately plotting retained-task performance, held-out transfer, persistent size and total computation. Learning can stall, overfit or regress; monotonic improvement is a claim to test, not an assumption built into the score.

Scientific, mathematical and literary material can supply candidate structures and relationships, but text ingestion alone does not specify valid update rules. The system needs a process that turns material into typed hypotheses, checks consequences and retains reusable results. This remains the central learning challenge in both tracks.


### 10.9 Learned restructuring of the whole computation

The intended learner is not limited to adding a pathway for each new lesson. It may reorganize an entire computation, share intermediates, fuse operations, replace an algorithm or remove unnecessary structure when the replacement is justified. Preserving valid earlier behavior does not require preserving the old nodes and wires.

![Whole-computation restructuring with preserved contracts](figures/whole-computation-restructuring.svg)

For exact integers, a simple example is:

$$ab+ac=a(b+c).$$

The left form has two multiplications and one addition; the right has one of each. This illustrates a supplied algebraic identity, not a newly learned Kavi optimization. Floating-point evaluation can round differently, and actual runtime depends on operand sizes and the executor. A shorter graph is not automatically faster on every input.

One shared configuration can expose addition, subtraction, multiplication and division through a typed operation selector and common components. It still has to distinguish their meanings. A fused composition can avoid materializing intermediate results or repeating a subcomputation, but arbitrary inputs do not acquire answers without computation. Division also needs a defined zero-divisor policy and a declared integer, rational or real-number semantics.

Let W denote a declared workload and R a set of protected input/output obligations. A possible restructuring objective is:

$$\min_{G'} C(G';W)+\lambda\ell(G')\quad\text{subject to}\quad F_{G'}(x)=y\;\;\forall(x,y)\in R.$$

New teaching obligations and type/resource constraints are additional conditions. This is a proposed objective. A finite R supplies finite retention evidence; proof-backed equivalence over a declared domain is stronger. Incorrect old answers should not be protected merely because they are old. If newly admitted evidence conflicts with a protected obligation, resolve the assumptions or labels rather than quietly changing the evaluation contract.

The permissible change can include many small coordinated edits or a complete replacement of a connected region. The system should inspect dependency effects, compare the replacement's outputs and costs, and only then promote the new configuration. When no beneficial replacement is found within the search budget, keeping the current configuration is a valid outcome. Discovering the globally shortest program is not assumed to be tractable; measured improvement under a bounded search is a realistic target.

Chemistry and physical dynamics might provide proposal mechanisms for those changes: local reactions suggest edits, catalytic context enables reusable transformations, and temperature changes the willingness to explore alternatives. They do not discharge the semantic obligations. A phase of fixed-graph settling can be followed by a checked restructuring step, but the stability proof for the old graph must not be asserted for the new graph without checking its assumptions.

The central hypothesis is that accumulated knowledge improves both the available computations and the learner's ability to reorganize them. Test separately whether additional teaching improves correctness, reduces execution cost, improves later learning, or changes persistent size. These outcomes may move in different directions. The desired trajectory is better capability per unit of computation and stored structure, not complexity growth for its own sake.
