"""Command-line interface (CLI) for JSON to CSV conversion."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .csv_writer import to_csv
from .flattener import flatten_records
from .headers import build_headers, filter_and_reorder_headers
from .parser import parse_json


def create_parser() -> argparse.ArgumentParser:
    """Creates the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="json-to-csv",
        description="Convert nested JSON data into RFC 4180 compliant CSV files with deep flattening and array handling.",
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        default=None,
        help="Input JSON file path (reads from standard input if omitted or '-').",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output CSV file path (prints to standard output if omitted).",
    )
    parser.add_argument(
        "-d", "--delimiter",
        type=str,
        default=",",
        help="CSV delimiter: comma (','), semicolon (';'), tab ('\\t'), pipe ('|') (default: ',').",
    )
    parser.add_argument(
        "-s", "--separator",
        type=str,
        default=".",
        help="Nested key separator (default: '.').",
    )
    parser.add_argument(
        "-a", "--array-strategy",
        choices=["join", "index", "explode", "json"],
        default="join",
        help="Strategy for handling arrays: join, index, explode, or json (default: 'join').",
    )
    parser.add_argument(
        "--array-joiner",
        type=str,
        default="; ",
        help="Delimiter used when array-strategy is 'join' (default: '; ').",
    )
    parser.add_argument(
        "-m", "--max-depth",
        type=int,
        default=10,
        help="Maximum recursion depth before stringifying nested data (default: 10).",
    )
    parser.add_argument(
        "--fill-value",
        type=str,
        default="",
        help="Replacement string for missing or null properties (default: empty).",
    )
    parser.add_argument(
        "--bom",
        action="store_true",
        help="Prepend UTF-8 Byte Order Mark (\\ufeff) for Excel compatibility.",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Exclude the CSV header row.",
    )
    parser.add_argument(
        "--no-sanitize",
        action="store_true",
        help="Disable formula sanitization (do not prefix =, +, -, @ with apostrophe).",
    )
    parser.add_argument(
        "--protect-numbers",
        action="store_true",
        help="Protect leading zeros (e.g. 00123) and scientific notations from auto-conversion in Excel.",
    )
    parser.add_argument(
        "-k", "--key",
        type=str,
        default=None,
        help="Top-level object key containing the collection to convert (for root objects like {'data': [...]}).",
    )
    parser.add_argument(
        "-c", "--columns",
        type=str,
        default=None,
        help="Comma-separated list of column names to export in order.",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the interactive local web application in your browser.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the local web application on (default: 8000).",
    )

    return parser


def main(args: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.web:
        from .web import run_server
        print(f"Starting JSON to CSV Studio Web App on http://localhost:{parsed_args.port}...")
        run_server(port=parsed_args.port, open_browser=True)
        return 0

    # Read JSON input
    if parsed_args.input is None or parsed_args.input == "-":
        if sys.stdin.isatty():
            parser.print_help()
            return 1
        raw_text = sys.stdin.read()
    else:
        path = Path(parsed_args.input)
        if not path.is_file():
            sys.stderr.write(f"Error: Input file '{parsed_args.input}' not found.\n")
            return 1
        raw_text = path.read_text(encoding="utf-8")

    # Parse JSON
    parsed = parse_json(raw_text)
    if not parsed["ok"]:
        line = parsed.get("line", 1)
        col = parsed.get("column", 1)
        sys.stderr.write(f"JSON Error [Line {line}, Column {col}]: {parsed['error']}\n")
        return 1

    target_data = parsed["data"]
    if parsed_args.key and isinstance(target_data, dict):
        if parsed_args.key in target_data:
            target_data = target_data[parsed_args.key]
        else:
            sys.stderr.write(f"Error: Specified key '{parsed_args.key}' not found in top-level object.\n")
            return 1

    # Flatten
    flat_rows, skipped = flatten_records(
        target_data,
        separator=parsed_args.separator,
        max_depth=parsed_args.max_depth,
        array_strategy=parsed_args.array_strategy,
        array_joiner=parsed_args.array_joiner,
    )

    all_headers = build_headers(flat_rows)
    selected_headers = (
        [c.strip() for c in parsed_args.columns.split(",") if c.strip()]
        if parsed_args.columns
        else all_headers
    )
    effective_headers = filter_and_reorder_headers(all_headers, selected_headers)

    # Delimiter translation (e.g. handle escaped \t)
    delim = parsed_args.delimiter.replace("\\t", "\t")

    csv_output = to_csv(
        flat_rows,
        effective_headers,
        delimiter=delim,
        include_header=not parsed_args.no_header,
        fill_value=parsed_args.fill_value,
        bom=parsed_args.bom,
        sanitize_formulas=not parsed_args.no_sanitize,
        protect_numbers=parsed_args.protect_numbers,
    )

    # Write output
    if parsed_args.output:
        out_path = Path(parsed_args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            f.write(csv_output)
        if skipped > 0:
            sys.stderr.write(f"Note: {skipped} non-object records were skipped.\n")
    else:
        sys.stdout.write(csv_output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
