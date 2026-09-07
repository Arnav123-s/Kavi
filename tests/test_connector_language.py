from dataclasses import replace
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from kavi.grounded_language import LanguageModel, tokens
from kavi.procedure_core import Limits, ProcedureLibrary, Procedure, ExecutionLimit
from kavi.procedure_optimizations import compile_product

ROOT = Path(__file__).resolve().parents[1]


class ConnectorTests(unittest.TestCase):
    def setUp(self):
        self.old = ProcedureLibrary.load(ROOT / "experiments/library-20260905-retained.json")
        self.new, self.certificate = compile_product(self.old)

    def test_swapped_requests_have_identical_execution(self):
        for a, b in [(3, 1000000), (0, 2**4095), (1, 2**4095), (1000000, 1000000)]:
            with patch("kavi.library_curriculum.target", side_effect=AssertionError("teacher unavailable")):
                forward = self.new.execute("multiply", (a, b), trace=True)
                reverse = self.new.execute("multiply", (b, a), trace=True)
            self.assertEqual(forward, reverse)
            self.assertEqual(forward.value, a*b)
            self.assertEqual(forward.iterations, min(a, b).bit_length())

    def test_binary_arithmetic_transfer_and_dependents(self):
        rng = random.Random(812)
        for _ in range(30):
            a, b = rng.getrandbits(120), rng.getrandbits(90)
            self.assertEqual(self.new.execute("multiply", (a, b)).value, a*b)
        self.assertEqual(self.new.execute("power", (20, 10)).value, 20**10)
        self.assertEqual(self.new.execute("factorial", (18,)).value, 6402373705728000)
        self.assertEqual(self.new.execute("sum_squares", (72, 83)).value, 12073)

    def test_ordered_operations_and_invalid_compilation(self):
        self.assertEqual(self.new.execute("subtract", (9, 3)).value, 6)
        with self.assertRaises(ValueError): self.new.execute("subtract", (3, 9))
        with self.assertRaises(ValueError): compile_product(self.old, "sum_squares")
        broken = ProcedureLibrary()
        for p in self.old.procedures.values():
            broken.add(replace(p, circuit=self.old.procedures["subtract"].circuit) if p.name == "add" else p)
        with self.assertRaises(ValueError): compile_product(broken)

    def test_schema_and_original_artifact_preserved(self):
        self.assertEqual(self.old.digest, "0a089a0b26fa2b453ed3f896637f47684920d1dfe9568edb6515bd6775285ec6")
        raw = self.new.to_dict()
        self.assertEqual(ProcedureLibrary.from_dict(raw).digest, self.new.digest)
        raw["schema"] = "kavi.procedure-library.v1"
        with self.assertRaises(ValueError): ProcedureLibrary.from_dict(raw)
        for name in self.old.procedures:
            if name != "multiply":
                self.assertEqual(self.new.procedures[name], self.old.procedures[name])

    def test_explicit_trace_loss_and_complete_call_trace(self):
        partial = self.old.execute("power", (20, 10), trace=True)
        complete = self.old.execute("power", (20, 10), trace=True, limits=Limits(max_trace_entries=10000))
        self.assertTrue(partial.trace_truncated)
        self.assertEqual(partial.trace_events, 221)
        self.assertEqual(len(partial.trace), 128)
        self.assertFalse(complete.trace_truncated)
        self.assertEqual(len(complete.trace), complete.calls)
        self.assertEqual(complete.value, partial.value)

    def test_fuel_and_value_bounds(self):
        with self.assertRaises(ExecutionLimit):
            self.new.execute("multiply", (1000000, 1000000), limits=Limits(max_iterations=4))
        with self.assertRaises(ValueError): self.new.execute("multiply", (2**4095, 4))
        with self.assertRaises(ValueError): self.new.execute("multiply", (-1, 4))

    def test_trace_bounds_and_cancellation(self):
        for cap in (-1, 100001, True):
            with self.assertRaises(ValueError):
                self.new.execute("multiply", (3, 5), trace=True, limits=Limits(max_trace_entries=cap))
            with self.assertRaises(ValueError):
                self.new.execute_expr(("call", "multiply", ("arg", 0), ("arg", 1)),
                                      (3, 5), trace=True, limits=Limits(max_trace_entries=cap))
        with self.assertRaisesRegex(RuntimeError, "stop requested"):
            self.new.execute("multiply", (3, 1000000), check=lambda: (_ for _ in ()).throw(RuntimeError("stop requested")))


class LanguageTests(unittest.TestCase):
    def lessons(self, operation="multiply"):
        return [{"text": f"multiply {a} by {b}", "source": "authored", "target":
                 {"kind": "calculation", "label": operation, "inputs": [a,b]}}
                for a,b in [(2,7),(5,9)]]

    def test_untrained_and_unseen_combinations(self):
        model = LanguageModel()
        self.assertEqual(model.interpret("multiply 1000000 by 3")["state"], "unsupported")
        model.teach(self.lessons())
        library, _ = compile_product(ProcedureLibrary.load(ROOT / "experiments/library-20260905-retained.json"))
        self.assertEqual(model.answer("Multiply 1000000 by 3?", library)["value"], 3000000)
        self.assertEqual(model.answer("multiply 3 by 1000000", library)["value"], 3000000)
        self.assertEqual(model.answer("please multiply 3 by 1000000", library)["state"], "unsupported")

    def test_directional_slots_and_ambiguity(self):
        lessons = [{"text": f"{a} because {b}", "source": "authored", "target":
                    {"kind": "relation", "label": "support", "slots": {"claim": a, "reason": b}}}
                   for a,b in [("the claim holds","evidence agrees"),("the road is wet","rain fell")]]
        model = LanguageModel()
        model.teach(lessons)
        value = model.interpret("the lamp glows because current flows")["meaning"]
        self.assertEqual(value["slots"], {"claim": "the lamp glows", "reason": "current flows"})
        self.assertEqual(model.interpret("a because b because c")["state"], "ambiguous")
        model.teach(self.lessons())
        model.teach(self.lessons("add"))
        self.assertEqual(model.interpret("multiply 3 by 5")["state"], "ambiguous")

    def test_serialization_unicode_and_lexical_accounting(self):
        model = LanguageModel()
        model.teach(self.lessons())
        model.read_passage("λόγος λόγος Erfahrung pramāṇa 学而", "source:1")
        self.assertEqual(model.lexicon[tokens("λόγος")[0]]["count"], 2)
        self.assertEqual(tokens("学而"), ["学", "而"])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "language.json"
            path.write_bytes(model.encoded())
            restored = LanguageModel.load(path)
            self.assertEqual(restored.encoded(), model.encoded())

    def test_lexical_senses_persist_and_unknown_senses_decline(self):
        model = LanguageModel()
        model.teach([{"text": f"what does {term} mean", "source": "authored", "target":
                      {"kind": "lookup", "label": "definition", "slots": {"term": term}}}
                     for term in ("idea", "impression")])
        entry = {"term": "idea", "meaning": "A source-specific sense.", "source": "source:1", "kind": "paraphrase"}
        model.definitions = {"idea": [entry]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "language.json"
            path.write_bytes(model.encoded())
            loaded = LanguageModel.load(path)
        self.assertEqual(loaded.answer("what does idea mean?", None)["definition"], entry)
        self.assertEqual(loaded.answer("what does justice mean?", None)["state"], "unsupported")
        loaded.definitions["idea"].append({**entry, "source": "source:2"})
        self.assertEqual(loaded.answer("what does idea mean?", None)["state"], "ambiguous")

    def test_invalid_typed_model_rejected(self):
        model = LanguageModel()
        model.teach(self.lessons())
        model.rules[0]["pattern"][1]["type"] = "text"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "language.json"
            path.write_bytes(model.encoded())
            with self.assertRaises(ValueError): LanguageModel.load(path)


if __name__ == "__main__":
    unittest.main()
