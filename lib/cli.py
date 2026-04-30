"""CLI orchestration -- parse args, dispatch to mode, print result."""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from .gc2w import GC2W
from .mvc import MVCInput
from .modes.mode_101 import render_101
from .modes.mode_expert import render_expert


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="decide",
        description="GC2W x MVC x SG100Y decision-making CLI",
    )
    p.add_argument("--mode", choices=["101", "expert"], required=True)
    p.add_argument("--input", type=str, help="JSON file path with decision parameters")
    p.add_argument("--label", type=str, default="(unnamed)")
    p.add_argument("--ic", type=float)
    p.add_argument("--roic-before", type=float)
    p.add_argument("--roic-after", type=float)
    p.add_argument("--wacc", type=float, help="WACC (used if --wacc-before/--wacc-after omitted)")
    p.add_argument("--wacc-before", type=float)
    p.add_argument("--wacc-after", type=float)
    p.add_argument("--growth", type=float)
    p.add_argument("--connection", type=float)
    p.add_argument("--confidence", type=float)
    p.add_argument("--horizon-months", type=int, default=1200)
    return p


def load_params(args: argparse.Namespace) -> dict:
    if args.input:
        path = Path(args.input)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {}
    overrides = {
        "label": args.label,
        "ic": args.ic,
        "roic_before": args.roic_before,
        "roic_after": args.roic_after,
        "wacc_before": args.wacc_before if args.wacc_before is not None else args.wacc,
        "wacc_after": args.wacc_after if args.wacc_after is not None else args.wacc,
        "growth": args.growth,
        "connection": args.connection,
        "confidence": args.confidence,
        "horizon_months": args.horizon_months,
    }
    for k, v in overrides.items():
        if v is not None and v != "(unnamed)":
            data[k] = v
        elif k not in data and v is not None:
            data[k] = v
    data.setdefault("label", "(unnamed)")
    data.setdefault("horizon_months", 1200)
    required = ["ic", "roic_before", "roic_after", "wacc_before", "wacc_after",
                "growth", "connection", "confidence"]
    missing = [k for k in required if k not in data or data[k] is None]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")
    return data


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        p = load_params(args)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    gc2w = GC2W(
        growth=p["growth"],
        connection=p["connection"],
        confidence=p["confidence"],
        wacc=p["wacc_after"],
    )
    before = MVCInput(ic=p["ic"], roic=p["roic_before"], wacc=p["wacc_before"])
    after = MVCInput(ic=p["ic"], roic=p["roic_after"], wacc=p["wacc_after"])

    if args.mode == "101":
        out = render_101(p["label"], gc2w, before, after, p["horizon_months"])
    else:
        out = render_expert(p["label"], gc2w, before, after, p["horizon_months"])

    print(out)
    return 0
