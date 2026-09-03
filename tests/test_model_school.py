"""Tests for the model-first generated curriculum and its hard stopping gates."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kavi.school import CurriculumPlan, ModelSchool, SchoolConfig
from kavi.symbol_core import SymbolEvaluator, SymbolPathwayCore
from kavi.symbol_runtime import (
    SymbolCurriculum,
    SymbolRuntime,
    SymbolRuntimeConfig,
    held_out_manifest,
    protected_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "curriculum" / "model-curriculum.json"


class SymbolCoreTests(unittest.TestCase):
    def test_candidate_compresses_generated_lessons_into_prototypes(self) -> None:
        core = SymbolPathwayCore()
        curriculum = SymbolCurriculum(seed=7)
        lessons = tuple(curriculum.event_at(step) for step in range(1, 9))
        evaluator = SymbolEvaluator(
            protected=protected_manifest(),
            held_out=held_out_manifest(),
        )
        assessment = evaluator.assess(core, lessons)
        self.assertTrue(assessment.accepted)
        self.assertEqual(assessment.candidate_state.letter.support, 4)
        self.assertEqual(assessment.candidate_state.digit.support, 4)
        core.promote(assessment.candidate_state)
        self.assertEqual(
            evaluator.evaluate(core, evaluator.held_out).exact_accuracy,
            1.0,
        )
        self.assertEqual(core.resource_ledger()["persistent_scalars"], 5)

    def test_finite_symbol_runtime_preserves_held_out_cases(self) -> None:
        runtime = SymbolRuntime(
            SymbolRuntimeConfig(steps=8, batch_size=8, interval_ms=0),
            emit=lambda _: None,
        )
        summary = runtime.run()
        self.assertFalse(summary.stopped)
        self.assertGreaterEqual(summary.promoted_candidates, 1)
        self.assertEqual(summary.protected.exact_accuracy, 1.0)
        self.assertEqual(summary.held_out.exact_accuracy, 1.0)


class ModelSchoolTests(unittest.TestCase):
    def test_plan_orders_runnable_foundations_before_waiting_text_stage(self) -> None:
        plan = CurriculumPlan.load(PLAN_PATH)
        self.assertEqual(plan.stages[0].stage_id, "glyph-kinds")
        self.assertEqual(plan.stages[1].stage_id, "quantity-and-exact-relations")
        self.assertEqual(plan.stages[2].status, "awaiting-model-capability")

    def test_school_checkpoints_only_after_passing_finite_stages(self) -> None:
        with TemporaryDirectory() as directory:
            state_path = Path(directory) / "school-state.json"
            school = ModelSchool(
                SchoolConfig(
                    plan_path=PLAN_PATH,
                    max_stages=3,
                    lessons_per_stage=12,
                    symbol_batch_size=8,
                    interval_ms=0,
                    state_file=state_path,
                ),
                emit=lambda _: None,
            )
            summary = school.run()
            restored = ModelSchool(
                SchoolConfig(plan_path=PLAN_PATH, state_file=state_path),
                emit=lambda _: None,
            )
        self.assertFalse(summary.stopped)
        self.assertEqual(
            summary.completed_stage_ids,
            ("glyph-kinds", "quantity-and-exact-relations"),
        )
        self.assertEqual(summary.results[-1].outcome, "waiting")
        self.assertEqual(restored.state.completed_stage_ids, summary.completed_stage_ids)


if __name__ == "__main__":
    unittest.main()
