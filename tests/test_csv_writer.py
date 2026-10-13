"""Tests for json_to_csv.csv_writer."""

import unittest
from json_to_csv.csv_writer import (
    escape_cell,
    is_formula_injection,
    should_protect_number,
    to_csv,
)


class TestCsvWriter(unittest.TestCase):
    def test_escaping_cells(self):
        self.assertEqual(escape_cell("Hello, World", sanitize_formulas=False), '"Hello, World"')
        self.assertEqual(escape_cell('He said "Hello"', sanitize_formulas=False), '"He said ""Hello"""')
        self.assertEqual(escape_cell("Line 1\nLine 2", sanitize_formulas=False), '"Line 1\nLine 2"')
        self.assertEqual(escape_cell("Simple", sanitize_formulas=False), "Simple")

    def test_crlf_line_endings(self):
        rows = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        headers = ["id", "name"]
        csv_str = to_csv(rows, headers, sanitize_formulas=False)
        self.assertEqual(csv_str, "id,name\r\n1,Alice\r\n2,Bob")

    def test_custom_delimiters(self):
        rows = [{"a": 1, "b": 2}]
        headers = ["a", "b"]
        self.assertEqual(to_csv(rows, headers, delimiter=";", sanitize_formulas=False), "a;b\r\n1;2")
        self.assertEqual(to_csv(rows, headers, delimiter="\t", sanitize_formulas=False), "a\tb\r\n1\t2")
        self.assertEqual(to_csv(rows, headers, delimiter="|", sanitize_formulas=False), "a|b\r\n1|2")

    def test_utf8_bom(self):
        rows = [{"x": "val"}]
        headers = ["x"]
        csv_with_bom = to_csv(rows, headers, bom=True, sanitize_formulas=False)
        self.assertTrue(csv_with_bom.startswith("\ufeff"))

    def test_omit_header_row(self):
        rows = [{"id": 10, "val": "foo"}]
        headers = ["id", "val"]
        csv_str = to_csv(rows, headers, include_header=False, sanitize_formulas=False)
        self.assertEqual(csv_str, "10,foo")

    def test_fill_value(self):
        rows = [
            {"id": 1, "name": "Alice", "score": 100},
            {"id": 2, "name": "Bob"},
        ]
        headers = ["id", "name", "score"]
        csv_str = to_csv(rows, headers, fill_value="N/A", sanitize_formulas=False)
        self.assertEqual(csv_str, "id,name,score\r\n1,Alice,100\r\n2,Bob,N/A")

    def test_formula_sanitization(self):
        self.assertTrue(is_formula_injection("=1+2"))
        self.assertTrue(is_formula_injection("+cmd"))
        self.assertTrue(is_formula_injection("-10"))
        self.assertTrue(is_formula_injection("@SUM(A1)"))
        self.assertFalse(is_formula_injection("Normal text"))

        rows = [{"cmd": "=SUM(A1:A10)"}]
        headers = ["cmd"]
        csv_str = to_csv(rows, headers, sanitize_formulas=True)
        self.assertIn("'=SUM(A1:A10)", csv_str)

    def test_protect_numbers(self):
        self.assertTrue(should_protect_number("00123"))
        self.assertTrue(should_protect_number("0123"))
        self.assertTrue(should_protect_number("1E5"))
        self.assertFalse(should_protect_number("12345"))

        rows = [{"code": "00123", "sci": "1E5"}]
        headers = ["code", "sci"]
        csv_str = to_csv(rows, headers, protect_numbers=True, sanitize_formulas=False)
        self.assertIn("'00123", csv_str)
        self.assertIn("'1E5", csv_str)


if __name__ == "__main__":
    unittest.main()
