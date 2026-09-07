# Kavi: Structural Sharing and Quantum Computation

Author: Arnav123-s

Revision: 7 September 2026

Structural learner baseline: 2ac3b5e; connector and sentence trial, 7 September 2026

## Abstract

Kavi investigates whether a learner can acquire reusable computations by changing executable structure. Its present arithmetic library is small and inspectable, but its search language, iteration rules and recent multiplication optimization are supplied. Learning reusable structure already has close precedents in DreamCoder and Babble. A stronger Kavi would have to demonstrate better acquisition, abstraction, correction or resource use under comparable conditions.

This study develops a concrete extension: typed program sharing, distinguishing probes, guarded consolidation and an optional interference-based search proposal. It derives the relevant constraints from quantum computation and examines both X-ray fluorescence and laser-induced breakdown spectroscopy as models of calibrated probing. Quantum states do not provide unrestricted access to all possible answers. Classical simulation, reversible execution, state preparation, measurement and verification all carry costs.

The recommended first implementation is classical. It should learn abstractions across equivalent programs, search for counterexamples before merging them, and measure reuse on withheld tasks. Quantum computation becomes a separate experimental backend only after a useful search problem and its reversible oracle are specified. Nine small classical algebra checks accompany this document. They verify examples and numerical identities; they do not demonstrate learning or quantum advantage.

## 1 Scope and present evidence

The central idea is to store a computation once and reuse it wherever its contract applies. Learning addition rather than a list of sums is a valid example. The distinction is between instance storage and procedure acquisition. Changing connections can encode durable knowledge even when transient signals disappear. A learner with persistent topology is therefore stateful: the topology is its memory.

This document separates the inspected implementation, published research, mathematical derivations under stated assumptions, and proposed experiments. It is a design study, not a claim that the proposed architecture exists. It does not establish priority for a new learning principle, general language understanding, graduate-level competence, or a performance advantage over another system.

### 1.1 What the current code does

The structural core acquires local Boolean arithmetic transitions and assembles programs from supplied arguments, constants, calls, repetition and ranges. `kavi/procedure_search.py` enumerates bounded expressions and uses their outputs on teaching cases to suppress duplicates. The inspected search admits up to three arguments and bounds expression size at four nodes. Its candidate ordering is not a learned neural proposal policy.

`kavi/procedure_optimizations.py` recognizes a specific repeated-addition form and supplies an unordered operand connector and binary-fold compilation. The addition transition is checked on all eight local input/carry combinations. These checks support that local truth-table identity; extending it to arbitrary binary inputs also depends on the supplied initialization, framing and iteration semantics.

`kavi/grounded_language.py` induces typed sentence frames from annotated examples. It also stores lexical occurrences and adjacency from admitted passages. Such records provide evidence about forms and co-occurrence, but do not by themselves identify an author's argument, establish the truth of a scientific claim, or teach creative writing.

### 1.2 Measurements already available

The 7 September connector and sentence trial reported the following. These are earlier recorded results, not new measurements from this research exercise.

| Item | Recorded result | Boundary |
| --- | --- | --- |
| Multiplication | 16,431 correct cases; 47 swapped pairs with identical complete call traces | Supplied canonicalization and compilation |
| Retention | 516 earlier successful cases preserved | Finite regression bank |
| Sentence learning | 18 frames from 36 annotated examples | Known constructions and typed slots |
| Declared sentence checks | 12 calculations, 7 clause checks, 2 definition recalls; 7 unsupported, ambiguous or invalid cases handled as specified | No general prose comprehension |
| Saved arithmetic | 2,272 bytes; 13 procedures | Excludes executor and search workspace |
| Saved arithmetic plus language | 29,082 bytes | Includes source-derived lexical state |
| Worker resources | 2.653 seconds; 26.36 MiB peak working set | One narrow trial; window measured separately |

The experiment record is `experiments/2026-09-07-connectors-language.md`. Earlier code validation reported 181 passing tests. This study adds only the algebra checks described in Section 12. No curriculum or quantum hardware run was performed.

## 2 The relationship to DreamCoder and Babble

DreamCoder combines example-driven program synthesis, reusable library acquisition and a trained neural search policy. Its wake/sleep process alternates solving tasks, compressing solutions into abstractions, and training the proposal mechanism with generated and replayed programs. The paper also uses equivalence representations during refactoring; it should not be described as merely manipulating isolated syntax trees. [D1](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)

Babble concentrates on abstraction discovery from programs under a supplied equational theory. It combines e-graphs and anti-unification to expose reusable forms across equivalent expressions. It is not, by itself, a complete language learner or the same example-to-program loop as DreamCoder. Its library selection and candidate generation remain approximate. [B1](https://arxiv.org/html/2212.04596)

| Mechanism | DreamCoder / Babble precedent | Kavi at the inspected baseline |
| --- | --- | --- |
| Reusable procedures | Both learn library abstractions | Acquired arithmetic and compositions |
| Search from examples | Central to DreamCoder | Bounded enumeration in supplied syntax |
| Learned search proposal | DreamCoder trains a neural recognizer | Absent from the structural core |
| Equivalence-aware abstraction | Present in both, with different methods | Teaching-output deduplication; selected compiler rules |
| Sharing beyond syntax | Babble uses supplied semantic equations | No general equivalent-program abstraction pass |
| Correction and retention | Not an exclusive principle of Kavi | Explicit finite retention records |
| Quantum computation | Not needed for either mechanism | Proposed only |

The meaningful question is therefore not whether Kavi has wires while these systems have programs. An executable graph and an executable program can represent the same computation. The research question is whether Kavi can discover useful shared structure with fewer examples, lower total search cost, better correction behavior, or smaller deployed state at equal competence.

### 2.1 Objective and representation

Let a library contain typed definitions, and let each task have a program composed from that library. A simplified form of DreamCoder's Bayesian library objective is:

$$J(D,\theta)=P(D,\theta)\prod_{x\in X}\sum_{\rho}P(x\mid\rho)P(\rho\mid D,\theta).$$

Here D is the library, theta its probabilistic grammar parameters, x a task, and rho a program. Practical search approximates the sum with finite candidate sets. The separate neural recognizer assists search rather than making this expression exactly tractable. [D1](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)

Babble instead seeks a smaller expression with abstractions whose expansion is equivalent to the supplied program corpus under an equational theory E. In compact notation:

$$\min_{\widehat t}\operatorname{size}(\widehat t),\qquad\widehat t\to_\beta^*t'\equiv_E t.$$

Beta reduction expands the introduced abstractions. Equivalence depends on E; the size objective counts definitions as well as their uses. This formulation describes an abstraction problem, not unrestricted inference from examples. [B1](https://arxiv.org/html/2212.04596)

For Kavi, a proposed engineering objective is an explicit description length plus error and execution cost:

$$\min_{L,\{p_i\}}\;\ell(L)+\sum_i\ell(p_i\mid L)+\lambda\sum_i\mathcal E_i(p_i)+\mu\sum_i C_i(p_i).$$

Lengths are measured in bits under a fixed serializer. Error and cost scales, lambda and mu must be declared before comparison. Type correctness, resource bounds and retained-task acceptance are constraints. This is a proposed objective built from established principles, not an implemented optimizer or a new theorem.

### 2.2 Sharing must include the definition cost

Suppose an expression occupies s bits at each of k sites, a new shared definition occupies d bits, and a call occupies c bits. Ignoring secondary changes, extraction saves space exactly when:

$$ks>d+kc\quad\Longleftrightarrow\quad k(s-c)>d.$$

Small abstractions can increase storage when called rarely. Runtime may increase through dispatch even when storage decreases. Search must also charge for trying rejected abstractions.

For example, anti-unifying `f(g(a),a)` and `f(g(b),b)` gives `f(g(X),X)`. The repeated variable matters: replacing its two occurrences independently would change the relation. If equivalent rewrites reveal this structure only after normalization, syntax matching alone misses it. Babble supplies a direct prior-art reference for this problem. [B1](https://arxiv.org/html/2212.04596)

### 2.3 A defensible difference to pursue

Kavi could combine abstraction extraction with explicit correction dependencies: identify the smallest reusable component responsible for a failure, propose a guarded replacement, find discriminating examples, and revalidate all dependent procedures before promotion. A useful contribution would be measured improvement from that integration. No claim of novelty follows simply from naming the integration or drawing it as a circuit.

## 3 Correct connectors and the limits of equivalence

For a commutative operation, the canonical connector can map an ordered pair to a shared representation:

$$c(a,b)=(\min(a,b),\max(a,b)),\qquad f=f\circ c.$$

The equality requires a valid commutativity contract over the relevant domain. It applies to exact integer multiplication. It does not apply to subtraction, implication, subject/object roles, or time-ordered events. Floating-point reductions also require attention to rounding and evaluation order; exact algebraic laws cannot be imported silently.

Equal outputs are weaker than equal cost or equal traces. A repeated-addition program may compute the same product after swapping arguments while taking radically different time. Kavi's revised connector addresses this particular issue through a supplied rule. The next step is learning when such a rule is valid and useful.

Define observational equivalence on a finite bank D and semantic equivalence on a specified domain Omega:

$$p\sim_D q\iff\forall x\in D,\;p(x)=q(x),\qquad p\equiv_\Omega q\iff\forall x\in\Omega,\;p(x)=q(x).$$

The first does not imply the second. The programs x and x squared agree at zero and one, then differ at two. More generally, for any finite set Q:

$$f(x)=x+1,\qquad g(x)=x+1+\prod_{a\in Q}(x-a).$$

They agree throughout Q and can differ elsewhere. A finite probe signature is a useful index for possible sharing, not a proof. A declared hypothesis class can change the conclusion: two polynomials of degree at most d that agree at d+1 distinct points are identical, because their difference cannot have more roots than its degree unless it is zero.

Each equivalence record should therefore contain its domain, assumptions, evidence kind, interpreter version and resource semantics. Proof-backed identities, exhaustive finite-domain checks and sampled agreements should have different status. An e-graph does not manufacture soundness; its equalities are only as sound as the rules and assumptions inserted into it.

## 4 What quantum mechanics contributes

### 4.1 State, interference and measurement

For an n-qubit register, a pure state is a normalized complex vector with 2 to the n components:

$$|\psi\rangle=\sum_{j=0}^{2^n-1}\alpha_j|j\rangle,\qquad\sum_j|\alpha_j|^2=1.$$

A density matrix includes mixtures and satisfies the following conditions. A pure state is the special case shown on the right. [Q1](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/introduction)

$$\rho\succeq0,\quad\operatorname{Tr}\rho=1,\qquad\rho_{\rm pure}=|\psi\rangle\langle\psi|.$$

Closed-system evolution is unitary. General measurement uses positive operators that sum to the identity; its probabilities follow the trace rule, with each E positive semidefinite. These are constraints on a physical model, not optional software conventions. [Q2](https://learning.quantum.ibm.com/course/general-formulation-of-quantum-information/general-measurements)

$$U^\dagger U=I,\qquad \rho'=U\rho U^\dagger,\qquad p(y)=\operatorname{Tr}(E_y\rho),\quad\sum_yE_y=I.$$

The simplest useful interference example uses a Hadamard gate, a relative phase and another Hadamard gate. Direct multiplication gives:

$$H=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},\quad P_\phi=\begin{pmatrix}1&0\\0&e^{i\phi}\end{pmatrix},\quad |\langle0|HP_\phi H|0\rangle|^2=\cos^2(\phi/2).$$

Changing the phase from zero to pi changes this output probability from one to zero. A classical probability mixture with the same initial computational-basis probabilities lacks those off-diagonal coherences and gives a different result after H. This distinction is real; its usefulness for program discovery remains an experimental question.

### 4.2 Entanglement is more specific than correlation

Entanglement requires a specified tensor-product decomposition. A bipartite mixed state is separable if it can be expressed as:

$$\rho_{AB}=\sum_k p_k\rho_A^{(k)}\otimes\rho_B^{(k)},\qquad p_k\ge0,\quad\sum_kp_k=1.$$

Failure of such a decomposition defines entanglement. For a pure state, the Bell state has Schmidt rank two and cannot be factored into two local vectors:

$$|\Phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2.$$

An outer product of route activations or a correlation matrix alone is not evidence of entanglement. Calling a graph a quantum circuit does not establish the required subsystem structure or physical operations.

### 4.3 Readout is not access to every branch

The Holevo bound limits recoverable classical information from an ensemble of quantum states. With no preshared entanglement assistance and an n-qubit transmitted system:

$$I_{\rm accessible}\le\chi=S\!\left(\sum_xp_x\rho_x\right)-\sum_xp_xS(\rho_x)\le n.$$

Entropy uses base-two logarithms. This is an information-theoretic statement about that communication setting, not a statement that quantum computation has no advantage. It rules out reading all exponentially many amplitudes as a freely accessible answer table. [Q3](https://www.preskill.caltech.edu/ph219/chap10_6A_2022.pdf)

Likewise, an unknown state cannot generally be cloned. If a unitary cloned both states a and b, inner-product preservation would require their overlap s to satisfy s=s squared. This only permits the identical or orthogonal cases. Copying a classical description of a circuit is different from cloning its unknown quantum state. [Q4](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/quantum-circuits/limitations-on-quantum-information)

### 4.4 Three meanings of a quantum Kavi

| Version | Meaning | Required evidence |
| --- | --- | --- |
| Classical complex routing | Complex numbers and interference computed on a CPU or GPU | Better results than matched real and random controls |
| Physical quantum backend | Prepared registers, valid gates or channels, repeated measurement | End-to-end benefit after compilation, noise and readout |
| Unrestricted imaginary dynamics | Custom transformations unconstrained by quantum theory | An ordinary algorithm and its actual computational cost |

Software may define nonlinear updates or inspect every simulated amplitude. That is permissible as classical computation. It does not inherit a physical quantum speedup. No choice of metaphor removes the cost of finding which answer is right.

## 5 Making pathways physically admissible

### 5.1 Reversible computation

Many classical operations lose information. AND maps several inputs to the same output. Sorting forgets the original order. A unitary map must be invertible, so it cannot directly implement those many-to-one maps on the same register.

For a bounded classical function f, a reversible embedding preserves the input and XORs its output into a separate register:

$$U_f|x,y\rangle=|x,y\oplus f(x)\rangle.$$

Real construction usually requires workspace. A search oracle computes an acceptance bit, changes a phase conditioned on that bit, and reverses the computation to clear workspace. Skipping that uncomputation can leave branch information entangled with the work registers and spoil intended interference.

For canonical multiplication, retain an orientation bit along with the sorted pair. On inputs zero through seven, sorting alone produces 36 distinct pairs from 64 ordered inputs. Adding the bit `a > b` gives 64 distinct records. This proves injectivity on those inputs; a reversible implementation must also specify a bijection on its full register space, including unused encodings.

### 5.2 Loss and directed flow

An open quantum system is described by a completely positive, trace-preserving channel. A Kraus representation is:

$$\Phi(\rho)=\sum_rK_r\rho K_r^\dagger,\qquad\sum_rK_r^\dagger K_r=I.$$

This permits resets, noise and irreversible behavior through interaction with an environment. It is not equivalent to an arbitrary directed adjacency matrix. [Q5](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/quantum-channels/representations-of-channels)

For example, amplitude damping with a number gamma between zero and one uses:

$$K_0=\begin{pmatrix}1&0\\0&\sqrt{1-\gamma}\end{pmatrix},\qquad K_1=\begin{pmatrix}0&\sqrt\gamma\\0&0\end{pmatrix}.$$

An initial excited state becomes a mixture with populations gamma and one minus gamma. Population transfer is valid, but it loses information into the environment. Interference cannot be assumed to survive unchanged.

Postselection is another possible operation. Conditioning on an event of probability p requires approximately 1/p independent attempts per accepted sample. Renormalizing the successful branch in a simulator and omitting failures would hide that cost. A low-probability correct answer is not a reliable free answer.

## 6 XRF and LIBS: what the instruments actually do

### 6.1 X-ray fluorescence

XRF excites a sample and measures characteristic X-ray emission. Atomic transitions contribute lines whose photon energy is the difference between levels. Calibration connects the detected spectrum to composition estimates. Peak overlap, absorption, secondary excitation and sample geometry affect interpretation. EPA Method 6200 provides a concrete analytical protocol; its scope is not a universal specification for every modern handheld instrument. [S1](https://www.epa.gov/sites/default/files/2015-12/documents/6200.pdf)

$$E_\gamma=E_u-E_l=h\nu=hc/\lambda_{\rm vac}.$$

NIST's transition-energy database supplies reference atomic transition data. It does not, by itself, solve an instrument's concentration-inference problem. [S2](https://www.nist.gov/pml/x-ray-transition-energies-database)

For a homogeneous mixture with mass fractions w, a useful attenuation approximation is:

$$I(E,L)=I_0(E)e^{-\mu(E)L},\qquad\mu(E)=\rho_{\rm mass}\sum_jw_j(\mu/\rho_{\rm mass})_j(E).$$

The fractions sum to one. Attenuation coefficients have units of inverse length; mass attenuation coefficients have area per mass. This mixture rule has a defined approximation scope, including limitations near fine structure. [S3](https://pml.nist.gov/PhysRefData/XrayMassCoef/chap2.html)

The following is a simplified forward model for this design discussion, not a full implementation of EPA's method:

$$\Lambda_k=t\left[b_k+\sum_jw_js_{kj}e^{-\mu(E_0)L_{\rm in}-\mu(E_j)L_{\rm out}}\right],\qquad Y_k\sim\operatorname{Poisson}(\Lambda_k).$$

Here k indexes a detector bin; t is exposure time; b is a background count rate; and s is a calibrated response rate per unit mass fraction. The representative incident and emission paths approximate a depth-dependent integral. Real instruments must handle energy distributions, line shapes and further interactions. Independent Poisson counting assumes a stable process without substantial pileup or dead-time distortion.

A possible constrained inverse estimate minimizes the negative count log-likelihood, dropping constants independent of composition:

$$\widehat w=\arg\min_{w\ge0,\;\mathbf1^Tw=1}\left\{\sum_k[\Lambda_k(w)-Y_k\log\Lambda_k(w)]+\alpha R(w)\right\}.$$

The regularizer encodes an explicitly chosen preference. If several compositions predict nearly the same spectrum, optimization alone cannot recover a unique answer. More information or better experimental conditions are needed.

### 6.2 Laser-induced breakdown spectroscopy

LIBS uses a focused laser pulse to create a plasma from sampled material and measures emitted light. NIST's LIBS model explicitly makes local thermodynamic equilibrium and optically thin plasma assumptions. Its calculated line pattern depends on temperature, electron density and available atomic data. [S4](https://pml.nist.gov/PhysRefData/ASD/Html/libshelp.html)

For element j, charge state q and excited level u, a corresponding population model is:

$$n_{j,q,u}=n_{j,q}\frac{g_u}{Z_{j,q}(T)}e^{-E_u/(k_BT)},\qquad I_{ul}=K n_{j,q,u}A_{ul}h\nu_{ul}.$$

T is temperature in kelvin; E is measured relative to the relevant ion's ground state; Z is its partition function; g is level degeneracy; A is the spontaneous transition rate. K collects the sampled volume, collection geometry and response appropriate to this simplified intensity expression. NIST provides atomic line and transition data. [S5](https://pml.nist.gov/PhysRefData/ASD/Html/lineshelp.html)

The ionization balance in this model follows the Saha relation:

$$\frac{n_{j,q+1}n_e}{n_{j,q}}=2\frac{Z_{j,q+1}(T)}{Z_{j,q}(T)}\left(\frac{2\pi m_ek_BT}{h^2}\right)^{3/2}e^{-\chi_{j,q}/(k_BT)}.$$

Plasma conditions, ablation yield, self-absorption and time-dependent gradients can break this simplified relationship between bulk material and observed light. NASA's ChemCam data description records background and instrument-response processing and calibration using standards. It illustrates why the signal is not its own interpretation. [S6](https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=MSL-M-CHEMCAM-LIBS-4%2F5-RDR-V1.0)

### 6.3 What transfers to Kavi

| Instrument feature | Computational counterpart | Important limit |
| --- | --- | --- |
| Controlled excitation | Chosen input or intervention | A probe requires an interpretable response |
| Spectrum | Output, trace, failure and cost signature | Similar signatures can hide different computations |
| Reference standards | Known programs and authored diagnostic tasks | Calibration data are external work |
| Inverse model | Candidate identification or model selection | Ambiguity remains when responses coincide |
| Additional measurement mode | Another probe family or formal analysis | More observations can still be insufficient |

Neither analyzer is a quantum computer. Quantum physics explains atomic emission, while ordinary signal processing and calibrated inference extract useful information. Elemental composition also need not uniquely identify a molecule, crystal phase or material history. NASA separates ChemCam's chemical measurements from CheMin's mineral analysis, illustrating this distinction. [S7](https://science.nasa.gov/mission/msl-curiosity/science-instruments/)

## 7 A concrete probing and consolidation mechanism

For candidate programs c and a set of probes q, define a response signature:

$$S_{ij}=\phi\big(F_{c_j}(q_i)\big).$$

The feature extractor phi records the output value or structured failure, termination status, relevant trace events and a cost measure. These fields should remain separate: two mathematically equivalent programs may be desirable alternatives because one is faster.

First cluster candidates by cheap signatures. Then search actively for an input that separates candidates in the same cluster. Only after that stage should the system attempt a proof, a complete finite-domain check, or a guarded merge whose limited evidence is recorded. Failure to find a counterexample within budget is not proof.

If there is a justified posterior over candidate identities, a proposed probe objective is information gain per positive probe cost:

$$q^*=\arg\max_q\frac{H(C\mid D)-\mathbb E_{y\mid D,q}[H(C\mid D,q,y)]}{\operatorname{cost}(q)}.$$

This is classical experimental design. Without calibrated probabilities, use a simpler declared disagreement heuristic, such as splitting the candidate set into balanced output groups. Do not label a heuristic score a probability of truth.

For continuously parameterized responses, let z equal F(theta;q) plus noise. Local identifiability can be examined using the sensitivity matrix:

$$J_{ij}=\frac{\partial F_i}{\partial\theta_j}.$$

Full column rank supports regular local identification under smoothness assumptions; it does not establish global uniqueness. Use independent coordinates when parameters obey constraints such as a composition simplex. Poor conditioning means small measurement errors can imply large parameter uncertainty even when rank is full.

### 7.1 Correction with dependency tracking

Store dependencies between definitions, callers and evidence. A correction proposes a replacement or a guarded specialization. Re-run affected tasks and a retained bank; compare storage and execution cost; then accept or reject atomically. Keep the previous library available until the candidate passes. A failed correction should add a diagnostic counterexample, not rewrite the meaning of success.

The word “wrong” should denote a failed contract with a witness. “Doubt” should denote unresolved alternatives or empirically calibrated uncertainty. “Confidence” should be evaluated against actual outcomes. Quantum amplitudes do not supply those meanings automatically.

### 7.2 From literature to reusable operations

Teaching from scientific and philosophical works should separate text form, attributed claims and executable consequences. An argument parser might identify a premise and conclusion; a mathematical interpreter might compile a stated recurrence; a verifier might test a consequence. None follows automatically from storing sentences.

Start with authored examples for quantifiers, negation, relations, variable binding and entailment. Then admit short original-source passages with edition, language, translator if applicable, and provenance. Hold out new wording and new combinations. A philosophical proposition may be disputed or contextual, so its annotation must preserve attribution instead of installing it as an unconditional fact.

Cross-domain sharing requires a shared typed intermediate representation. Repeated accumulation could support arithmetic, inventory accounting and a discretized physical quantity. The transfer comes from matching contracts and units, not from assuming every sentence is secretly an addition circuit. Natural language ambiguity, reference, context and pragmatic intent remain separate modeling problems.

## 8 Classical complex routing with stable dynamics

Let psi be a vector of M computational modes. A proposed continuous routing model uses a Hermitian coupling H and positive semidefinite damping Gamma:

$$\dot\psi=(-\Gamma-iH)\psi,\qquad H=H^\dagger,\quad\Gamma\succeq0.$$

With time measured in consistent computational units, differentiation gives:

$$\frac{d}{dt}\|\psi\|^2=-2\psi^\dagger\Gamma\psi\le0.$$

This proves non-increasing signal norm for the stated unforced linear system. It does not prove task correctness, useful learning, convergence to an answer, or stability after arbitrary nonlinear routing changes. External input adds a forcing term and changes the balance.

### 8.1 Numerical integration matters

Explicit Euler applied to undamped evolution can increase norm. For an eigenvalue h of H, the multiplier has squared magnitude one plus step-size squared times h squared. A Cayley update avoids that error for Hermitian H:

$$U_{\Delta t}=\left(I+i\frac{\Delta t}{2}H\right)^{-1}\left(I-i\frac{\Delta t}{2}H\right),\qquad U_{\Delta t}^\dagger U_{\Delta t}=I.$$

This follows by diagonalizing H: each real eigenvalue produces a quotient whose numerator and denominator have equal magnitude. Solving the linear system costs work. It should not be implemented as a free abstract inverse.

An optional split update with damping is contractive:

$$\psi_{t+1}=D\,U_{\Delta t}\,D\psi_t,\qquad D=e^{-\Delta t\Gamma/2},\quad\Delta t\ge0.$$

Each D has operator norm at most one and U has norm one. This is a classical numerical proposal; normalizing its output into measurement probabilities does not by itself make it a complete physical quantum channel.

### 8.2 Types and direction cannot be hidden in the matrix

A directed connection mask generally makes a matrix non-Hermitian. Symmetrizing it reintroduces reverse couplings, which may violate intended causal or type constraints. A Hermitian embedding exists:

$$H_A=\begin{pmatrix}0&A\\A^\dagger&0\end{pmatrix}.$$

It introduces a larger space and both coupling directions. It is not a proof that arbitrary one-way program execution has been implemented correctly. Restrict interference to compatible proposal states, and let a typed executor carry out the chosen program. If true dissipative direction is needed on hardware, specify the channel and its environment explicitly.

Learned phases, damping values and couplings are numerical parameters. They count as saved state even if they are called connections. A purely discrete variant is possible, but then the learned information resides in graph choices, operator choices and control rules. “Weight-free” should never mean “information-free.”

## 9 Candidate quantum backends

### 9.1 Amplitude amplification over bounded candidates

Suppose N candidate programs are encoded, with 0 < M <= N satisfying a specified finite verifier, and a reversible oracle marks them. For a uniform initial state, define theta and the success probability after k ideal Grover iterations:

$$\theta=\arcsin\sqrt{M/N},\qquad P_k=\sin^2((2k+1)\theta).$$

Amplitude amplification gives a quadratic improvement in oracle calls for this search model. Unknown success rates require an appropriate schedule rather than arbitrary repeated iterations; over-rotation can reduce success. It does not establish an advantage over a classical searcher that exploits structure. [Q6](https://arxiv.org/pdf/quant-ph/0005055)

For Kavi, the oracle must decode a valid typed program, execute it reversibly within a fixed time and integer-width bound, compare its outputs against the teaching cases, mark acceptance, and uncompute workspace. Invalid programs, overflows and timeouts must have defined outcomes. An oracle that somehow knows which unseen answers are correct merely relocates the unsolved learning problem.

A useful accounting expression is:

$$T_Q=T_{\rm setup}+k(T_O+T_R)+T_{\rm measure}+T_{\rm verify},\qquad k=O(\sqrt{N/M}).$$

The comparator must include state preparation, reversible oracle cost, reflection cost, readout and fresh classical verification. Repeated shots and unsuccessful attempts add to this budget. A bound on calls to an oracle is not a bound on device time.

Generalization still requires withheld tasks or stronger proof. Marking programs that fit examples amplifies example-fitting programs, including spurious ones. Library priors and counterexamples may shrink the candidate set more effectively than unstructured amplification.

### 9.2 Variational circuits

Another proposal encodes candidate costs in a diagonal Hamiltonian and alternates cost and mixing unitaries, following the QAOA pattern. [Q7](https://arxiv.org/pdf/1411.4028)

$$|\psi(\vec\gamma,\vec\beta)\rangle=\prod_{r=p}^{1}\left[e^{-i\beta_rH_M}e^{-i\gamma_rH_C}\right]|+\rangle^{\otimes n},\qquad H_C|z\rangle=C(z)|z\rangle.$$

The product convention applies the r=1 layer first. Costs could include example errors, program length and invalid encodings. But constructing the cost unitary can itself require reversible program execution; a simple mathematical diagonal matrix is not automatically an inexpensive gate sequence.

Angles are learned numerical parameters. Training consumes circuit evaluations and classical optimization. Certain broad random circuit families exhibit exponentially suppressed gradients; this is a design risk rather than a theorem that every ansatz fails. [Q8](https://arxiv.org/abs/1803.11173) A variational circuit must therefore earn its place against strong classical optimizers under the same task and resource limits.

### 9.3 Reservoir dynamics

A quantum reservoir takes sequential input into an evolving state and trains a readout. A generic formulation is:

$$\rho_{t+1}=\Phi_{u_t}(\rho_t),\qquad z_{t,j}=\operatorname{Tr}(O_j\rho_t),\qquad\widehat y_t=Wz_t+b.$$

This is closer to the changing-flow aspect of Kavi's initial intuition. Fujii and Nakajima study this mechanism for temporal learning. It retains dynamical memory and trains numerical readout weights; it does not automatically discover reusable symbolic definitions. Measurements, repeated preparations and observable selection determine the available features. [Q9](https://arxiv.org/html/1602.08159)

A reservoir could be tested as a proposal mechanism for sequential tasks. It should not replace the verified library merely because its internal state is large. The required comparison is matched temporal prediction or proposal quality, not an arbitrary conversion from qubits to neural parameters.

### 9.4 Matrix transformations and data access

Quantum singular value transformation provides algorithms built around access to a unitary that encodes a matrix block. An ideal block encoding with positive scale alpha obeys:

$$(\langle0^a|\otimes I)U(|0^a\rangle\otimes I)=A/\alpha,\qquad\alpha\ge\|A\|.$$

The framework supports polynomial transformations under specified access and approximation conditions. It does not give free construction of U from an arbitrary classical table. [Q10](https://arxiv.org/pdf/1806.01838) For a Kavi response matrix S, first charge for evaluating its entries and constructing that access. Recovering every transformed entry would also incur output cost. No matrix speedup is claimed here.

Quantum learning advantages can be meaningful in settings with access to quantum experimental data. Huang and colleagues study such advantages under specified learning protocols. That evidence cannot simply be transferred to ingesting classical books. [Q11](https://arxiv.org/abs/2112.00778) Their separate work on the role of classical training data reinforces the need for strong data-aware classical comparisons. [Q12](https://arxiv.org/abs/2011.01938)

## 10 Proposed architecture and implementation order

The following components are new work to build and evaluate. They are not a description of the current execution path.

| Component | Stored information | Responsibility |
| --- | --- | --- |
| Typed library | Definitions, signatures, dependencies, version | Executable persistent knowledge |
| Equivalence store | Rules, assumptions, domains, proof or test evidence | Distinguish proven rewrites from observed agreement |
| Probe manager | Diagnostic inputs, response signatures, costs | Separate candidate meanings efficiently |
| Abstraction extractor | Candidate parameterized subprograms | Search shared structure across equivalent forms |
| Proposal backend | Search state; optional learned scores or phases | Suggest programs and repairs |
| Verifier | Independent task contracts and retained banks | Decide acceptance under declared scope |
| Consolidator | Accepted rewrites and dependency updates | Promote changes atomically and preserve rollback |
| Resource recorder | State bytes, workspace, time, evaluations | Make comparisons reproducible |

### 10.1 Phase A: a strong classical baseline

First add an explicit equivalence-evidence record and typed representation shared by arithmetic and a small authored relational language. Keep input order unless a contract permits canonicalization. Add candidate abstraction extraction with repeated-variable preservation. Charge definition and call costs using the actual serializer.

Next add counterexample search for proposed merges. Exhaust small finite domains when practical; otherwise record the sampled evidence and unresolved scope. Introduce guarded specializations rather than globally merging programs on weak evidence. Run dependency-aware retention before accepting changes.

Finally evaluate whether abstractions discovered in one task family improve acquisition in another with compatible types. Compare against the same library with extraction disabled, ordinary common-subexpression extraction, and an equivalence-aware baseline. Use the original DreamCoder and Babble methods as relevant references, adapting interfaces transparently rather than claiming reproduction without matching their protocols.

### 10.2 Phase B: an interference proposal experiment

Freeze the executor, task banks and consolidation rules. Substitute a small complex-valued proposal module. Compare it with real-valued, zero-phase and fixed-random-phase versions. Match saved scalar count or report its difference, arithmetic precision, candidate-evaluation budget and peak memory. If the complex module offers no repeatable benefit, remove it without changing the verified library interface.

This stage can establish a useful classical mechanism. It cannot establish physical quantum advantage. A simulator that inspects all amplitudes must charge for those operations and cannot pretend that a physical measurement returned the full vector.

### 10.3 Phase C: a bounded physical search experiment

Choose a finite program grammar and fixed-width data, then build and count a reversible verifier. Specify candidate preparation, gate set, workspace, uncomputation, readout, expected repetitions and noise model. Compare total work with the strongest available classical search on the same tasks before committing to hardware execution.

The acceptance criterion is a measured end-to-end benefit or a carefully scoped resource estimate that justifies a later experiment. A smaller number of oracle calls alone is insufficient. Hardware success at a toy task would still not establish language competence or a scalable learner.

## 11 Size, memory and cost

The current 2,272-byte arithmetic library is compact because it describes a narrow set of computations and delegates interpretation to supplied software. Its size is not comparable to a general language model's parameter file without matching capability, external dependencies and runtime costs. Adding a quantum register does not change that requirement.

For dense classical simulation with 16-byte complex numbers, state-vector and density-matrix storage are:

$$B_{\rm vector}=16\cdot2^n,\qquad B_{\rm density}=16\cdot4^n.$$

| Qubits represented | Dense state vector | Dense density matrix |
| --- | --- | --- |
| 12 | 64 KiB | 256 MiB |
| 16 | 1 MiB | 64 GiB |
| 20 | 16 MiB | 16 TiB |
| 24 | 256 MiB | 4 PiB |
| 28 | 4 GiB | 1 EiB |
| 30 | 16 GiB | 16 EiB |

These are array payloads only, using binary units. Workspace, gates, observables and the host process add memory. Specialized representations can exploit structure, but the dense figures must not be replaced by an assumed compression without demonstrating it for the actual circuits. An M-mode classical wave vector needs M complex entries; it is not automatically an M-qubit state.

Physical qubits cannot be equated with these byte counts. A hardware budget must distinguish logical registers, workspace, error correction, control systems and repeated execution. No universal ratio converts physical qubits into reliable logical qubits or intelligence.

### 11.1 Sampling cost

For S independent Bernoulli measurements, Hoeffding's bound gives the following sufficient number of shots to estimate one probability within epsilon with failure probability at most delta:

$$\Pr(|\widehat p-p|\ge\epsilon)\le2e^{-2S\epsilon^2},\qquad S\ge\frac{\ln(2/\delta)}{2\epsilon^2}.$$

At epsilon 0.01 and delta 0.05, round up to 18,445 shots. This is a conservative sufficient bound, not a universal minimum. Estimating m quantities with a union-bound guarantee replaces delta by delta/m. Correlated noise and systematic bias require separate treatment; more shots do not automatically remove bias.

For every experiment, report saved library bytes, learned numeric state, source-derived memory, verifier data, peak workspace, candidate executions, CPU time, wall time and hardware shots when relevant. Teacher work and calibration costs should be visible. A storage claim that excludes most of the learned information is not a meaningful compression result.

## 12 Reproducible algebra checks

`scripts/check_quantum_proposal.py` uses only the Python standard library. It operates on vectors and matrices of dimension at most four. It performs no learning, model update, external download or physical experiment. The result file is `experiments/2026-09-07-quantum-math-checks.json`.

Run the checks from the repository root:

```text
python -B scripts/check_quantum_proposal.py --output results.json
```

All nine check groups passed under Python 3.13.5 on 7 September 2026. Approximate values below are rounded for reading.

| Check | Result | What it establishes |
| --- | --- | --- |
| Phase interference | Output probabilities 1, 0.5, 0 | Hadamard-phase-Hadamard identity |
| Coherence versus mixture | Probability 1 versus 0.5 after H | Same initial basis probabilities can hide different coherence |
| Four-candidate Grover step | Marked probability 0.25 before diffusion; 1 after | Marking alone does not concentrate probability |
| Directed matrix update | Output norm squared 2 from normalized input | Arbitrary directed update need not be unitary |
| Cayley versus Euler | After 100 steps: 1.000000000000017 versus 2.704813829421526 | Norm preservation versus Euler growth in the stated example |
| Amplitude damping | Populations 0.3 and 0.7; completeness verified | Valid example of directed population loss |
| Finite signature collision | x and x squared agree at 0,1; differ at 2 | Finite agreement does not imply equivalence |
| Sorting with orientation | 36 records without bit; 64 with bit | Information needed for reversible canonicalization |
| Sampling bound | 18,445 shots | Arithmetic of the stated sufficient bound |

These tests are consistency checks on illustrative mathematics. They do not validate an entire architecture, prove speedup, or compare trained models. The stability proofs in Section 8 and the finite-polynomial argument in Section 3 establish their own precisely stated results independently of floating-point checks.

## 13 Evaluation and decision rules

Use three separate question sets: acquisition tasks with explicit supervision, withheld compositional tasks, and a retained bank frozen before consolidation. Separate new arguments in familiar syntax from genuinely new structure. Include unsupported inputs so refusal or ambiguity handling is measured rather than silently excluded.

| Experiment | Primary measure | Essential control |
| --- | --- | --- |
| Learned canonical connectors | Correctness and cost across ordered/swapped inputs | Noncommutative negative cases |
| Abstraction extraction | Total saved bits at equal held-out success | No extraction; syntactic extraction; equivalent-form extraction |
| Active probes | Candidate executions until a valid distinction or acceptance | Random and fixed diagnostic probes |
| Correction | Retention and affected-dependency repair cost | Whole-library re-search with same budget |
| Cross-domain reuse | Acquisition cost after learning a compatible source domain | No transferred library; incompatible-domain transfer |
| Complex proposals | Success per total compute and stored state | Real, zero-phase and fixed-random-phase variants |
| Quantum search | End-to-end work and verified success | Strong structured classical search; oracle cost included |

Fix task generators, budgets, serializer and selection rules before running comparisons. Use multiple independent seeds where randomness exists and publish the per-seed results, not only the best run. If tasks or seeds are few, report uncertainty and raw counts rather than claiming a general trend.

Useful compression means fewer total persistent bits at comparable held-out success and acceptable execution cost. Useful transfer means that the reused library lowers acquisition cost on a new compatible family without importing its answers. Useful quantum computation means that a defined quantum access model and real resource accounting improve a task; calling an internal state quantum is not an outcome measure.

Stop or revise a mechanism when it saves storage only by reducing competence, improves apparent success through evaluation leakage, repeatedly corrupts retained skills, or costs more than a simpler alternative without a compensating benefit. Keep failed trials and rejected abstractions in the evidence record.

## 14 Assessment

Kavi's strongest near-term direction is an inspectable learner of reusable typed programs with efficient correction. The present work gives a narrow foundation for that direction, not evidence that the larger ambition is already achieved. DreamCoder and Babble set a substantial baseline for library discovery; Kavi should build on and test against that work.

The spectroscopy connection yields a concrete engineering proposal: choose informative probes, calibrate interpretation, preserve uncertainty and distinguish candidates before merging them. This can be implemented and measured on the current device without speculative hardware assumptions.

Interference is worth testing as an optional search mechanism. Physical quantum search becomes relevant only when a useful reversible verifier can be constructed cheaply enough. Quantum reservoirs and matrix algorithms offer other conditional possibilities, but each introduces its own representation, measurement and learning costs.

The ambitious hypothesis is that accumulated abstractions make later learning cheaper while preserving prior competence. There is no theorem here that storage will stop growing, that reading great works creates the right abstractions, or that quantum mechanics supplies understanding. The path to a stronger system is to make those hypotheses executable and measure where they hold.

## 15 References and inspection scope

Research sources were accessed on 7 September 2026. References below identify original papers, author-hosted papers or institutional technical documentation. Equations labeled as proposed models and the worked counterexamples are this study's constructions. No numerical advantage from another paper is presented as a Kavi result.

**[D1]** Ellis et al. (2021). [DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf). PLDI. Inspected method, objectives, refactoring and evaluation scope; author repository: [ellisk42/ec](https://github.com/ellisk42/ec).

**[B1]** Cao et al. (2023; preprint 2022). [babble: Learning Better Abstractions with E-Graphs and Anti-Unification](https://arxiv.org/html/2212.04596). POPL. Inspected abstraction formulation, e-graph methods, evaluation and limitations; author repository: [dcao/babble](https://github.com/dcao/babble).

**[Q1]** IBM Quantum Learning. [Density matrices: introduction](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/introduction). Technical definitions of pure and mixed states.

**[Q2]** IBM Quantum Learning. [General measurements](https://learning.quantum.ibm.com/course/general-formulation-of-quantum-information/general-measurements). Measurement operators and outcome probabilities.

**[Q3]** Preskill (2022 lecture version). [Quantum Shannon Theory](https://www.preskill.caltech.edu/ph219/chap10_6A_2022.pdf), Section 10.6. Accessible information and Holevo bound; inspected the stated communication setting and derivation.

**[Q4]** IBM Quantum Learning. [Limitations on quantum information](https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/quantum-circuits/limitations-on-quantum-information). No-cloning argument.

**[Q5]** IBM Quantum Learning. [Channel representations](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/quantum-channels/representations-of-channels). Kraus completeness and channel examples.

**[Q6]** Brassard, Hoyer, Mosca and Tapp (2000 preprint). [Quantum Amplitude Amplification and Estimation](https://arxiv.org/pdf/quant-ph/0005055). Inspected success-amplitude formulation and oracle assumptions.

**[Q7]** Farhi, Goldstone and Gutmann (2014). [A Quantum Approximate Optimization Algorithm](https://arxiv.org/pdf/1411.4028). Inspected cost and mixing unitary construction.

**[Q8]** McClean et al. (2018). [Barren plateaus in quantum neural network training landscapes](https://arxiv.org/abs/1803.11173). Nature Communications 9, 4812. Abstract-level scope used for the random-circuit gradient limitation; no new quantitative extrapolation.

**[Q9]** Fujii and Nakajima (2017; preprint 2016). [Harnessing disordered-ensemble quantum dynamics for machine learning](https://arxiv.org/html/1602.08159). Physical Review Applied 8, 024030. Inspected reservoir dynamics, input injection and trained readout. Use the paper's publication record rather than the HTML conversion's displayed build date.

**[Q10]** Gilyen, Su, Low and Wiebe (2019; preprint 2018). [Quantum singular value transformation and beyond](https://arxiv.org/pdf/1806.01838). STOC. Framework and matrix-access setting; no Kavi implementation or complexity reduction claimed.

**[Q11]** Huang et al. (2022). [Quantum advantage in learning from experiments](https://arxiv.org/abs/2112.00778). Science. Abstract-level statement of quantum experimental learning scope; no reproduction or hardware-size extrapolation.

**[Q12]** Huang et al. (2021). [Power of data in quantum machine learning](https://arxiv.org/abs/2011.01938). Nature Communications 12, 2631. Abstract-level conclusions on data-dependent classical comparisons.

**[S1]** US EPA (2007). [Method 6200: Field Portable X-Ray Fluorescence Spectrometry](https://www.epa.gov/sites/default/files/2015-12/documents/6200.pdf). Analytical method and interference discussion.

**[S2]** NIST. [X-Ray Transition Energies Database](https://www.nist.gov/pml/x-ray-transition-energies-database). Reference transition energies.

**[S3]** Hubbell and Seltzer, NIST. [X-Ray Mass Attenuation Coefficients, Section 2](https://pml.nist.gov/PhysRefData/XrayMassCoef/chap2.html). Exponential attenuation, mixture approximation and its scope.

**[S4]** NIST Atomic Spectra Database. [LIBS interface help](https://pml.nist.gov/PhysRefData/ASD/Html/libshelp.html). Plasma assumptions and Saha-Boltzmann model.

**[S5]** NIST Atomic Spectra Database. [Spectral lines help](https://pml.nist.gov/PhysRefData/ASD/Html/lineshelp.html). Atomic transition and level quantities.

**[S6]** NASA Planetary Data System. [ChemCam LIBS derived data](https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=MSL-M-CHEMCAM-LIBS-4%2F5-RDR-V1.0). Instrument response, calibration and processing description. The separately indexed Wiens calibration paper was not used as if its full text had been inspected.

**[S7]** NASA. [Curiosity science instruments](https://science.nasa.gov/mission/msl-curiosity/science-instruments/). Chemical and mineralogical instrument roles.
