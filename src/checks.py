"""Data-quality rules for the long-format indicator table.

Errors stop the pipeline. Warnings are printed for a human to review
(for example, a big year-on-year swing that may reflect a survey change).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.config import DATASETS, EXPECTED_SEGMENTS, YEARS

YOY_SWING_PP = 10.0  # flag year-on-year moves larger than this for review


@dataclass
class CheckResult:
    rule: str
    severity: str  # "error" or "warning"
    passed: bool
    issues: list[str] = field(default_factory=list)


def check_known_segments(df: pd.DataFrame) -> CheckResult:
    bad = df.loc[df["segment"].isna(), ["indicator", "DataSeries"]].drop_duplicates()
    issues = [f"{r.indicator}: unknown series '{r.DataSeries}'" for r in bad.itertuples()]
    return CheckResult("Every series label maps to a known segment", "error", not issues, issues)


def check_expected_segments(df: pd.DataFrame) -> CheckResult:
    issues = []
    for indicator, meta in DATASETS.items():
        found = set(df.loc[df["indicator"] == indicator, "segment"].dropna())
        missing = EXPECTED_SEGMENTS[meta["segment_type"]] - found
        if missing:
            issues.append(f"{indicator}: missing segments {sorted(missing)}")
    return CheckResult("Each indicator has all expected segments", "error", not issues, issues)


def check_year_coverage(df: pd.DataFrame) -> CheckResult:
    issues = []
    for indicator in DATASETS:
        years = set(df.loc[df["indicator"] == indicator, "year"])
        missing = sorted(set(YEARS) - years)
        if missing:
            issues.append(f"{indicator}: missing years {missing}")
    return CheckResult(f"Full year coverage {YEARS[0]}-{YEARS[-1]}", "error", not issues, issues)


def check_no_nulls(df: pd.DataFrame) -> CheckResult:
    bad = df[df["pct"].isna()]
    issues = [f"{r.indicator} / {r.segment} / {r.year}: value missing" for r in bad.itertuples()]
    return CheckResult("No missing values", "error", not issues, issues)


def check_range(df: pd.DataFrame) -> CheckResult:
    bad = df[(df["pct"] < 0) | (df["pct"] > 100)]
    issues = [f"{r.indicator} / {r.segment} / {r.year}: {r.pct} outside 0-100" for r in bad.itertuples()]
    return CheckResult("Percentages within 0-100", "error", not issues, issues)


def check_unique_keys(df: pd.DataFrame) -> CheckResult:
    dup = df[df.duplicated(["indicator", "segment", "year"], keep=False)]
    keys = dup[["indicator", "segment", "year"]].drop_duplicates()
    issues = [f"{r.indicator} / {r.segment} / {r.year}: duplicate row" for r in keys.itertuples()]
    return CheckResult("One row per indicator x segment x year", "error", not issues, issues)


def check_overall_within_bands(df: pd.DataFrame) -> CheckResult:
    """The 18+ overall figure is a weighted average, so it must sit between the
    lowest and highest age-band values for the same indicator and year."""
    age = df[(df["segment_type"] == "age") & df["pct"].notna()]
    issues = []
    for (indicator, year), g in age.groupby(["indicator", "year"]):
        overall = g.loc[g["segment"] == "all_18_plus", "pct"]
        bands = g.loc[g["segment"].isin(["age_18_39", "age_40_59", "age_60_plus"]), "pct"]
        if overall.empty or bands.empty:
            continue
        o = overall.iloc[0]
        if not (bands.min() - 0.01 <= o <= bands.max() + 0.01):
            issues.append(f"{indicator} / {year}: overall {o} outside band range "
                          f"{bands.min()}-{bands.max()}")
    return CheckResult("Overall 18+ value lies within age-band range", "error", not issues, issues)


def check_ladder_order(df: pd.DataFrame) -> CheckResult:
    """Buying online needs internet use, so online purchase should not exceed
    internet usage for the same group and year. Warning only: the two questions
    use different reference periods, so small breaches are possible."""
    age = df[df["segment_type"] == "age"].pivot_table(
        index=["segment", "year"], columns="indicator", values="pct")
    issues = []
    if {"online_purchase", "internet_usage"} <= set(age.columns):
        bad = age[age["online_purchase"] > age["internet_usage"]]
        issues = [f"{seg} / {yr}: online purchase {row.online_purchase} > internet usage "
                  f"{row.internet_usage}" for (seg, yr), row in bad.iterrows()]
    return CheckResult("Online purchase <= internet usage", "warning", not issues, issues)


def check_yoy_swings(df: pd.DataFrame, threshold: float = YOY_SWING_PP) -> CheckResult:
    issues = []
    for (indicator, segment), g in df.dropna(subset=["pct"]).groupby(["indicator", "segment"]):
        g = g.sort_values("year")
        diff = g["pct"].diff()
        for year, d in zip(g["year"], diff):
            if pd.notna(d) and abs(d) > threshold:
                issues.append(f"{indicator} / {segment} / {year}: {d:+.2f}pp vs previous year")
    return CheckResult(f"Year-on-year swings under {threshold:.0f}pp", "warning", not issues, issues)


RULES = [
    check_known_segments,
    check_expected_segments,
    check_year_coverage,
    check_no_nulls,
    check_range,
    check_unique_keys,
    check_overall_within_bands,
    check_ladder_order,
    check_yoy_swings,
]


def run_all(df: pd.DataFrame) -> list[CheckResult]:
    return [rule(df) for rule in RULES]


def format_report(results: list[CheckResult]) -> str:
    lines = ["Data-quality report", "-" * 60]
    for r in results:
        status = "PASS" if r.passed else ("FAIL" if r.severity == "error" else "REVIEW")
        lines.append(f"[{status}] {r.rule}")
        lines.extend(f"    - {i}" for i in r.issues)
    return "\n".join(lines)
