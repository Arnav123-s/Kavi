import unittest
from collections import Counter

from kavi.mixed_quizzes import exercise, mixed_questions, task_name


class MixedQuizTests(unittest.TestCase):
    def test_all_families_have_independent_exact_answers(self):
        expected = {"copy": "aBअ", "join": "aBअ", "first": "a", "last": "अ"}
        for operation, answer in expected.items():
            q = exercise(operation, "aBअ")
            self.assertEqual(q.answer, answer)
            self.assertTrue(q.correct(answer))
            self.assertFalse(q.correct("possibly " + answer))

    def test_quiz_varies_operators_scripts_and_combinations(self):
        seen = set()
        for cycle in range(20):
            rows = mixed_questions(cycle, count=32, difficulty=4, extra_characters=("अ", "ب", "ñ"), exclude=seen)
            keys = {q.key for q in rows}
            self.assertFalse(keys & seen)
            self.assertEqual(Counter(task_name(q) for q in rows), {"copy": 8, "join": 8, "first": 8, "last": 8})
            self.assertTrue(any(any(c in q.prompt for c in ("अ", "ب", "ñ")) for q in rows))
            seen.update(keys)

    def test_legacy_copy_keys_cannot_be_relabelled_fresh(self):
        from kavi.language_curriculum import letters_case
        self.assertEqual(exercise("copy", "abc").key, letters_case("abc").key)
        rows = mixed_questions(43, count=32)
        newer = mixed_questions(43, count=32, exclude={q.key for q in rows})
        self.assertFalse({q.key for q in rows} & {q.key for q in newer})

    def test_invalid_budget_is_rejected(self):
        for difficulty in (0, 2, 7):
            with self.assertRaises(ValueError):
                mixed_questions(1, difficulty=difficulty)
        with self.assertRaises(ValueError):
            mixed_questions(1, extra_characters=("two",))


if __name__ == "__main__":
    unittest.main()
