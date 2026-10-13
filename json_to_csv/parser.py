"""Parser module for JSON validation, error position extraction, and object introspection."""

from __future__ import annotations

import json
from typing import Any, TypedDict, Union


class ParseSuccess(TypedDict):
    ok: bool
    data: Any


class ParseError(TypedDict):
    ok: bool
    error: str
    line: int
    column: int


ParseResult = Union[ParseSuccess, ParseError]


def parse_json(text: str) -> ParseResult:
    """Parses JSON text and extracts exact line and column numbers on failure.

    Validates that the top-level structure is an array (list) or an object (dict),
    rejecting primitive JSON values (numbers, strings, booleans, null).

    Args:
        text: The raw JSON string to parse.

    Returns:
        A dictionary with {"ok": True, "data": ...} on success,
        or {"ok": False, "error": ..., "line": int, "column": int} on failure.
    """
    if not isinstance(text, str):
        return {
            "ok": False,
            "error": "Input must be a valid string.",
            "line": 1,
            "column": 1,
        }

    trimmed = text.strip()
    if not trimmed:
        return {
            "ok": False,
            "error": "JSON text is empty. Please provide JSON content.",
            "line": 1,
            "column": 1,
        }

    try:
        data = json.loads(text)

        # Validate top-level is list or dict, not primitive
        if data is None or not isinstance(data, (dict, list)):
            detected_type = "null" if data is None else type(data).__name__
            return {
                "ok": False,
                "error": f"Top-level JSON must be an array of objects or an object, but received primitive type '{detected_type}'.",
                "line": 1,
                "column": 1,
            }

        return {
            "ok": True,
            "data": data,
        }

    except json.JSONDecodeError as err:
        return {
            "ok": False,
            "error": f"Syntax error: {err.msg}",
            "line": err.lineno,
            "column": err.colno,
        }
    except Exception as err:
        return {
            "ok": False,
            "error": f"Error parsing JSON: {err}",
            "line": 1,
            "column": 1,
        }


def find_array_of_object_keys(obj: Any) -> list[str]:
    """Finds all top-level keys in a dictionary that contain a list of objects.

    Useful when a single top-level object wraps collections (e.g. {"data": [...]}).

    Args:
        obj: The dictionary to inspect.

    Returns:
        List of matching key names.
    """
    if not isinstance(obj, dict):
        return []

    keys: list[str] = []
    for key, value in obj.items():
        if isinstance(value, list) and len(value) > 0:
            if any(isinstance(item, dict) for item in value):
                keys.append(str(key))
    return keys
