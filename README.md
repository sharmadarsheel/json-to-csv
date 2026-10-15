# JSON to CSV Studio (Python Edition) 🐍📊

> A high-performance, privacy-first JSON to CSV converter built in pure Python. Available as an **importable Python library**, a **CLI tool**, and an **interactive local web application**. Features deep recursive flattening, customizable array strategies, formula injection protection, live preview, and RFC 4180 compliance.

---

## 🌟 Features

- **Zero External Dependencies**: Built with 100% Python 3 standard library modules. Runs instantly on any modern Python installation.
- **Three Ways to Use**:
  1. **Python Library**: Clean, typed functions (`parse_json`, `flatten_records`, `build_headers`, `to_csv`) for seamless programmatic integration.
  2. **CLI Utility**: Powerful command-line interface (`json-to-csv` or `python -m json_to_csv`) with file and pipe (stdin/stdout) support.
  3. **Interactive Local Web Studio**: Modern browser UI with live 50-row preview, column reordering, sample datasets, and dark/light mode.
- **Deep Recursive Flattening**: Automatically flattens nested objects into path-based columns (e.g. `{"user": {"address": {"city": "Paris"}}}` becomes `user.address.city`) using configurable separators (`.`, `_`, `/`).
- **4 Array Strategies**:
  1. **Join**: Combines primitive elements into a single cell with a chosen delimiter (e.g. `apple; banana; cherry`).
  2. **Indexed Columns**: Flattens elements into distinct columns (e.g. `tags.0`, `tags.1`).
  3. **Explode Rows**: Replicates parent records per array item (Cartesian expansion for multiple arrays).
  4. **Raw JSON String**: Retains array values as intact JSON strings in one cell.
- **Root Object Key Extraction**: If your JSON contains a root object wrapping arrays (e.g. `{"data": [...], "meta": {...}}`), specify `--key data` or select it in the UI.
- **RFC 4180 Escaping & Excel Ready**:
  - Automatically wraps cells containing commas, double quotes, and newlines in double quotes and doubles internal quotes (`""`).
  - Standard `\r\n` line endings.
  - Optional **UTF-8 Byte Order Mark (BOM)** flag (`--bom`) for seamless opening in Microsoft Excel.
- **Formula Injection Sanitization (CSV Injection Protection)**: Prefixes cell values starting with `=`, `+`, `-`, `@`, `\t`, or `\r` with an apostrophe (`'`) so spreadsheet software does not execute arbitrary formulas.
- **Number & Leading-Zero Protection**: Preserves leading zeros (`00123`) and scientific notations (`1E5`) from spreadsheet auto-formatting.
- **Reverse CSV to JSON Converter**: Built-in utility to turn CSV tables back into JSON arrays of objects.

---

## 🚀 Quick Start

### 1. Launch the Interactive Local Web App
```bash
python app.py
```
Or:
```bash
python -m json_to_csv --web
```
This starts the local web server at `http://127.0.0.1:8000` with the live studio interface.

---

### 2. Command-Line Usage (CLI)

#### Convert a file:
```bash
python -m json_to_csv -i samples/nested.json -o output.csv
```

#### Pipe JSON from another command (stdin &rarr; stdout):
```bash
curl -s https://api.example.com/items | python -m json_to_csv > items.csv
```

#### Custom options:
```bash
python -m json_to_csv \
  -i input.json \
  -o output.csv \
  --delimiter ";" \
  --separator "_" \
  --array-strategy explode \
  --bom \
  --protect-numbers
```

---

### 3. Programmatic Usage in Python

```python
from json_to_csv import parse_json, flatten_records, build_headers, to_csv

raw_json = '[{"id": 1, "user": {"name": "Alice"}}]'

# 1. Parse and validate JSON
result = parse_json(raw_json)
if not result["ok"]:
    raise ValueError(f"Invalid JSON at line {result['line']}, col {result['column']}")

# 2. Flatten records
flat_rows, skipped = flatten_records(
    result["data"],
    separator=".",
    array_strategy="join",
    max_depth=10
)

# 3. Detect column headers
headers = build_headers(flat_rows)

# 4. Generate RFC 4180 CSV
csv_text = to_csv(
    flat_rows,
    headers,
    delimiter=",",
    include_header=True,
    sanitize_formulas=True
)

print(csv_text)
# Output:
# id,user.name
# 1,Alice
```

---

## ⚙️ CLI Reference Table

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `-i`, `--input` | `path` | `stdin` | Input JSON file path (reads from stdin if omitted or `-`). |
| `-o`, `--output` | `path` | `stdout` | Output CSV file path (prints to stdout if omitted). |
| `-d`, `--delimiter` | `string` | `,` | CSV delimiter: comma `,`, semicolon `;`, tab `\t`, pipe `\|`. |
| `-s`, `--separator` | `string` | `.` | Nested key path separator (e.g. `user.profile.name`). |
| `-a`, `--array-strategy` | `choice` | `join` | One of `join`, `index`, `explode`, or `json`. |
| `--array-joiner` | `string` | `; ` | Delimiter used between elements when array strategy is `join`. |
| `-m`, `--max-depth` | `int` | `10` | Maximum nesting depth before serializing deeper values as JSON strings. |
| `--fill-value` | `string` | `""` | Value inserted for missing properties (e.g. `NULL` or `N/A`). |
| `--bom` | `flag` | `False` | Prepend UTF-8 Byte Order Mark (`\ufeff`) for Microsoft Excel. |
| `--no-header` | `flag` | `False` | Exclude the top column header row. |
| `--no-sanitize` | `flag` | `False` | Disable formula injection prevention. |
| `--protect-numbers` | `flag` | `False` | Preserve leading zeros (`00123`) and scientific format (`1E5`). |
| `-k`, `--key` | `string` | `None` | Top-level dictionary key holding the array to convert (e.g. `-k data`). |
| `-c`, `--columns` | `string` | `None` | Comma-separated list of columns to include in custom export order. |
| `--web` | `flag` | `False` | Launch interactive browser studio. |
| `--port` | `int` | `8000` | Port for the local web server. |

---

## 🔄 Array Strategy Comparison

Given input:
```json
{
  "id": 1,
  "product": "Keyboard",
  "tags": ["gaming", "wireless"]
}
```

- **`join` (default)**: `gaming; wireless` in one cell
- **`index`**: creates `tags.0` (`gaming`) and `tags.1` (`wireless`)
- **`explode`**: generates 2 rows, repeating `id=1` and `product=Keyboard`
- **`json`**: stores raw JSON string `["gaming","wireless"]` in one cell

---

## 🧪 Running Tests

The test suite is built on Python's native `unittest` module:

```bash
python -m unittest discover tests
```

To run with verbose output:
```bash
python -m unittest discover tests -v
```

All 34 tests cover parser validation, line/column tracking, flattener strategies, RFC 4180 writer, CLI behavior, REST API endpoints, and fixture verification for all sample files.

---

## 📁 Repository Structure

```
json-to-csv/
├── app.py                       # Root launcher (runs web app or CLI)
├── pyproject.toml               # Package configuration
├── setup.py                     # Setup script
├── json_to_csv/                 # Core Python package
│   ├── __init__.py              # Package exports
│   ├── parser.py                # JSON validation & error locator
│   ├── flattener.py             # Recursive flattening & array handling
│   ├── headers.py               # Union-of-keys builder
│   ├── csv_writer.py            # RFC 4180 serializer
│   ├── cli.py                   # Command-line interface
│   ├── web.py                   # Embedded local HTTP server
│   └── static/                  # Web Studio UI assets
│       ├── index.html
│       ├── css/styles.css
│       └── js/app.js
├── tests/                       # Unit & integration test suite
│   ├── test_parser.py
│   ├── test_flattener.py
│   ├── test_headers.py
│   ├── test_csv_writer.py
│   ├── test_cli.py
│   ├── test_web.py
│   └── test_samples.py
├── samples/                     # Test datasets
│   ├── flat.json
│   ├── nested.json
│   ├── mixed-keys.json
│   ├── arrays.json
│   ├── unicode.json
│   ├── malformed.json
│   └── expected/                # Expected CSV fixtures
├── README.md
└── CHANGELOG.md
```

---

## 📄 License

MIT License. Free for personal and commercial use.
