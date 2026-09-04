"""Tests for Kavi's finite source-gated adaptive syllabus loop."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kavi.adaptive_syllabus import (
    AdaptiveRuntimeConfig,
    AdaptiveStudyState,
    AdaptiveSyllabus,
    AdaptiveSyllabusRuntime,
)
from kavi.textbook_core import TextbookConceptPathwayCore


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "curriculum" / "source-manifest.json"
SOURCE_ID = "basic-algebra-with-applications-6e"


class AdaptiveSyllabusTests(unittest.TestCase):
    @staticmethod
    def _digest(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    def _write_private_lesson(self, root: Path, lesson_id: str = "adaptive-test-lesson") -> Path:
        private = root / "private"
        lessons = private / "lessons"
        sources = private / "sources"
        extracts = private / "extracts"
        lessons.mkdir(parents=True)
        sources.mkdir()
        extracts.mkdir()
        source_body = b"adaptive test source"
        extract_body = b"adaptive test extract"
        (sources / "source.pdf").write_bytes(source_body)
        (extracts / "extract.txt").write_bytes(extract_body)
        payload = {
            "schema_version": 1,
            "lesson_id": lesson_id,
            "source_id": SOURCE_ID,
            "source_file": "../sources/source.pdf",
            "source_file_sha256": self._digest(source_body),
            "extract_file": "../extracts/extract.txt",
            "source_extract_sha256": self._digest(extract_body),
            "locator": "local test page",
            "concept_id": "expression-relation-classification",
            "prerequisites": [],
            "lesson_summary": "Test only: distinguish two symbolic categories.",
            "verifier_id": "symbolic-structure-and-safe-arithmetic",
            "attribution": "Test metadata only.",
            "events": [
                {"event_id": "train-e1", "partition": "train", "notation": "8", "target": "expression"},
                {"event_id": "train-r1", "partition": "train", "notation": "2 = 2", "target": "relation"},
                {"event_id": "train-e2", "partition": "train", "notation": "6 - 1", "target": "expression"},
                {"event_id": "train-r2", "partition": "train", "notation": "8 > 3", "target": "relation"},
                {"event_id": "protected-e", "partition": "protected", "notation": "x + 1", "target": "expression"},
                {"event_id": "protected-r", "partition": "protected", "notation": "x = 1", "target": "relation"},
                {"event_id": "held-e", "partition": "held-out", "notation": "(5 + 3) / 2", "target": "expression"},
                {"event_id": "held-r", "partition": "held-out", "notation": "1 < 1", "target": "relation"},
            ],
        }
        path = lessons / f"{lesson_id}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    @staticmethod
    def _write_syllabus(
        root: Path,
        *,
        lesson_id: str,
        max_attempts: int = 2,
    ) -> Path:
        syllabus_dir = root / "private" / "syllabi"
        syllabus_dir.mkdir(parents=True)
        payload = {
            "schema_version": 1,
            "syllabus_id": "adaptive-test-v1",
            "title": "Adaptive test syllabus",
            "seed": 17,
            "minimum_protected_accuracy": 0.9,
            "minimum_held_out_accuracy": 0.9,
            "evaluation_cases_per_partition": 2,
            "default_max_attempts": max_attempts,
            "units": [
                {
                    "unit_id": "symbolic-foundation",
                    "title": "Test symbolic foundation",
                    "lesson_id": lesson_id,
                    "repair_lesson_ids": [],
                    "prerequisites": [],
                }
            ],
        }
        path = syllabus_dir / "adaptive-test.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_adaptive_pass_checkpoints_compact_state_and_visible_grades(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lesson_path = self._write_private_lesson(root)
            syllabus_path = self._write_syllabus(root, lesson_id=lesson_path.stem)
            state_path = root / "runs" / "adaptive-state.json"
            trace: list[str] = []
            runtime = AdaptiveSyllabusRuntime(
                AdaptiveRuntimeConfig(
                    syllabus_path=syllabus_path,
                    source_manifest_path=MANIFEST_PATH,
                    lesson_root=root / "private" / "lessons",
                    state_file=state_path,
                    interval_ms=0,
                ),
                emit=trace.append,
            )
            summary = runtime.run()
            state = AdaptiveStudyState.load(state_path)

        self.assertFalse(summary.stopped)
        self.assertEqual(summary.completed_unit_ids, ("symbolic-foundation",))
        self.assertEqual(summary.results[-1].outcome, "mastered")
        self.assertEqual(summary.results[-1].protected_accuracy, 1.0)
        self.assertEqual(summary.results[-1].held_out_accuracy, 1.0)
        self.assertEqual(state.completed_unit_ids, ("symbolic-foundation",))
        self.assertEqual(state.model_state.expression.support, 2)
        self.assertEqual(state.model_state.relation.support, 2)
        serialized = json.dumps(state.as_mapping())
        self.assertNotIn("2 = 2", serialized)
        self.assertIn("[test] protected", "\n".join(trace))
        self.assertIn("[grade] PASS", "\n".join(trace))

    def test_failed_gate_needs_a_reviewed_repair_lesson(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lesson_path = self._write_private_lesson(root)
            syllabus_path = self._write_syllabus(
                root,
                lesson_id=lesson_path.stem,
                max_attempts=2,
            )
            original_confidence = TextbookConceptPathwayCore.MINIMUM_CONFIDENCE
            TextbookConceptPathwayCore.MINIMUM_CONFIDENCE = 1.01
            try:
                summary = AdaptiveSyllabusRuntime(
                    AdaptiveRuntimeConfig(
                        syllabus_path=syllabus_path,
                        source_manifest_path=MANIFEST_PATH,
                        lesson_root=root / "private" / "lessons",
                        interval_ms=0,
                    ),
                    emit=lambda _: None,
                ).run()
            finally:
                TextbookConceptPathwayCore.MINIMUM_CONFIDENCE = original_confidence

        self.assertFalse(summary.stopped)
        self.assertEqual(summary.completed_unit_ids, ())
        self.assertEqual(summary.results[-1].outcome, "needs-reviewed-repair-lesson")

    def test_syllabus_rejects_primary_lesson_reused_as_repair(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "syllabus_id": "invalid",
                        "title": "Invalid syllabus",
                        "units": [
                            {
                                "unit_id": "unit",
                                "title": "Unit",
                                "lesson_id": "lesson",
                                "repair_lesson_ids": ["lesson"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                AdaptiveSyllabus.load(path)


if __name__ == "__main__":
    unittest.main()
