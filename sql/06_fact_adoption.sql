-- Star schema, part 2: the fact table.
-- Grain: one row per indicator x segment x year.
-- Measures: pct (adoption rate) and yoy_change_pp (change from the previous year).
CREATE OR REPLACE TABLE fact_adoption AS
SELECT
    i.indicator_key,
    s.segment_key,
    y.year_key,
    st.pct,
    ROUND(
        st.pct - LAG(st.pct) OVER (PARTITION BY st.indicator, st.segment ORDER BY st.year),
        2
    ) AS yoy_change_pp
FROM stg_indicators st
JOIN dim_indicator i ON i.indicator_code = st.indicator
JOIN dim_segment   s ON s.segment_code   = st.segment
JOIN dim_year      y ON y.year           = st.year
ORDER BY i.indicator_key, s.segment_key, y.year_key;
