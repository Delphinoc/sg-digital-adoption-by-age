"""SQL model outputs are complete and internally consistent."""
import duckdb
import pytest

from src.pipeline import load_raw, run_models


@pytest.fixture(scope="module")
def con():
    c = duckdb.connect(":memory:")
    run_models(c, load_raw())
    yield c
    c.close()


def q(con, sql):
    return con.execute(sql).fetchall()


def test_staging_row_count(con):
    # 3 age indicators x 4 segments x 8 years + 1 household indicator x 3 segments x 8 years
    assert q(con, "SELECT COUNT(*) FROM stg_indicators")[0][0] == 3 * 4 * 8 + 3 * 8


def test_every_segment_has_a_label(con):
    assert q(con, "SELECT COUNT(*) FROM stg_indicators WHERE segment_label IS NULL")[0][0] == 0


def test_age_gap_one_row_per_indicator_year(con):
    assert q(con, "SELECT COUNT(*) FROM mart_age_gap")[0][0] == 3 * 8


def test_gap_equals_young_minus_senior(con):
    bad = q(con, """SELECT COUNT(*) FROM mart_age_gap
                    WHERE ABS(gap_pp - (pct_18_39 - pct_60_plus)) > 0.01""")[0][0]
    assert bad == 0


def test_parity_between_zero_and_one(con):
    assert q(con, """SELECT COUNT(*) FROM mart_age_gap
                     WHERE senior_parity < 0 OR senior_parity > 1""")[0][0] == 0


def test_ladder_first_step_has_no_drop(con):
    assert q(con, """SELECT COUNT(*) FROM mart_adoption_ladder
                     WHERE ladder_step = 1 AND drop_from_prev_pp IS NOT NULL""")[0][0] == 0


def test_ladder_reconciles_to_staging(con):
    """Ladder values must match staging exactly (no rows lost or altered in the mart)."""
    diff = q(con, """
        SELECT COUNT(*) FROM mart_adoption_ladder l
        JOIN stg_indicators s USING (segment, year, indicator)
        WHERE l.pct <> s.pct""")[0][0]
    n_ladder = q(con, "SELECT COUNT(*) FROM mart_adoption_ladder")[0][0]
    n_stg_age = q(con, "SELECT COUNT(*) FROM stg_indicators WHERE segment_type = 'age'")[0][0]
    assert diff == 0 and n_ladder == n_stg_age


def test_gap_change_covers_each_indicator(con):
    assert q(con, "SELECT COUNT(*) FROM mart_gap_change")[0][0] == 3
