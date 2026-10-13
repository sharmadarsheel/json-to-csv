"""Tests for json_to_csv.cli."""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from json_to_csv.cli import main


class TestCLI(unittest.TestCase):
    def test_cli_file_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            in_file = Path(tmpdir) / "input.json"
            out_file = Path(tmpdir) / "output.csv"

            data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
            in_file.write_text(json.dumps(data), encoding="utf-8")

            ret = main(["-i", str(in_file), "-o", str(out_file), "--no-sanitize"])
            self.assertEqual(ret, 0)
            self.assertTrue(out_file.is_file())

            # Read with newline="" so CRLF is preserved exactly as written
            with open(out_file, "r", newline="", encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content, "id,name\r\n1,Alice\r\n2,Bob")

    def test_cli_stdin_to_stdout(self):
        data = '[{"id": 99, "status": "ok"}]'
        with patch("sys.stdin", io.StringIO(data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                ret = main(["-i", "-", "--no-sanitize"])
                self.assertEqual(ret, 0)
                self.assertEqual(mock_stdout.getvalue(), "id,status\r\n99,ok")

    def test_cli_malformed_json_returns_error_code(self):
        with patch("sys.stdin", io.StringIO("invalid json {")):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                ret = main(["-i", "-"])
                self.assertEqual(ret, 1)
                self.assertIn("JSON Error", mock_stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
