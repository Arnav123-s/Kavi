"""Provenance and permission gates for a document-based curriculum.

The public repository keeps source metadata, citations, hashes, and lesson
claims. It does not copy books, papers, raw PDFs, or a private document cache
into version control.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any


class SourceStatus(str, Enum):
    """A source may be approved, quarantined, or explicitly rejected."""

    APPROVED = "approved"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"


class LicenseClass(str, Enum):
    """Only known, compatible rights statements may enter the curriculum."""

    US_GOVERNMENT_PUBLIC_USE = "us-government-public-use-permitted"
    CC_BY_4 = "cc-by-4.0"
    CC_BY_SA_4 = "cc-by-sa-4.0"
    REQUIRES_REVIEW = "requires-per-item-review"
    UNKNOWN = "unknown"


ADMISSIBLE_LICENSES = frozenset(
    {
        LicenseClass.US_GOVERNMENT_PUBLIC_USE,
        LicenseClass.CC_BY_4,
        LicenseClass.CC_BY_SA_4,
    }
)


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """One reviewed source record, with no body text stored in the repository."""

    source_id: str
    title: str
    creator: str
    original_url: str
    license_class: LicenseClass
    license_url: str
    status: SourceStatus
    review_note: str
    subjects: tuple[str, ...]
    levels: tuple[str, ...]

    @property
    def is_admissible(self) -> bool:
        return (
            self.status is SourceStatus.APPROVED
            and self.license_class in ADMISSIBLE_LICENSES
        )

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "SourceRecord":
        return cls(
            source_id=str(value["source_id"]),
            title=str(value["title"]),
            creator=str(value["creator"]),
            original_url=str(value["original_url"]),
            license_class=LicenseClass(value["license_class"]),
            license_url=str(value["license_url"]),
            status=SourceStatus(value["status"]),
            review_note=str(value["review_note"]),
            subjects=tuple(str(item) for item in value["subjects"]),
            levels=tuple(str(item) for item in value["levels"]),
        )


@dataclass(frozen=True, slots=True)
class SourceManifest:
    """A locally validated collection of source records."""

    schema_version: int
    sources: tuple[SourceRecord, ...]

    @classmethod
    def load(cls, path: Path) -> "SourceManifest":
        raw = json.loads(path.read_text(encoding="utf-8"))
        records = tuple(SourceRecord.from_mapping(item) for item in raw["sources"])
        manifest = cls(schema_version=int(raw["schema_version"]), sources=records)
        manifest.validate()
        return manifest

    def validate(self) -> None:
        """Reject duplicate identifiers and impossible source states."""

        identifiers = [source.source_id for source in self.sources]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Source manifest has duplicate source identifiers.")
        for source in self.sources:
            if source.status is SourceStatus.APPROVED and (
                source.license_class not in ADMISSIBLE_LICENSES
            ):
                raise ValueError(
                    f"Approved source {source.source_id} lacks an admissible license."
                )
            if not source.original_url.startswith(("https://", "http://")):
                raise ValueError(f"Source {source.source_id} needs an original URL.")

    def by_id(self, source_id: str) -> SourceRecord:
        for source in self.sources:
            if source.source_id == source_id:
                return source
        raise KeyError(source_id)

    @property
    def admissible_sources(self) -> tuple[SourceRecord, ...]:
        return tuple(source for source in self.sources if source.is_admissible)


@dataclass(frozen=True, slots=True)
class SourceLesson:
    """A small, verifiable claim derived from a reviewed document section.

    The source body remains in a local, separately approved document workspace.
    The hash lets an experiment record identify exactly which reviewed extract
    supported the lesson without republishing that extract in this repository.
    """

    source_id: str
    locator: str
    concept_id: str
    prerequisites: tuple[str, ...]
    explanation: str
    verifier_id: str
    source_extract_sha256: str

    def validate_against(self, manifest: SourceManifest) -> None:
        source = manifest.by_id(self.source_id)
        if not source.is_admissible:
            raise ValueError(
                f"Source {self.source_id} is not admitted to the curriculum."
            )
        if not self.locator or not self.concept_id or not self.verifier_id:
            raise ValueError("A lesson needs a locator, concept, and verifier.")
        if len(self.source_extract_sha256) != 64:
            raise ValueError("A lesson needs a SHA-256 extract fingerprint.")
