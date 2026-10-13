#!/usr/bin/env python3
"""JSON to CSV Studio - Application Runner.

Run without arguments to launch the local web interface:
    python app.py

Or use with CLI arguments to convert from command-line:
    python app.py -i input.json -o output.csv
"""

import sys
from json_to_csv.cli import main

if __name__ == "__main__":
    # If no arguments provided, default to launching the interactive web app
    if len(sys.argv) == 1:
        sys.exit(main(["--web"]))
    else:
        sys.exit(main())
