"""Tests for json_to_csv.web request handler and REST APIs."""

import json
import unittest
from json_to_csv.web import StudioRequestHandler


class MockWFile:
    def __init__(self):
        self.data = bytearray()

    def write(self, b):
        self.data.extend(b)


class MockRFile:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read(self, size=-1):
        if size == -1 or size is None:
            res = self.data[self.pos:]
            self.pos = len(self.data)
            return res
        res = self.data[self.pos:self.pos + size]
        self.pos += len(res)
        return res


class TestWebServer(unittest.TestCase):
    def test_convert_api_endpoint(self):
        payload = {
            "json_text": json.dumps([{"id": 1, "nested": {"val": "xyz"}}]),
            "options": {"delimiter": ",", "separator": "."},
            "selected_headers": ["id", "nested.val"],
        }
        body = json.dumps(payload).encode("utf-8")

        handler = StudioRequestHandler.__new__(StudioRequestHandler)
        handler.rfile = MockRFile(body)
        handler.wfile = MockWFile()
        handler.headers = {"Content-Length": str(len(body))}
        handler.path = "/api/convert"

        # Mock send_response, send_header, end_headers
        handler.send_response = lambda code: None
        handler.send_header = lambda k, v: None
        handler.end_headers = lambda: None

        handler.do_POST()

        res = json.loads(handler.wfile.data.decode("utf-8"))
        self.assertTrue(res["ok"])
        self.assertEqual(res["total_rows"], 1)
        self.assertIn("nested.val", res["all_headers"])
        self.assertIn("1,xyz", res["csv"])

    def test_reverse_api_endpoint(self):
        payload = {
            "csv_text": "id,name\r\n10,Alice\r\n20,Bob",
            "delimiter": ",",
        }
        body = json.dumps(payload).encode("utf-8")

        handler = StudioRequestHandler.__new__(StudioRequestHandler)
        handler.rfile = MockRFile(body)
        handler.wfile = MockWFile()
        handler.headers = {"Content-Length": str(len(body))}
        handler.path = "/api/reverse"

        handler.send_response = lambda code: None
        handler.send_header = lambda k, v: None
        handler.end_headers = lambda: None

        handler.do_POST()

        res = json.loads(handler.wfile.data.decode("utf-8"))
        self.assertTrue(res["ok"])
        self.assertEqual(len(res["data"]), 2)
        self.assertEqual(res["data"][0]["name"], "Alice")


if __name__ == "__main__":
    unittest.main()
