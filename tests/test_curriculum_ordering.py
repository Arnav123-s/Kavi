"""Checks for fixed foundational order and multilingual catalog structure."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kavi.runtime import ArithmeticCurriculum
from kavi.school import CurriculumPlan
from kavi.symbol_runtime import SymbolCurriculum
from kavi.types import Operation


ROOT = Path(__file__).resolve().parents[1]
PEOPLE_PATH = ROOT / "curriculum" / "people-and-works.json"
ACCESS_PATH = ROOT / "curriculum" / "access-records.json"


class GeneratedOrderTests(unittest.TestCase):
    def test_symbol_bootstrap_is_seed_independent_and_canonical(self) -> None:
        first = SymbolCurriculum(seed=1)
        second = SymbolCurriculum(seed=999)
        first_glyphs = tuple(first.event_at(step).glyph for step in range(1, 9))
        second_glyphs = tuple(second.event_at(step).glyph for step in range(1, 9))
        self.assertEqual(first_glyphs, second_glyphs)
        self.assertEqual(first_glyphs, ("b", "1", "c", "2", "d", "4", "f", "5"))

    def test_arithmetic_establishes_addition_before_subtraction(self) -> None:
        first = ArithmeticCurriculum(seed=1, conflict_every=0)
        second = ArithmeticCurriculum(seed=999, conflict_every=0)
        first_events = tuple(first.event_at(step) for step in range(1, 9))
        second_events = tuple(second.event_at(step) for step in range(1, 9))
        self.assertEqual(first_events, second_events)
        self.assertEqual(
            tuple(event.operation for event in first_events[:5]),
            (Operation.ADD,) * 5,
        )
        self.assertEqual(
            tuple(event.operation for event in first_events[5:]),
            (Operation.SUBTRACT,) * 3,
        )


class CurriculumGraphTests(unittest.TestCase):
    def test_plan_rejects_a_prerequisite_declared_later(self) -> None:
        plan = {
            "schema_version": 1,
            "title": "invalid order",
            "stages": [
                {
                    "stage_id": "first",
                    "title": "first",
                    "status": "awaiting-model-capability",
                    "engine": None,
                    "prerequisites": ["second"],
                    "source_ids": [],
                },
                {
                    "stage_id": "second",
                    "title": "second",
                    "status": "awaiting-model-capability",
                    "engine": None,
                    "prerequisites": [],
                    "source_ids": [],
                },
            ],
        }
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "only earlier prerequisites"):
                CurriculumPlan.load(path)


class MultilingualCatalogTests(unittest.TestCase):
    def test_catalog_has_global_lanes_and_original_language_metadata(self) -> None:
        catalog = json.loads(PEOPLE_PATH.read_text(encoding="utf-8"))
        entries = [
            entry
            for track in catalog["tracks"]
            for entry in track["entries"]
        ]
        lanes = {entry.get("language_lane") for entry in entries}
        self.assertTrue(
            {
                "south-asian-scripts",
                "east-asian-scripts",
                "arabic-family",
                "african-scripts-and-languages",
                "indigenous-americas-and-oceania",
            }.issubset(lanes)
        )
        self.assertTrue(
            any(
                entry.get("title_in_original_language")
                and entry.get("original_language")
                and entry.get("script")
                for entry in entries
            )
        )

    def test_access_records_are_review_locators_not_admitted_sources(self) -> None:
        records = json.loads(ACCESS_PATH.read_text(encoding="utf-8"))["records"]
        self.assertGreaterEqual(len(records), 12)
        self.assertTrue(all(record["url"].startswith("https://") for record in records))
        self.assertTrue(all("catalog-only" in record["status"] or "candidate" in record["status"] for record in records))


if __name__ == "__main__":
    unittest.main()
