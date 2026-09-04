"""Tests for document provenance and curriculum-admission controls."""

from __future__ import annotations

from pathlib import Path
import unittest

from kavi.source_manifest import SourceLesson, SourceManifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "curriculum" / "source-manifest.json"


class SourceManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = SourceManifest.load(MANIFEST_PATH)

    def test_only_explicitly_approved_sources_are_admissible(self) -> None:
        identifiers = {source.source_id for source in self.manifest.admissible_sources}
        self.assertEqual(
            identifiers,
            {"basic-algebra-with-applications-6e", "nasa-ntrs-19830024400"},
        )

    def test_quarantined_source_cannot_supply_a_lesson(self) -> None:
        lesson = SourceLesson(
            source_id="openstax-physics",
            locator="1.1",
            concept_id="measurement",
            prerequisites=(),
            explanation="A test explanation.",
            verifier_id="domain-specific",
            source_extract_sha256="0" * 64,
        )
        with self.assertRaises(ValueError):
            lesson.validate_against(self.manifest)

    def test_approved_source_lesson_needs_a_complete_audit_record(self) -> None:
        lesson = SourceLesson(
            source_id="nasa-ntrs-19830024400",
            locator="section-1",
            concept_id="technical-communication",
            prerequisites=(),
            explanation="A test explanation.",
            verifier_id="curated-human-and-formal",
            source_extract_sha256="a" * 64,
        )
        lesson.validate_against(self.manifest)


if __name__ == "__main__":
    unittest.main()
