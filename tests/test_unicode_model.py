"""Tests for Kavi's exact-scalar and generated script-pathway stages."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kavi.school import CurriculumPlan, ModelSchool, SchoolConfig
from kavi.unicode_core import UnicodeSignalContract
from kavi.unicode_runtime import (
    UnicodeContractRuntime,
    UnicodeContractRuntimeConfig,
    UnicodeScriptCurriculum,
    UnicodeScriptRuntime,
    UnicodeScriptRuntimeConfig,
    held_out_manifest,
    protected_manifest,
)
from kavi.unicode_core import UnicodeScriptEvaluator, UnicodeScriptPathwayCore


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "curriculum" / "model-curriculum.json"


class UnicodeSignalContractTests(unittest.TestCase):
    def test_contract_preserves_visually_similar_scalars_as_distinct_inputs(self) -> None:
        latin = UnicodeSignalContract.inspect("A")
        greek = UnicodeSignalContract.inspect("\u0391")
        cyrillic = UnicodeSignalContract.inspect("\u0410")
        self.assertEqual((latin.code_point, greek.code_point, cyrillic.code_point), (0x41, 0x391, 0x410))
        self.assertEqual((latin.glyph, greek.glyph, cyrillic.glyph), ("A", "\u0391", "\u0410"))
        self.assertEqual(tuple(chr(signal.code_point) for signal in (latin, greek, cyrillic)), ("A", "\u0391", "\u0410"))

    def test_contract_never_replaces_input_with_a_normalized_value(self) -> None:
        signal = UnicodeSignalContract.inspect("\u0340")
        self.assertEqual(signal.glyph, "\u0340")
        self.assertEqual(signal.code_point, 0x0340)
        self.assertFalse(signal.nfc_matches_input)

    def test_contract_rejects_non_scalars_but_accepts_a_combining_mark(self) -> None:
        self.assertEqual(UnicodeSignalContract.inspect("\u0301").code_point, 0x0301)
        for value in ("", "ab", "\ud800"):
            with self.assertRaises(ValueError):
                UnicodeSignalContract.inspect(value)

    def test_finite_contract_runtime_passes_fixed_checks(self) -> None:
        runtime = UnicodeContractRuntime(
            UnicodeContractRuntimeConfig(interval_ms=0),
            emit=lambda _: None,
        )
        summary = runtime.run()
        self.assertFalse(summary.stopped)
        self.assertEqual(summary.protected.exact_accuracy, 1.0)
        self.assertEqual(summary.held_out.exact_accuracy, 1.0)


class UnicodeScriptCoreTests(unittest.TestCase):
    def test_balanced_candidate_compresses_one_lesson_per_pathway(self) -> None:
        core = UnicodeScriptPathwayCore()
        curriculum = UnicodeScriptCurriculum(seed=1)
        lessons = tuple(curriculum.event_at(step) for step in range(1, 12))
        evaluator = UnicodeScriptEvaluator(
            protected=protected_manifest(),
            held_out=held_out_manifest(),
        )
        assessment = evaluator.assess(core, lessons)
        self.assertTrue(assessment.accepted)
        self.assertEqual(assessment.candidate_state.total_support, 11)
        core.promote(assessment.candidate_state)
        self.assertEqual(evaluator.evaluate(core, evaluator.protected).exact_accuracy, 1.0)
        self.assertEqual(evaluator.evaluate(core, evaluator.held_out).exact_accuracy, 1.0)
        self.assertEqual(core.resource_ledger()["persistent_scalars"], 23)

    def test_curriculum_is_fixed_and_script_balanced(self) -> None:
        first = UnicodeScriptCurriculum(seed=1)
        second = UnicodeScriptCurriculum(seed=999)
        first_events = tuple(first.event_at(step) for step in range(1, 12))
        second_events = tuple(second.event_at(step) for step in range(1, 12))
        self.assertEqual(first_events, second_events)
        self.assertEqual(
            tuple(event.target.value for event in first_events),
            (
                "latin",
                "greek",
                "cyrillic",
                "arabic",
                "devanagari",
                "bengali",
                "tamil",
                "hiragana",
                "katakana",
                "han",
                "hangul",
            ),
        )

    def test_finite_runtime_keeps_protected_and_held_out_checks(self) -> None:
        runtime = UnicodeScriptRuntime(
            UnicodeScriptRuntimeConfig(steps=22, batch_size=11, interval_ms=0),
            emit=lambda _: None,
        )
        summary = runtime.run()
        self.assertFalse(summary.stopped)
        self.assertGreaterEqual(summary.promoted_candidates, 1)
        self.assertEqual(summary.protected.exact_accuracy, 1.0)
        self.assertEqual(summary.held_out.exact_accuracy, 1.0)


class UnicodeSchoolIntegrationTests(unittest.TestCase):
    def test_plan_exposes_only_source_free_unicode_stages_as_runnable(self) -> None:
        plan = CurriculumPlan.load(PLAN_PATH)
        contract, scripts = plan.stages[2:4]
        self.assertEqual((contract.status, scripts.status), ("runnable", "runnable"))
        self.assertEqual(
            (contract.engine, scripts.engine),
            ("unicode-scalar-contract", "unicode-script-prototypes"),
        )
        self.assertEqual((contract.source_ids, scripts.source_ids), ((), ()))

    def test_school_can_complete_four_generated_stages_in_an_isolated_checkpoint(self) -> None:
        with TemporaryDirectory() as directory:
            state_path = Path(directory) / "school-state.json"
            school = ModelSchool(
                SchoolConfig(
                    plan_path=PLAN_PATH,
                    max_stages=4,
                    lessons_per_stage=12,
                    symbol_batch_size=8,
                    interval_ms=0,
                    state_file=state_path,
                ),
                emit=lambda _: None,
            )
            summary = school.run()
        self.assertFalse(summary.stopped)
        self.assertEqual(
            summary.completed_stage_ids,
            (
                "glyph-kinds",
                "quantity-and-exact-relations",
                "unicode-signal-contract",
                "multiscript-glyph-foundations",
            ),
        )
        self.assertEqual(len(summary.results), 4)
        self.assertTrue(all(result.outcome == "passed" for result in summary.results))


if __name__ == "__main__":
    unittest.main()
