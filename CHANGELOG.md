# Changelog

All notable changes and deliverables implemented for JSON to CSV Studio.

## [1.0.0] - 2026-10-13

### Added
- **Core Architecture & Modules**:
  - `parser.js`: Robust JSON parsing with line and column extraction for syntax errors, primitive rejection, and top-level object array detection.
  - `flattener.js`: Pure recursive flattening logic supporting custom separators (`.`, `_`, `/`), maximum depth limit (`maxDepth`), collision handling (`_2`), and all 4 array strategies (`join`, `index`, `explode`, `json`).
  - `headers.js`: Union-of-keys header builder maintaining first-seen insertion order and column selection filtering.
  - `csvWriter.js`: RFC 4180 serializer featuring proper quote escaping, CRLF line endings, customizable delimiters (comma, semicolon, tab, pipe), UTF-8 BOM, missing fill values, formula injection protection, and leading-zero number preservation.
  - `utils.js`: Helpers for client-side CSV download, clipboard copying, byte formatting, localStorage preset storage, and reverse CSV-to-JSON parsing.
  - `worker.js`: Web Worker implementation for non-blocking conversion of large JSON files (> 10MB) in a background thread.
- **User Interface**:
  - Accessible, responsive single-page application with modern dark/light mode and glassmorphic card design.
  - 3-step structured workflow: Input, Configuration, and Preview & Export.
  - File upload with drag-and-drop zone and paste textarea with live character counter.
  - Quick-load sample data dropdown (Flat, Nested, Arrays, Mixed Keys, Unicode).
  - Top-level collection dropdown for nested array selection.
  - Live 50-row preview table with sticky headers and responsive stats counter.
  - Interactive draggable column picker with real-time search filter and select/deselect all actions.
  - Reverse CSV to JSON modal dialog.
  - Settings preset save and load capability via `localStorage`.
- **Test Suite**:
  - Unit tests using Node 22's native test runner (`node:test`) covering parser, flattener, headers, csvWriter, and sample fixture verifications (34 passing tests).
- **Samples & Documentation**:
  - Pre-packaged sample files (`flat.json`, `nested.json`, `mixed-keys.json`, `arrays.json`, `unicode.json`, `malformed.json`) and expected CSV outputs.
  - Complete `README.md` and `CHANGELOG.md`.
