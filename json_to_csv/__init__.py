"""JSON to CSV Studio - High-performance Python converter with recursive flattening,
customizable array strategies, formula injection protection, and RFC 4180 compliance.
"""

from .parser import parse_json, find_array_of_object_keys
from .flattener import flatten_record, flatten_records
from .headers import build_headers, filter_and_reorder_headers
from .csv_writer import to_csv

__version__ = "1.0.0"
__all__ = [
    "parse_json",
    "find_array_of_object_keys",
    "flatten_record",
    "flatten_records",
    "build_headers",
    "filter_and_reorder_headers",
    "to_csv",
]
