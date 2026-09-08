# Design alignment and configuration replacement

Author: [Arnav123-s](https://github.com/Arnav123-s)

Subsequent evidence: the [direct state and adaptive courses](../experiments/2026-09-07-incremental-inquiry-transfer.md) acquire recurrent word transitions, couple operation outputs to older arithmetic and propose executable connections during input. This implements part of the intended architecture. The coupling schedule, proposal rules and learning procedure remain supplied. Additional teaching did not improve the matched adaptive follow-up result, and learned self-assessment was unreliable. Algebraic understanding has not been demonstrated. The [adaptive protocol](ADAPTIVE_EVENT_PROTOCOL.md) defines those measurements.

7 September 2026. This audit compares the intended learner with the implemented cores, the local conversation application and completed experiments. The starting published revision was 3c17ce1. The initial audit paused an untrained English prototype. The subsequent [English courses](../experiments/2026-09-07-published-english.md) and [interacting runtime](INTERACTING_CONFIGURATIONS.md) add measured partial mechanisms; they do not close the overall alignment gap.

## Finding

The assembled application does not yet implement the intended learner. Some cores learn reusable computations and recurrent connections. Much of the interpretation, choice of quantities, connection between subjects and response behavior is supplied by the surrounding software.

The conversation extension increased the number of questions for which the application could display something. Source retrieval and dictionary lookup did not create the learned semantic configuration required by the design. Presenting that extension as the culmination of the learning work would be misleading.

The useful foundation is the acquired arithmetic, recurrence, composition and correction machinery. The central missing work is connecting perception, meaning, problem construction and correction through learned organization, then showing that the same organization transfers to unfamiliar language and problems. Another collection of supplied subject handlers would leave that gap intact.

## The intended system

The design has remained consistent through its different analogies:

1. Experience changes a persistent executable configuration. A lesson need not remain as a retrievable episode or a question-answer record.
2. Inputs activate that configuration. Later input can change what earlier activity means, without an externally assigned subject label. Visible answers wait until the input turn is complete.
3. A learned operation applies to many inputs. Learning addition should produce an addition procedure, not a list of sums.
4. Existing configurations can participate in new configurations. A connection, a component and a whole pathway can expose the same kind of interface at different scales.
5. Familiar cases use acquired structure. An unresolved case can trigger bounded construction and comparison of alternatives.
6. Correction changes the responsible computation or interpretation. It should help related cases, including cases absent from the lesson.
7. Any part, or the entirety, of the configuration can be replaced. Earlier valid abilities constrain the successor; earlier wiring need not survive.
8. Internal roles can be learned without human-readable labels. Their effects must still be measurable.
9. Physics, chemistry, geometry and biological learning suggest possible operations and ways of constructing configurations. They are examples, not a requirement to preinstall a catalog of simulated substances.
10. Eventually, configurations may implement and improve the procedures that learn other configurations. That is a further learning problem, not an automatic consequence of using graphs.

The [expanding pathway design](OPEN_ENDED_PATHWAY_LEARNING.md), [input-driven design](INPUT_DRIVEN_PATHWAYS.md), [neural study](NEURAL_PATHWAY_LEARNING.md) and [animal-learning study](ANIMAL_LEARNING_AND_CONFIGURATION_CHANGE.md) already contain these requirements. The application has advanced further on task-specific demonstrations than on their integration.

## What the code actually learns

| Implementation | Changed by learning | Supplied by the implementation | Alignment |
| --- | --- | --- | --- |
| Initial pathway fabric, [graph.py](../kavi/graph.py) | Numerical readout coefficients and selected pathway state | Arithmetic features, typed routes, joining behavior and update rule | A parameter-learning baseline. Calling its edges pipes does not remove its learned weights. |
| Recurrent byte model, [wave_core.py](../kavi/wave_core.py) | Embeddings, transmission, phase, gates and readout parameters | Candidate connectivity, recurrence, next-byte objective and backpropagation with Adam | Actual text learning, but primarily parameter updates on a fixed substrate. No demonstrated broad English competence. |
| Gate learner, [circuit_search.py](../kavi/circuit_search.py) | Boolean expressions, shared gates and transition/output wiring | AND/XOR/NOT, bit-stream encoding, one working-state bit, executor and finite search | A genuine reusable-rule result. It does not learn the input encoding or general semantics. |
| Procedure learner, [procedure_search.py](../kavi/procedure_search.py) | Calls, argument connections and bounded procedure arrangements | Expression grammar, iteration semantics, constants, types and search | Learns computations from examples using existing operations. |
| Recurrent graph learner, [recurrent_configuration.py](../kavi/recurrent_configuration.py) | States, transitions, outputs and recurrent connections | Token vocabulary, deterministic transition semantics and state-merging algorithm | Closest existing result to whole-configuration replacement with retained behavior. |
| Sentence learner and [incremental paths](../kavi/incremental_paths.py) | Typed sentence templates and shared token transitions | Annotated target meanings, slot types, execution interfaces and template induction | Limited incremental interpretation; unfamiliar general prose remains outside the learned grammar. |
| Hierarchical configuration lab, composable_configurations.py | Small nested call arrangements and a corrected subcomputation | Primitive behavior, a supplied missing-call boundary, enumeration, expansion and dependency guards | Shared composition is implemented. General autonomous problem decomposition is not. |
| Science and published lessons, science_course.py and published_learning.py | Numerical program arrangements that fit annotated worked quantities | Quantity names, physical relations, units, selected intermediate lessons, primitive arithmetic and dependency resolution | Calculation learning. The system did not infer these physical meanings from the original prose. |
| Conversation application, conversation.py | No persistent configuration update from a conversational correction | Arithmetic parsing, scientific patterns, response formatting, passage ranking and dictionary access | An interface to narrow calculations and retrieval. It is not the intended conversational learner. |
| English configurations, english_configurations.py and published_english.py | Predicate connections for quantity relevance, operation preferences and program selection | Token features, annotation alignment, programs from worked solutions, arithmetic primitives and candidate search | Measured limited English-to-calculation learning, with substantial unsupported coverage and earlier-answer regressions. |
| Signal runtime, signal_configurations.py | Executes acquired arithmetic and recurrent definitions; supplies no new learning procedure | Current-state propagation, hold/release, event triggers, input completion and dependency guards | Supports part of the interaction contract; general recurrent language dynamics remain unlearned. |
| Shared English representation, shared_english_configurations.py | Preserves existing acquired decisions; performs no new teaching | Recognition of identical ordered structures and a complete preservation check | Smaller representation of the same model, including its errors. Live states of separate uses remain distinct. |

The local module names in this table identify inspected code, not evidence of achieved capability. A class named a learner, a graph with many nodes or an animated signal display is insufficient evidence by itself.

### The present conversation path

~~~mermaid
flowchart TD
    Q[Question text] --> P[Supplied parser and routing rules]
    P --> A[Acquired arithmetic procedures]
    P --> B[Supplied quantity interpretation]
    B --> C[Acquired numerical compositions]
    P --> D[Source passage ranking]
    P --> E[Dictionary lookup]
    A --> O[Displayed response]
    C --> O
    D --> O
    E --> O
    F[Conversational correction] --> P
    F -. no persistent teaching update .-> M[Model configuration]
~~~

The source index contains actual passages. The dictionary contains actual lexical records. Those are external stored information in the answering application. They do not satisfy a configuration-only learning requirement merely because the arithmetic subsystem uses acquired programs.

The current conversation object also retains the last response temporarily for follow-up display. That is session state, not learned long-term knowledge. Neither it nor the interface's history should be confused with a configuration update.

## The strongest evidence, and what it means

**Reusable arithmetic:** the acquired five-gate addition graph occupies 321 serialized bytes and satisfies all eight full-adder identities. Under the documented executor assumptions, those identities establish addition for every finite bit width in the abstract model. The implementation has a 4,096-bit input limit. Selection used 129 operand pairs. This is a successful acquired artifact satisfying a classical correctness argument, not a new theorem about learning from three examples. See the [certificate](ADDITION_CORRECTNESS.md).

**Whole-configuration replacement:** the recurrent experiment replaced a two-state graph with a single eight-state successor. In each of three seeds it passed 256 fresh longer streams, and an exact finite-state comparison established preservation of the old task for all streams in its original alphabet. The successor runs without the old graph or its teaching sequences. This directly supports one part of the intended design. Its learning method and formal task were supplied; it did not acquire general language or its own updater.

**Correction can also hurt:** in the earlier recurrent course, one seed's development result rose from 215 to 253 correct, then fell to 216 after another rebuild. Previously taught labels remained satisfied. The final successful course required more informative teaching coverage. Rebuilding the whole graph is therefore possible, but every rebuild is not automatically more accurate. The [record](../experiments/2026-09-07-recurrent-configuration.md) preserves both courses.

**Reuse and faster construction:** a later local-completion experiment evaluated the same 338 candidates in both conditions. Reusing a known prefix during learning reduced primitive-kernel calls from 1,272 to 932. The missing region was explicitly supplied. The experiment did not learn where an unfamiliar prose problem should be decomposed.

**Physics questions:** after the source-based numerical course, the frozen model initially answered 0/8 annotated numerical targets from a different textbook. Further published worked quantities and supplied semantic relations raised practice performance to 8/8. A subsequent fresh set scored 4/5. The remaining inequality was then corrected as practice, with 17 earlier checks retained and no new unseen inequality examination. These are structured quantity tests; the reported scores do not establish that the model read and understood the textbook questions independently.

The [completed extension report](../experiments/2026-09-07-composable-science-and-conversation.md) records the additional configurations, costs and evidence boundaries. Historical generated teaching examples remain labeled as such. They are not reclassified as source-only lessons.

## Configuration-only memory

The meaningful requirement is: retain executable organization that can reconstruct or derive an answer; do not answer by retrieving a saved teaching episode.

For addition, that means keeping the carry transition and its wiring. It does not require storing an entry for each sum. For language, removing a dictionary is insufficient: useful distinctions and relationships would have to be acquired elsewhere in the configuration.

There are three different resources:

| Resource | Role | Intended treatment |
| --- | --- | --- |
| Persistent configuration | Connections, operations, internal distinctions, conditions and any retained constants | The deployed learned state; fully counted |
| Temporary activity | Current input, active signals, intermediate values and candidate computations | Discarded or explicitly reset between independent invocations |
| External teaching and audit records | Original sources, feedback, reference answers and experiment evidence | Kept outside deployed inference; separately counted and unavailable as an answer lookup |

Simulation does not remove information storage. If a fixed interpreter must distinguish N acquired behaviors, a fixed-length state representation needs at least ceiling(log2 N) bits. Connections can encode those bits instead of a dense weight array. Compression exploits shared structure; it cannot guarantee unlimited arbitrary knowledge in fixed space.

A configuration may still overfit by encoding a separate branch for every lesson. The test is transfer to genuinely unseen cases and reusable internal structure, not merely the absence of a file called memory.

## Learning by replacing the configuration

Whole-configuration replacement can be the primary learning mechanism without backpropagation. The following is an architectural contract, not a completed general-purpose algorithm.

Let K_t be the current persistent configuration, a_j the temporary activity during one invocation, and x_j the next input event:

$$a_{j+1}=F_{K_t}(a_j,x_j).$$

Correction supplies evidence e_t about the behavior or interpretation. A proposal procedure constructs a finite set of alternatives:

$$\mathcal H_t=P_{\phi_t}(K_t,e_t;B),$$

where B is a declared search budget and phi_t describes the proposal procedure. Alternatives may rewire, split, merge, compose or replace the entire structure. They need not preserve node identifiers or contain the old graph as a subgraph. The available transformations must have executable definitions.

Define C_t as the corrected requirements and R_t as earlier valid behavioral obligations outside the disputed claim. Candidate configurations must satisfy both:

$$\mathcal A_t=\{K\in\mathcal H_t:K\models C_t\ \land\ K\models R_t\}.$$

Here satisfaction means the declared checker: a proof for a supported formal domain, or finite evidence for a broader task. It must not be presented as universal proof when only examples were checked. Conflicting requirements need to be resolved; a correction must not preserve the very mistake it is meant to replace.

Select the successor from admissible candidates by declared development performance, then by resource cost when performance is tied. An independent final set remains outside selection. If no admissible candidate is found, keep the current configuration and report the unresolved correction, or continue within an explicitly available budget. Do not silently promote a candidate merely because it fits the newest example.

This selects the best verified candidate found under the stated conditions. It does not identify the globally most accurate configuration on unknown future questions.

~~~mermaid
flowchart TD
    K[Current configuration] --> A[Input-driven temporary activity]
    X[Input] --> A
    A --> Y[Candidate answer and interpretation]
    Y --> E[Correction or other teaching evidence]
    E --> P[Construct alternative configurations]
    K --> P
    R[Earlier valid behavioral obligations] --> V[Check correction and retention]
    P --> V
    V --> S[Select a verified successor]
    S --> N[One revised configuration]
    N --> A
    V --> U[Unresolved if no candidate qualifies]
~~~

The unit replaced at commitment is the complete model configuration. Constructing that successor can reuse parts of the old graph or build a completely different graph. Whole-model replacement does not require wastefully rebuilding every unchanged part after every correction.

Replacement between invocations is the first tractable implementation target. Replacement during an active computation additionally requires a defined way to transfer temporary state; a new graph identifier alone does not solve that problem.

The updater phi_t is initially supplied. To claim that Kavi learns how to learn, a later experiment must represent and modify that updater, then test improvement on new learning tasks at matched total cost. Moving a supplied search function into a node does not make it learned.

### Reuse before construction

During learning, first check whether an existing configuration already expresses the required behavior under the new evidence. If it does, learn or repair the route into that configuration. Construct a new arrangement when the existing alternatives are inadequate. A newly constructed arrangement should itself become available for later reuse.

At inference, an applicable acquired route should run directly. Ambiguous or unusable routes can trigger construction using existing components. This requires learned applicability and a way to detect unresolved execution; the presence of a program in a catalog does not establish that it answers the current question.

There are distinct levels of reuse: the same primitive operation, the same multi-operation program, and the same learned route from an input to that program. Count them separately. Structural identity is a useful first check, but different-looking programs may be equivalent under explicit assumptions.

### Loops retain current state, not a history of steps

A loop can repeatedly activate the same configuration, change its order of calls, or move into another configuration. Let c_j identify the currently active configuration and s_j contain its temporary working state:

$$ (c_{j+1},s_{j+1})=T_K(c_j,s_j,x_j). $$

The next step does not require a list of every earlier step if the current state retains everything the computation still needs. Addition uses a carry. A running sum uses an accumulator and a position. A nested computation may also need pending return information. These are current working values, not a retrieved teaching episode.

Calling the most recent scalar output the entire state can discard necessary information. What matters is a sufficient current state, not an arbitrary rule that only one number may survive. Similarly, routing into a differently organized configuration requires compatible state interpretation or an explicit state conversion.

The existing bit-stream arithmetic and procedure runtimes already reuse operations with temporary control state. This does not establish that the English learner has acquired arbitrary looping programs. Execution support, discovery of a loop and learning when to invoke it remain separate claims.

The architecture should not define a permanent capability ceiling by a small number of arithmetic steps. Longer computation, larger configurations and loops can be admitted progressively. Every actual run still has finite hardware, work and stopping conditions; a loop without progress or a correct stopping rule is not an improvement. Compare candidate methods at the required accuracy and include verification, working memory and compilation costs when identifying a faster method.

### Why rebuilding does not guarantee maximum accuracy

Several different configurations can fit the same correction and disagree elsewhere. More detailed feedback can reduce that ambiguity. It cannot eliminate all uncertainty from finite observations.

The space of arrangements also grows rapidly. For n labeled nodes, even simple directed graphs without self-loops admit 2 to the power n(n-1) connection patterns, before adding operation choices, port ordering or values. A digital representation permits flexible changes; it does not make exploring them free.

A practical comparison should therefore measure local repair, full reconstruction and reuse-assisted reconstruction under the same evidence and total budget. Record corrected-case transfer, earlier-skill regressions, candidate work, runtime and stored configuration size. More elaborate topology is not an objective in itself.

## What must change in the next core

One logical learned configuration should connect input interpretation, reusable computations, applicability conditions and candidate construction. Internal modules are allowed; the requirement is shared learned representations and a common execution contract, not a single source file.

Keep the initial supplied substrate explicit: input encoding, generic executable operations, connection semantics, scheduling, finite resource control and the feedback interface. A learner needs such starting structure. Domain-specific meanings added in code must be counted as supplied competence.

Learn the relationships that decide what a question asks and what a component is applicable to. A word such as mass should not reach a physical relation solely because a new hand-written parser branch was added. Teaching may include genuine worked examples and human annotations, but the acquired mapping must later work without those annotations.

Allow bounded alternatives when the current configuration is inadequate. Select the proposed answer without its reference answer. Finding the correct number somewhere in a list of candidates is not the same as answering the question.

Let a conversational correction enter the same learning transaction as other lessons. Commit an accepted successor and test a related fresh case. Simply displaying the correction, saving its text or appending a special-case response would not meet the requirement.

Use one operational definition of a configuration at different scales. The current hierarchical interface is a useful start, but separate finite-state, arithmetic, byte-model and sentence formats do not yet provide that unified execution and learning system.

Physics and chemistry mechanisms should enter as precise executable hypotheses, with matched controls. The existing heat and two-state quantum examples use supplied evolution equations; they do not show learned physics or a generally stronger search procedure. The negative temperature trial does not test every physical mechanism. Previously deferred external implementation recommendations remain deferred.

## Acceptance gates before claiming an intelligent conversational learner

| Gate | Required evidence |
| --- | --- |
| Learned interpretation | Original published questions reach the appropriate computation without task labels or per-question quantity annotations at inference |
| Transfer | A separately sourced, withheld set changes wording and required compositions; a frozen model answers without consulting its teaching material |
| Correction | Genuine feedback changes the configuration and improves related fresh questions, beyond the corrected example |
| Retention | Earlier valid abilities survive measured replacement; formal guarantees are limited to domains with actual certificates |
| Reuse | Inspectable shared computations serve distinct inputs or tasks; removing a shared part affects the predicted related behaviors |
| Unknown problem construction | The model constructs and selects an answer-producing configuration using its learned relationships; evaluation does not provide the answer to search |
| Configuration-only inference | A fresh process loads only the declared configuration and substrate, with source indexes, dictionaries and example stores unavailable |
| Whole-model replacement | A successor can change global organization while satisfying correction and retention obligations; old wiring is not required to remain |
| Better learning | Changing the learned updater improves acquisition on held-out task families at matched total computation and storage |

Use authentic, inspected teaching material. Keep published-problem identifiers and human annotations distinct from raw-text understanding. No new synthetic teaching course is authorized by this audit. The privately withheld user questions remain unavailable to development.

Learning during use can be measured separately as an online sequence: score each answer before its feedback changes the configuration. Preserve a frozen evaluation track as well. Otherwise changing the model during a test makes it impossible to tell what the earlier teaching achieved.

The first English course covers two to five explicit quantities and scores 100/150 supported ASDiv questions. The expanded course admits up to eight quantities and relevance selection, but scores 30/303 admitted GSM8K questions and loses 32 earlier correct ASDiv answers while gaining 19. These are limited semantic-parsing results. The [report](../experiments/2026-09-07-published-english.md) preserves source exclusions, full denominators, costs and regression counts.

## Assessment

Kavi has demonstrated narrow structural learning. It has not demonstrated a unified semantic learner, general conversation, a learned learning algorithm or the stated graduate-level targets. The strongest starting points are reusable arithmetic and recurrent configuration replacement. The next milestone is an integrated learning loop that passes the gates above, rather than expanding the retrieval interface.

The implementation relatives remain [automata learning](../experiments/2026-09-07-recurrent-configuration.md) and [program synthesis with reusable libraries](STRUCTURAL_SHARING_AND_QUANTUM_RESEARCH.md). The broader design can be described as a recurrent executable graph transformed by feedback, with behavioral constraints on its successors. That description does not establish novelty or guarantee that the proposed system will acquire general intelligence.
