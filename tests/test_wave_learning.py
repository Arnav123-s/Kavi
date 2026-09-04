from dataclasses import asdict
import importlib.util
from pathlib import Path
import tempfile
import unittest

from kavi.book_curriculum import Question, UNITS, number_words, questions, split_paragraphs


class BookCurriculumTests(unittest.TestCase):
    def test_source_split_has_no_shared_paragraph(self):
        paragraphs = [f"Original paragraph {i} is distinct." for i in range(40)]
        split = split_paragraphs(paragraphs, 43)
        self.assertEqual(split, split_paragraphs(paragraphs, 43))
        groups = [set(v) for v in split.values()]
        self.assertEqual(sum(map(len, groups)), len(paragraphs))
        self.assertFalse(groups[0] & groups[1] or groups[1] & groups[2] or groups[0] & groups[2])

    def test_every_unit_has_fresh_answerable_questions(self):
        for unit, _, _ in UNITS:
            train = questions(unit, 3, 16)
            validation = questions(unit, 8, 16, exclude={q.key for q in train})
            harder = questions(unit, 10, 16, harder=True, exclude={q.key for q in train + validation})
            self.assertEqual(len({q.key for q in train + validation + harder}), 48)
            for q in train + validation + harder:
                self.assertTrue(q.correct(q.answer))
                self.assertFalse(q.correct("nonsense " + q.answer))
                self.assertFalse(q.correct(q.answer + " and another answer"))

    def test_numeric_grading_is_exact(self):
        q = Question("A half?", "1/2", "Two equal parts.")
        self.assertTrue(q.correct("0.5"))
        for wrong in ("1/0", "0.5001", "probably 1/2", "1/2 1/3", "NaN"):
            self.assertFalse(q.correct(wrong))
        self.assertEqual(number_words(306), "three hundred and six")


@unittest.skipUnless(importlib.util.find_spec("torch"), "Optional wave dependency not installed")
class WaveCoreTests(unittest.TestCase):
    def core(self):
        from kavi.wave_core import WaveConfig, WaveLearner
        return WaveLearner(WaveConfig(nodes=16, fan_in=3, hops=1, threads=1, sequence_length=32))

    def test_internal_learning_changes_routes_without_growth(self):
        import torch
        core = self.core()
        before = core.fingerprint()
        phase = core.network.phase.detach().clone()
        gates = core.network.edge_logits.detach().clone()
        size = core.ledger()["parameters"]
        for _ in range(2):
            core.learn("One and one make two. Two and one make three.\n")
        self.assertNotEqual(core.fingerprint(), before)
        self.assertFalse(torch.equal(phase, core.network.phase))
        self.assertFalse(torch.equal(gates, core.network.edge_logits))
        self.assertEqual(core.ledger()["parameters"], size)
        self.assertFalse(core.ledger()["infinite_memory"])

    def test_inference_and_measurement_do_not_teach_their_own_answers(self):
        core = self.core()
        before, updates = core.fingerprint(), core.updates
        parts = []
        answer = core.generate("Question: a+b?\nAnswer: ", max_bytes=12, on_token=parts.append)
        metrics = core.measure("Original text, not used to update this model.")
        self.assertEqual(before, core.fingerprint())
        self.assertEqual(updates, core.updates)
        self.assertLessEqual(sum(map(len, parts)), 12)
        self.assertIsInstance(answer, str)
        self.assertGreater(metrics["bits_per_byte"], 0)

    def test_checkpoint_preserves_predictions_and_optimizer_state(self):
        from kavi.wave_core import WaveLearner
        core = self.core()
        core.learn("Language, numbers and arithmetic.\n")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "learner.pt"
            core.save(path)
            restored = WaveLearner.load(path)
            self.assertEqual(core.fingerprint(), restored.fingerprint())
            self.assertEqual(core.generate("Numbers", max_bytes=8), restored.generate("Numbers", max_bytes=8))
            self.assertEqual(core.ledger(), restored.ledger())
            core.learn("Another lesson.\n")
            restored.learn("Another lesson.\n")
            self.assertEqual(core.fingerprint(), restored.fingerprint())

    def test_early_stop_and_supervision_boundary(self):
        core = self.core()
        result = core.learn("a" * 200, callback=lambda _: False)
        self.assertTrue(result["interrupted"])
        self.assertEqual(core.updates, 1)
        with self.assertRaises(ValueError):
            core.learn("short", answer_start=10)
        with self.assertRaises(ValueError):
            core.generate("x", max_bytes=1000)

    def test_local_correction_reduces_training_loss(self):
        core = self.core()
        text = "Question: one plus one?\nAnswer: 2\n"
        before = core.measure(text)["bits_per_byte"]
        for _ in range(12):
            core.learn(text)
        self.assertLess(core.measure(text)["bits_per_byte"], before)
        # This is a training-fit check, not a held-out intelligence claim.


if __name__ == "__main__":
    unittest.main()
