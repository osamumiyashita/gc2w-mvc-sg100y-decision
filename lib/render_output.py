"""Fill the output_template.html with payload values.

Pure substitution: `{{key}}` -> str(value). No template engine dependency.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def render_template(template_path: Path, out_path: Path, payload: dict[str, Any]) -> Path:
    text = Path(template_path).read_text(encoding="utf-8")
    for key, value in payload.items():
        text = text.replace("{{" + key + "}}", str(value))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(text, encoding="utf-8")
    return Path(out_path)
