# Adaptive dataflow circuits

Author: [Arnav123-s](https://github.com/Arnav123-s)

Revision: 5 September 2026

Status: proposed architecture. This note clarifies the intended learned representation beyond the program-library design in the [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md). It introduces no implementation or experimental result.

## 1. The learned object

Kavi's intended memory is the configuration of a circuit that processes information and can change its own configuration. Connections, junction operations, branch conditions and reusable subgraphs determine where an input goes and what computation occurs. Learning changes these structures. Individual signals may disappear after a response while the acquired configuration remains.

The circuit may also rearrange temporary connections during a computation. That allows an input to select or construct an appropriate execution route without permanently changing every later response. Lasting adaptation occurs when a structural change survives the current interaction. The distinction is between temporary activity and retained organization; both can change over time.

This design need not store an independently trained real-valued multiplier on each connection. A connection can instead identify a destination and a junction can select a Boolean operation, a comparison or a control action. These choices still occupy memory and are parameters in the broad mathematical sense. Moving learned information into topology changes the representation and the learning problem; it does not eliminate stored information.

Stateless junctions are compatible with this design. A completely stateless learner is not: if every consequence of a lesson disappears, the same input cannot reliably receive a different answer because of that lesson. The retained circuit is the memory. A temporary register used for carrying a bit or recording intermediate results is working memory, even if reset between requests.

## 2. Routing must perform computation

A wire carries a value. A useful junction must be able to transform, combine, test or store values as well as forward them. Conditional routing can implement a logical operation when the condition and selected outputs have defined semantics. Unconditional routing among fixed answer terminals provides a lookup mechanism, whose generalization is limited by what those terminals and routing conditions already represent.

For example, a reusable addition circuit must respond to operand bits and carry state. It cannot obtain arbitrary sums merely by selecting among a small list of remembered answers. A small bit-serial circuit can reuse the same Boolean operations for each successive bit, maintaining temporary carry state. Its structural size can remain fixed while its running time grows with operand length. The learner must discover the relevant arrangement if acquisition of addition is the experiment's claim.

Different modalities can share a storage format and an execution substrate. Their interpretation still needs an encoding and a context: a byte representing a digit, a pixel intensity and part of an audio sample does not have the same operational meaning. This interface must be specified rather than delegated to the word "energy."

## 3. A mathematical model

Represent the persistent circuit as a directed graph or port graph with node operations, connections, branch conditions and explicit constants. Ports identify the inputs and outputs of each operation. Shared subgraphs permit reuse. A graph rewrite replaces a matched piece of this structure with another piece under a stated condition.

Let `G_n` denote the retained configuration before interaction `n`, `s_t` the temporary execution state, `x` the encoded input, and `f_n` the feedback for that interaction. One possible decomposition, with temporary state initialized for each request, is:

$$
s_{t+1}=F(\widetilde G_{n,t},s_t,x),\qquad
\widetilde G_{n,t+1}=R(\widetilde G_{n,t},s_t,x),\qquad
\widetilde G_{n,0}=G_n.
$$

`F` executes operations. `R` changes the temporary graph during execution. A bounded run returns a candidate result, its evidence status and an execution trace. A lasting learning update has the form:

$$
G_{n+1}=U(G_n,\operatorname{trace}_n,f_n).
$$

These equations define interfaces, not a solved learning algorithm. `U` must determine which changes to propose, how to evaluate them and which to retain. The execution trace identifies what participated in a response; it does not by itself identify the cause of an error or the correct repair. Several different failures can produce the same wrong answer.

The first implementation can use an engineered update rule. A later experiment could represent parts of that rule as editable graphs and test whether experience improves the learning process itself. The two claims must be evaluated separately: learning a task circuit and learning how to modify task circuits. Graph instructions remain a bounded executable representation, rather than permission to alter arbitrary host source code.

A useful structural search criterion balances error, total encoded size, execution cost and edit size. Restrict it with previously verified behavioral obligations. Size includes node choices, connection addresses, constants, shared libraries, retained evidence and any learned search policy. Candidate evaluations, unsuccessful proposals and verification work belong in the learning-cost report.

## 4. Correction, doubt and confirmation

An answer and the evidence supporting it are different values. The circuit can carry a structured result such as `(candidate, status, context, evidence_reference)`. The status can itself control routing through shared rejection, investigation or response operations. This does not require a separate model for every status.

| Interaction | Warranted change | What remains unresolved |
| --- | --- | --- |
| `2 + 2` produces `1` | Record the candidate and the route that produced it | Correctness is unknown without relevant evidence |
| Feedback states that `1` is wrong | Retain a context-specific rejection of this answer | Negative feedback does not identify `4` |
| Feedback suggests `4`, with uncertainty | Store `4` as a provisional candidate | The suggestion is not a proof |
| An accepted teaching signal confirms this case | Prefer `4` for this particular input and meaning of addition | Confirmation of one case does not establish a general algorithm |
| A general addition procedure passes a proof under specified assumptions | Reuse the procedure throughout the proved domain | Different representations or changed dependencies may require verification |

The rejection concerns `2 + 2 -> 1`. It must not disable every computation producing `1`, since `2 - 1 -> 1` is valid. A patch needs a scope that distinguishes those cases. Likewise, certainty supplied by a speaker is an assertion from that source. The learner may accept it as a training label, but that is a different evidence class from a mechanically checked theorem.

Once a computation has adequate evidence, the circuit can invoke its verified route directly. It need not recompute the complete history of failed candidates each time. The retained evidence should name the graph version, input domain and dependencies that justify the shortcut. A relevant change invalidates that justification; unrelated changes need not invalidate it.

The initial experiment should provide feedback through explicit control fields such as `reject`, `suggest` and `confirm`. Understanding the English words "wrong" and "perhaps" is a separate learning problem. Those words can later be grounded in the same control operations without presupposing language understanding at initialization.

Repeated exposure can establish associations or useful compression. Frequency alone cannot promote a statement to mathematical truth. A shared confidence circuit also needs an interpretation and evaluation: confidence should track predictive reliability on new cases, rather than merely count visits to a path.

## 5. Acquiring a procedure

The examples `1 + 1 = 2` and `1 + 2 = 3` are compatible with ordinary addition, a small answer table and many other functions. Generalization requires a bias toward particular circuit families, additional evidence or an independently supplied specification. No representation removes that ambiguity.

A useful learning sequence starts with small cases, includes carry-producing examples, and then tests operand combinations and lengths withheld from learning. Inspect the acquired graph to establish whether the same mechanism is reused. Check that the input encoder, teacher or verifier has not supplied the target computation to the learner through an unintended interface.

There are two distinct arithmetic experiments. Providing an `ADD` primitive and learning where to invoke it tests composition. Providing lower-level gates and learning their arrangement tests acquisition of the arithmetic mechanism. Both are legitimate, but only the second addresses the strongest interpretation of this proposal.

Proved facts and acquired subcircuits can be reused as components. Their contracts must state their domain. For example, addition on arbitrary-length bit strings and fixed-width machine addition have different overflow behavior. Reuse is valid when the calling context satisfies the component's assumptions.

## 6. Repair without losing earlier behavior

A new branch can repair one context while preserving the route used elsewhere. Shared structure makes this economical when the failing context is distinguishable. There is no general guarantee that a repair consists of one small jump: the existing representation may lack the required distinction, or several shared computations may need revision.

For a finite protected domain, exhaustive comparison can establish that a candidate retains every required old result. For an unbounded domain, tests establish only sampled behavior unless a proof applies. Counterexamples should refine the repair search. Equivalent rewrites can shorten a circuit while preserving its behavior, including its mistakes; repairing those mistakes requires a separate behavioral change.

The learner should record which earlier correct cases became wrong after each accepted update. Counting only the total number of correct answers hides regressions. Protection should concern required behavior, rather than prohibit all changes to the internal representation. A better shared circuit may replace several older circuits if its obligations are checked.

Versioned candidate configurations and a reversible acceptance step make this research inspectable. They are implementation mechanisms for controlled learning; they are not evidence that forgetting has been solved.

## 7. Interpreting the quantum analogy

The useful part of the Schrödinger analogy is keeping several possible configurations unresolved until evidence favors one. That can be represented by alternative graphs, a packed graph of shared alternatives or a distribution over candidate rewrites. Candidate uncertainty is an ordinary computational object; it does not require physical quantum hardware.

A simulated circuit can use rules unlike those of a physical electrical circuit. It can introduce nonlocal connections, complex amplitudes or interference-like operations if their execution semantics are defined. The simulator still pays for the represented state, precision, executed operations and selection of an answer. Declaring all configurations to coexist does not provide a procedure that identifies the correct one.

If a quantum-style mechanism is proposed later, specify its state representation, allowed transformations, readout and computational cost, then compare it with a classical mechanism under the same budget. The current architectural claim depends on adaptive structure and reusable computation. It has no demonstrated quantum speed advantage.

## 8. Closest research relatives

The closest mathematical description of this clarification is a **dynamical system on computational graphs with feedback-dependent graph rewriting**. This is a modeling judgment about the proposed mechanism. Typed program synthesis remains useful for bounded acquisition and verification; a program library describes only part of the intended adaptive medium.

| Research | Connection to the proposal | Important boundary |
| --- | --- | --- |
| [Harding, Miller and Banzhaf, Self-Modifying Cartesian Genetic Programming, 2007](https://www.cs.mun.ca/~banzhaf/papers/smcgp.pdf) | Executable graphs contain operations that modify their own structure | Evolution supplies the search; self-modification alone does not establish learning from experience |
| [Harding, Miller and Banzhaf, Evolution, Development and Learning Using Self-Modifying Cartesian Genetic Programming, 2009](https://www.cs.mun.ca/~banzhaf/papers/gecco09-3.pdf) | Evolved programs change their graphs using an error signal | The study uses small Boolean tasks, numeric primitives and real-valued genes; unseen-task learning remains incomplete |
| [Gaier and Ha, Weight Agnostic Neural Networks, 2019](https://weightagnostic.github.io/) | Searches for architectures whose structure carries useful task behavior | Evaluation still uses a shared numerical weight; this is not a demonstration of weight-free continual learning |
| [Petersen et al., Deep Differentiable Logic Gate Networks, 2022](https://arxiv.org/abs/2210.08277) | Learns gate choices and deploys a discrete Boolean circuit | Training uses a continuous relaxation; the paper's connections are predefined |
| [Schlag, Irie and Schmidhuber, Linear Transformers Are Secretly Fast Weight Programmers, 2021](https://proceedings.mlr.press/v139/schlag21a.html) | Incoming information changes temporary computation through fast weights | Slow learned weights remain; this addresses temporary adaptation rather than eliminating weights |
| [Ellis et al., DreamCoder, 2021](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf) | Learns programs and reusable abstractions that assist later learning | Library acquisition is relevant, but does not fully describe a continuously reshaping circuit |

The 2009 self-modifying graph experiment is particularly instructive. Of 111 evolutionary runs, 18 produced learners that mastered the 12 training truth tables. None learned all four held-out truth tables correctly. Its strongest generalizing solution learned 14 of the 16 tables exactly. This supports the feasibility of error-driven structural adaptation on a small domain while exposing the gap to reliable generalization. [Original paper, sections 6–8](https://www.cs.mun.ca/~banzhaf/papers/gecco09-3.pdf).

These are distinct precedents. Combining their desirable properties is a research objective, not an already validated architecture or an established novelty claim.

## 9. A decisive first experiment

Build a bounded interpreter whose learned circuit contains discrete gate choices and connections. Use Boolean inputs, basic gates, branch operations and temporary registers. Specify every primitive, the input encoding, the permitted graph edits, the initialization and the search budget before training. The strict structural condition excludes trainable edge multipliers and target-specific answer tables; integer addresses and operation identifiers still count as stored configuration.

1. Acquire small Boolean computations from explicit examples and corrections. Establish whether a learned update rule adapts to held-out truth tables, or whether a fixed search algorithm is performing acquisition.
2. Learn addition from gates. Withhold an `ADD` instruction and the target gate arrangement. Separate learning a fixed-width circuit from discovering a repeated step with carry state; test each claim at its actual scope.
3. For a fixed-width task, reserve operand pairs for final evaluation. For a repeated-step task, additionally reserve greater bit lengths and long carry chains. Evaluation of greater lengths must use the acquired mechanism without inserting a hand-written addition procedure.
4. Teach a second operation and introduce a correction that affects shared structure. Measure every previously correct case again, including cases that should still produce the formerly rejected answer in another context.
5. Test rejection, provisional answers, conflicting testimony and confirmed cases independently. Measure answer accuracy and whether the stated evidence status is warranted.
6. Compare with answer lookup, a fixed-grammar program learner and a small numerical model using the same task information. Record total persistent bytes, peak temporary memory, executed operations, complete learning cost and per-case regressions across several seeds.

A successful result would establish that the circuit acquires a transferable computation through structural changes and retains specified earlier behavior within the declared budget. It would not yet establish general language learning. Broader success would require successive demonstrations of useful abstraction, efficient adaptation, perception, language grounding and reliable behavior as tasks become less structured.

The existing symbolic circuit and recurrent text core do not implement this complete mechanism. Their actual behavior remains documented in the [implementation reference](IMPLEMENTATION_REFERENCE.md) and [experiment records](../experiments/README.md).
