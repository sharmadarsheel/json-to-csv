"""Module execution entry point (python -m json_to_csv)."""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
