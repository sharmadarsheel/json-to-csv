"""Tests for json_to_csv.parser."""

import unittest
from json_to_csv.parser import parse_json, find_array_of_object_keys


class TestParser(unittest.TestCase):
    def test_parse_valid_array_of_objects(self):
        text = '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'
        res = parse_json(text)
        self.assertTrue(res["ok"])
        self.assertIsInstance(res["data"], list)
        self.assertEqual(len(res["data"]), 2)
        self.assertEqual(res["data"][0]["name"], "Alice")

    def test_parse_valid_single_object(self):
        text = '{"user": {"name": "Alice", "age": 30}}'
        res = parse_json(text)
        self.assertTrue(res["ok"])
        self.assertIsInstance(res["data"], dict)
        self.assertEqual(res["data"]["user"]["name"], "Alice")

    def test_reject_empty_input(self):
        res = parse_json("   ")
        self.assertFalse(res["ok"])
        self.assertIn("empty", res["error"].lower())
        self.assertEqual(res["line"], 1)

    def test_reject_top_level_primitives(self):
        res_num = parse_json("42")
        self.assertFalse(res_num["ok"])
        self.assertIn("primitive", res_num["error"].lower())

        res_str = parse_json('"hello world"')
        self.assertFalse(res_str["ok"])
        self.assertIn("primitive", res_str["error"].lower())

        res_bool = parse_json("true")
        self.assertFalse(res_bool["ok"])
        self.assertIn("primitive", res_bool["error"].lower())

    def test_syntax_error_returns_line_and_column(self):
        malformed = '[\n  {"a": 1},\n  {"b": \n]'
        res = parse_json(malformed)
        self.assertFalse(res["ok"])
        self.assertGreaterEqual(res["line"], 2)
        self.assertGreaterEqual(res["column"], 1)

    def test_find_array_of_object_keys(self):
        obj = {
            "meta": {"page": 1},
            "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            "tags": ["a", "b", "c"],
            "count": 2,
        }
        keys = find_array_of_object_keys(obj)
        self.assertEqual(keys, ["users"])


if __name__ == "__main__":
    unittest.main()
