# Provisional configurations during input

Author: [Arnav123-s](https://github.com/Arnav123-s)

7 September 2026. Recorded before the adaptive event course.

## Mechanism

The direct recurrent language model changes its activity during input, but its persistent connections remain fixed until teaching. This experiment additionally constructs provisional connection changes while words arrive. Each live candidate contains only its current state and proposed new edges. A known route executes directly. An undefined transition opens bounded alternatives among existing states, including holding the current state. Later input traverses those provisional connections and can eliminate candidates that exceed the search bound.

Use at most 16 live candidates and four new edges per candidate. Prefer fewer new edges, then stable proposal order. A candidate's label is available only after input completion. Agreement among surviving labels is a diagnostic, not learned confidence or a correctness certificate. The candidate constructor and ranking rule are supplied; accepted connections become acquired persistent structure through genuine correction feedback.

No source answer is available while constructing or ranking the input-driven candidates. After predicting, the teacher can provide the original worked relation. If a completed candidate agrees, accept its new edges. The graph contains no saved question-answer record afterward. Candidate construction can still encode details of a lesson in connections; structure alone is not proof against memorization.

An accepted extension leaves every previously defined transition and output unchanged. Induction on the event sequence therefore preserves every earlier defined execution, including any incorrect one. This is a conditional preservation property, not an unconditional no-forgetting result for arbitrary rewrites. Extending undefined routes cannot fix an already defined wrong route. If feedback requires that repair, permit a separately recorded whole-graph reconstruction from genuine teaching constraints; verify its earlier correct teaching answers before acceptance.

## Course

Start from the frozen 144-lesson direct event model. Use the next 24 eligible ASDiv training questions in the same fixed signature order. Keep the original vocabulary and numeric event interface. At each lesson, first run provisional adaptation without its label, then expose the published relation. Accept the first minimum-edit consistent candidate after retention checks. If none is available, allow up to six whole-graph reconstructions in the course, using seed 19 and all genuine lessons encountered so far. Failed or unavailable corrections stay recorded; do not substitute fabricated feedback.

The teacher holds the source bank outside the deployed learner. Replaying earlier constraints for a global repair consumes data access, memory and computation and must be counted. Persistent inference artifacts retain the graph and vocabulary, not the teacher bank. Before each accepted global replacement, require retention of all earlier correct teaching answers and improvement on the current correction. If no candidate passes, keep the previous graph.

Report first-prediction accuracy separately from the post-correction teaching score. After the 24 lessons, freeze a snapshot and revisit the same 80 development and 102 follow-up questions with both direct execution and provisional adaptation. These follow-ups do not choose a new candidate and do not become teaching feedback. Count unresolved results as wrong. A candidate containing the correct answer is not a correct first prediction.

## Controls and scope

Learn a small self-assessment component from the 24 actual first-prediction outcomes. Its inputs are current candidate count, maximum simultaneous activity, proposed operation, number of provisional connections, whether the route already existed and whether candidate labels agree. Its targets are `can_propose` after a correct first prediction and `needs_help` after a wrong or absent prediction. Reference answers are never inputs to this component. Use a supplied predicate learner at depth three and minimum leaf size three, with no development selection. Retain only its learned predicate connections and action ordering. During follow-up, record actual accuracy within each predicted category. Neither category is a truth certificate, a psychological feeling or proof of broad self-knowledge. These 24 observations arise under changing parent models, so transfer of the assessment to the final model is itself a limitation to measure.

Use a visible worker with Pause, Resume and Stop, a five-minute wall ceiling and observed 512 MiB memory ceiling. Each global repair has at most 100 million work units; each query has at most one million. Save every correction decision, candidate count, accepted extension, rejected repair, data replay, resource measurement and artifact fingerprint. Record all regression checks and failed constraints.

This tests a bounded form of changing executable structure during input and accepting changes after feedback. It is not unlimited computation, quantum simulation, a learned proposal algorithm, automatic truth, general algebra or cross-field emergence. The earlier learned question policy remains a separate experiment. No claim of unified capabilities follows from these components existing in the same repository.
