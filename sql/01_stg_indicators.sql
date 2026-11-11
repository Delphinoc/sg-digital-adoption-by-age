-- Staging: one tidy row per indicator x segment x year.
-- Source: raw_long (built in Python from the data.gov.sg wide CSVs).
CREATE OR REPLACE TABLE stg_indicators AS
SELECT
    indicator,
    segment,
    segment_type,
    ladder_step,
    CAST(year AS INTEGER)        AS year,
    CAST(pct AS DOUBLE)          AS pct,
    CASE segment
        WHEN 'age_18_39'   THEN '18-39'
        WHEN 'age_40_59'   THEN '40-59'
        WHEN 'age_60_plus' THEN '60+'
        WHEN 'all_18_plus' THEN 'All 18+'
        WHEN 'hh_all'             THEN 'All households'
        WHEN 'hh_school_children' THEN 'Households with school-going children'
        WHEN 'hh_seniors_only'    THEN 'Seniors-only households'
    END                          AS segment_label
FROM raw_long;
