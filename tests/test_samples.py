"""Tests verifying all sample JSON files against expected CSV outputs."""

import unittest
from pathlib import Path

from json_to_csv.csv_writer import to_csv
from json_to_csv.flattener import flatten_records
from json_to_csv.headers import build_headers
from json_to_csv.parser import parse_json

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
EXPECTED_DIR = SAMPLES_DIR / "expected"


class TestSamples(unittest.TestCase):
    def test_sample_conversions(self):
        sample_names = ["flat", "nested", "mixed-keys", "arrays", "unicode"]

        for name in sample_names:
            with self.subTest(sample=name):
                json_path = SAMPLES_DIR / f"{name}.json"
                expected_path = EXPECTED_DIR / f"{name}.csv"

                self.assertTrue(json_path.is_file(), f"Missing sample {json_path}")
                self.assertTrue(expected_path.is_file(), f"Missing expected fixture {expected_path}")

                json_text = json_path.read_text(encoding="utf-8")
                expected_csv = expected_path.read_text(encoding="utf-8")

                parsed = parse_json(json_text)
                self.assertTrue(parsed["ok"], f"Failed parsing {name}.json: {parsed.get('error')}")

                flat_rows, _ = flatten_records(parsed["data"])
                headers = build_headers(flat_rows)
                generated_csv = to_csv(flat_rows, headers, sanitize_formulas=False)

                # Normalize CRLF / LF for comparison
                norm_gen = generated_csv.replace("\r\n", "\n").strip()
                norm_exp = expected_csv.replace("\r\n", "\n").strip()
                self.assertEqual(norm_gen, norm_exp, f"Mismatch in {name}.csv conversion")

    def test_malformed_json_reporting(self):
        malformed_path = SAMPLES_DIR / "malformed.json"
        self.assertTrue(malformed_path.is_file())

        text = malformed_path.read_text(encoding="utf-8")
        parsed = parse_json(text)

        self.assertFalse(parsed["ok"])
        self.assertGreater(parsed["line"], 0)
        self.assertGreater(parsed["column"], 0)
        self.assertIn("error", parsed)


if __name__ == "__main__":
    unittest.main()
