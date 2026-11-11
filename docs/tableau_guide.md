# Tableau Public dashboard: build guide

Goal: one dashboard, "Singapore's Senior Digital Divide", that a non-technical reader understands in under a minute.

## 1. Connect the data
1. Run `python -m src.pipeline` so `data/processed/` is up to date.
2. In Tableau Public: **Connect → Text file** → `stg_indicators.csv`.
3. Add `mart_age_gap.csv` and `mart_adoption_ladder.csv` as separate data sources (don't join them; each sheet uses one source).
4. Set `year` to a **discrete dimension** for bar charts and **continuous** for line charts.

## 2. Build four sheets

**KPI tiles** (source: `mart_age_gap`, filter `year = 2024`)
- Three big numbers: senior internet use (77%), senior online purchase (30%), and the internet-use gap closed since 2017 (from `mart_gap_change`: 37pp).

**Adoption ladder** (source: `mart_adoption_ladder`)
- Columns: `indicator` (sort by `ladder_step`); Rows: `pct`; Colour: `segment_label`.
- Filter out `All 18+`. Add a **year** filter shown as a single-value slider, default 2024.
- Label bars with `pct` (rounded).

**Trend by age** (source: `stg_indicators`, `segment_type = age`)
- Columns: `year` (continuous); Rows: `pct`; Colour: `segment_label`.
- Add an `indicator` filter shown as a single-value dropdown.
- Turn on line-end labels instead of relying on colour alone.

**Gap over time** (source: `mart_age_gap`)
- Columns: `year`; Rows: `gap_pp`; Colour: `indicator`.
- Title: "Gap between 18–39 and 60+ (percentage points)".

## 3. Colours (keep consistent across sheets)
| Group | Hex |
|---|---|
| 18–39 | `#2a78d6` |
| 40–59 | `#eb6834` |
| 60+ | `#1baf7a` |

## 4. Assemble the dashboard
- Size: **Automatic** or 1200 × 800.
- Top: title + one-line takeaway ("Seniors are online, but most still don't transact online").
- Row 1: KPI tiles. Row 2: adoption ladder (left), trend by age (right). Row 3: gap over time.
- Use the year filter as a dashboard action so it drives the ladder.
- Footer: "Source: IMDA Annual Survey on Infocomm Usage, via data.gov.sg (Open Data Licence)".

## 5. Publish
- **File → Save to Tableau Public**. Copy the link into the README under "Dashboard".
