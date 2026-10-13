"""RFC 4180 compliant CSV serializer with formula sanitization, BOM support, and number protection."""

from __future__ import annotations

import json
import re
from typing import Any

FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")
LEADING_ZERO_RE = re.compile(r"^0\d+$")
SCIENTIFIC_RE = re.compile(r"^[+-]?\d+(\.\d+)?[eE][+-]?\d+$")
LONG_DIGITS_RE = re.compile(r"^\d{16,}$")


def is_formula_injection(val: str) -> bool:
    """Checks if a string starts with a spreadsheet formula trigger."""
    return bool(val and val.startswith(FORMULA_TRIGGERS))


def should_protect_number(val: str) -> bool:
    """Checks if a string has leading zeros or scientific format prone to Excel mutation."""
    if not val:
        return False
    return bool(
        LEADING_ZERO_RE.match(val)
        or SCIENTIFIC_RE.match(val)
        or LONG_DIGITS_RE.match(val)
    )


def escape_cell(
    val: Any,
    delimiter: str = ",",
    fill_value: str = "",
    sanitize_formulas: bool = True,
    protect_numbers: bool = False,
) -> str:
    """Formats and escapes a single field value according to RFC 4180 rules.

    Args:
        val: Raw cell value.
        delimiter: CSV separator string.
        fill_value: Value used for None or missing entries.
        sanitize_formulas: Whether to prefix formula characters with an apostrophe.
        protect_numbers: Whether to protect strings like 00123 or 1E5 with an apostrophe.

    Returns:
        Properly escaped CSV cell string.
    """
    if val is None:
        if fill_value:
            return escape_cell(
                fill_value,
                delimiter=delimiter,
                fill_value="",
                sanitize_formulas=sanitize_formulas,
                protect_numbers=protect_numbers,
            )
        return ""

    if isinstance(val, bool):
        return "true" if val else "false"

    if isinstance(val, (int, float)):
        # Integer or float
        if isinstance(val, float) and val.is_integer():
            s = str(int(val))
        else:
            s = str(val)
    elif isinstance(val, (dict, list)):
        s = json.dumps(val, separators=(",", ":"))
    else:
        s = str(val)

    if not s and fill_value:
        s = fill_value

    if protect_numbers and should_protect_number(s):
        s = f"'{s}"

    if sanitize_formulas and is_formula_injection(s):
        if not s.startswith("'"):
            s = f"'{s}"

    # RFC 4180 escaping: wrap in quotes if contains delimiter, quote, or newline
    needs_quotes = (delimiter in s) or ('"' in s) or ("\n" in s) or ("\r" in s)
    if needs_quotes:
        escaped = s.replace('"', '""')
        return f'"{escaped}"'

    return s


def to_csv(
    rows: list[dict[str, Any]],
    headers: list[str],
    delimiter: str = ",",
    include_header: bool = True,
    fill_value: str = "",
    bom: bool = False,
    sanitize_formulas: bool = True,
    protect_numbers: bool = False,
) -> str:
    """Converts flattened row dictionaries and headers into an RFC 4180 CSV string.

    Args:
        rows: List of flat row dictionaries.
        headers: List of headers in desired column order.
        delimiter: Field separator (',', ';', '\t', '|').
        include_header: Whether to include the header row.
        fill_value: Replacement text for missing/null properties.
        bom: Whether to prepend UTF-8 Byte Order Mark (\ufeff).
        sanitize_formulas: Prefix dangerous formula triggers with apostrophe.
        protect_numbers: Protect leading zeros and scientific notation strings.

    Returns:
        Formatted CSV string with \r\n line endings.
    """
    lines: list[str] = []

    # Header line
    if include_header and headers:
        header_cells = [
            escape_cell(h, delimiter=delimiter, fill_value="", sanitize_formulas=False, protect_numbers=False)
            for h in headers
        ]
        lines.append(delimiter.join(header_cells))

    # Data lines
    for row in rows:
        cells = [
            escape_cell(
                row.get(h) if isinstance(row, dict) else None,
                delimiter=delimiter,
                fill_value=fill_value,
                sanitize_formulas=sanitize_formulas,
                protect_numbers=protect_numbers,
            )
            for h in headers
        ]
        lines.append(delimiter.join(cells))

    csv_text = "\r\n".join(lines)
    if bom:
        csv_text = "\ufeff" + csv_text

    return csv_text
