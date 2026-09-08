# Published English, algebra and configuration reuse

Author: [Arnav123-s](https://github.com/Arnav123-s)

7 September 2026. Recorded before the expanded course. The initial English run scored 100/150 supported test questions, compared with 43/150 for its language-blind control. Including unsupported questions, its test score is 100/337. Those results are retained unchanged.

## Sources and teaching

Use the same source exclusions and fixed ASDiv signature partitions as the [first protocol](ENGLISH_CONFIGURATION_PROTOCOL.md). Add learned relevance selection and admit single-unknown linear equations whose worked solution can be expressed in the supported arithmetic grammar. Unit removal, equation isolation and annotation alignment are supplied teacher procedures. The learner receives annotated connections; at inference it receives only the question text.

Also use the human-written base GSM8K training file, described by [Cobbe et al.](https://arxiv.org/abs/2110.14168) and distributed in the [author repository](https://github.com/openai/grade-school-math). Exclude the automatically generated Socratic files and model-produced solution files. Keep the original license with the local data. Inspect training material only while developing the annotation reader. The separately downloaded official test file remains unopened until the selected model has been frozen.

The GSM8K training file has SHA-256 17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465. The test file has SHA-256 3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14. These are the unmodified base files. Use the published calculation annotations to reconstruct a variable-input computation. Admit it only if the annotation gives one supported computation with a matching final answer. No invented question, altered-number lesson or generated explanation enters teaching.

Keep unsupported problems in the full-source denominator. Source exclusions and annotation failures are different categories. Reconstructing a worked solution for supervision does not demonstrate that Kavi independently discovered that derivation.

## Acquisition and reuse

Learn three discrete connection structures: which quantities to retain, which existing program applies, and which arithmetic operations connect quantity pairs when a unique existing route is unavailable. The retained artifact contains predicate connections, ordered ports and variable-input programs. It excludes lesson texts, answers, example counts and source passages.

During teaching, identify an existing program with the same argument structure before adding a new definition. Count both reuses and new definitions. This is structural identity, not an unrestricted semantic-equivalence test. The worked-solution annotation supplies the program arrangement; language learning supplies the route into it.

At inference, a uniquely supported learned program route executes directly when its arity and numerical domain fit. No alternative programs are constructed in that case. Otherwise, bounded composition uses existing numerical operations. A unique training route is not proof that a novel question was interpreted correctly.

Compare full reconstruction at depths 8, 12 and 16. Use the same evidence in each configuration and select only by development answer accuracy, with serialized size as the tie-breaker. After selection, compare reuse-first execution with composition on every question under the same retained relevance and pair-operation connections. Measure both accuracy and candidate work; a faster route can still be a worse interpretation.

GSM8K's training file supplies training and development partitions using the existing normalized-input signature hash: buckets zero through seven train, eight and nine develop. Exclude GSM8K training-file questions whose normalized signatures overlap ASDiv's final partition. Do not train on either final partition. Check exact signature overlaps across all partitions.

## Computation and evaluation

The expanded annotation grammar permits up to eight explicit active quantities rather than the first course's five. Reusable programs run directly; fallback search considers progressively larger quantity subsets and charges all candidate constructions. This is still a finite prototype. General loops, repeated use of quantities, implicit constants and arbitrary symbolic calculus are not acquired merely by increasing the bound.

Use one visible five-minute worker with Pause, Resume and Stop and the existing 512 MiB observed working-set ceiling. Each learning phase has a 100-million-unit work allowance. Each answer has a one-million-candidate/work ceiling; budget exhaustion counts as unanswered for that question. Time and memory exhaustion stop the worker. Numerical and input-format restrictions remain explicit. These are device controls and declared experiment conditions, not a claim about a maximum possible intelligence level.

Freeze the selected configuration before reading the GSM8K test file. Test it once; report supported-subset accuracy and accuracy with all original test questions in the denominator. Report same-ASDiv-bank results as follow-up measurements, not a new independent examination. Report the algebra and irrelevant-quantity subsets separately, including their sizes. Score the first answer, without using the reference answer to select among candidates.

Recheck the previously solved published scientific questions and the acquired arithmetic dependency. Source texts and full evidence remain local. The shared interpreter, arithmetic programs, temporary activity, teaching workspace, source storage and configuration bytes all count separately.

## Wider curriculum

English, algebra and calculation transfer are the present measurable prerequisites. Calculus, philosophy, advanced and discrete mathematics, machine learning, physics, chemistry and biology remain separate target domains. Source exposure, imported definitions and supplied numerical kernels do not constitute completed teaching in those subjects. A later report must distinguish taught and independently tested skills from unimplemented learning mechanisms.
