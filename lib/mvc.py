"""MVC — Monthly Value Created.

Definition (海憲法 §2):
    MVC_t = IC × (ROIC_t - WACC) / 12

Pure functions. All rates are annual decimals.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class MVCInput:
    ic: float            # invested capital (currency units)
    roic: float          # return on invested capital (annual decimal)
    wacc: float          # weighted average cost of capital (annual decimal)


def monthly_value_created(x: MVCInput) -> float:
    """Single-month MVC. Positive => value-creating, negative => value-destroying."""
    if x.ic < 0:
        raise ValueError(f"IC must be non-negative, got {x.ic}")
    return x.ic * (x.roic - x.wacc) / 12.0


def mvc_delta(before: MVCInput, after: MVCInput) -> float:
    """ΔMVC from a decision (after − before)."""
    return monthly_value_created(after) - monthly_value_created(before)


def annualized(mvc_monthly: float) -> float:
    """Annualize a single-month MVC by ×12 (pre-discount)."""
    return mvc_monthly * 12.0
