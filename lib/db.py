"""DuckDB persistence for decision history. Single-process, single-user."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "decisions.duckdb"

_COLUMNS = [
    "ts", "label",
    "ic", "roic_before", "roic_after", "wacc_before", "wacc_after",
    "growth", "connection", "confidence", "horizon_months",
    "mvc_before", "mvc_after", "mvc_delta",
    "sg_before", "sg_after", "sg_delta",
    "composite", "verdict",
]


def init_db(db_path: Path = DEFAULT_DB) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                ts TIMESTAMP,
                label VARCHAR,
                ic DOUBLE, roic_before DOUBLE, roic_after DOUBLE,
                wacc_before DOUBLE, wacc_after DOUBLE,
                growth DOUBLE, connection DOUBLE, confidence DOUBLE,
                horizon_months INTEGER,
                mvc_before DOUBLE, mvc_after DOUBLE, mvc_delta DOUBLE,
                sg_before DOUBLE, sg_after DOUBLE, sg_delta DOUBLE,
                composite DOUBLE, verdict VARCHAR
            )
            """
        )
    finally:
        con.close()


def insert_decision(row: dict[str, Any], db_path: Path = DEFAULT_DB) -> None:
    init_db(db_path)
    placeholders = ",".join(["?"] * len(_COLUMNS))
    cols_csv = ",".join(_COLUMNS)
    values = [row.get(c) for c in _COLUMNS]
    con = duckdb.connect(str(db_path))
    try:
        con.execute(f"INSERT INTO decisions ({cols_csv}) VALUES ({placeholders})", values)
    finally:
        con.close()


def fetch_recent(n: int = 10, db_path: Path = DEFAULT_DB) -> list[dict[str, Any]]:
    init_db(db_path)
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        cur = con.execute("SELECT * FROM decisions ORDER BY ts DESC LIMIT ?", [n])
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
    finally:
        con.close()
    return [dict(zip(cols, r)) for r in rows]
