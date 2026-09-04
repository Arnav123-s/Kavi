"""End-to-end checks of corrections, fresh exams, and visible teaching."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from kavi.composition_evaluation import final_audit_manifest
from kavi.developmental import DevelopmentalRuntime
from kavi.friendly_live import format_event
from kavi.pathway_live import PathwayLiveConfig
from kavi.script_reference import ScriptReference
import test_pathway_circuit as fixtures


ROOT = Path(__file__).resolve().parents[1]


class DevelopmentalTeachingTests(unittest.TestCase):
    def test_corrective_teaching_improves_without_forgetting(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lesson = fixtures.PathwayLiveRuntimeTests()._write_lesson(root)
            run_dir = root / "run"
            # A local source fixture; the real CLI run verifies the original file.
            reference = ScriptReference(((0x4E00, 0x9FFF, "han"),))
            with patch("kavi.developmental.ScriptReference.load", return_value=reference):
                runtime = DevelopmentalRuntime(
                    PathwayLiveConfig(
                        run_dir=run_dir, lesson_path=lesson,
                        source_manifest_path=ROOT / "curriculum/source-manifest.json",
                        interval_ms=0, start_delay_seconds=0,
                    ),
                    policy_path=ROOT / "curriculum/teaching-policy.json",
                    script_source=root / "fixture.txt", emit=lambda _: None,
                )
            result = runtime.run()
            report = json.loads((run_dir / "teaching-report.json").read_text())
            changes = [
                json.loads(line) for line in
                (run_dir / "learning.jsonl").read_text().splitlines()
            ]
            corrections = [
                event for event in changes
                if event.get("stage") == "corrective-teaching"
                and event["kind"] == "candidate-change"
            ]
            self.assertFalse(result.failed)
            self.assertEqual(len(result.completed_stage_ids), 6)
            self.assertEqual(report["tests"][0]["score"], 62 / 64)
            self.assertEqual(report["tests"][-1]["score"], 1.0)
            self.assertTrue(report["tests"][-1]["earlier_skills_retained"])
            self.assertFalse(report["all_languages_learned"])
            self.assertEqual(len(corrections), 1)
            self.assertEqual(corrections[0]["decision"], "PROMOTED")
            self.assertEqual(corrections[0]["created_routes"], [])
            self.assertEqual(corrections[0]["modified_routes"], ["path/unicode-script/han"])
            state = runtime.core.state
            self.assertEqual(runtime.core.evaluate_compositions(final_audit_manifest()).errors, 0)
            self.assertEqual(runtime.core.state, state)

    def test_harder_exam_has_no_repeated_whole_questions(self):
        original = {item.display_text for item in final_audit_manifest()}
        fresh = final_audit_manifest(seed=20260905, harder=True)
        self.assertEqual(len(fresh), 64)
        self.assertTrue(original.isdisjoint(item.display_text for item in fresh))

    def test_reference_requires_matching_fingerprint(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "script.txt"
            data = b"4E00..9FFF ; Han # fixture\nAC00..D7A3 ; Hangul\n"
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                ScriptReference.load(path)
            reference = ScriptReference.load(path, hashlib.sha256(data).hexdigest())
            self.assertEqual(reference.label("語"), "han")
            alternatives = reference.alternatives("語", {"誟"})
            self.assertEqual(len(alternatives), 2)
            self.assertNotIn("語", alternatives)
            self.assertNotIn("誟", alternatives)

    def test_teaching_view_distinguishes_instruction_from_model_output(self):
        text = format_event({
            "channel": "lessons", "kind": "teaching-step",
            "title": "Different example", "detail": "Teach a different character.",
            "source_id": "unicode-17-script-property",
        })
        self.assertIn("Different example", text)
        self.assertIn("Source:", text)
        answer = format_event({
            "channel": "answers", "kind": "model-answer", "input": "add(1,2)",
            "answer": 3, "expected": 3,
        })
        self.assertIn("Kavi answered: 3", answer)
        self.assertIn("Checked answer: 3", answer)


if __name__ == "__main__":
    unittest.main()
