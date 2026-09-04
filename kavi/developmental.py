"""Visible mastery, correction, and fresh-test loop for the supported core.

This automates the teaching procedure. It does not turn a script recognizer
into a reader, or claim that cataloged languages have been learned.
"""

from __future__ import annotations

import json
from pathlib import Path

from .composition_evaluation import display_program, final_audit_manifest
from .pathway_circuit import CompositionCall, CompositionExample, CompositionLiteral
from .pathway_live import PathwayCurriculumRuntime, _safe_write_json, _script_sample
from .script_reference import SCRIPT_SOURCE_ID, ScriptReference
from .source_manifest import SourceManifest
from .teaching_search import search_candidates
from .unicode_core import ScriptEvent, ScriptKind
from .unicode_runtime import SCRIPT_SPECS


def all_calls(node: CompositionLiteral | CompositionCall):
    if isinstance(node, CompositionCall):
        yield node
        for child in node.arguments:
            yield from all_calls(child)


class DevelopmentalRuntime(PathwayCurriculumRuntime):
    """Teach, diagnose, attempt guarded corrections, and test fresh programs."""

    def __init__(self, config, *, policy_path: Path, script_source: Path, emit=None):
        super().__init__(config, emit=emit)
        try:
            self.policy = json.loads(policy_path.read_text(encoding="utf-8"))
            if not 0.9 <= self.policy["mastery_threshold"] <= 1.0:
                raise ValueError("The mastery threshold must be at least 90%.")
            if self.policy["retention_threshold"] != 1.0:
                raise ValueError("Earlier foundation checks must retain 100%.")
            if not 1 <= self.policy["max_repair_rounds"] <= 20:
                raise ValueError("The repair round limit must be between 1 and 20.")
            if not 1 <= self.policy["harder_test_cases"] <= 256:
                raise ValueError("The harder test must have between 1 and 256 cases.")
            manifest = SourceManifest.load(config.source_manifest_path)
            if not manifest.by_id(SCRIPT_SOURCE_ID).is_teaching_admissible:
                raise ValueError("The script teaching source is not admitted.")
            self.reference = ScriptReference.load(script_source)
        except Exception as error:
            self.bus.update_status("failed", error=str(error), next_gate="teaching source")
            raise
        self.excluded_glyphs = {
            glyph for spec in SCRIPT_SPECS
            for glyph in (*spec.training_glyphs, spec.protected_glyph, spec.held_out_glyph)
        }
        self.used_questions: set[str] = set()
        self.report: list[dict[str, object]] = []

    def lesson(self, title: str, detail: str, **values) -> None:
        self.bus.emit("lessons", "teaching-step", title=title, detail=detail, **values)
        self.emit(f"[teaching] {title}: {detail}")

    def _mistakes(self, examples):
        return tuple(
            example for example in examples
            if self.core.infer_composition(example).answer != example.expected_value
        )

    def _remember_exam(self, examples) -> None:
        for example in examples:
            self.used_questions.add(example.display_text)
            for call in all_calls(example.expression):
                for child in call.arguments:
                    if isinstance(child, CompositionLiteral) and child.type_id == "scalar":
                        self.excluded_glyphs.add(child.value)

    def _repair_scripts(self, examples, round_number: int) -> bool:
        mistakes = {}
        for example in self._mistakes(examples):
            for call in all_calls(example.expression):
                if call.operator_id != "unicode-script":
                    continue
                glyph = call.arguments[0].value
                expected = self.reference.label(glyph)
                query = CompositionExample(
                    f"diagnose-{call.node_id}", call, "concept-label", expected,
                    display_program(call),
                )
                actual = self.core.infer_composition(query).answer
                if actual != expected:
                    mistakes[glyph] = (actual, expected)
        if not mistakes:
            self.lesson(
                "A new learning method is needed",
                "The remaining mistakes are outside this teacher's script-correction method.",
            )
            return False

        training = []
        current = []
        for glyph, (actual, expected) in mistakes.items():
            try:
                kind = ScriptKind(expected)
            except ValueError:
                continue
            self.lesson(
                "Why this answer was wrong",
                f"The writing-system path called {glyph!r} {actual!r}. "
                f"Unicode's original reference identifies it as {expected}. "
                "The current path places this part of the character range too close "
                "to another writing system. I will teach different nearby characters.",
                source_id=SCRIPT_SOURCE_ID,
            )
            current.append(_script_sample(ScriptEvent(
                f"mistake-{ord(glyph)}", glyph, kind, "correction-check"
            )))
            alternatives = self.reference.alternatives(glyph, self.excluded_glyphs, count=4)
            for alternative in alternatives:
                self.excluded_glyphs.add(alternative)
                sample = _script_sample(ScriptEvent(
                    f"repair-{round_number}-{ord(alternative)}", alternative,
                    kind, "different-teaching-example",
                ))
                before = self.core.infer_category(sample)
                self._trace_category("corrective-teaching", "before-lesson", sample, before)
                self._answer_category("corrective-teaching", "before-lesson", sample, before)
                training.append(sample)
                self.lesson(
                    "Different example, same concept",
                    f"{alternative!r} (U+{ord(alternative):04X}) belongs to {expected}. "
                    "This character was excluded from all tests already shown.",
                    source_id=SCRIPT_SOURCE_ID,
                )
        if not training:
            return False

        parent_state = self.core.state
        before = self.core.evaluate_categories(current)
        previously_correct = tuple(
            example for example in examples
            if self.core.infer_composition(example).answer == example.expected_value
        )

        def proposals():
            for count in sorted({1, min(2, len(training)), len(training)}):
                candidate, delta = self.core.propose_category_update(training[:count])
                yield f"teach-{count}-examples", candidate, delta

        def assess(candidate):
            errors = self.core.evaluate_categories(current, state=candidate).errors
            retained, _ = self._earlier_skills_retained(candidate)
            old_correct = self.core.evaluate_compositions(
                previously_correct, state=candidate
            ).errors == 0
            return errors, retained, old_correct

        selected, trials = search_candidates(
            proposals(), parent_mistakes=before.errors, assess=assess,
            max_serialized_bytes=self.policy["max_model_json_bytes"],
        )
        for trial in trials:
            self.lesson(
                "Trying a candidate change",
                f"{trial.proposal_id}: remaining diagnosed mistakes={trial.mistakes}; "
                f"older skills retained={trial.retained}; "
                f"eligible={trial.eligible}. This trial has not replaced the model.",
                model_json_bytes=trial.serialized_bytes,
                evaluation_ms=round(trial.elapsed_ms, 3),
            )
        if selected is None:
            self.lesson("No candidate passed", "The active model stays unchanged.")
            assert self.core.state == parent_state
            return False
        candidate, delta = selected.candidate, selected.delta
        accepted = True
        after = self.core.evaluate_categories(current, state=candidate)
        retained, retention = self._earlier_skills_retained(candidate)
        candidate_bytes = selected.serialized_bytes
        self.lesson(
            "Choosing the best passing candidate",
            f"Selected {selected.proposal_id}: fewer mistakes, retained older skills, "
            "then smaller saved state and fewer changes as tie breakers.",
        )
        self._emit_learning(
            "corrective-teaching", delta, accepted, candidate,
            parent_protected=before, candidate_protected=after,
            parent_held_out=self.core.evaluate_compositions(examples),
            candidate_held_out=self.core.evaluate_compositions(examples, state=candidate),
        )
        self.lesson(
            "Checking the proposed pathway change",
            f"Mistakes on the diagnosed characters: {before.errors} -> {after.errors}. "
            f"Earlier skills retained: {retained}. "
            f"Change {'accepted' if accepted else 'rejected'}.",
            retention=retention, model_json_bytes=candidate_bytes,
        )
        if not accepted:
            assert self.core.state == parent_state
            return False
        self._promote(candidate, "corrective-teaching", delta)
        self._checkpoint()
        for sample in training:
            after_inference = self.core.infer_category(sample)
            self._trace_category("corrective-teaching", "after-lesson", sample, after_inference)
            self._answer_category("corrective-teaching", "after-lesson", sample, after_inference)
        return self._step_wait()

    def _grade_composition_stage(self, stage_id: str) -> bool:
        initial_pass = super()._grade_composition_stage(stage_id)
        if self._stop_requested():
            return False
        examples = final_audit_manifest()
        self._remember_exam(examples)
        initial = self.core.evaluate_compositions(examples)
        self.report.append({"test": "initial-audit", "score": initial.exact_accuracy})
        self.lesson(
            "First wider test finished",
            f"{initial.correct}/{initial.cases} correct ({initial.exact_accuracy:.1%}). "
            "Mistakes remain visible. Corrections change model parameters; they do not "
            "change the answer key or scoring threshold.",
        )
        for round_number in range(1, self.policy["max_repair_rounds"] + 1):
            if self._stop_requested() or not self._wait_if_paused():
                return False
            if self._mistakes(examples):
                if not self._repair_scripts(examples, round_number):
                    self._save_teaching_report(False)
                    return False
            # Preserve the original stricter audit rather than lowering its floor.
            initial_pass = self.core.evaluate_compositions(final_audit_manifest()).errors == 0
            seed = self.policy["harder_test_seed"] + round_number - 1
            fresh = final_audit_manifest(
                seed=seed, cases=self.policy["harder_test_cases"], harder=True
            )
            if any(case.display_text in self.used_questions for case in fresh):
                raise ValueError("A supposedly fresh test repeats an earlier question.")
            self.lesson(
                "Harder test on new questions",
                f"Round {round_number}: {len(fresh)} new combinations, larger numbers "
                "and deeper arithmetic paths. This test does not update the model.",
                seed=seed,
            )
            frozen_state = self.core.state
            correct = 0
            for question_index, case in enumerate(fresh, 1):
                inference = self.core.infer_composition(case)
                self._trace_composition(stage_id, "harder-new-test", case, inference)
                passed = inference.answer == case.expected_value
                correct += int(passed)
                self.bus.emit(
                    "grading", "test-case", stage=stage_id,
                    partition="harder-new-test", event_id=case.event_id,
                    question_index=question_index, question_total=len(fresh),
                    running_accuracy=correct / question_index,
                    input=case.display_text, expected=case.expected_value,
                    answer=inference.answer, result="PASS" if passed else "FAIL",
                )
                if not self._step_wait():
                    return False
            if self.core.state != frozen_state:
                raise RuntimeError("Evaluation unexpectedly changed the model.")
            score = correct / len(fresh)
            retained, _ = self._earlier_skills_retained(self.core.state)
            passed = score >= self.policy["mastery_threshold"] and retained and initial_pass
            self.report.append({
                "test": "harder-new-test", "round": round_number, "seed": seed,
                "correct": correct, "cases": len(fresh), "score": score,
                "earlier_skills_retained": retained, "original_audit_passed": initial_pass,
            })
            self.lesson(
                "Ready to advance" if passed else "More learning is needed",
                f"Harder test: {correct}/{len(fresh)} ({score:.1%}); "
                f"required: {self.policy['mastery_threshold']:.0%}. "
                f"Earlier skills retained: {retained}.",
            )
            self._remember_exam(fresh)
            self._save_teaching_report(passed)
            if passed:
                return True
            examples = (*examples, *fresh)
        return False

    def _save_teaching_report(self, passed: bool) -> None:
        _safe_write_json(self.bus.run_dir / "teaching-report.json", {
            "schema_version": 1, "supported_composition_mastered": passed,
            "tests": self.report,
            "next_missing_capabilities": [
                "word formation and meaning", "sentence formation and understanding",
                "multiplication and division learning", "language-specific source lessons",
            ],
            "source_id": SCRIPT_SOURCE_ID,
            "all_languages_learned": False,
        })

    def run(self):
        self.lesson(
            "Today's learning order",
            "Symbols and numbers, exact character handling, writing-system patterns, "
            "the reviewed notation lesson, then combinations of these paths. "
            "After each test I will show corrections and a harder fresh test.",
        )
        summary = super().run()
        self.lesson(
            "Current curriculum boundary",
            "Word and sentence learning require a sequence-learning core that has "
            "not been implemented. The language catalog is a teaching plan, not a "
            "list of languages Kavi already knows.",
        )
        return summary
