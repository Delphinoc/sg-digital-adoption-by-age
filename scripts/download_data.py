"""Refresh data/raw/ from the data.gov.sg API.

The CSVs committed in data/raw/ were checked against the data.gov.sg API
(11 Nov 2026). Run this script to pull a newer survey year,
then rerun the pipeline and tests:

    python scripts/download_data.py
    python -m src.pipeline
    pytest
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATASETS, RAW_DIR  # noqa: E402

API = "https://data.gov.sg/api/action/datastore_search"


def fetch(dataset_id: str) -> pd.DataFrame:
    resp = requests.get(API, params={"resource_id": dataset_id, "limit": 1000}, timeout=30)
    resp.raise_for_status()
    records = resp.json()["result"]["records"]
    df = pd.DataFrame(records).drop(columns=["_id"], errors="ignore")
    year_cols = sorted([c for c in df.columns if c.isdigit()], reverse=True)
    return df[["DataSeries", *year_cols]]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, meta in DATASETS.items():
        df = fetch(meta["dataset_id"])
        df.to_csv(RAW_DIR / meta["file"], index=False)
        print(f"{name}: {len(df)} rows -> {meta['file']}")
        time.sleep(1)  # stay well inside the public rate limit


if __name__ == "__main__":
    main()
