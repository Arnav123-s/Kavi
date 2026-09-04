"""Teacher-only access to an original, fingerprinted Unicode reference.

The model never imports this module or consults this table during inference.
Its purpose is to check corrections and choose different teaching examples.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path


SCRIPT_SOURCE_ID = "unicode-17-script-property"
SCRIPT_SOURCE_SHA256 = "9f5e50d3abaee7d6ce09480f325c706f485ae3240912527e651954d2d6b035bf"


@dataclass(frozen=True, slots=True)
class ScriptReference:
    ranges: tuple[tuple[int, int, str], ...]

    @classmethod
    def load(cls, path: Path, expected_sha256: str = SCRIPT_SOURCE_SHA256) -> "ScriptReference":
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != expected_sha256:
            raise ValueError("The original Unicode source fingerprint does not match.")
        ranges = []
        for line in content.decode("utf-8").splitlines():
            data = line.partition("#")[0].strip()
            if not data:
                continue
            interval, label = (part.strip() for part in data.split(";"))
            bounds = interval.split("..")
            first, last = int(bounds[0], 16), int(bounds[-1], 16)
            if not 0 <= first <= last <= 0x10FFFF:
                raise ValueError("Invalid Unicode source interval.")
            ranges.append((first, last, label.lower()))
        if not ranges:
            raise ValueError("The script reference contains no data.")
        return cls(tuple(sorted(ranges)))

    def label(self, glyph: str) -> str:
        if len(glyph) != 1:
            raise ValueError("Script lookup requires exactly one scalar.")
        codepoint = ord(glyph)
        for first, last, label in self.ranges:
            if first <= codepoint <= last:
                return label
        return "unknown"

    def alternatives(
        self, glyph: str, excluded: set[str], count: int = 2
    ) -> tuple[str, ...]:
        """Find nearby, differently written examples verified by the source."""

        label = self.label(glyph)
        if label in {"unknown", "inherited", "common"}:
            return ()
        result = []
        for distance in range(1, 257):
            for codepoint in (ord(glyph) + distance, ord(glyph) - distance):
                if not 0 <= codepoint <= 0x10FFFF:
                    continue
                candidate = chr(codepoint)
                if candidate in excluded or candidate == glyph:
                    continue
                if self.label(candidate) == label:
                    result.append(candidate)
                    if len(result) == count:
                        return tuple(result)
        return tuple(result)
