# Meaning resolved by incoming signals

Author: [Arnav123-s](https://github.com/Arnav123-s)

## Protocol before execution

Scope clarification after the run: the owner's intended system includes **learned recurrent feedback**, allowing later information to revisit earlier bindings. This trial's graph compiler is acyclic and does not implement that capability. Its forward alternatives and structural sharing are a narrower experiment. The [recurrent learning contract](../docs/INPUT_DRIVEN_PATHWAYS.md#learned-feedback-is-a-separate-requirement) records the distinction.

This experiment follows the owner's clarification that input should flow through a shared configuration and acquire its interpretation from later input, without a subject-context label or a separate route lookup. It supersedes the proposed route-memory follow-up as the next architectural experiment. The route-memory prototype remains an isolated, tested alternative; its curriculum has not been run or incorporated into the main model.

Fourteen authored annotated examples teach three constructions: arithmetic assignment, a description beginning with the article `a`, and an explicit notation mapping to a Greek letter. Arithmetic and notation examples include `a`, `α` and `alpha`. Annotation supplies the target roles and arithmetic operations; the learner aligns variable spans to induce sentence frames. It does not infer those labels from unannotated prose.

An engineered compiler combines common prefixes and interns equivalent continuation states into a directed acyclic graph. This is sharing of structurally identical grammar states, not general algebraic rewriting or e-graph search. Equivalent mathematical continuations can therefore be shared by different written symbols without globally declaring the symbols identical. The original token sequence remains in temporary execution state.

Let the acquired graph be G, incoming token be x_t, and A_t be the finite set of active nodes with temporary slot bindings. Execution is:

$$A_{t+1}=\operatorname{advance}_G(A_t,x_t).$$

A compatible literal edge advances; a numeric edge binds one natural number; a text edge may bind one or more tokens. An incompatible edge becomes inactive. Identical active node/binding states are merged. No task category is given to this transition. End-of-input accepts a unique complete interpretation, preserves ambiguity when multiple complete meanings remain, and reports unsupported input when none completes. An open text span may remain possible until the end marker, even when another route already has a complete interpretation.

This is a finite-state transducer with captures and shared continuations, not a general semantic world model. Its active signals and bindings carry information across tokens. They are temporary state inside execution, not a separate semantic planning workspace. A conventional software runtime still stores those signals in data structures. Eliminating every trace of temporary state would also eliminate sequence dependence.

The owner's input-as-power analogy is implemented only as input-driven transitions and finite work limits. No physical energy or conservation law is simulated. Each supplied token triggers real transition work; multiple compatible bindings still cost work. The executor permits at most 96 tokens and 10,000 active candidate bindings. It does not force an answer merely because the input stream ends.

Five queries use unseen slot contents: `a equals 12 plus 13`, its `α` and `alpha` variants, `a fox is alert`, and `a denotes the Greek letter gamma`. Compare the incremental meaning with the existing batch interpreter and inspect the states after each token. The first `a` must retain three possible roles. The mathematical variants must share continuation nodes while retaining distinct original forms. `alpha fox is alert` is a negative test: mathematical sharing must not license a Greek-name token as an English article.

Next, record the unsupported query `a multiplies 12 by 13`. Teach multiplication wording using only `a multiplies 2 by 3` and `a multiplies 4 by 5`, rebuild the shared graph, and test the fresh query `a multiplies 17 by 19`. Preserve the original unsupported result. Retest all five earlier meanings after graph growth and execute the recognized arithmetic through the existing acquired library.

This is teaching during a sequential evaluation workflow: later model versions learn after a recorded failure. It is not final-test feedback secretly added to the frozen routing comparison. Nor does silent inference learn that its own output is correct. Teacher feedback is the evidence that justifies the new structure.

Run `python -B -m scripts.run_incremental_paths live --run-dir runs/incremental-paths-20260907-01`. Input presentation is paced at 0.2 seconds per token for readability; that delay is included in wall time and is not computation or learning effort. The worker has a 60-second limit and Pause, Resume and Stop controls. The small fixed teaching packet and graph limits bound this demonstration; it has no sampled process-memory guard. No literary source ingestion, automatic source-code modification or changes to the existing arithmetic library occur.

## Relation to the research direction

The [expanding pathway design](../docs/OPEN_ENDED_PATHWAY_LEARNING.md) describes learned uses of shared structures. This trial tests incremental ambiguity and shared continuation, while the [experience-routing comparison](2026-09-07-experience-routing.md) tests learned search guidance. They address different levels: understanding which learned construction an input follows versus choosing components while acquiring a new computation.

Operational meaning here means a tested relation between input construction, slot roles and executable output. General understanding would require unfamiliar constructions, grounded reference, broader compositional transfer and independent semantic assessment. No such claim follows from this small grammar trial.

## Measured results

All five fresh interpretations agreed with the existing batch interpreter. After the initial `a`, the active graph supported arithmetic, description and notation roles without a subject label. Mathematical continuations shared nodes across `a`, `α` and `alpha`; original input tokens remained distinct. The negative article-substitution case passed its unit test. These checks establish behavior under annotated constructions, not independent understanding of Greek notation or English grammar.

The multiplication phrase was unsupported before teaching. After two different teaching examples, `a multiplies 17 by 19` resolved to multiplication with arguments 17 and 19. All five older meanings remained unchanged. Executing the recognized arithmetic through the existing library gave 25 for 12 plus 13 and 323 for 17 times 19. The saved live-run arithmetic checks use the batch interpretation as a reference; the public incremental CLI executes the incremental graph's completed meaning directly.

The initial graph had 15 shared states in 1,236 canonical bytes. The extended graph has 19 states in 1,544 bytes. The retained sentence frames occupy 1,584 bytes separately; preserving both representations costs 3,128 bytes before adding the arithmetic library, executor and transient state. Wall time was 7.129 seconds and includes deliberate 0.2-second input presentation intervals. No throughput or inference-speed claim is made from that time.

The [machine-readable record](2026-09-07-incremental-paths.json) contains every token transition and the original unsupported result. The [public authored sentence model](incremental-language-20260907.json) can be queried directly:

```powershell
python -B -m kavi.incremental_cli "a equals 12 plus 13" --trace
python -B -m kavi.incremental_cli "α equals 12 plus 13" --trace
python -B -m kavi.incremental_cli "a multiplies 17 by 19"
```

The [input-driven pathway design](../docs/INPUT_DRIVEN_PATHWAYS.md) records how additional semantic evidence, output guards and input-driven activation extend this idea. Physical-unit checks and learned semantic constraints remain a next representation step, not a result of this grammar trial.

## Missing-symbol correction protocol

A final bounded follow-up directly tests the owner's correction example. Start a separate model with the same authored lesson packet except the four constructions beginning with `α`. Record its response to `α equals 12 plus 13`. Then teach the two previously withheld `α equals 2 plus 3` and `α equals 4 plus 5` annotations, and assess `α equals 17 plus 19`. The teacher supplies the addition interpretation; it is not inferred from a bare correct number alone. The new graph must share mathematical continuation with the `a` construction, retain the English article example and reject `α fox is alert`.

Record graph size before and after. The retained model contains frames and the compiled graph separately, not a stored wrong-answer episode. The error remains in the external experiment record. This probes transfer to new numbers in one construction, not every possible use of alpha. Run `python -B -m scripts.run_symbol_correction live --run-dir runs/symbol-correction-20260907-01` with the same 60-second limit, input presentation pacing and visible controls.

Measured result: the original alpha query was unsupported; the fresh query after teaching produced 36 through the acquired addition library. The graph grew from 15 states / 1,195 canonical bytes to 16 states / 1,300 bytes, and the retained frame model occupied another 1,202 bytes. The alpha and `a` arithmetic traces shared completed state 5. The English article interpretation survived; using `α` as that article remained unsupported. The 2.036-second wall time includes presentation pacing. [Correction evidence](2026-09-07-symbol-correction.json) preserves the original failure, supplied annotations and new-input result. No broad alias equivalence or one-example semantic-learning claim is made.

Verification after these additions: all 197 repository tests passed on Python 3.13.5. Direct CLI queries through the incremental graph returned 25 and 323. The first Greek-symbol trace exposed a legacy Windows output-encoding error; the CLI now uses the existing UTF-8 terminal configuration, and that query passed on retry. No learning result was changed by the display repair.
