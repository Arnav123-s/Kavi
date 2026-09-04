from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from kavi.file_io import atomic_replace
from kavi.pathway_live import _safe_write_json


class AtomicFileTests(unittest.TestCase):
    def test_transient_reader_lock_is_retried(self):
        with patch.object(Path, "replace", side_effect=[PermissionError("reader"), None]) as replace:
            with patch("kavi.file_io.time.sleep"):
                atomic_replace(Path("a.tmp"), Path("a"))
        self.assertEqual(replace.call_count, 2)

    def test_permanent_errors_are_not_silenced(self):
        with patch.object(Path, "replace", side_effect=PermissionError("permanent")):
            with patch("kavi.file_io.time.sleep"), self.assertRaises(PermissionError):
                atomic_replace(Path("a.tmp"), Path("a"), attempts=2)
        with patch.object(Path, "replace", side_effect=FileNotFoundError("missing")) as replace:
            with self.assertRaises(FileNotFoundError):
                atomic_replace(Path("a.tmp"), Path("a"))
            self.assertEqual(replace.call_count, 1)

    def test_status_is_complete_valid_json(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            _safe_write_json(path, {"state": "learning", "step": 1})
            _safe_write_json(path, {"state": "learning", "step": 2})
            self.assertEqual(json.loads(path.read_text())["step"], 2)


if __name__ == "__main__":
    unittest.main()
