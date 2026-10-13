"""Tests for json_to_csv.headers."""

import unittest
from json_to_csv.headers import build_headers, filter_and_reorder_headers


class TestHeaders(unittest.TestCase):
    def test_build_headers_union_in_first_seen_order(self):
        records = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "email": "bob@example.com", "name": "Bob"},
            {"country": "Canada", "id": 3},
        ]
        headers = build_headers(records)
        self.assertEqual(headers, ["id", "name", "age", "email", "country"])

    def test_empty_records(self):
        self.assertEqual(build_headers([]), [])
        self.assertEqual(build_headers(None), [])

    def test_filter_and_reorder_headers(self):
        all_headers = ["id", "name", "age", "email", "country"]
        selected = ["email", "id", "non_existent_key"]
        res = filter_and_reorder_headers(all_headers, selected)
        self.assertEqual(res, ["email", "id"])


if __name__ == "__main__":
    unittest.main()
