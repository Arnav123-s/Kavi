# Adaptive dataflow circuits

Author: [Arnav123-s](https://github.com/Arnav123-s)

Revision: 5 September 2026

Status: proposed architecture. This note clarifies the intended learned representation beyond the program-library design in the [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md). It introduces no implementation or experimental result.

## 1. The learned object

Kavi's intended memory is the configuration of a circuit that processes information and can change its own configuration. Connections, junction operations, branch conditions and reusable subgraphs determine where an input goes and what computation occurs. Learning changes these structures. Individual signals may disappear after a response while the acquired configuration remains.

The retained knowledge is the operation itself. An addition pathway combines quantities for new operands; it does not need an independently stored record of having learned `2 + 2 = 4`. Teaching examples constrain and diagnose the procedure during acquisition. The deployed learner must generate answers by executing the acquired procedure, without consulting an answer table or retrieving teaching episodes. Experimental records may remain outside the learner for reproducibility and evaluation, with that boundary explicitly enforced.

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

Correction targets the learned computation. Under a trusted input interpretation and teaching signal, a wrong result is a counterexample to the claim that the current pathway implements the intended operation. It calls for diagnosis and repair of that pathway. The feedback does not establish that every earlier output or every participating subcomponent is wrong.

The circuit can carry a temporary structured result such as `(value, procedure_version, status, context)`. Status concerns the evidence for the procedure and its applicability to this input. It can control routing through shared diagnosis, investigation or response operations. Persistent evidence may consist of contracts or certificates attached to the procedure; an input-specific answer record is not the intended learned representation.

| Interaction | Warranted change | What remains unresolved |
| --- | --- | --- |
| `2 + 2` produces `1` | Inspect the procedure and its temporary execution trace | Correctness is unknown without relevant evidence |
| Feedback states that `1` is wrong | Treat this case as a counterexample to the current addition pathway | Negative feedback does not identify the defective operation or its repair |
| Feedback suggests `4`, with uncertainty | Use the suggestion to investigate candidate procedures provisionally | The suggestion is not a proof or an accepted permanent correction |
| An accepted teaching signal confirms this case | Constrain the repaired addition procedure to produce four units from these operands | Correcting one case does not establish the procedure's general correctness |
| A general addition procedure passes a proof under specified assumptions | Reuse the procedure throughout the proved domain | Different representations or changed dependencies may require verification |

The experiment must reject a repair that merely adds `if input is 2 + 2, return 4` while leaving the defective general computation intact. A useful repair changes the mechanism responsible for the error. For example, a missing carry operation calls for a carry repair that also succeeds on unseen carry cases. The repair must preserve valid uses of shared components in other operations, including computations whose correct result is `1`.

The source of failure may be a junction, a termination condition, an input interpretation or the composition of otherwise valid subcircuits. Diagnose that distinction before attributing the failure to the entire addition operation or to the learning rule itself. Certainty supplied by a speaker is an assertion from that source; accepting it as a teaching label remains different from obtaining a mechanically checked theorem.

Once a computation has adequate evidence, the circuit can invoke its verified route directly. It need not recompute the complete history of failed candidates each time. The retained evidence should name the graph version, input domain and dependencies that justify the shortcut. A relevant change invalidates that justification; unrelated changes need not invalidate it.

The initial experiment should provide feedback through explicit control fields such as `reject`, `suggest` and `confirm`. Understanding the English words "wrong" and "perhaps" is a separate learning problem. Those words can later be grounded in the same control operations without presupposing language understanding at initialization.

Repeated exposure can establish associations or useful compression. Frequency alone cannot promote a statement to mathematical truth. A shared confidence circuit also needs an interpretation and evaluation: confidence should track predictive reliability on new cases, rather than merely count visits to a path.

## 5. Acquiring a procedure

For nonnegative integer quantities, an elementary target is a pathway that combines two collections of distinct unit occurrences. It can transfer one unit at a time from one collection into the other until the source is empty. The same circuit is reused for every pair of quantities within its execution budget. The result contains the units from both collections. The arrangement implements the operation; there is no separate remembered answer for each pair.

Let `0` denote no units and `S` the operation of introducing one additional unit. A recursive characterization of the desired operation `A` is:

$$
A(a,0)=a,\qquad A(a,S(b))=S(A(a,b)).
$$

These equations determine ordinary addition on nonnegative integers, by induction on `b`. They illustrate the reusable rule the learner should acquire. Giving the learner this recurrence as executable code would instead supply the target solution. An acquisition experiment must declare what is already available, such as unit representation and successor, and what must be discovered, such as iteration, combination and termination. Supplying a complete collection-merging operation already supplies addition at the level of quantity; learning how to call it is a different experiment.

The deployed operation can retain a fixed description while processing larger quantities through repeated execution. A direct unit-transfer procedure takes work proportional to the number of transferred units; a positional representation and carry mechanism can be much more economical for large values. Structural reuse may reduce the number of examples needed once the rule is discovered. It does not by itself establish that discovering the rule is fast.

The examples `1 + 1 = 2` and `1 + 2 = 3` are compatible with ordinary addition, a small answer table and many other functions. Generalization requires a bias toward particular circuit families, additional evidence or an independently supplied specification. No representation removes that ambiguity.

A useful learning sequence starts with small cases, includes carry-producing examples, and then tests operand combinations and lengths withheld from learning. Inspect the acquired graph to establish whether the same mechanism is reused. Check that the input encoder, teacher or verifier has not supplied the target computation to the learner through an unintended interface.

Counterexamples should eliminate defective candidate procedures and guide a revision of the shared computation. This connects the proposed learning mechanism to [counterexample-guided inductive synthesis](https://www.cis.upenn.edu/~alur/SyGuS13.pdf): a candidate implementation is checked, a failure constrains the search, and a revised implementation is checked again. The graph representation and the method for finding efficient structural repairs remain separate design choices.

There are two distinct arithmetic experiments. Providing an `ADD` primitive and learning where to invoke it tests composition. Providing lower-level gates and learning their arrangement tests acquisition of the arithmetic mechanism. Both are legitimate, but only the second addresses the strongest interpretation of this proposal.

Proved facts and acquired subcircuits can be reused as components. Their contracts must state their domain. For example, addition on arbitrary-length bit strings and fixed-width machine addition have different overflow behavior. Reuse is valid when the calling context satisfies the component's assumptions.

## 6. Repair without losing earlier behavior

A repair changes the shared computation while preserving its required earlier behavior. A new branch is appropriate when it expresses a general distinction, such as whether a carry remains after the final digit. A branch dedicated to a single teaching pair does not meet the operation-learning objective. There is no general guarantee that a repair consists of one small jump: the existing representation may lack the required distinction, or several shared computations may need revision.

For a finite protected domain, exhaustive comparison can establish that a candidate retains every required old result. For an unbounded domain, tests establish only sampled behavior unless a proof applies. Counterexamples should refine the repair search. Equivalent rewrites can shorten a circuit while preserving its behavior, including its mistakes; repairing those mistakes requires a separate behavioral change.

The desired retained objects are reusable contracts and the procedures that satisfy them. A preservation proof can establish behavior without requiring the deployed circuit to remember the examples used during acquisition. External test records remain useful for detecting regressions but do not provide an unlimited preservation guarantee. A counterexample refutes universal correctness; it does not require discarding the parts of the procedure that already satisfy their contracts.

The external evaluation harness should record which earlier correct cases became wrong after each accepted update. Counting only the total number of correct answers hides regressions. Protection should concern required behavior, rather than prohibit all changes to the internal representation. A better shared circuit may replace several older circuits if its obligations are checked.

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
2. Learn an operation on unit collections or learn positional addition from gates. Withhold an `ADD` instruction, a complete collection-merging primitive and the target arrangement. Declare all simpler primitives supplied. Separate learning a fixed-width circuit from discovering a repeated step; test each claim at its actual scope.
3. For a fixed-width task, reserve operand pairs for final evaluation. For a repeated-step task, additionally reserve greater quantities or representation lengths; positional addition must also cover long carry chains. Evaluation of larger inputs must use the acquired mechanism without inserting a hand-written addition procedure.
4. Introduce a systematic defect, diagnose it from counterexamples and repair the shared operation. Test unseen inputs exercising the same defect and exclude operand-specific answer patches. Then teach a second operation and measure every previously correct case again, including valid uses of shared components in another context.
5. Test rejection, provisional answers, conflicting testimony and confirmed cases independently. Measure answer accuracy and whether the stated evidence status is warranted.
6. Evaluate the deployed circuit with access to teaching records disabled. Compare with answer lookup, a fixed-grammar program learner and a small numerical model using the same task information. Record total persistent bytes, peak temporary memory, executed operations, complete learning cost and per-case regressions across several seeds.

A successful result would establish that the circuit acquires a transferable computation through structural changes and retains specified earlier behavior within the declared budget. It would not yet establish general language learning. Broader success would require successive demonstrations of useful abstraction, efficient adaptation, perception, language grounding and reliable behavior as tasks become less structured.

The existing symbolic circuit and recurrent text core do not implement this complete mechanism. Their actual behavior remains documented in the [implementation reference](IMPLEMENTATION_REFERENCE.md) and [experiment records](../experiments/README.md).
