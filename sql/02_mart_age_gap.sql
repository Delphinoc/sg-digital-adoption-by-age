-- Mart: the senior digital divide per indicator per year.
-- gap_pp = adoption among 18-39 minus adoption among 60+ (percentage points).
-- senior_parity = 60+ adoption as a share of 18-39 adoption (1.0 = no gap).
CREATE OR REPLACE TABLE mart_age_gap AS
WITH pivoted AS (
    SELECT
        indicator,
        year,
        MAX(CASE WHEN segment = 'age_18_39'   THEN pct END) AS pct_18_39,
        MAX(CASE WHEN segment = 'age_40_59'   THEN pct END) AS pct_40_59,
        MAX(CASE WHEN segment = 'age_60_plus' THEN pct END) AS pct_60_plus,
        MAX(CASE WHEN segment = 'all_18_plus' THEN pct END) AS pct_all_18_plus
    FROM stg_indicators
    WHERE segment_type = 'age'
    GROUP BY indicator, year
)
SELECT
    indicator,
    year,
    pct_18_39,
    pct_40_59,
    pct_60_plus,
    pct_all_18_plus,
    ROUND(pct_18_39 - pct_60_plus, 2)            AS gap_pp,
    ROUND(pct_60_plus / NULLIF(pct_18_39, 0), 3) AS senior_parity
FROM pivoted
ORDER BY indicator, year;
