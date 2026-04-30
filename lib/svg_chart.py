"""Pure-Python SVG charts. No matplotlib, no external graph library.

Generates inline SVG strings that embed directly into HTML.
"""
from __future__ import annotations


def bar_chart_mvc(mvc_before: float, mvc_after: float, width: int = 480, height: int = 280) -> str:
    margin = 40
    inner_w = width - 2 * margin
    inner_h = height - 2 * margin
    max_abs = max(abs(mvc_before), abs(mvc_after), 1e-9) * 1.2
    zero_y = margin + inner_h / 2
    bar_w = inner_w / 5
    bars = [("Before", mvc_before, "#999"), ("After", mvc_after, "#0a7")]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<text x="{width/2:.0f}" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">MVC monthly: before vs after</text>',
        f'<line x1="{margin}" y1="{zero_y:.1f}" x2="{width-margin}" y2="{zero_y:.1f}" stroke="#333"/>',
    ]
    for i, (label, val, color) in enumerate(bars):
        x = margin + (i + 1) * inner_w / 3 - bar_w / 2
        h = abs(val) / max_abs * (inner_h / 2)
        y = zero_y - h if val >= 0 else zero_y
        text_y = y - 6 if val >= 0 else y + h + 14
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{color}"/>')
        parts.append(f'<text x="{x+bar_w/2:.1f}" y="{height-margin/2:.0f}" text-anchor="middle" font-family="sans-serif" font-size="12">{label}</text>')
        parts.append(f'<text x="{x+bar_w/2:.1f}" y="{text_y:.1f}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#222">{val:+,.2f}</text>')
    parts.append("</svg>")
    return "".join(parts)


def line_chart_sg(curve: list[float], width: int = 480, height: int = 280) -> str:
    margin = 40
    inner_w = width - 2 * margin
    inner_h = height - 2 * margin
    n = len(curve)
    if n < 2:
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><text x="20" y="40">No curve data</text></svg>'
    max_y = max(curve) if max(curve) > 0 else 1.0
    min_y = min(curve) if min(curve) < 0 else 0.0
    span = max_y - min_y if max_y != min_y else 1.0
    pts = []
    for i, v in enumerate(curve):
        x = margin + i / (n - 1) * inner_w
        y = margin + (1 - (v - min_y) / span) * inner_h
        pts.append(f"{x:.1f},{y:.1f}")
    poly = " ".join(pts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="#fff"/>'
        f'<text x="{width/2:.0f}" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">SG100Y NPV by horizon</text>'
        f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="#333"/>'
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="#333"/>'
        f'<polyline fill="none" stroke="#0a7" stroke-width="2" points="{poly}"/>'
        f'<text x="{margin}" y="{height-margin+15}" font-family="sans-serif" font-size="10">1 mo</text>'
        f'<text x="{width-margin}" y="{height-margin+15}" text-anchor="end" font-family="sans-serif" font-size="10">{n} pts</text>'
        f'<text x="{margin-5}" y="{margin+5}" text-anchor="end" font-family="sans-serif" font-size="10">{max_y:,.0f}</text>'
        f'<text x="{margin-5}" y="{height-margin}" text-anchor="end" font-family="sans-serif" font-size="10">{min_y:,.0f}</text>'
        f"</svg>"
    )


def nine_box_svg(row: int, col: int, label: str, width: int = 320, height: int = 320) -> str:
    margin = 40
    cell_w = (width - 2 * margin) / 3
    cell_h = (height - 2 * margin) / 3
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#fff"/>',
        f'<text x="{width/2:.0f}" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">GCC 9-Box</text>',
    ]
    for r in range(3):
        for c in range(3):
            x = margin + c * cell_w
            y = margin + r * cell_h
            fill = "#0a7" if (r == row and c == col) else "#f4f4f4"
            text_color = "#fff" if (r == row and c == col) else "#666"
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w:.1f}" height="{cell_h:.1f}" fill="{fill}" stroke="#999"/>')
            parts.append(f'<text x="{x+cell_w/2:.1f}" y="{y+cell_h/2+4:.1f}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="{text_color}">{r},{c}</text>')
    parts.append(f'<text x="{width/2:.0f}" y="{height-margin+22:.0f}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#222">{label}</text>')
    parts.append(f'<text x="{margin-5}" y="{margin+cell_h*0.5:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">High G</text>')
    parts.append(f'<text x="{margin-5}" y="{margin+cell_h*2.5:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">Low G</text>')
    parts.append(f'<text x="{margin+cell_w*0.5:.1f}" y="{height-margin+10:.0f}" text-anchor="middle" font-family="sans-serif" font-size="10">Weak</text>')
    parts.append(f'<text x="{margin+cell_w*2.5:.1f}" y="{height-margin+10:.0f}" text-anchor="middle" font-family="sans-serif" font-size="10">Strong</text>')
    parts.append("</svg>")
    return "".join(parts)
