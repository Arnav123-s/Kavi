"""Reviewed-source retrieval and small original-language teaching packets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .file_io import atomic_replace
from .source_manifest import SourceManifest


class ReviewedRedirect(HTTPRedirectHandler):
    """Reject redirects before any request is sent to a different destination."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urlsplit(req.full_url), urlsplit(newurl)
        if (new.scheme != "https" or new.hostname != old.hostname or new.username
                or new.password or new.port not in (None, 443)):
            raise ValueError("Unexpected source redirect; explicit review required.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class TeachingSources:
    def __init__(self, repo: Path, catalog: Path) -> None:
        self.repo = repo.resolve()
        raw = json.loads(catalog.read_text(encoding="utf-8"))
        self.catalog_hash = hashlib.sha256(catalog.read_bytes()).hexdigest()
        self.records = {v["source_id"]: v for v in raw["sources"]}
        self.packets = {v["packet_id"]: v for v in raw["packets"]}
        self.manifest = SourceManifest.load(self.repo / "curriculum/source-manifest.json")

    def ensure(self, source_id: str) -> tuple[Path, bool]:
        record = self.records[source_id]
        approved = self.manifest.by_id(source_id)
        if not approved.is_teaching_admissible or record["translation"] is not False:
            raise ValueError("Only admitted original-language sources may be fetched.")
        path = (self.repo / record["local_path"]).resolve()
        if not path.is_relative_to(self.repo / "private"):
            raise ValueError("Source path escaped the private source workspace.")
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
                raise ValueError("Cached source changed; re-review it instead of silently overwriting it.")
            return path, False
        url = urlsplit(record["access_url"])
        if url.scheme != "https" or url.hostname not in {"www.gutenberg.org", "www.unicode.org"} or url.username or url.password or url.port not in (None, 443):
            raise ValueError("Source is outside the reviewed anonymous retrieval allowlist.")
        request = Request(record["access_url"], headers={"User-Agent": "Kavi-Educational-Research/1.0"})
        with build_opener(ReviewedRedirect()).open(request, timeout=15) as response:
            final = urlsplit(response.url)
            if final.scheme != "https" or final.hostname != url.hostname:
                raise ValueError("Unexpected source redirect; explicit review required.")
            data = response.read(3_000_001)
        if len(data) > 3_000_000 or hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError("Downloaded source size or fingerprint differs from the approved witness.")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".download.tmp")
        temporary.write_bytes(data)
        atomic_replace(temporary, path)
        return path, True

    def packet(self, packet_id: str) -> tuple[str, dict, bool]:
        packet = self.packets[packet_id]
        path, fetched = self.ensure(packet["source_id"])
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        start, end = packet["lines"]
        if not 1 <= start <= end <= len(lines):
            raise ValueError("Source packet boundaries are invalid.")
        text = "\n".join(lines[start-1:end])
        if not text.strip():
            raise ValueError("Source packet is empty.")
        return text, packet, fetched
