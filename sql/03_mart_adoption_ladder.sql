-- Mart: the "adoption ladder" for each age band and year.
-- Step 1 own a smartphone -> step 2 use the internet -> step 3 buy online.
-- drop_from_prev_pp shows where each age group falls off the ladder.
CREATE OR REPLACE TABLE mart_adoption_ladder AS
SELECT
    segment,
    segment_label,
    year,
    ladder_step,
    indicator,
    pct,
    ROUND(
        pct - LAG(pct) OVER (PARTITION BY segment, year ORDER BY ladder_step),
        2
    ) AS drop_from_prev_pp
FROM stg_indicators
WHERE segment_type = 'age'
ORDER BY segment, year, ladder_step;
