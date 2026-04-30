"""SG100Y — Sustainable Growth 100 Years NPV.

Definition (海憲法 §9):
    SG100Y = Σ_{t=1..H} MVC_t / (1 + WACC/12)^t      (H months, default 1200 = 100yrs)

Pure functions. Returns scalar NPV in currency units.
"""
from .mvc import MVCInput, monthly_value_created


def sg100y_npv(x: MVCInput, horizon_months: int = 1200) -> float:
    """100-year NPV under constant ROIC/WACC assumption (closed form)."""
    if horizon_months <= 0:
        raise ValueError(f"horizon_months must be positive, got {horizon_months}")
    mvc = monthly_value_created(x)
    if mvc == 0.0:
        return 0.0
    r = x.wacc / 12.0
    if r == 0.0:
        return mvc * horizon_months
    return mvc * (1.0 - (1.0 + r) ** (-horizon_months)) / r


def delta_sg100y(before: MVCInput, after: MVCInput, horizon_months: int = 1200) -> float:
    """ΔSG100Y for a decision. ΔSG100Y > 0 ⟺ value-creating decision."""
    return sg100y_npv(after, horizon_months) - sg100y_npv(before, horizon_months)


def sensitivity_wacc(x: MVCInput, bp: int = 100, horizon_months: int = 1200) -> dict:
    """Sensitivity of SG100Y to ±bp basis-point shift in WACC."""
    delta = bp / 10000.0
    base = sg100y_npv(x, horizon_months)
    up = sg100y_npv(MVCInput(x.ic, x.roic, x.wacc + delta), horizon_months)
    down = sg100y_npv(MVCInput(x.ic, x.roic, x.wacc - delta), horizon_months)
    return {
        "base": base,
        f"wacc_+{bp}bp": up,
        f"wacc_-{bp}bp": down,
        f"delta_+{bp}bp": up - base,
        f"delta_-{bp}bp": down - base,
    }
