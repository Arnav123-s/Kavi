"""Read-only review interface for Kavi's people-and-works curriculum catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_catalog(path: Path) -> dict[str, object]:
    """Load catalog metadata without downloading or opening any listed work."""

    catalog = json.loads(path.read_text(encoding="utf-8"))
    if int(catalog["schema_version"]) != 1:
        raise ValueError("Unsupported people-and-works catalog schema.")
    if not isinstance(catalog.get("tracks"), list):
        raise ValueError("Catalog needs an ordered tracks list.")
    return catalog


def build_parser() -> argparse.ArgumentParser:
    """Create the read-only review command."""

    parser = argparse.ArgumentParser(
        prog="python -m kavi.catalog_cli",
        description="Print Kavi's people-and-works list without reading source bodies.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("curriculum/people-and-works.json"),
    )
    parser.add_argument(
        "--track",
        help="show only one track identifier",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Print the ordered review list."""

    args = build_parser().parse_args(argv)
    catalog = load_catalog(args.catalog)
    print(str(catalog["title"]))
    print(f"  selection rule: {catalog['selection_basis']}")
    found = False
    for track_value in catalog["tracks"]:
        track = dict(track_value)
        if args.track and track["track_id"] != args.track:
            continue
        found = True
        print(f"\n[{track['track_id']}] {track['title']}")
        print(f"  status: {track['training_disposition']}")
        print(f"  purpose: {track['purpose']}")
        for entry_value in track["entries"]:
            entry = dict(entry_value)
            author = entry["person"] or "Generated Kavi lessons"
            print(f"  - {author}: {entry['work']}")
            print(f"    role: {entry['why_here']}")
            print(f"    source status: {entry['source_status']}")
    if args.track and not found:
        raise ValueError(f"Unknown catalog track: {args.track}")
    print(f"\nAdmission rule: {catalog['admission_rule']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
