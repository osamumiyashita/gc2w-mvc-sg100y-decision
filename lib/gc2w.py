"""GC²W — Growth, Connection, Confidence, WACC 4-dimensional decision vector.

Pure functions. No I/O. No mutation. Bounded ranges enforced at boundary.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class GC2W:
    growth: float        # [0.0, 1.0]  expected revenue growth rate (annual)
    connection: float    # [0.0, 1.0]  ROIC efficiency proxy
    confidence: float    # [0.0, 1.0]  inverse of WACC risk (higher = safer)
    wacc: float          # [0.0, 1.0]  weighted average cost of capital (annual)

    def __post_init__(self) -> None:
        for name, value in (
            ("growth", self.growth),
            ("connection", self.connection),
            ("confidence", self.confidence),
            ("wacc", self.wacc),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"GC2W.{name}={value} out of [0,1]")


def composite_score(v: GC2W) -> float:
    """Single scalar from 4D vector. Higher = more value-creating decision.

    Geometric mean of (G, C, C) divided by WACC penalty term.
    Range: [0, ∞).  Reference: ~1.0 = neutral, >1.5 = strong, <0.5 = weak.
    """
    gcc_geom = (max(v.growth, 1e-9) * max(v.connection, 1e-9) * max(v.confidence, 1e-9)) ** (1.0 / 3.0)
    wacc_penalty = 1.0 + v.wacc
    return gcc_geom / wacc_penalty


def nine_box_cell(v: GC2W) -> tuple[int, int, str]:
    """Map (Growth, Connection×Confidence) onto a 3×3 GCC matrix.

    Returns (row, col, label) where row 0=top (high G), col 0=left (low strength).
    """
    g_band = 2 if v.growth >= 0.66 else (1 if v.growth >= 0.33 else 0)
    strength = (v.connection + v.confidence) / 2.0
    s_band = 2 if strength >= 0.66 else (1 if strength >= 0.33 else 0)
    row = 2 - g_band
    col = s_band
    labels = {
        (0, 0): "High-G / Weak-base — risky bet",
        (0, 1): "High-G / Mid-base — scaling candidate",
        (0, 2): "High-G / Strong-base — flagship",
        (1, 0): "Mid-G / Weak-base — re-evaluate",
        (1, 1): "Mid-G / Mid-base — steady core",
        (1, 2): "Mid-G / Strong-base — cash cow upgrade",
        (2, 0): "Low-G / Weak-base — divest",
        (2, 1): "Low-G / Mid-base — harvest",
        (2, 2): "Low-G / Strong-base — cash cow",
    }
    return row, col, labels[(row, col)]
