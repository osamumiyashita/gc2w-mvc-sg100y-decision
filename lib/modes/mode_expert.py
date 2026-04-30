"""Expert mode — full mathematical breakdown.

Tabular output: GC²W vector, ΔMVC, SG100Y NPV before/after, ΔSG100Y, 9-box, WACC sensitivity.
"""
from ..gc2w import GC2W, composite_score, nine_box_cell
from ..mvc import MVCInput, monthly_value_created, mvc_delta, annualized
from ..sg100y import sg100y_npv, delta_sg100y, sensitivity_wacc


def render_expert(
    label: str,
    gc2w: GC2W,
    before: MVCInput,
    after: MVCInput,
    horizon_months: int = 1200,
) -> str:
    score = composite_score(gc2w)
    row, col, cell_label = nine_box_cell(gc2w)

    mvc_b = monthly_value_created(before)
    mvc_a = monthly_value_created(after)
    d_mvc = mvc_delta(before, after)

    sg_b = sg100y_npv(before, horizon_months)
    sg_a = sg100y_npv(after, horizon_months)
    d_sg = delta_sg100y(before, after, horizon_months)

    sens = sensitivity_wacc(after, bp=100, horizon_months=horizon_months)

    lines = [
        f"=== EXPERT REPORT -- {label} ===",
        "",
        "[GC2W vector]",
        f"  Growth     = {gc2w.growth:.4f}",
        f"  Connection = {gc2w.connection:.4f}",
        f"  Confidence = {gc2w.confidence:.4f}",
        f"  WACC       = {gc2w.wacc:.4f}",
        f"  Composite  = {score:.4f}   (>1.0 strong, <0.5 weak)",
        "",
        "[GCC 9-box]",
        f"  Cell (row={row}, col={col}): {cell_label}",
        "",
        "[MVC monthly]",
        f"  Before: IC={before.ic:,.2f}  ROIC={before.roic:.4f}  WACC={before.wacc:.4f}  -> MVC={mvc_b:+,.4f}",
        f"  After : IC={after.ic:,.2f}  ROIC={after.roic:.4f}  WACC={after.wacc:.4f}  -> MVC={mvc_a:+,.4f}",
        f"  Delta : {d_mvc:+,.4f}/month  ({annualized(d_mvc):+,.4f}/yr pre-discount)",
        "",
        f"[SG100Y NPV @ {horizon_months} months]",
        f"  Before: {sg_b:+,.4f}",
        f"  After : {sg_a:+,.4f}",
        f"  Delta : {d_sg:+,.4f}    {'<- value CREATED' if d_sg > 0 else '<- value DESTROYED'}",
        "",
        "[WACC sensitivity (post-decision, +/-100bp)]",
        f"  base       = {sens['base']:+,.4f}",
        f"  +100bp     = {sens['wacc_+100bp']:+,.4f}  (delta {sens['delta_+100bp']:+,.4f})",
        f"  -100bp     = {sens['wacc_-100bp']:+,.4f}  (delta {sens['delta_-100bp']:+,.4f})",
        "",
        "[Verdict]",
        f"  ΔSG100Y > 0 : {d_sg > 0}",
        f"  Composite >= 1.0 : {score >= 1.0}",
        f"  -> {'GO' if d_sg > 0 and score >= 1.0 else ('HOLD' if d_sg > 0 or score >= 1.0 else 'NO-GO')}",
    ]
    return "\n".join(lines)
