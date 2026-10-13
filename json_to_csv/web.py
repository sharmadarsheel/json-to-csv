"""Python Web Server and REST API for the JSON to CSV Studio interactive UI."""

from __future__ import annotations

import csv
import io
import json
import mimetypes
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .csv_writer import to_csv
from .flattener import flatten_records
from .headers import build_headers, filter_and_reorder_headers
from .parser import find_array_of_object_keys, parse_json

STATIC_DIR = Path(__file__).parent / "static"


class StudioRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler supporting static assets and converter REST APIs."""

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress noisy request logs in production mode."""
        pass

    def do_GET(self) -> None:
        """Serves web interface static files."""
        clean_path = self.path.split("?")[0].lstrip("/")
        if clean_path in ("", "index.html"):
            target_file = STATIC_DIR / "index.html"
        else:
            target_file = STATIC_DIR / clean_path

        if target_file.is_file():
            mime_type, _ = mimetypes.guess_type(target_file)
            content = target_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime_type or "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File not found")

    def do_POST(self) -> None:
        """Handles JSON conversion and reverse conversion API requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            self._send_json({"ok": False, "error": "Invalid request JSON payload."}, status=400)
            return

        if self.path == "/api/convert":
            self._handle_convert(payload)
        elif self.path == "/api/reverse":
            self._handle_reverse(payload)
        else:
            self.send_error(404, "API endpoint not found")

    def _handle_convert(self, payload: dict[str, Any]) -> None:
        json_text = payload.get("json_text", "")
        opts = payload.get("options", {})
        user_selected_headers = payload.get("selected_headers")

        parsed = parse_json(json_text)
        if not parsed["ok"]:
            self._send_json(parsed, status=200)
            return

        target_data = parsed["data"]
        detected_keys = []
        if isinstance(target_data, dict):
            detected_keys = find_array_of_object_keys(target_data)

        data_key = opts.get("data_key")
        if data_key and isinstance(target_data, dict) and data_key in target_data:
            target_data = target_data[data_key]

        separator = opts.get("separator", ".")
        max_depth = int(opts.get("max_depth", 10))
        array_strategy = opts.get("array_strategy", "join")
        array_joiner = opts.get("array_joiner", "; ")
        delimiter = opts.get("delimiter", ",").replace("\\t", "\t")
        include_header = bool(opts.get("include_header", True))
        fill_value = str(opts.get("fill_value", ""))
        bom = bool(opts.get("bom", False))
        sanitize_formulas = bool(opts.get("sanitize_formulas", True))
        protect_numbers = bool(opts.get("protect_numbers", False))

        flat_rows, skipped = flatten_records(
            target_data,
            separator=separator,
            max_depth=max_depth,
            array_strategy=array_strategy,
            array_joiner=array_joiner,
        )

        all_headers = build_headers(flat_rows)
        effective_headers = (
            filter_and_reorder_headers(all_headers, user_selected_headers)
            if user_selected_headers is not None
            else all_headers
        )

        csv_result = to_csv(
            flat_rows,
            effective_headers,
            delimiter=delimiter,
            include_header=include_header,
            fill_value=fill_value,
            bom=bom,
            sanitize_formulas=sanitize_formulas,
            protect_numbers=protect_numbers,
        )

        preview_rows = flat_rows[:50]

        self._send_json({
            "ok": True,
            "csv": csv_result,
            "all_headers": all_headers,
            "effective_headers": effective_headers,
            "preview_rows": preview_rows,
            "total_rows": len(flat_rows),
            "total_columns": len(effective_headers),
            "skipped_count": skipped,
            "detected_array_keys": detected_keys,
        })

    def _handle_reverse(self, payload: dict[str, Any]) -> None:
        csv_text = payload.get("csv_text", "")
        delimiter = payload.get("delimiter", ",").replace("\\t", "\t")

        if not csv_text.strip():
            self._send_json({"ok": False, "error": "CSV input is empty."}, status=200)
            return

        try:
            # Strip BOM if present
            clean_csv = csv_text.lstrip("\ufeff")
            reader = csv.DictReader(io.StringIO(clean_csv), delimiter=delimiter)
            records = []
            for row in reader:
                parsed_row = {}
                for k, v in row.items():
                    if k is None:
                        continue
                    val = v
                    if val == "true":
                        val = True
                    elif val == "false":
                        val = False
                    elif val and val.replace(".", "", 1).isdigit() and not val.startswith("0"):
                        val = float(val) if "." in val else int(val)
                    parsed_row[k] = val
                records.append(parsed_row)

            self._send_json({"ok": True, "data": records})
        except Exception as e:
            self._send_json({"ok": False, "error": f"Error parsing CSV: {e}"})

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = 8000, host: str = "127.0.0.1", open_browser: bool = False) -> None:
    """Launches the threaded local web server."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, StudioRequestHandler)
    url = f"http://{host}:{port}"
    print(f"JSON to CSV Studio running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port=port, open_browser=True)
