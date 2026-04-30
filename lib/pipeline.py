"""End-to-end pipeline: input dict -> compute -> persist -> render output.html."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .gc2w import GC2W, composite_score, nine_box_cell
from .mvc import MVCInput, monthly_value_created
from .sg100y import sg100y_npv
from .modes.mode_101 import render_101
from .db import insert_decision, fetch_recent
from .svg_chart import bar_chart_mvc, line_chart_sg, nine_box_svg
from .render_output import render_template


def _verdict(d_sg: float, score: float) -> str:
    if d_sg > 0 and score >= 1.0:
        return "GO"
    if d_sg > 0 or score >= 1.0:
        return "HOLD"
    return "NO-GO"


def _sg_curve(after: MVCInput, horizon: int, points: int = 60) -> list[float]:
    n = max(2, min(horizon, points))
    return [sg100y_npv(after, max(1, int(1 + (horizon - 1) * i / (n - 1)))) for i in range(n)]


def _history_html(rows: list[dict[str, Any]]) -> str:
    out = ['<table><tr><th>Time</th><th>Label</th><th>Verdict</th><th>&Delta;SG100Y</th></tr>']
    for h in rows:
        out.append(
            f'<tr><td>{h["ts"]}</td><td>{h["label"]}</td>'
            f'<td>{h["verdict"]}</td><td>{h["sg_delta"]:+,.2f}</td></tr>'
        )
    out.append("</table>")
    return "".join(out)


def run_pipeline(params: dict[str, Any], template_path: Path, out_dir: Path) -> Path:
    horizon = int(params.get("horizon_months", 1200))
    g = GC2W(
        growth=params["growth"],
        connection=params["connection"],
        confidence=params["confidence"],
        wacc=params["wacc_after"],
    )
    before = MVCInput(ic=params["ic"], roic=params["roic_before"], wacc=params["wacc_before"])
    after = MVCInput(ic=params["ic"], roic=params["roic_after"], wacc=params["wacc_after"])

    mvc_b = monthly_value_created(before)
    mvc_a = monthly_value_created(after)
    sg_b = sg100y_npv(before, horizon)
    sg_a = sg100y_npv(after, horizon)
    score = composite_score(g)
    row, col, cell_label = nine_box_cell(g)
    d_sg = sg_a - sg_b
    verdict = _verdict(d_sg, score)

    ts = datetime.now()
    record = {
        "ts": ts, "label": params["label"],
        "ic": params["ic"], "roic_before": params["roic_before"], "roic_after": params["roic_after"],
        "wacc_before": params["wacc_before"], "wacc_after": params["wacc_after"],
        "growth": params["growth"], "connection": params["connection"],
        "confidence": params["confidence"], "horizon_months": horizon,
        "mvc_before": mvc_b, "mvc_after": mvc_a, "mvc_delta": mvc_a - mvc_b,
        "sg_before": sg_b, "sg_after": sg_a, "sg_delta": d_sg,
        "composite": score, "verdict": verdict,
    }
    insert_decision(record)

    plain = render_101(params["label"], g, before, after, horizon)
    history = fetch_recent(10)

    payload = {
        "label": params["label"], "verdict": verdict,
        "verdict_class": verdict.replace("-", ""),
        "plain": plain,
        "svg_bar": bar_chart_mvc(mvc_b, mvc_a),
        "svg_line": line_chart_sg(_sg_curve(after, horizon)),
        "svg_9box": nine_box_svg(row, col, cell_label),
        "mvc_before": f"{mvc_b:+,.4f}", "mvc_after": f"{mvc_a:+,.4f}",
        "mvc_delta": f"{mvc_a-mvc_b:+,.4f}",
        "sg_before": f"{sg_b:+,.2f}", "sg_after": f"{sg_a:+,.2f}",
        "sg_delta": f"{d_sg:+,.2f}",
        "composite": f"{score:.4f}",
        "ic": f"{params['ic']:,.2f}", "horizon_months": horizon,
        "roic_before": f"{params['roic_before']:.4f}",
        "roic_after": f"{params['roic_after']:.4f}",
        "wacc_before": f"{params['wacc_before']:.4f}",
        "wacc_after": f"{params['wacc_after']:.4f}",
        "growth": f"{params['growth']:.4f}",
        "connection": f"{params['connection']:.4f}",
        "confidence": f"{params['confidence']:.4f}",
        "history_table": _history_html(history),
        "ts": ts.strftime("%Y-%m-%d %H:%M:%S"),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"output_{ts.strftime('%Y%m%d_%H%M%S')}.html"
    return render_template(template_path, out_path, payload)
