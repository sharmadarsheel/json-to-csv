"""Header builder for union-of-keys in first-seen order and column filtering."""

from __future__ import annotations

from typing import Any


def build_headers(flat_records: list[dict[str, Any]]) -> list[str]:
    """Builds a union of all dictionary keys across all records, preserving first-seen order.

    Args:
        flat_records: List of flattened dictionaries.

    Returns:
        List of unique column headers.
    """
    if not isinstance(flat_records, list):
        return []

    seen: set[str] = set()
    headers: list[str] = []

    for record in flat_records:
        if not isinstance(record, dict):
            continue
        for key in record.keys():
            key_str = str(key)
            if key_str not in seen:
                seen.add(key_str)
                headers.append(key_str)

    return headers


def filter_and_reorder_headers(
    all_headers: list[str], selected_headers: list[str] | None
) -> list[str]:
    """Filters and reorders headers according to custom user selection.

    Args:
        all_headers: Full list of detected headers.
        selected_headers: User-specified order/selection.

    Returns:
        Ordered list of selected headers that exist in all_headers.
    """
    if selected_headers is None:
        return list(all_headers)

    available = set(all_headers)
    return [h for h in selected_headers if h in available]
