#!/usr/bin/env python3
"""Serverless I/O orchestrator.

Three modes:
  python decide_io.py            # default: open form + watch inbox/ for new JSON
  python decide_io.py form       # open input form only
  python decide_io.py compute X  # compute from JSON file X, write+open output HTML
  python decide_io.py watch      # poll inbox/ until new JSON arrives, then compute

No HTTP listener. No DB daemon. Pure one-shot Python with file-watching.
"""
from __future__ import annotations

import sys
import time
import json
import webbrowser
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.pipeline import run_pipeline

UI_DIR = ROOT / "ui"
INBOX = ROOT / "inbox"
OUT_DIR = ROOT / "outputs"
TEMPLATE = UI_DIR / "output_template.html"
WATCH_TIMEOUT_S = 600


def open_input_form() -> None:
    INBOX.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    url = (UI_DIR / "input.html").as_uri()
    print(f"Opening input form: {url}")
    webbrowser.open(url)


def compute(input_path: Path) -> Path:
    p = json.loads(Path(input_path).read_text(encoding="utf-8"))
    out = run_pipeline(p, TEMPLATE, OUT_DIR)
    print(f"Wrote {out}")
    webbrowser.open(out.as_uri())
    return out


def watch_inbox(timeout_s: int = WATCH_TIMEOUT_S) -> None:
    INBOX.mkdir(exist_ok=True)
    print(f"Watching {INBOX}/ for new *.json (timeout {timeout_s}s)")
    seen = {p.name for p in INBOX.glob("*.json")}
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        for p in sorted(INBOX.glob("*.json")):
            if p.name not in seen:
                print(f"Detected: {p.name}")
                compute(p)
                return
        time.sleep(2)
    print("Timeout - no new file in inbox/.")


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        open_input_form()
        watch_inbox()
        return 0
    cmd = args[0]
    if cmd == "form":
        open_input_form()
        return 0
    if cmd == "watch":
        watch_inbox()
        return 0
    if cmd == "compute":
        if len(args) < 2:
            print("Usage: python decide_io.py compute <input.json>", file=sys.stderr)
            return 2
        compute(Path(args[1]))
        return 0
    print(f"Unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
