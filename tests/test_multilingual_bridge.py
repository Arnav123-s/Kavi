"""Engineering tests; mock results do not demonstrate multilingual ability."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import Mock

from kavi.language_curriculum import LETTERS, LanguageExample, letters_case
from kavi.multilingual_bridge import MultilingualBridgeTeacher, reserved_bank, sequence_practice


class BridgeCurriculumTests(unittest.TestCase):
    def test_reserved_banks_are_separate_and_excluded_from_practice(self):
        old = {letters_case("abc").key, letters_case("ABCD").key}
        banks = reserved_bank(4301, old, count=32)
        rows = [LanguageExample(**q) for group in banks.values() for q in group]
        keys = {q.key for q in rows}
        self.assertEqual(len(keys), 64)
        self.assertFalse(keys & old)
        self.assertEqual(banks, reserved_bank(4301, old, count=32))
        for cycle in range(10):
            practice = sequence_practice(cycle, keys, max_length=4)
            self.assertFalse({q.key for q in practice} & keys)
            self.assertTrue(all(q.correct(q.answer) for q in practice))

    def test_writing_lanes_are_explicit_limited_subsets(self):
        path = Path(__file__).resolve().parents[1] / "curriculum/multilingual-bridge.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual({lane["language_goal"] for lane in data["lanes"]}, {"Hindi", "Arabic", "Spanish"})
        for lane in data["lanes"]:
            self.assertEqual(len(set(lane["characters"])), len(lane["characters"]))
            self.assertTrue(all(len(c) == 1 for c in lane["characters"]))
            self.assertIn("not", lane["scope"].lower())
        self.assertEqual(data["lanes"][1]["direction"], "rtl")

    def test_unicode_targets_preserve_exact_written_form(self):
        for text in ("अ", "आ", "بت", "ñ", "é"):
            q = letters_case(text)
            self.assertTrue(q.correct(text))
            self.assertFalse(q.correct("other " + text))
        # This stage tests exact stored forms, not normalization equivalence.
        self.assertFalse(letters_case("é").correct("e\u0301"))

    def test_rehearsal_covers_all_previously_learned_scripts(self):
        teacher = object.__new__(MultilingualBridgeTeacher)
        teacher.bridge = {"lanes": {
            "hindi": {"correct_characters": ["अ", "आ"]},
            "arabic": {"correct_characters": ["ا", "ب"]},
            "spanish": {"correct_characters": ["ñ", "é"]}}}
        rows = teacher.script_rehearsal()
        self.assertEqual({q.answer for q in rows}, {"अ", "आ", "ا", "ب", "ñ", "é"})
        self.assertEqual(len(rows), 6)

    def test_reserved_answer_cannot_enter_automatic_training(self):
        teacher = object.__new__(MultilingualBridgeTeacher)
        q = letters_case("abc")
        teacher.reserved_keys = {q.key}
        teacher.bridge = {"invalidated_bank_keys": []}
        with self.assertRaises(ValueError):
            teacher.teach_examples([q])

    def test_candidate_save_does_not_publish_an_unaccepted_model(self):
        teacher = object.__new__(MultilingualBridgeTeacher)
        teacher.candidate_active = True
        # No other state exists. Returning without saving is the required behavior.
        teacher.save("periodic")
        teacher.save("exception-recovery")

    def test_audit_uses_only_questions_and_cannot_update_parameters(self):
        teacher = object.__new__(MultilingualBridgeTeacher)
        teacher.core = Mock()
        teacher.core.fingerprint.return_value = "frozen"
        teacher.core.generate.return_value = "अ"
        teacher.core.updates = 50
        teacher.control = Mock(return_value=True)
        teacher.emit = Mock()
        score, correct = teacher.audit("Hindi subset", [letters_case("अ")], show_answers=True)
        self.assertEqual(score, 1)
        self.assertEqual(len(correct), 1)
        teacher.core.generate.assert_called_once_with("Copy अ => ", max_bytes=24)
        teacher.core.learn.assert_not_called()
        teacher.core.learn_answers.assert_not_called()


if __name__ == "__main__":
    unittest.main()
