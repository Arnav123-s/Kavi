"""Inspect the source-admission gate without downloading any document."""

from __future__ import annotations

import argparse
from pathlib import Path

from .source_manifest import SourceManifest


def main(argv: list[str] | None = None) -> int:
    """Print current source-review decisions."""

    parser = argparse.ArgumentParser(
        description="Validate Kritjnah's document curriculum source manifest."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("curriculum/source-manifest.json"),
    )
    args = parser.parse_args(argv)
    manifest = SourceManifest.load(args.manifest)
    print(f"source manifest schema {manifest.schema_version}")
    for source in manifest.sources:
        decision = "admit" if source.is_admissible else "do not ingest"
        print(
            f"  {source.source_id}: {decision}; "
            f"{source.status.value}; {source.license_class.value}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
