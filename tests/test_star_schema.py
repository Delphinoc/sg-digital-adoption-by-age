"""Star schema (dim_* + fact_adoption) has the right grain, valid keys and
reconciles back to staging."""
import duckdb
import pytest

from src.pipeline import load_raw, run_models


@pytest.fixture(scope="module")
def con():
    c = duckdb.connect(":memory:")
    run_models(c, load_raw())
    yield c
    c.close()


def one(con, sql):
    return con.execute(sql).fetchone()[0]


@pytest.mark.parametrize(
    "table,key,expected_rows",
    [("dim_indicator", "indicator_key", 4),
     ("dim_segment", "segment_key", 7),
     ("dim_year", "year_key", 8)],
)
def test_dimension_keys_unique_and_complete(con, table, key, expected_rows):
    assert one(con, f"SELECT COUNT(*) FROM {table}") == expected_rows
    assert one(con, f"SELECT COUNT(DISTINCT {key}) FROM {table}") == expected_rows
    assert one(con, f"SELECT COUNT(*) FROM {table} WHERE {key} IS NULL") == 0


def test_fact_grain_one_row_per_indicator_segment_year(con):
    dupes = one(con, """
        SELECT COUNT(*) FROM (
            SELECT indicator_key, segment_key, year_key FROM fact_adoption
            GROUP BY ALL HAVING COUNT(*) > 1)""")
    assert dupes == 0


def test_fact_has_no_orphan_keys(con):
    """Every foreign key in the fact table must exist in its dimension."""
    orphans = one(con, """
        SELECT COUNT(*) FROM fact_adoption f
        LEFT JOIN dim_indicator i USING (indicator_key)
        LEFT JOIN dim_segment   s USING (segment_key)
        LEFT JOIN dim_year      y USING (year_key)
        WHERE i.indicator_key IS NULL OR s.segment_key IS NULL OR y.year_key IS NULL""")
    assert orphans == 0


def test_fact_reconciles_to_staging(con):
    """No rows lost or values changed when moving from staging to the star schema."""
    assert one(con, "SELECT COUNT(*) FROM fact_adoption") == one(con, "SELECT COUNT(*) FROM stg_indicators")
    mismatched = one(con, """
        SELECT COUNT(*) FROM fact_adoption f
        JOIN dim_indicator i USING (indicator_key)
        JOIN dim_segment   s USING (segment_key)
        JOIN stg_indicators st
          ON st.indicator = i.indicator_code AND st.segment = s.segment_code AND st.year = f.year_key
        WHERE st.pct <> f.pct""")
    assert mismatched == 0


def test_star_query_matches_age_gap_mart(con):
    """Rebuilding the senior gap from the star schema gives the same answer as the mart."""
    diff = one(con, """
        WITH star AS (
            SELECT i.indicator_code AS indicator, f.year_key AS year,
                   MAX(CASE WHEN s.segment_code = 'age_18_39'   THEN f.pct END)
                 - MAX(CASE WHEN s.segment_code = 'age_60_plus' THEN f.pct END) AS gap
            FROM fact_adoption f
            JOIN dim_indicator i USING (indicator_key)
            JOIN dim_segment   s USING (segment_key)
            WHERE s.segment_type = 'age'
            GROUP BY ALL)
        SELECT COUNT(*) FROM star JOIN mart_age_gap m USING (indicator, year)
        WHERE ABS(star.gap - m.gap_pp) > 0.01""")
    assert diff == 0
