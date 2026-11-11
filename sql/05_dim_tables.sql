-- Star schema, part 1: dimension tables.
-- Each dimension has a surrogate key and the descriptive fields that used to be
-- repeated on every staging row.

-- dim_indicator: one row per survey indicator.
CREATE OR REPLACE TABLE dim_indicator AS
SELECT
    ROW_NUMBER() OVER (ORDER BY ladder_step, indicator) AS indicator_key,
    indicator                                           AS indicator_code,
    CASE indicator
        WHEN 'smartphone_ownership'      THEN 'Owns a smartphone'
        WHEN 'internet_usage'            THEN 'Uses the internet'
        WHEN 'online_purchase'           THEN 'Made an online purchase'
        WHEN 'household_internet_access' THEN 'Household has internet access'
    END                                                 AS indicator_name,
    ladder_step,
    ladder_step > 0                                     AS is_on_ladder,
    MIN(segment_type)                                   AS population_unit
FROM stg_indicators
GROUP BY indicator, ladder_step;

-- dim_segment: one row per age band or household type.
CREATE OR REPLACE TABLE dim_segment AS
SELECT
    ROW_NUMBER() OVER (ORDER BY segment_type, segment) AS segment_key,
    segment                                            AS segment_code,
    segment_label,
    segment_type,
    segment IN ('age_60_plus', 'hh_seniors_only')      AS is_senior_segment,
    segment IN ('all_18_plus', 'hh_all')               AS is_overall_segment
FROM (SELECT DISTINCT segment, segment_label, segment_type FROM stg_indicators);

-- dim_year: one row per survey year, flagging the first and latest year.
CREATE OR REPLACE TABLE dim_year AS
WITH yrs AS (SELECT DISTINCT year FROM stg_indicators)
SELECT
    year                                   AS year_key,
    year,
    year = (SELECT MIN(year) FROM yrs)     AS is_first_year,
    year = (SELECT MAX(year) FROM yrs)     AS is_latest_year,
    year >= 2020                           AS is_post_2020
FROM yrs;
