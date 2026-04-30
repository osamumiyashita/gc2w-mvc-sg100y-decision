"""Unit tests covering pure-function laws and CLI edge cases."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.gc2w import GC2W, composite_score, nine_box_cell
from lib.mvc import MVCInput, monthly_value_created, mvc_delta
from lib.sg100y import sg100y_npv, delta_sg100y, sensitivity_wacc
from lib.cli import run


class TestGC2W(unittest.TestCase):
    def test_bounded_range(self):
        with self.assertRaises(ValueError):
            GC2W(1.5, 0.5, 0.5, 0.5)
        with self.assertRaises(ValueError):
            GC2W(0.5, -0.1, 0.5, 0.5)

    def test_composite_monotone(self):
        low = GC2W(0.1, 0.1, 0.1, 0.5)
        high = GC2W(0.9, 0.9, 0.9, 0.05)
        self.assertGreater(composite_score(high), composite_score(low))

    def test_nine_box_corners(self):
        top_right = GC2W(0.9, 0.9, 0.9, 0.05)
        bot_left = GC2W(0.1, 0.1, 0.1, 0.5)
        self.assertEqual(nine_box_cell(top_right)[:2], (0, 2))
        self.assertEqual(nine_box_cell(bot_left)[:2], (2, 0))


class TestMVC(unittest.TestCase):
    def test_zero_when_roic_equals_wacc(self):
        x = MVCInput(ic=1000, roic=0.07, wacc=0.07)
        self.assertEqual(monthly_value_created(x), 0.0)

    def test_sign(self):
        plus = MVCInput(ic=1000, roic=0.10, wacc=0.07)
        minus = MVCInput(ic=1000, roic=0.05, wacc=0.07)
        self.assertGreater(monthly_value_created(plus), 0)
        self.assertLess(monthly_value_created(minus), 0)

    def test_negative_ic_rejected(self):
        with self.assertRaises(ValueError):
            monthly_value_created(MVCInput(ic=-1, roic=0.1, wacc=0.05))

    def test_delta_additivity(self):
        b = MVCInput(1000, 0.08, 0.07)
        a = MVCInput(1000, 0.12, 0.07)
        self.assertAlmostEqual(
            mvc_delta(b, a),
            monthly_value_created(a) - monthly_value_created(b),
        )


class TestSG100Y(unittest.TestCase):
    def test_npv_zero_for_zero_mvc(self):
        x = MVCInput(1000, 0.07, 0.07)
        self.assertEqual(sg100y_npv(x), 0.0)

    def test_npv_finite_and_positive(self):
        x = MVCInput(1000, 0.10, 0.07)
        npv = sg100y_npv(x)
        self.assertGreater(npv, 0)
        self.assertLess(npv, 1e9)

    def test_delta_decision(self):
        before = MVCInput(1000, 0.08, 0.07)
        after = MVCInput(1000, 0.12, 0.07)
        self.assertGreater(delta_sg100y(before, after), 0)

    def test_sensitivity_keys(self):
        x = MVCInput(1000, 0.10, 0.07)
        s = sensitivity_wacc(x, bp=100)
        self.assertIn("base", s)
        self.assertIn("wacc_+100bp", s)
        self.assertIn("wacc_-100bp", s)

    def test_zero_wacc_branch(self):
        x = MVCInput(1000, 0.05, 0.0)
        npv = sg100y_npv(x, horizon_months=12)
        expected = monthly_value_created(x) * 12
        self.assertAlmostEqual(npv, expected)


class TestCLI(unittest.TestCase):
    def test_101_mode_runs(self):
        sample = Path(__file__).resolve().parents[1] / "examples" / "sample_decision.json"
        rc = run(["--mode", "101", "--input", str(sample)])
        self.assertEqual(rc, 0)

    def test_expert_mode_runs(self):
        sample = Path(__file__).resolve().parents[1] / "examples" / "sample_decision.json"
        rc = run(["--mode", "expert", "--input", str(sample)])
        self.assertEqual(rc, 0)

    def test_missing_required_returns_error(self):
        rc = run(["--mode", "101", "--label", "x"])
        self.assertEqual(rc, 2)

    def test_inline_args(self):
        rc = run([
            "--mode", "expert",
            "--ic", "1000",
            "--roic-before", "0.08",
            "--roic-after", "0.12",
            "--wacc", "0.07",
            "--growth", "0.05",
            "--connection", "0.6",
            "--confidence", "0.7",
            "--label", "inline-test",
        ])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
