import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from kavi.teaching_sources import TeachingSources


class TeachingSourceTests(unittest.TestCase):
    def registry(self, root, payload=b"original\nsource\n"):
        registry = object.__new__(TeachingSources)
        registry.repo = root
        registry.manifest = Mock()
        registry.manifest.by_id.return_value.is_teaching_admissible = True
        registry.records = {"test": {"translation": False, "local_path": "private/source.txt",
                            "sha256": hashlib.sha256(payload).hexdigest(),
                            "access_url": "https://www.gutenberg.org/approved.txt"}}
        registry.packets = {"lesson": {"source_id": "test", "lines": [1, 2]}}
        return registry

    def test_cache_hash_boundaries_and_translation_control(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = self.registry(root)
            (root / "private").mkdir()
            path = root / "private/source.txt"
            path.write_bytes(b"original\nsource\n")
            text, packet, fetched = registry.packet("lesson")
            self.assertEqual(text, "original\nsource")
            self.assertFalse(fetched)
            registry.packets["lesson"]["lines"] = [0, 2]
            with self.assertRaises(ValueError):
                registry.packet("lesson")
            registry.records["test"]["translation"] = True
            with self.assertRaises(ValueError):
                registry.ensure("test")
            registry.records["test"]["translation"] = False
            path.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                registry.ensure("test")

    def test_unapproved_source_or_host_never_fetches(self):
        with tempfile.TemporaryDirectory() as directory, patch("kavi.teaching_sources.build_opener") as network:
            registry = self.registry(Path(directory))
            registry.manifest.by_id.return_value.is_teaching_admissible = False
            with self.assertRaises(ValueError):
                registry.ensure("test")
            registry.manifest.by_id.return_value.is_teaching_admissible = True
            registry.records["test"]["access_url"] = "https://unreviewed.example/text"
            with self.assertRaises(ValueError):
                registry.ensure("test")
            network.assert_not_called()

    def test_source_path_cannot_escape_private_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = self.registry(Path(directory))
            registry.records["test"]["local_path"] = "private/../other.txt"
            with self.assertRaises(ValueError):
                registry.ensure("test")


if __name__ == "__main__":
    unittest.main()
