# Interacting configurations, input completion and learned grouping

Author: [Arnav123-s](https://github.com/Arnav123-s)

The subsequent [correction and state-learning report](../experiments/2026-09-07-incremental-inquiry-transfer.md) adds current-activity English processing, inherited-path correction, learned asking and a separate direct recurrent word learner. Static predicate routes must be distinguished from acquired word transitions. The latter directly implements part of this interaction contract, but generalizes poorly and does not learn its coupling schedule.

7 September 2026. This document records the configuration design and distinguishes it from the implemented execution checks. A configuration is an organized, executable interaction among components. It may participate as a component inside another configuration.

## Meaning depends on the interaction

The same components may participate in different meanings. Their identities alone are insufficient: current values, activation order, triggering conditions, retained intermediate state and connections to other active components can change the result. One component may hold a value while another changes, release a signal after a later input, or influence which route becomes available.

The pendulum analogy describes these interacting states. A component can be held at one state while a coupled component continues changing. A later event can release either one or alter their relationship. A larger group can itself expose a component interface. No fixed correspondence between one word, one node and one concept is required.

For example, the desired language learner should interpret a request that introduces a name, binds the result of an addition to a symbol, then asks for that symbol squared. It must preserve the relevant temporary binding while preventing unrelated name information from changing the calculation. The current signal tests supply numerical ports and the arithmetic arrangement. They do not demonstrate that Kavi learned this interpretation from the sentence.

## Persistent organization and current activity

Let the persistent configuration be K and the temporary activity be s. An input event x changes activity through an executable transition:

$$ s_{j+1}=F_K(s_j,x_j). $$

Internal propagation can require several steps between external events. The implementation keeps the latest port values, revision markers and ready calls. A step history is not required if that state contains everything needed for the next transition. A current token, a carried value and a pending dependency still occupy memory.

Learning has a distinct effect:

$$ K_{t+1}=L(K_t,e_t), $$

where e_t is teaching evidence and L constructs a successor. It can change any part of the structure. Original lessons need not be retained by deployed inference, but their acquired distinctions have to exist somewhere in K. Continuous activity during reading is not, by itself, a persistent learning update.

Intent can be distributed across the active configuration. An observer might name a stable distinction such as a request to compare or calculate; the learner need not begin with that named category. Any claim that an internal arrangement represents intent must be supported by its effects on outputs and by controlled changes to that arrangement.

## Learning component boundaries

The proposed learner should discover useful recurring relationships, construct groups, use those groups in larger arrangements, and revise the grouping after feedback. Similar word forms can supply evidence, but they do not establish equivalent meanings. Context and consequences matter.

| Change | Intended behavior | Required check |
| --- | --- | --- |
| Create a group | Repeated relationships become a reusable configuration | Unfamiliar inputs use it successfully |
| Compose groups | Existing configurations support a new combination | New combinations work without their answers being supplied at inference |
| Merge definitions | Identical or verified equivalent computations share a definition | The declared behavior remains equivalent |
| Split a group | A correction reveals a distinction that was incorrectly collapsed | Related corrected cases improve and earlier valid cases remain correct |
| Replace global organization | A different arrangement carries the acquired abilities | Retention obligations hold under the declared checker |
| Learn an update procedure | Experience changes how successors are constructed | New learning tasks improve at matched total cost |

Definition sharing does not imply state sharing. Three calls to the same stateful component can require three separate current states. Merging their live activity because their code matches would change the computation. Likewise, the same set of activated components can yield different results when order or current state differs.

One formal way to discuss grouping is behavioral distinguishability. For a fixed configuration K and allowed continuation set U, two activity states may be grouped only if no continuation in U distinguishes their observable results:

$$ s\equiv_{K,U}t \quad\Longleftrightarrow\quad
\forall u\in U,\; O_K(F_K^*(s,u))=O_K(F_K^*(t,u)). $$

Here F_K* processes a continuation and its input-complete marker. The observable result includes unresolved execution or interruption under the declared semantics. Restricting U to a finite test bank gives a finite observation, not universal equivalence. This is an operational criterion for a proposed grouping, not a definition or proof of human-like understanding.

The current English predicate learner forms groups using supplied features and annotated arithmetic meanings. The new sharing pass recognizes only identical ordered structures. Learning the broader context-dependent grouping and its own update procedure remains unimplemented.

## Answer only after the input is complete

An internal proposal may change as input arrives. A visible answer is released only after the caller marks the turn complete, every required external port has received input, pending activity has settled, and an available result remains. Failed execution or an unresolved final result blocks release.

$$ \mathrm{release}=
\mathrm{inputComplete}\land\mathrm{portsComplete}\land
\mathrm{settled}\land\mathrm{resultAvailable}\land\neg\mathrm{failed}. $$

The application supplies the end-of-input boundary, such as the user pressing Send. This tells the runtime that the turn has ended; it does not establish that the runtime understood the request. For streaming input, each event must be consumed in order. An arbitrary pause is not silently treated as completion.

~~~mermaid
flowchart LR
    X[Next input event] --> S[Current interacting state]
    S --> H[Hold or update a value]
    H --> T[Trigger dependent activity]
    T --> S
    S --> P[Internal proposed result]
    P --> G[Input complete and activity settled]
    E[End of input] --> G
    G --> Y[Release available answer]
    F[Failure or unresolved result] --> B[No answer released]
~~~

Settling means the declared scheduler has no pending calls. It is not a physical claim that all energy has disappeared. A useful retained value can remain after settling. Conversely, a loop can keep generating work indefinitely unless its configuration supplies a stopping rule or execution is interrupted.

## Implemented runtime

[signal_configurations.py](../kavi/signal_configurations.py) provides a current-state execution substrate:

- Configurations read connected inputs and emit a value or HOLD. HOLD preserves the prior value and emits no new event. An explicit unresolved output clears answer availability.
- Connections can revisit earlier nodes and include feedback. An optional trigger interface distinguishes an event that activates a call from state that the call merely reads.
- New revisions activate dependent calls. A trigger signature prevents one external token from being consumed again merely because its own resulting state changed.
- The ready queue stores at most one pending entry per call. Each call retains only its latest input signature, and each connection retains only its latest value.
- Input completion closes the invocation. Later input requires a new invocation. Independent invocations do not share their held values.
- Compiled acquired definitions retain dependency guards. A changed dependency requires a new compilation and invocation; transferring active state across a global replacement is not implemented.
- All scheduler steps, calls and dependency checks use the work counter and interruption callback. A failed call cannot release an earlier provisional result.

Use accept to consume an ordered input event before submitting the next. The lower-level feed method supports assembling current port values; overwriting a port repeatedly before processing it coalesces those values and is not suitable for preserving a word stream. General real-time interleaving of nonsettling dynamics and incoming words needs additional scheduling semantics.

The supplied recurrent adapter executes the already acquired eight-state model using this runtime. It has a current-token port, a feedback-state port and an output port. It imports no teaching sequences. The arithmetic adapter expands acquired programs into the same execution machinery. These adapters establish execution compatibility, not a jointly trained language-and-arithmetic core.

The runtime does not learn oscillator equations, physical damping, quantum amplitudes, semantic input encoding, intent labels or its own scheduler. The representation can be extended to such explicitly defined mechanisms, but naming a component after a physical process does not supply its behavior or establish a learning benefit.

## Measured execution checks

The [tests](../tests/test_signal_configurations.py) are interpreter checks. They introduce no teaching data and no new accuracy benchmark.

| Check | Result |
| --- | --- |
| A partial addition waits for its other input | No answer released |
| A supplied addition-then-square arrangement receives 4 and 4 | Intermediate 8 and internal result 64; answer withheld until completion |
| A later value revises the second input from 4 to 5 | Final result 81 after completion |
| A held intermediate is released by a later control input | Final result 64 |
| Countdown feedback starts at 1,000 | 1,001 calls, final zero, one live value and one current trigger signature |
| A continuing feedback loop exceeds its budget | Interrupted |
| Independent invocations use the same definition | Held values remain separate |
| Input arrives after completion | Rejected for that closed invocation |
| A required external port never receives input | No answer released |
| A compiled dependency changes | Stale invocation rejected |
| A later computation fails after an earlier provisional answer | No earlier answer released |
| The acquired recurrent graph receives the same tokens in two orders | Different correct graph outputs, with three live values |
| The acquired graph receives 101 copies of a token | Each consumed once; three live values and no token history |
| An unknown final token follows a known token | No earlier answer released |

For the order check, the acquired token stream [?a, ?b, b] ends at output 1, whereas [?b, ?a, b] ends at output 0. Both contain the same tokens and end with b. The carried state preserves the order-dependent distinction. These symbols belong to the earlier finite-state teaching task; they are not ordinary English intent categories.

There are twelve test methods; several combine related checks. One live value does not mean one byte or zero memory. Integer values, revision numbers and work counters occupy storage, and their bit widths can grow. Registry storage, graph definitions, queues, runtime objects and any external observer trace are additional resources. An observer may record a trace for inspection; the execution object does not consult that trace.

## Mathematical relatives and next evidence

The implemented substrate is a discrete event-driven transition system with feedback and retained current values. A version with continuous state evolution between events would also need differential equations, event guards and numerical integration rules. Lee and Seshia's [Introduction to Embedded Systems](https://ptolemy.berkeley.edu/books/leeseshia/index.html), especially discrete dynamics, hybrid systems, composition and equivalence, provides the relevant mathematical vocabulary. This is a comparison of formalisms, not evidence of quantum computation or biological equivalence.

The existing learning relatives remain [automata learning](../experiments/2026-09-07-recurrent-configuration.md) and [program/library learning](STRUCTURAL_SHARING_AND_QUANTUM_RESEARCH.md). The proposed combination is a recurrent executable configuration whose grouping and update procedures can themselves change through learning.

The direct word-event experiment connects learned recurrent interpretation to acquired arithmetic and changes the transition graph after correction. It retains its finite teaching answers, but its poor follow-up score leaves useful state generalization unresolved. Learned scope, questioning and coupling changes still need to work inside that same configuration. Event propagation, sharing and source exposure each test a different part of the problem; none establishes the full result.
