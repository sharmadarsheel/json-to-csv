# Changelog

All notable changes and deliverables for JSON to CSV Studio.

## [2.0.0] - 2026-10-13 (Python Refactor)

### Added
- **Core Python Package (`json_to_csv`)**:
  - `parser.py`: JSON parsing with exact line and column numbers on syntax errors, rejection of primitive types, and top-level object array detection.
  - `flattener.py`: Recursive flattening with custom separators, recursion depth limit (`max_depth`), key collision deduplication (`_2`), and all 4 array strategies (`join`, `index`, `explode`, `json`).
  - `headers.py`: Union-of-keys header builder maintaining first-seen insertion order and column selection filtering.
  - `csv_writer.py`: RFC 4180 compliant CSV generator with quote escaping, CRLF line endings, custom delimiters, UTF-8 BOM, missing fill values, formula injection sanitization, and leading-zero preservation.
  - `cli.py`: Feature-rich CLI supporting file and stdin/stdout pipelines, argument parsing, and custom column filtering.
  - `web.py`: Multi-threaded local HTTP server serving REST API (`/api/convert`, `/api/reverse`) and static web studio.
  - `app.py`: Top-level application runner (`python app.py` launches web app or runs CLI).
- **Packaging**:
  - Standard `pyproject.toml` and `setup.py` configurations with `json-to-csv` console script entry point.
- **Python Test Suite (`tests/`)**:
  - 34 comprehensive unit and integration tests using Python's native `unittest` runner covering parser, flattener, headers, csv_writer, cli, web REST API, and sample fixture verifications.
- **Samples & Fixtures**:
  - Maintained complete test datasets in `samples/` and `samples/expected/`.

### Removed
- Removed legacy JavaScript/Node codebase files in favor of pure Python implementation.
