"""Each data-quality rule passes on clean data and catches an injected issue."""
import pandas as pd
import pytest

from src import checks
from src.pipeline import load_raw


@pytest.fixture
def clean():
    return load_raw()


def _result(df, rule):
    return rule(df)


def test_clean_snapshot_has_no_errors(clean):
    results = checks.run_all(clean)
    failed = [r.rule for r in results if r.severity == "error" and not r.passed]
    assert failed == []


def test_unknown_segment_caught(clean):
    df = clean.copy()
    df.loc[0, "segment"] = None
    df.loc[0, "DataSeries"] = "Residents Aged 99+"
    assert not checks.check_known_segments(df).passed


def test_missing_segment_caught(clean):
    df = clean[~((clean.indicator == "online_purchase") & (clean.segment == "age_60_plus"))]
    r = checks.check_expected_segments(df)
    assert not r.passed and "online_purchase" in r.issues[0]


def test_missing_year_caught(clean):
    df = clean[~((clean.indicator == "internet_usage") & (clean.year == 2020))]
    assert not checks.check_year_coverage(df).passed


def test_null_value_caught(clean):
    df = clean.copy()
    df.loc[5, "pct"] = float("nan")
    assert not checks.check_no_nulls(df).passed


@pytest.mark.parametrize("bad_value", [-1.0, 100.5, 914.0])
def test_out_of_range_caught(clean, bad_value):
    df = clean.copy()
    df.loc[3, "pct"] = bad_value
    assert not checks.check_range(df).passed


def test_duplicate_row_caught(clean):
    df = pd.concat([clean, clean.iloc[[0]]], ignore_index=True)
    assert not checks.check_unique_keys(df).passed


def test_overall_outside_bands_caught(clean):
    df = clean.copy()
    mask = (df.indicator == "smartphone_ownership") & (df.segment == "all_18_plus") & (df.year == 2024)
    df.loc[mask, "pct"] = 50.0  # below every age band that year
    assert not checks.check_overall_within_bands(df).passed


def test_ladder_breach_flagged_as_warning(clean):
    df = clean.copy()
    mask = (df.indicator == "online_purchase") & (df.segment == "age_60_plus") & (df.year == 2024)
    df.loc[mask, "pct"] = 95.0
    r = checks.check_ladder_order(df)
    assert not r.passed and r.severity == "warning"


def test_yoy_swing_flagged(clean):
    df = clean.copy()
    mask = (df.indicator == "smartphone_ownership") & (df.segment == "age_18_39") & (df.year == 2022)
    df.loc[mask, "pct"] = 70.0
    assert not checks.check_yoy_swings(df).passed


def test_na_string_coerced_to_null(tmp_path, clean):
    """data.gov.sg writes 'na' for unavailable values; the loader must not crash on it."""
    from src.config import DATASETS
    for meta in DATASETS.values():
        src = pd.read_csv(f"data/raw/{meta['file']}")
        src.to_csv(tmp_path / meta["file"], index=False)
    f = tmp_path / DATASETS["internet_usage"]["file"]
    raw = pd.read_csv(f)
    raw["2019"] = raw["2019"].astype(object)
    raw.loc[0, "2019"] = "na"
    raw.to_csv(f, index=False)
    df = load_raw(tmp_path)
    assert df["pct"].isna().sum() == 1
    assert not checks.check_no_nulls(df).passed
