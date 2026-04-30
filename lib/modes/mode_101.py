"""101 mode — plain-language verdict for non-finance readers.

No jargon. No formulas. 5 lines + GO / NO-GO / HOLD.
"""
from ..gc2w import GC2W, composite_score, nine_box_cell
from ..mvc import MVCInput, mvc_delta
from ..sg100y import delta_sg100y


def render_101(
    label: str,
    gc2w: GC2W,
    before: MVCInput,
    after: MVCInput,
    horizon_months: int = 1200,
) -> str:
    d_mvc = mvc_delta(before, after)
    d_sg = delta_sg100y(before, after, horizon_months)
    score = composite_score(gc2w)
    _, _, cell_label = nine_box_cell(gc2w)

    if d_sg > 0 and score >= 1.0:
        verdict = "GO"
        gut = "This decision creates lasting value. The numbers and the position both agree."
    elif d_sg > 0 and score < 1.0:
        verdict = "HOLD"
        gut = "Numbers say yes, but the strategic position is shaky. Confirm assumptions before committing."
    elif d_sg <= 0 and score >= 1.0:
        verdict = "HOLD"
        gut = "Strategic position looks strong, but the math does not show value creation. Re-check the IC/ROIC inputs."
    else:
        verdict = "NO-GO"
        gut = "This decision destroys value. Either pass, or redesign it before re-evaluating."

    money_per_month = f"{d_mvc:+,.1f}"
    money_100y = f"{d_sg:+,.1f}"

    return "\n".join([
        f"DECISION: {label}",
        f"VERDICT:  {verdict}",
        f"  -> Monthly value change: {money_per_month}",
        f"  -> 100-year value change: {money_100y}",
        f"  -> Strategic position:   {cell_label}",
        f"  -> Plain take: {gut}",
    ])
