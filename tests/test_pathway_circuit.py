"""Tests for Kavi's unified path-centric circuit and live curriculum feeds."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kavi.pathway_circuit import (
    CircuitSample,
    CircuitState,
    ElementKind,
    PathwayCircuitCore,
    arithmetic_target_weights,
)
from kavi.pathway_live import (
    PathwayCurriculumRuntime,
    PathwayLiveConfig,
    _notation_sample,
    _symbol_sample,
    format_live_event,
)
from kavi.symbol_core import GlyphKind, SymbolEvent
from kavi.textbook_core import ConceptKind, TextbookEvent
from kavi.types import ArithmeticEvent, Operation


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "curriculum" / "source-manifest.json"
SOURCE_ID = "basic-algebra-with-applications-6e"


def glyph(event_id: str, value: str, target: GlyphKind) -> SymbolEvent:
    return SymbolEvent(event_id, value, target, event_id)


def notation(event_id: str, value: str, target: ConceptKind) -> TextbookEvent:
    return TextbookEvent(event_id, value, target, event_id)


class PathwayCircuitCoreTests(unittest.TestCase):
    def test_elements_are_local_circuit_roles_and_routes_hold_the_learning(self) -> None:
        core = PathwayCircuitCore()
        self.assertEqual(
            {element.kind for element in core.ELEMENTS},
            {
                ElementKind.DETECTOR,
                ElementKind.RESISTOR,
                ElementKind.SWITCH,
                ElementKind.CAPACITOR,
                ElementKind.JUNCTION,
                ElementKind.LOOP,
                ElementKind.JUMP,
                ElementKind.TRANSFORMER,
            },
        )
        samples = (
            _symbol_sample(glyph("letter", "b", GlyphKind.LETTER)),
            _symbol_sample(glyph("digit", "4", GlyphKind.DIGIT)),
        )
        candidate, delta = core.propose_category_update(samples)
        self.assertEqual(set(delta.created_route_ids), {
            "path/glyph-kind/letter",
            "path/glyph-kind/digit",
        })
        self.assertGreater(len(delta.created_adapter_ids), 0)
        core.promote(candidate)
        inference = core.infer_category(
            _symbol_sample(glyph("unseen", "7", GlyphKind.DIGIT))
        )
        self.assertEqual(inference.prediction, "digit")
        self.assertGreater(len(inference.active_adapter_ids), 0)

    def test_only_target_route_changes_and_parent_remains_frozen_until_promotion(self) -> None:
        core = PathwayCircuitCore()
        initial = (
            _symbol_sample(glyph("letter", "b", GlyphKind.LETTER)),
            _symbol_sample(glyph("digit", "4", GlyphKind.DIGIT)),
        )
        candidate, _ = core.propose_category_update(initial)
        core.promote(candidate)
        parent = core.state
        parent_digit = parent.route_map()["path/glyph-kind/digit"]
        update, delta = core.propose_category_update(
            (_symbol_sample(glyph("letter-two", "m", GlyphKind.LETTER)),)
        )
        self.assertEqual(delta.modified_route_ids, ("path/glyph-kind/letter",))
        self.assertEqual(
            update.route_map()["path/glyph-kind/digit"],
            parent_digit,
        )
        self.assertEqual(core.state, parent)

    def test_algebra_route_reuses_prior_glyph_and_arithmetic_paths(self) -> None:
        core = PathwayCircuitCore()
        glyph_candidate, _ = core.propose_category_update(
            (
                _symbol_sample(glyph("letter", "b", GlyphKind.LETTER)),
                _symbol_sample(glyph("digit", "4", GlyphKind.DIGIT)),
            )
        )
        core.promote(glyph_candidate)
        arithmetic = ArithmeticEvent("add", 1, 2, Operation.ADD, "add")
        arithmetic_candidate, _ = core.propose_arithmetic_update(
            arithmetic,
            arithmetic_target_weights(Operation.ADD),
        )
        core.promote(arithmetic_candidate)
        expression = _notation_sample(
            notation("expression", "2x + 1", ConceptKind.EXPRESSION), core
        )
        relation = _notation_sample(
            notation("relation", "2x + 1 = 7", ConceptKind.RELATION), core
        )
        candidate, _ = core.propose_category_update((expression, relation))
        sources = {
            adapter.source_path_id
            for adapter in candidate.adapters
            if adapter.target_route_id.startswith("path/notation-kind/")
        }
        self.assertIn("path/glyph-kind/letter", sources)
        self.assertIn("path/glyph-kind/digit", sources)
        self.assertIn("path/arithmetic/add", sources)

    def test_compact_state_round_trip_contains_no_prompt_text(self) -> None:
        core = PathwayCircuitCore()
        sample = CircuitSample(
            event_id="private-event",
            task_id="private-task",
            target="answer",
            feature_names=("bias", "shape"),
            features=(1.0, 0.25),
            source_activations=(("component/context-loop", 1.0),),
            display_text="private sentence that must not persist",
        )
        candidate, _ = core.propose_category_update((sample,))
        serialized = json.dumps(candidate.as_mapping())
        self.assertNotIn("private sentence", serialized)
        self.assertEqual(CircuitState.from_mapping(candidate.as_mapping()), candidate)


class PathwayLiveRuntimeTests(unittest.TestCase):
    @staticmethod
    def _digest(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    def _write_lesson(self, root: Path) -> Path:
        private = root / "private"
        lessons = private / "lessons"
        sources = private / "sources"
        extracts = private / "extracts"
        lessons.mkdir(parents=True)
        sources.mkdir()
        extracts.mkdir()
        source_body = b"pathway circuit test source"
        extract_body = b"pathway circuit test extract"
        (sources / "source.pdf").write_bytes(source_body)
        (extracts / "extract.txt").write_bytes(extract_body)
        payload = {
            "schema_version": 1,
            "lesson_id": "pathway-test-lesson",
            "source_id": SOURCE_ID,
            "source_file": "../sources/source.pdf",
            "source_file_sha256": self._digest(source_body),
            "extract_file": "../extracts/extract.txt",
            "source_extract_sha256": self._digest(extract_body),
            "locator": "local synthetic test fixture",
            "concept_id": "pathway-expression-relation",
            "prerequisites": ["glyph-kinds", "quantity-and-exact-relations"],
            "lesson_summary": "Test fixture for path composition.",
            "verifier_id": "symbolic-structure-and-safe-arithmetic",
            "attribution": "Test metadata only.",
            "events": [
                {"event_id": "t1", "partition": "train", "notation": "8", "target": "expression"},
                {"event_id": "t2", "partition": "train", "notation": "2 = 2", "target": "relation"},
                {"event_id": "t3", "partition": "train", "notation": "6 - 1", "target": "expression"},
                {"event_id": "t4", "partition": "train", "notation": "8 > 3", "target": "relation"},
                {"event_id": "t5", "partition": "train", "notation": "x + 1", "target": "expression"},
                {"event_id": "t6", "partition": "train", "notation": "x = 1", "target": "relation"},
                {"event_id": "p1", "partition": "protected", "notation": "y + 2", "target": "expression"},
                {"event_id": "p2", "partition": "protected", "notation": "y = 2", "target": "relation"},
                {"event_id": "h1", "partition": "held-out", "notation": "(5 + 3) / 2", "target": "expression"},
                {"event_id": "h2", "partition": "held-out", "notation": "1 < 1", "target": "relation"},
            ],
        }
        lesson_path = lessons / "pathway-test-lesson.json"
        lesson_path.write_text(json.dumps(payload), encoding="utf-8")
        return lesson_path

    def test_full_finite_run_uses_separate_feeds_and_external_parent_archives(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lesson_path = self._write_lesson(root)
            run_dir = root / "runs" / "live"
            runtime = PathwayCurriculumRuntime(
                PathwayLiveConfig(
                    run_dir=run_dir,
                    lesson_path=lesson_path,
                    source_manifest_path=MANIFEST_PATH,
                    interval_ms=0,
                    start_delay_seconds=0,
                ),
                emit=lambda _: None,
            )
            summary = runtime.run()
            active_state_text = (run_dir / "model-state.json").read_text(encoding="utf-8")
            grading_text = (run_dir / "grading.jsonl").read_text(encoding="utf-8")
            learning_events = [
                json.loads(line)
                for line in (run_dir / "learning.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            pathway_text = (run_dir / "pathways.jsonl").read_text(encoding="utf-8")
            archives = sorted((run_dir / "archive").glob("parent-*.json"))
            first_archive = json.loads(archives[0].read_text(encoding="utf-8"))

        self.assertFalse(summary.stopped)
        self.assertEqual(len(summary.completed_stage_ids), 5)
        self.assertEqual(summary.routes, 17)
        self.assertGreater(summary.jump_adapters, 0)
        self.assertNotIn("2 = 2", active_state_text)
        self.assertIn('"result": "PASS"', grading_text)
        self.assertIn("curriculum-boundary", grading_text)
        self.assertIn("path/glyph-kind/digit", pathway_text)
        last_promotion = [
            event
            for event in learning_events
            if event.get("kind") == "candidate-change" and event.get("decision") == "PROMOTED"
        ][-1]
        self.assertEqual(last_promotion["model_routes"], summary.routes)
        self.assertEqual(last_promotion["model_jump_adapters"], summary.jump_adapters)
        self.assertGreater(len(archives), 0)
        self.assertFalse(first_archive["active_during_inference"])

    def test_existing_stop_control_prevents_the_first_stage(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lesson_path = self._write_lesson(root)
            stop_file = root / "stop"
            stop_file.write_text("stop", encoding="utf-8")
            summary = PathwayCurriculumRuntime(
                PathwayLiveConfig(
                    run_dir=root / "runs" / "stopped",
                    lesson_path=lesson_path,
                    source_manifest_path=MANIFEST_PATH,
                    interval_ms=0,
                    start_delay_seconds=0,
                    stop_file=stop_file,
                ),
                emit=lambda _: None,
            ).run()
        self.assertTrue(summary.stopped)
        self.assertEqual(summary.completed_stage_ids, ())

    def test_archive_event_is_explicitly_outside_inference(self) -> None:
        text = format_live_event(
            {
                "channel": "learning",
                "kind": "parent-archived",
                "stage": "test-stage",
                "archive": "parent-0001.json",
                "active_during_inference": False,
            }
        )
        self.assertIn("outside the active brain", text)
        self.assertIn("False", text)


if __name__ == "__main__":
    unittest.main()
