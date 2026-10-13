"""Tests for json_to_csv.flattener."""

import unittest
from json_to_csv.flattener import flatten_record, flatten_records


class TestFlattener(unittest.TestCase):
    def test_flatten_nested_objects_default_separator(self):
        input_data = {
            "user": {
                "name": "Alice",
                "address": {
                    "city": "Paris",
                    "zip": "75001",
                },
            },
            "active": True,
        }
        res = flatten_record(input_data)
        self.assertEqual(res, {
            "user.name": "Alice",
            "user.address.city": "Paris",
            "user.address.zip": "75001",
            "active": True,
        })

    def test_custom_separators(self):
        input_data = {"a": {"b": {"c": 10}}}
        res_underscore = flatten_record(input_data, separator="_")
        self.assertEqual(res_underscore, {"a_b_c": 10})

        res_slash = flatten_record(input_data, separator="/")
        self.assertEqual(res_slash, {"a/b/c": 10})

    def test_array_strategy_join(self):
        sample = {"id": 101, "tags": ["apple", "banana", "cherry"]}
        res = flatten_record(sample, array_strategy="join", array_joiner="; ")
        self.assertEqual(res, {"id": 101, "tags": "apple; banana; cherry"})

    def test_array_strategy_index(self):
        sample = {"id": 101, "tags": ["apple", "banana", "cherry"]}
        res = flatten_record(sample, array_strategy="index")
        self.assertEqual(res, {
            "id": 101,
            "tags.0": "apple",
            "tags.1": "banana",
            "tags.2": "cherry",
        })

    def test_array_strategy_json(self):
        sample = {"id": 101, "tags": ["apple", "banana", "cherry"]}
        res = flatten_record(sample, array_strategy="json")
        self.assertEqual(res, {"id": 101, "tags": '["apple","banana","cherry"]'})

    def test_array_strategy_explode(self):
        sample = {"id": 101, "tags": ["apple", "banana", "cherry"]}
        res = flatten_record(sample, array_strategy="explode")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        self.assertEqual(res, [
            {"id": 101, "tags": "apple"},
            {"id": 101, "tags": "banana"},
            {"id": 101, "tags": "cherry"},
        ])

    def test_array_strategy_explode_with_nested_objects(self):
        complex_data = {
            "orderId": 99,
            "items": [
                {"sku": "A1", "qty": 2},
                {"sku": "B2", "qty": 5},
            ],
        }
        res = flatten_record(complex_data, array_strategy="explode")
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertEqual(res, [
            {"orderId": 99, "items.sku": "A1", "items.qty": 2},
            {"orderId": 99, "items.sku": "B2", "items.qty": 5},
        ])

    def test_max_depth_serialization(self):
        deep_obj = {
            "level1": {
                "level2": {
                    "level3": {
                        "leaf": "deep value"
                    }
                }
            }
        }
        res = flatten_record(deep_obj, max_depth=2)
        self.assertEqual(res["level1.level2"], '{"level3":{"leaf":"deep value"}}')

    def test_key_collision_resolution(self):
        collision_input = {
            "user.name": "First literal name",
            "user": {
                "name": "Nested name",
            },
        }
        res = flatten_record(collision_input)
        self.assertEqual(res["user.name"], "First literal name")
        self.assertEqual(res["user.name_2"], "Nested name")

    def test_flatten_records_skips_and_counts_non_objects(self):
        records = [
            {"id": 1, "name": "Alice"},
            "invalid primitive string",
            42,
            None,
            {"id": 2, "name": "Bob"},
        ]
        flat_rows, skipped = flatten_records(records)
        self.assertEqual(len(flat_rows), 2)
        self.assertEqual(skipped, 3)
        self.assertEqual(flat_rows[0]["name"], "Alice")
        self.assertEqual(flat_rows[1]["name"], "Bob")


if __name__ == "__main__":
    unittest.main()
