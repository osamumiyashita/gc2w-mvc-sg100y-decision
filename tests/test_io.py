"""Unit tests for serverless I/O layer: db, svg, render, pipeline."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.db import init_db, insert_decision, fetch_recent
from lib.svg_chart import bar_chart_mvc, line_chart_sg, nine_box_svg
from lib.render_output import render_template
from lib.pipeline import run_pipeline


class TestDB(unittest.TestCase):
    def test_init_insert_fetch_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "t.duckdb"
            init_db(db)
            from datetime import datetime
            row = {
                "ts": datetime.now(), "label": "T1",
                "ic": 1000.0, "roic_before": 0.08, "roic_after": 0.12,
                "wacc_before": 0.07, "wacc_after": 0.07,
                "growth": 0.5, "connection": 0.5, "confidence": 0.5,
                "horizon_months": 1200,
                "mvc_before": 1.0, "mvc_after": 2.0, "mvc_delta": 1.0,
                "sg_before": 100.0, "sg_after": 200.0, "sg_delta": 100.0,
                "composite": 0.7, "verdict": "GO",
            }
            insert_decision(row, db)
            rows = fetch_recent(10, db)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["label"], "T1")
            self.assertEqual(rows[0]["verdict"], "GO")


class TestSVG(unittest.TestCase):
    def test_bar_chart_returns_svg(self):
        s = bar_chart_mvc(1.0, 2.0)
        self.assertTrue(s.startswith("<svg"))
        self.assertIn("Before", s)
        self.assertIn("After", s)

    def test_bar_chart_handles_negative(self):
        s = bar_chart_mvc(-3.0, 2.0)
        self.assertIn("-3", s)

    def test_line_chart_returns_svg(self):
        s = line_chart_sg([0.0, 10.0, 25.0, 40.0, 50.0])
        self.assertTrue(s.startswith("<svg"))
        self.assertIn("polyline", s)

    def test_line_chart_short_input(self):
        s = line_chart_sg([1.0])
        self.assertTrue(s.startswith("<svg"))

    def test_nine_box_highlights_cell(self):
        s = nine_box_svg(0, 2, "test")
        self.assertTrue(s.startswith("<svg"))
        self.assertIn("test", s)
        self.assertIn("#0a7", s)


class TestRenderTemplate(unittest.TestCase):
    def test_substitution(self):
        with tempfile.TemporaryDirectory() as td:
            tpl = Path(td) / "tpl.html"
            tpl.write_text("Hello {{name}}, score {{score}}", encoding="utf-8")
            out = Path(td) / "out.html"
            render_template(tpl, out, {"name": "Kai", "score": 42})
            self.assertEqual(out.read_text(encoding="utf-8"), "Hello Kai, score 42")


class TestPipeline(unittest.TestCase):
    def test_pipeline_e2e(self):
        with tempfile.TemporaryDirectory() as td:
            params = {
                "label": "E2E", "ic": 1000.0,
                "roic_before": 0.08, "roic_after": 0.12,
                "wacc_before": 0.07, "wacc_after": 0.07,
                "growth": 0.5, "connection": 0.6, "confidence": 0.7,
                "horizon_months": 1200,
            }
            template = Path(__file__).resolve().parents[1] / "ui" / "output_template.html"
            out_dir = Path(td) / "out"
            from unittest.mock import patch
            with patch("lib.pipeline.insert_decision"), patch("lib.pipeline.fetch_recent", return_value=[]):
                out = run_pipeline(params, template, out_dir)
            self.assertTrue(out.exists())
            html = out.read_text(encoding="utf-8")
            self.assertIn("E2E", html)
            self.assertIn("svg", html.lower())
            self.assertNotIn("{{", html)


if __name__ == "__main__":
    unittest.main()
