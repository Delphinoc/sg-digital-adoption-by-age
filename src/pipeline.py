"""Load raw data.gov.sg CSVs, reshape to long format, run DuckDB SQL models,
run data-quality checks and export Tableau-ready CSVs.

Run from the repo root:  python -m src.pipeline
"""
from __future__ import annotations

import sys

import duckdb
import pandas as pd

from src import checks
from src.config import DATASETS, DB_PATH, PROCESSED_DIR, RAW_DIR, SEGMENT_MAP, SQL_DIR


def load_raw(raw_dir=RAW_DIR) -> pd.DataFrame:
    """Read every wide CSV (DataSeries + one column per year) into one long table."""
    frames = []
    for indicator, meta in DATASETS.items():
        wide = pd.read_csv(raw_dir / meta["file"])
        wide = wide.rename(columns={wide.columns[0]: "DataSeries"})
        wide["DataSeries"] = wide["DataSeries"].astype(str).str.strip()
        long = wide.melt(id_vars="DataSeries", var_name="year", value_name="pct")
        long["year"] = long["year"].astype(int)
        # data.gov.sg uses "na" for not available; coerce to NaN so checks can catch it
        long["pct"] = pd.to_numeric(long["pct"], errors="coerce")
        long["segment"] = long["DataSeries"].map(SEGMENT_MAP)
        long["indicator"] = indicator
        long["segment_type"] = meta["segment_type"]
        long["ladder_step"] = meta["ladder_step"]
        frames.append(long)
    return pd.concat(frames, ignore_index=True)[
        ["indicator", "segment", "segment_type", "ladder_step", "DataSeries", "year", "pct"]
    ]


def run_models(con: duckdb.DuckDBPyConnection, raw_long: pd.DataFrame) -> None:
    con.register("raw_long_df", raw_long)
    con.execute("CREATE OR REPLACE TABLE raw_long AS SELECT * FROM raw_long_df")
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        con.execute(sql_file.read_text())


def export(con: duckdb.DuckDBPyConnection, out_dir=PROCESSED_DIR) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = [
        "stg_indicators", "mart_age_gap", "mart_adoption_ladder", "mart_gap_change",
        "dim_indicator", "dim_segment", "dim_year", "fact_adoption",
    ]
    for t in tables:
        con.execute(f"SELECT * FROM {t}").df().to_csv(out_dir / f"{t}.csv", index=False)
    return tables


def main(db_path=DB_PATH) -> int:
    raw_long = load_raw()
    results = checks.run_all(raw_long)
    print(checks.format_report(results))
    if any(r.severity == "error" and not r.passed for r in results):
        print("\nPipeline stopped: fix the failed data-quality checks above.")
        return 1

    con = duckdb.connect(str(db_path))
    run_models(con, raw_long)
    tables = export(con)
    con.close()
    print(f"\nExported {len(tables)} tables to {PROCESSED_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
