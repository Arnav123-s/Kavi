"""Tests for Kavi's bounded, locally reviewed textbook-concept stage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kavi.source_manifest import SourceManifest
from kavi.textbook_core import (
    ConceptKind,
    TextbookConceptEvaluator,
    TextbookConceptPathwayCore,
    TextbookEvent,
    notation_kind,
    response_text,
    semantic_outcome,
)
from kavi.textbook_runtime import LocalTextbookLesson, TextbookConceptRuntime, TextbookRuntimeConfig


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "curriculum" / "source-manifest.json"
SOURCE_ID = "basic-algebra-with-applications-6e"


def event(event_id: str, notation: str, target: ConceptKind) -> TextbookEvent:
    """Build a source-free test event checked by the structural verifier."""

    return TextbookEvent(
        event_id=event_id,
        notation=notation,
        target=target,
        correlation_id=event_id,
    )


class TextbookConceptCoreTests(unittest.TestCase):
    def test_independent_symbolic_verifier_has_exact_bounded_outcomes(self) -> None:
        self.assertIs(notation_kind("5 + 2"), ConceptKind.EXPRESSION)
        self.assertIs(notation_kind("5 = 2 + 3"), ConceptKind.RELATION)
        self.assertEqual(semantic_outcome("5 + 2"), "value=7")
        self.assertEqual(semantic_outcome("5 = 2 + 3"), "truth=true")
        self.assertEqual(semantic_outcome("1 < 1"), "truth=false")
        self.assertEqual(
            semantic_outcome("x = 1"),
            "truth is unknown without variable values",
        )

    def test_candidate_gate_retains_only_compact_prototypes(self) -> None:
        core = TextbookConceptPathwayCore()
        train = (
            event("train-expression-one", "8", ConceptKind.EXPRESSION),
            event("train-relation-one", "2 = 2", ConceptKind.RELATION),
            event("train-expression-two", "6 - 1", ConceptKind.EXPRESSION),
            event("train-relation-two", "8 > 3", ConceptKind.RELATION),
        )
        evaluator = TextbookConceptEvaluator(
            protected=(
                event("protected-expression", "x + 1", ConceptKind.EXPRESSION),
                event("protected-relation", "x = 1", ConceptKind.RELATION),
            ),
            held_out=(
                event("held-expression", "(5 + 3) / 2", ConceptKind.EXPRESSION),
                event("held-relation", "1 < 1", ConceptKind.RELATION),
            ),
        )

        assessment = evaluator.assess(core, train)
        self.assertTrue(assessment.accepted)
        core.promote(assessment.candidate_state)

        self.assertEqual(core.state.expression.support, 2)
        self.assertEqual(core.state.relation.support, 2)
        self.assertEqual(evaluator.evaluate(core, evaluator.protected).exact_accuracy, 1.0)
        self.assertEqual(evaluator.evaluate(core, evaluator.held_out).exact_accuracy, 1.0)
        inference = core.infer(evaluator.held_out[0])
        self.assertEqual(response_text(inference), "expression; value=4")
        self.assertNotIn("held-expression", repr(core.state))

    def test_declared_label_cannot_override_the_structure_verifier(self) -> None:
        with self.assertRaises(ValueError):
            event("invalid", "1 = 1", ConceptKind.EXPRESSION)


class LocalTextbookRuntimeTests(unittest.TestCase):
    @staticmethod
    def _digest(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    def _write_lesson(self, root: Path, *, source_hash: str | None = None) -> Path:
        private = root / "private"
        lessons = private / "lessons"
        sources = private / "sources"
        extracts = private / "extracts"
        lessons.mkdir(parents=True)
        sources.mkdir()
        extracts.mkdir()
        source_body = b"private approved source test file"
        extract_body = b"private reviewed lesson extract"
        source_path = sources / "source.pdf"
        extract_path = extracts / "extract.txt"
        source_path.write_bytes(source_body)
        extract_path.write_bytes(extract_body)
        lesson = {
            "schema_version": 1,
            "lesson_id": "test-textbook-lesson",
            "source_id": SOURCE_ID,
            "source_file": "../sources/source.pdf",
            "source_file_sha256": source_hash or self._digest(source_body),
            "extract_file": "../extracts/extract.txt",
            "source_extract_sha256": self._digest(extract_body),
            "locator": "test pages",
            "concept_id": "test-expression-relation",
            "prerequisites": ["glyph-kinds"],
            "lesson_summary": "Test only: verify a compact symbolic distinction.",
            "verifier_id": "symbolic-structure-and-safe-arithmetic",
            "attribution": "Test metadata only; no source body is public.",
            "events": [
                {"event_id": "t1", "partition": "train", "notation": "8", "target": "expression"},
                {"event_id": "t2", "partition": "train", "notation": "2 = 2", "target": "relation"},
                {"event_id": "t3", "partition": "train", "notation": "6 - 1", "target": "expression"},
                {"event_id": "t4", "partition": "train", "notation": "8 > 3", "target": "relation"},
                {"event_id": "p1", "partition": "protected", "notation": "x + 1", "target": "expression"},
                {"event_id": "p2", "partition": "protected", "notation": "x = 1", "target": "relation"},
                {"event_id": "h1", "partition": "held-out", "notation": "(5 + 3) / 2", "target": "expression"},
                {"event_id": "h2", "partition": "held-out", "notation": "1 < 1", "target": "relation"},
            ],
        }
        lesson_path = lessons / "test-textbook-lesson.json"
        lesson_path.write_text(json.dumps(lesson), encoding="utf-8")
        return lesson_path

    def test_runtime_verifies_private_fingerprints_and_emits_a_finite_trace(self) -> None:
        with TemporaryDirectory() as directory:
            lesson_path = self._write_lesson(Path(directory))
            lines: list[str] = []
            runtime = TextbookConceptRuntime(
                TextbookRuntimeConfig(
                    lesson_path=lesson_path,
                    source_manifest_path=MANIFEST_PATH,
                    interval_ms=0,
                ),
                emit=lines.append,
            )
            summary = runtime.run()

        trace = "\n".join(lines)
        self.assertFalse(summary.stopped)
        self.assertEqual(summary.completed_steps, 4)
        self.assertEqual(summary.promoted_candidates, 2)
        self.assertEqual(summary.protected.exact_accuracy, 1.0)
        self.assertEqual(summary.held_out.exact_accuracy, 1.0)
        self.assertIn("reviewed textbook-concept trace", trace)
        self.assertNotIn("private reviewed lesson extract", trace)

    def test_runtime_rejects_a_source_fingerprint_mismatch(self) -> None:
        with TemporaryDirectory() as directory:
            lesson_path = self._write_lesson(Path(directory), source_hash="0" * 64)
            manifest = SourceManifest.load(MANIFEST_PATH)
            with self.assertRaises(ValueError):
                LocalTextbookLesson.load(lesson_path, manifest)


if __name__ == "__main__":
    unittest.main()
