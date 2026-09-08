# Kavi

Author: [Arnav123-s](https://github.com/Arnav123-s)

The new [PCL architecture and development plan](docs/PCL_DESIGN.md) defines a stable template and complete learned circuit generations, with coupled phase activity and supervised reconstruction. The implementation has mechanism regression checks; general language, learned visual world models and psychology understanding remain development targets. The [completed psychology comparison](experiments/2026-09-08-psychology-transfer.md) records the earlier event learner's failed generalization test.

The latest [configuration-learning report](experiments/2026-09-07-incremental-inquiry-transfer.md) records five completed English courses, including learned recurrent word transitions and provisional executable connections during input. The latest model retains 168/168 teaching answers but answers only 29/102 follow-up questions with adaptation; the same adaptive constructor scored 31/102 before the extra teaching. The results do not establish broad understanding, reliable self-assessment or learned algebra.

The [original-notebook curriculum](docs/PRIMARY_NOTEBOOK_CURRICULUM.md) catalogues scientific and philosophical notebooks and published first-person accounts. It records edition, language and provenance. These sources have not been taught to the new configuration models.

Kavi studies learning through reusable computational configurations. Its experimental cores acquire gates, programs and recurrent connections from examples. Inputs drive temporary activity through the retained structure; feedback changes the configuration. The objective is to acquire new abilities while carrying earlier valid behavior into the revised structure.

The latest [published English experiments](experiments/2026-09-07-published-english.md) learn routes from authentic word problems into arithmetic configurations. The first model scores 100/150 supported ASDiv questions; the expanded model scores 30/303 admitted GSM8K questions and 30/1,319 with unsupported types included. The larger model loses 32 earlier correct answers while gaining 19. Sharing identical structures reduces its artifact from 149,917 to 109,826 bytes while preserving its decisions, including its mistakes.

The [interacting-configuration design](docs/INTERACTING_CONFIGURATIONS.md) treats meaning as a pattern of current states, connections and activation order. Its execution substrate supports held values, feedback and ordered token events, and releases an answer only after input completion and settled activity. A check using the acquired recurrent graph preserves different outputs for different orders of the same tokens. Learning those interactions from general language remains a separate target.

The [design alignment audit](docs/DESIGN_ALIGNMENT_AUDIT.md) identifies the current gap: the separate cores demonstrate narrow learning, but the assembled application does not yet implement the intended self-configuring conversational learner. Scientific interpretation and much of the language interface are supplied. Source and dictionary lookup do not close that gap. Whole-configuration replacement is a central design requirement and has a measured finite-state example; general semantic replacement remains unimplemented.

The [current design refinement](docs/REUSABLE_RELATIONAL_CONFIGURATIONS.md) treats a component and a pathway as the same executable object at different scales. Known structure runs directly; unresolved parts trigger local reasoning; successful reasoning and correction should produce reusable guarded configurations. Richer relational and physical dynamics are proposed ways to support that process. The integrated mechanism remains an implementation target.

The latest [configuration reuse and repair experiment](experiments/2026-09-07-mechanism-audit.md) learns shared notation, connects the recurrent core to acquired arithmetic through numerical feedback, and constructs a new graph from existing operations. The new computation reuses one intermediate and passes 128 fresh inputs with 104 earlier-operation checks preserved. Temperature did not improve exact repair in the tested conditions. The [project assessment](docs/PROJECT_ASSESSMENT.md) explains the strongest results, the addition theorem, current capabilities and the remaining gap to graduate-level work.

The earlier [recurrent-configuration experiment](experiments/2026-09-07-recurrent-configuration.md) learns connections from labeled token streams and replaces an earlier two-state graph with an eight-state successor. After a failed course and a coverage repair, all three seeds passed 256 fresh longer streams and exact checks of the new task and earlier behavior. The 195-byte saved graph excludes the runtime and learning workspace. This is a finite stream task; it does not establish broad language or graduate subject competence.

The structural learner acquires addition and subtraction transitions from examples using AND, XOR and NOT gates, then learns programs that call acquired operations. The original retained library contains 13 procedures in 2,238 bytes; a checked multiplication optimization produces a 2,272-byte library with the same 13 entries. Its arithmetic model contains no teaching equations or learned numerical edge weights. Encoding, state registers, iteration semantics, types and the search controller are supplied.

The acquired 321-byte addition graph satisfies all eight local full-adder identities. Together with the specified bit-stream executor, this gives a [correctness theorem for every finite width](docs/ADDITION_CORRECTNESS.md); the implementation currently accepts inputs up to 4,096 bits. The theorem is separate from the learning claim, which includes a 129-case selection bank.

The [expanding pathway system](docs/OPEN_ENDED_PATHWAY_LEARNING.md) treats chemistry and physics as examples of structures that might be learned, rather than a fixed component inventory. The [physical-pathway research](docs/PHYSICAL_PATHWAY_RESEARCH.md) distinguishes mechanisms we engineer from mechanisms the model learns to select, compose or improve. Temperature and error-path priority now have a small measured search comparison; physical reaction systems and learned update rules remain proposals. The [earlier configuration-reuse experiment](experiments/2026-09-07-pathway-growth.md) measures acquired components helping later arithmetic learning.

The [neural pathway study](docs/NEURAL_PATHWAY_LEARNING.md) examines population activity, correction, mastery and behavior. The [animal-learning study](docs/ANIMAL_LEARNING_AND_CONFIGURATION_CHANGE.md) develops the design requirement: transform part or all of the configuration while retaining earlier valid abilities, then test whether the learning procedure itself can improve. Learned update procedures and the broader biological mechanisms remain research proposals.

A first sentence-learning extension induces typed frames from annotated examples and routes recognized calculations to those procedures. It also retains source-linked lexical memory from six short original-language passages. General prose comprehension and autonomous invention of control semantics remain research goals. See the [connector and language results](experiments/2026-09-07-connectors-language.md).

## Run and inspect

Query the newly acquired computation and the learned arithmetic connections:

```powershell
python -B -m kavi.configuration_cli graph relation_01 17 19
python -B -m kavi.configuration_cli bridge 17 19 a
python -B -m kavi.configuration_cli bridge 17 19 a a
```

These return `1296`, `323` and `36`. The first graph computes `(17 + 19)²`, reusing the sum. The next two use token-driven connections to select multiplication or addition. The [report](experiments/2026-09-07-mechanism-audit.md) includes the supervised admission process and visible reproduction commands.

Query the new recurrent graph without its teaching data:

```powershell
python -B -m kavi.recurrent_cli a b "?b" b "?a" --trace
```

The final answer is `1`. The [experiment report](experiments/2026-09-07-recurrent-configuration.md) explains the tokens, shows the learned connections and gives visible teaching commands with Pause and Stop controls.

The latest [input-driven pathway study](experiments/2026-09-07-incremental-paths.md) follows tokens through shared learned sentence states without an external subject label. It also tests a missing-symbol correction that preserves other uses of `a`. Inspect the published small grammar with:

```powershell
python -B -m kavi.incremental_cli "α equals 12 plus 13" --trace
python -B -m kavi.incremental_cli "a multiplies 17 by 19"
```

The [design note](docs/INPUT_DRIVEN_PATHWAYS.md) distinguishes this implemented grammar from the proposed physical and semantic constraints. A separate [learned-routing comparison](experiments/2026-09-07-experience-routing.md) tests using previous programs to guide later acquisition.

The latest [foundation teaching and repair study](experiments/2026-09-07-foundation-curriculum.md) adds a consolidated 22-procedure natural-number library, exact signed fractions and 24 public authored sentence frames. The [graduate capability program](docs/GRADUATE_CAPABILITY_PROGRAM.md) covers mathematics, physics and language; current results remain at the foundation stage.

```powershell
python -B -m kavi.curriculum_cli show
python -B -m kavi.curriculum_cli ask "twice kinetic energy for mass 7 and speed 11"
python -B -m kavi.curriculum_cli exact mean_pair -- -1/2 2/3
```

These queries return `847` and `1/12`. The public sentence artifact excludes source-derived lexical memory and definitions, which stay local. For visible teaching with Pause, Resume and Stop controls, follow the study's run instructions and use a fresh run directory.

The structural learner uses the Python standard library. Query the latest compiled library without source files:

```powershell
python -B -m kavi library ask --library experiments/library-20260907-compiled.json multiply 1000000 3 --trace
```

For the new original-source sentence trial, use the [reviewed configuration and live-window instructions](docs/CONNECTORS_AND_LANGUAGE_PROTOCOL.md). Its source packet and learned lexical artifact remain local. Earlier procedure-learning runs can be inspected or reproduced with their historical source prerequisites:

```powershell
python -B -m kavi.learning_window --config curriculum/library-scaling-run.json --run-dir runs/library-trial
```

Inspect the configuration and press **Start teaching**. The window shows the actual process, pause/stop controls and saved-procedure queries. Append `--start` for an already reviewed and authorized run. A full teaching replay needs the admitted local source witness. The published model supports inference without that source:

```powershell
python -m kavi library ask --library experiments/library-20260905-retained.json factorial 18
python -m kavi library ask --library experiments/library-20260905-retained.json power 20 10 --trace
python -m kavi library ask --library experiments/library-20260905-retained.json sum_squares 72 83
```

The [procedure runtime](docs/PROCEDURE_LIBRARY_RUNTIME.md) documents the complete interface. The original gate-acquisition experiment remains available:

```powershell
python -u -m kavi circuit run --config curriculum/circuit-run.json --run-dir runs/circuit-trial --interactive
```

Use a new run directory. The automatic trial has a 180-second limit and displays candidate graphs, counterexamples, accepted repairs, retention and final results. The console then accepts `12345 + 67890`, `/trace 7 5`, `/circuit`, `/status` and `/quit`. The launcher `scripts/start-circuit.ps1` provides the same workflow with a fresh timestamped directory.

To query the small published model directly:

```powershell
python -m kavi circuit ask --model experiments/circuit-20260905-model.json 255 1 --trace
```

The [runtime reference](docs/CIRCUIT_RUNTIME.md) documents pause, resume, stop, file formats and the complete interface.

## Measured result

The latest audit completed in 22.967 seconds, including 19.907 seconds of display pacing. Three trials learned an eight-state, 216-byte notation graph with identical `a` and `α` destinations, passing 128 fresh streams each and exact old/new task checks. Numerical feedback connected that controller to arithmetic, and a separate 338-candidate search acquired a two-call computation from four examples. The controller, bridge, new catalog and shared arithmetic dependency occupy 2,856 bytes; worker peak memory was 38.883 MiB. All 217 implementation regressions passed before the run.

Heated repair found no exact solution in the three cases. Each greedy method solved one; complete one-edge search solved all three with a larger 224-proposal budget. One sampled-perfect repair still failed exact comparison. Six supported sentence calculations worked; six broad reasoning and writing requests remained unsupported. The [full audit](experiments/2026-09-07-mechanism-audit.md) reports costs and unsuccessful searches alongside the improvements.

The recurrent study first exposed a coverage failure: development accuracy reached 256/256, but fresh longer-stream accuracy was only 125, 114 and 115 out of 256 across the three seeds. More systematic teaching produced an eight-state, 32-transition graph in every seed, passing all fresh cases and the exact finite-state audit. The earlier task was preserved for every finite stream over its original alphabet. The [report and diagrams](experiments/2026-09-07-recurrent-configuration.md) include both courses, the single-correction failure and the complete storage and work accounting.

The foundation study found and repaired search interference, missing signed/fractional execution, a sampling failure and a language-pattern regression. With supplied operation hints, both fixed and cumulative conditions acquired all eight numeric tasks under two seeds, passing 175/175 final cases and 254/254 earlier-skill checks per arm. Five rational procedures passed 108 final cases across an initial run and its repair. The hints and scalar semantics were supplied; these are not demonstrations of independent representation invention. The combined checkpoint passed 44 numeric, ten rational and 28 local language retention checks. Its [full record](experiments/2026-09-07-foundation-curriculum.md) preserves the preceding failures and distinguishes model storage from total resource costs.

The 7 September connector and sentence trial completed in 2.653 seconds. All 16,431 multiplication cases passed; 47 swapped pairs had identical complete call traces, and 516 earlier successful cases had zero regressions. Multiplication now canonicalizes interchangeable inputs and uses binary scanning through the acquired addition gates. This is a supplied compiler optimization, not discovery of a new algorithm by the learner.

The language model acquired 18 frames from 36 annotated sentences. It passed 12 new-argument calculations and seven clause-role checks in known constructions, recalled two taught definitions, and correctly reported the seven declared unsupported, ambiguous or invalid cases. The combined saved arithmetic and language artifacts occupy 29,082 bytes; the worker peaked at 26.36 MiB. Unfamiliar wording, philosophical explanation and creative writing remain unsupported. The [study](experiments/2026-09-07-connectors-language.md) records source scope, costs and all evidence boundaries.

Two library trials ran across three seeds each in 45.868 and 56.349 seconds. The second added a lesson that acquired a 113-byte call arrangement for scaling a large quantity by a small count. Powers and factorials then passed every declared follow-up test, including `20^10` and `18!`. The resulting programs execute acquired addition through earlier learned procedures.

Library growth also made search harder: the follow-up timed out on sum of squares. That operation was retained from the first trial after exact dependency checks, yielding the original 13-procedure artifact. Its multiplication remains sensitive to operand order; the new compiled artifact addresses that defect. Storage is compact, but the results do not establish advanced subject competence or nearly free future learning. See the [earlier study and failures](experiments/2026-09-05-procedure-library.md) and [advanced capability protocol](docs/ADVANCED_CAPABILITY_PROTOCOL.md).

The first declared trial used three seeds. Every seed acquired the same five-gate, 321-byte circuit. Each passed 127 unseen four-bit pairs, the full 65,536-pair eight-bit audit, and 190 longer-input cases up to 1,024 bits. The audit preserved all 6,561 answers the foundation circuit previously got right. The complete run took 5.281 seconds on one CPU process.

The eight-bit audit includes selection examples; the separate 127-case and length-transfer banks were withheld. The 321-byte figure is the model artifact, excluding the executor and learning workspace. These results establish a narrow operation-learning mechanism under strong, declared representation assumptions. See the [experiment record](experiments/2026-09-05-circuit-learning.md) and [machine-readable results](experiments/2026-09-05-circuit-learning.json).

## Documentation

- [Design alignment and configuration replacement](docs/DESIGN_ALIGNMENT_AUDIT.md): intended behavior, learned and supplied mechanisms, architectural gaps and acceptance criteria
- [Composition, science and conversation results](experiments/2026-09-07-composable-science-and-conversation.md): completed extensions, textbook failures and corrections, costs and retrieval limitations
- [Project assessment](docs/PROJECT_ASSESSMENT.md): plain-language explanation, theorem, capabilities, research relatives and remaining work
- [Configuration reuse and repair](experiments/2026-09-07-mechanism-audit.md): latest measurements and diagrams
- [Certified arithmetic and software efficiency](docs/CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md): review audit, software algorithms, physical pathways and deferred recommendations
- [Printable certificate and software study](docs/Kavi_Certified_Arithmetic_and_Software_Efficiency.pdf)
- [Architecture](docs/DESIGN.md)
- [Engineering and research specification](docs/KAVI_ENGINEERING_SPECIFICATION.md)
- [Printable baseline specification](docs/Kavi_Engineering_and_Research.pdf)
- [Structural sharing and quantum research](docs/STRUCTURAL_SHARING_AND_QUANTUM_RESEARCH.md): DreamCoder, Babble, XRF/LIBS, mathematical design and evaluation
- [Printable structural sharing study](docs/Kavi_Structural_Sharing_and_Quantum_Research.pdf)
- [Shared connectors and sentence learning](docs/CONNECTORS_AND_LANGUAGE_PROTOCOL.md)
- [Adaptive circuit formulation](docs/ADAPTIVE_DATAFLOW_CIRCUIT.md)
- [Discrete circuit runtime](docs/CIRCUIT_RUNTIME.md)
- [Procedure library runtime](docs/PROCEDURE_LIBRARY_RUNTIME.md)
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md)
- [Complete documentation index](docs/DOCUMENTATION_INDEX.md)

## Earlier experiments and development

The repository also retains a symbolic pathway circuit with supplied operation contracts and a separate 66,880-parameter recurrent text model. Their measured language limitations and regressions remain documented. They are separate implementations; their capabilities are not part of the new circuit model.

Python 3.11 or later is declared. The first circuit trial used Python 3.12.14; the library and sentence trials used Python 3.13.5. The test command below checks all current experiments; PyTorch is needed only for the optional earlier text core and its tests. Test counts for measured revisions appear in their experiment records.

```powershell
python -B -m unittest discover -s tests -q
python -m kavi --help
python -m kavi circuit --help
```

Private sources, conversations, large checkpoints, source-derived lexical memory and complete run logs remain in ignored local folders. Public artifacts contain arithmetic programs, measurements, authored exercises and source metadata. A software license has not yet been selected.
