#!/usr/bin/env python3
"""Entry point. Run `python decide.py --help`."""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from lib.cli import run

if __name__ == "__main__":
    sys.exit(run())
