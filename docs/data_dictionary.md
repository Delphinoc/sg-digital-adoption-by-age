# Data dictionary

All percentages are the share of Singapore residents (or resident households) in the segment, from IMDA's Annual Survey on Infocomm Usage.

## stg_indicators
One row per indicator × segment × year.

| Field | Type | Description |
|---|---|---|
| indicator | text | `smartphone_ownership`, `internet_usage`, `online_purchase` or `household_internet_access` |
| segment | text | Segment code, e.g. `age_60_plus`, `hh_seniors_only` |
| segment_type | text | `age` (individuals aged 18+) or `household` |
| ladder_step | int | 1 = own smartphone, 2 = use internet, 3 = bought online; 0 = household access (not on the ladder) |
| year | int | Survey year, 2017–2024 |
| pct | float | Percentage of the segment |
| segment_label | text | Readable label for dashboards, e.g. `60+` |

## mart_age_gap
One row per age-based indicator × year.

| Field | Type | Description |
|---|---|---|
| pct_18_39 / pct_40_59 / pct_60_plus | float | Adoption in each age band |
| pct_all_18_plus | float | Adoption across all residents aged 18+ |
| gap_pp | float | `pct_18_39 − pct_60_plus`, in percentage points |
| senior_parity | float | `pct_60_plus ÷ pct_18_39`; 1.0 means no gap |

## mart_adoption_ladder
One row per age segment × year × ladder step.

| Field | Type | Description |
|---|---|---|
| pct | float | Adoption at this step |
| drop_from_prev_pp | float | Change from the previous ladder step for the same group and year (blank for step 1) |

## mart_gap_change
One row per age-based indicator.

| Field | Type | Description |
|---|---|---|
| senior_pct_first / senior_pct_latest | float | 60+ adoption in the first and latest year |
| gap_pp_first / gap_pp_latest | float | Gap with 18–39 in the first and latest year |
| gap_closed_pp | float | How many points the gap narrowed (positive = narrowed) |

## Star schema

### fact_adoption
One row per indicator × segment × year.

| Field | Type | Description |
|---|---|---|
| indicator_key | int | Foreign key to `dim_indicator` |
| segment_key | int | Foreign key to `dim_segment` |
| year_key | int | Foreign key to `dim_year` (the survey year) |
| pct | float | Adoption rate for the segment |
| yoy_change_pp | float | Change from the previous survey year, in percentage points (blank for 2017) |

### dim_indicator
| Field | Type | Description |
|---|---|---|
| indicator_key | int | Surrogate key |
| indicator_code / indicator_name | text | Code and readable name |
| ladder_step | int | Position on the adoption ladder (0 = not on the ladder) |
| is_on_ladder | bool | True for the three individual indicators |
| population_unit | text | `age` (individuals) or `household` |

### dim_segment
| Field | Type | Description |
|---|---|---|
| segment_key | int | Surrogate key |
| segment_code / segment_label | text | Code and readable label |
| segment_type | text | `age` or `household` |
| is_senior_segment | bool | True for `60+` and seniors-only households |
| is_overall_segment | bool | True for the all-residents / all-households totals |

### dim_year
| Field | Type | Description |
|---|---|---|
| year_key / year | int | Survey year |
| is_first_year / is_latest_year | bool | Flags 2017 and 2024 (recomputed if a new year is added) |
| is_post_2020 | bool | True from 2020 onwards |
