-- Mart: how much each gap closed between the first and latest survey year.
CREATE OR REPLACE TABLE mart_gap_change AS
WITH bounds AS (
    SELECT MIN(year) AS first_year, MAX(year) AS latest_year FROM mart_age_gap
)
SELECT
    g.indicator,
    b.first_year,
    b.latest_year,
    MAX(CASE WHEN g.year = b.first_year  THEN g.pct_60_plus END) AS senior_pct_first,
    MAX(CASE WHEN g.year = b.latest_year THEN g.pct_60_plus END) AS senior_pct_latest,
    MAX(CASE WHEN g.year = b.first_year  THEN g.gap_pp END)      AS gap_pp_first,
    MAX(CASE WHEN g.year = b.latest_year THEN g.gap_pp END)      AS gap_pp_latest,
    ROUND(
        MAX(CASE WHEN g.year = b.first_year  THEN g.gap_pp END)
      - MAX(CASE WHEN g.year = b.latest_year THEN g.gap_pp END), 2
    ) AS gap_closed_pp
FROM mart_age_gap g
CROSS JOIN bounds b
GROUP BY g.indicator, b.first_year, b.latest_year
ORDER BY gap_closed_pp DESC;
