"""Recursive flattening logic with array strategies, depth limits, and collision handling."""

from __future__ import annotations

import json
from typing import Any, Literal, Union

ArrayStrategy = Literal["join", "index", "explode", "json"]


def resolve_key_collision(key: str, existing_keys: set[str] | dict[str, Any]) -> str:
    """Resolves duplicate column keys by appending _2, _3, etc.

    Args:
        key: Desired key name.
        existing_keys: Set or dict of already allocated keys.

    Returns:
        A unique key name.
    """
    if key not in existing_keys:
        return key

    counter = 2
    candidate = f"{key}_{counter}"
    while candidate in existing_keys:
        counter += 1
        candidate = f"{key}_{counter}"
    return candidate


def _walk_non_explode(
    current: Any,
    prefix: str,
    depth: int,
    separator: str,
    max_depth: int,
    array_strategy: ArrayStrategy,
    array_joiner: str,
    output: dict[str, Any],
) -> None:
    """Recursively walks nested structures for non-explode strategies."""
    # Beyond max depth: serialize complex containers as JSON strings
    if depth > max_depth and isinstance(current, (dict, list)):
        final_key = resolve_key_collision(prefix, output)
        output[final_key] = json.dumps(current, separators=(",", ":"))
        return

    if isinstance(current, dict):
        if not current and prefix:
            final_key = resolve_key_collision(prefix, output)
            output[final_key] = {}
            return
        for k, v in current.items():
            next_key = f"{prefix}{separator}{k}" if prefix else str(k)
            _walk_non_explode(
                v, next_key, depth + 1, separator, max_depth, array_strategy, array_joiner, output
            )
        return

    if isinstance(current, list):
        if array_strategy == "json":
            final_key = resolve_key_collision(prefix, output)
            output[final_key] = json.dumps(current, separators=(",", ":"))
            return

        if array_strategy == "join":
            final_key = resolve_key_collision(prefix, output)
            if not current:
                output[final_key] = ""
            else:
                parts = []
                for item in current:
                    if item is None:
                        parts.append("")
                    elif isinstance(item, (dict, list)):
                        parts.append(json.dumps(item, separators=(",", ":")))
                    else:
                        parts.append(str(item))
                output[final_key] = array_joiner.join(parts)
            return

        if array_strategy == "index":
            if not current:
                final_key = resolve_key_collision(prefix, output)
                output[final_key] = ""
                return
            for idx, item in enumerate(current):
                next_key = f"{prefix}{separator}{idx}"
                _walk_non_explode(
                    item, next_key, depth + 1, separator, max_depth, array_strategy, array_joiner, output
                )
            return

    # Primitive scalar value
    final_key = resolve_key_collision(prefix, output)
    output[final_key] = current


def _walk_explode(
    obj: dict[str, Any],
    separator: str,
    max_depth: int,
    array_joiner: str,
) -> list[dict[str, Any]]:
    """Cartesian expansion across array fields for the 'explode' strategy."""

    def extract_paths(val: Any, prefix: str = "", depth: int = 1) -> tuple[dict[str, Any], dict[str, list[Any]]]:
        if depth > max_depth and isinstance(val, (dict, list)):
            return {prefix: json.dumps(val, separators=(",", ":"))}, {}

        if isinstance(val, list):
            return {}, {prefix: val}

        if isinstance(val, dict):
            if not val and prefix:
                return {prefix: {}}, {}
            scalars: dict[str, Any] = {}
            arrays: dict[str, list[Any]] = {}
            for k, v in val.items():
                next_key = f"{prefix}{separator}{k}" if prefix else str(k)
                sub_scalars, sub_arrays = extract_paths(v, next_key, depth + 1)
                scalars.update(sub_scalars)
                arrays.update(sub_arrays)
            return scalars, arrays

        return {prefix: val}, {}

    scalars, arrays = extract_paths(obj)
    array_keys = list(arrays.keys())

    # If no arrays exist, return single flattened row
    if not array_keys:
        final_row: dict[str, Any] = {}
        for k, v in scalars.items():
            resolved = resolve_key_collision(k, final_row)
            final_row[resolved] = v
        return [final_row]

    rows: list[dict[str, Any]] = [dict(scalars)]

    for arr_key in array_keys:
        arr = arrays[arr_key]
        new_rows: list[dict[str, Any]] = []

        if not arr:
            for row in rows:
                new_row = dict(row)
                new_row[arr_key] = None
                new_rows.append(new_row)
        else:
            for item in arr:
                item_fields: dict[str, Any] = {}
                if isinstance(item, dict):
                    flattened_item: dict[str, Any] = {}
                    _walk_non_explode(
                        item, arr_key, 1, separator, max_depth, "join", array_joiner, flattened_item
                    )
                    item_fields = flattened_item
                elif isinstance(item, list):
                    item_fields[arr_key] = json.dumps(item, separators=(",", ":"))
                else:
                    item_fields[arr_key] = item

                for r in rows:
                    combined = dict(r)
                    combined.update(item_fields)
                    new_rows.append(combined)

        rows = new_rows

    # Resolve collisions on all rows
    resolved_rows: list[dict[str, Any]] = []
    for r in rows:
        fixed: dict[str, Any] = {}
        for k, v in r.items():
            res = resolve_key_collision(k, fixed)
            fixed[res] = v
        resolved_rows.append(fixed)

    return resolved_rows


def flatten_record(
    obj: Any,
    separator: str = ".",
    max_depth: int = 10,
    array_strategy: ArrayStrategy = "join",
    array_joiner: str = "; ",
) -> Union[dict[str, Any], list[dict[str, Any]]]:
    """Flattens a single JSON object.

    Args:
        obj: Dict object to flatten.
        separator: String delimiter for nested properties (default: '.').
        max_depth: Max recursion depth before serializing as JSON (default: 10).
        array_strategy: Array handling strategy ('join', 'index', 'explode', 'json').
        array_joiner: Sub-delimiter when array_strategy='join' (default: '; ').

    Returns:
        Flattened dict, or a list of flattened dicts if array_strategy='explode'.
    """
    if not isinstance(obj, dict):
        return {}

    strategy: ArrayStrategy = array_strategy if array_strategy in ("join", "index", "explode", "json") else "join"
    depth = max(1, max_depth) if isinstance(max_depth, int) else 10

    if strategy == "explode":
        return _walk_explode(obj, separator, depth, array_joiner)

    output: dict[str, Any] = {}
    _walk_non_explode(obj, "", 1, separator, depth, strategy, array_joiner, output)
    return output


def flatten_records(
    data: Any,
    separator: str = ".",
    max_depth: int = 10,
    array_strategy: ArrayStrategy = "join",
    array_joiner: str = "; ",
) -> tuple[list[dict[str, Any]], int]:
    """Flattens a list of records (or single record) into flat row dictionaries.

    Non-dict items inside the collection are skipped and counted.

    Args:
        data: List of records or single dict.
        separator: Key separator string.
        max_depth: Max recursion depth.
        array_strategy: Chosen array strategy.
        array_joiner: String joiner for arrays.

    Returns:
        Tuple of (list of flattened row dicts, skipped records count).
    """
    rows = data if isinstance(data, list) else [data]
    flat_rows: list[dict[str, Any]] = []
    skipped_count = 0

    for item in rows:
        if not isinstance(item, dict):
            skipped_count += 1
            continue

        flattened = flatten_record(
            item,
            separator=separator,
            max_depth=max_depth,
            array_strategy=array_strategy,
            array_joiner=array_joiner,
        )

        if isinstance(flattened, list):
            flat_rows.extend(flattened)
        else:
            flat_rows.append(flattened)

    return flat_rows, skipped_count
