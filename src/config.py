"""Dataset registry and project paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SQL_DIR = ROOT / "sql"
CHART_DIR = ROOT / "outputs" / "charts"
DB_PATH = ROOT / "data" / "digital_adoption.duckdb"

YEARS = list(range(2017, 2025))

# Each dataset is an IMDA annual survey series republished by SingStat on data.gov.sg.
# segment_type tells the pipeline whether rows are age bands (individuals) or household types.
DATASETS = {
    "internet_usage": {
        "file": "internet_usage_by_age.csv",
        "dataset_id": "d_3f4bfee2d42f8fb3bea3218c01aa9902",
        "title": "Individuals Internet Usage By Age Group, Annual",
        "singstat_table": "M920341",
        "segment_type": "age",
        "ladder_step": 2,
    },
    "smartphone_ownership": {
        "file": "smartphone_ownership_by_age.csv",
        "dataset_id": "d_65567444c3df02aceb795897bbd183c9",
        "title": "Individuals Smartphone Ownership By Age Group, Annual",
        "singstat_table": "M920321",
        "segment_type": "age",
        "ladder_step": 1,
    },
    "online_purchase": {
        "file": "online_purchase_by_age.csv",
        "dataset_id": "d_c98105aa8d0585e55e44cd3d2c3384dd",
        "title": "Individuals Who Made Online Purchase By Age Group, Annual",
        "singstat_table": "M920331",
        "segment_type": "age",
        "ladder_step": 3,
    },
    "household_internet_access": {
        "file": "household_internet_access.csv",
        "dataset_id": "d_66ad6d9200e5223a4773df8a615f0c5f",
        "title": "Household Access To Internet By Household Composition, Annual",
        "singstat_table": "M920301",
        "segment_type": "household",
        "ladder_step": 0,
    },
}

# Raw "Data Series" label -> tidy segment code
SEGMENT_MAP = {
    "Overall (Singapore Residents Aged 18 And Over)": "all_18_plus",
    "Singapore Residents Aged 18 - 39": "age_18_39",
    "Singapore Residents Aged 40 - 59": "age_40_59",
    "Singapore Residents Aged 60 And Over": "age_60_plus",
    "All Resident Households": "hh_all",
    "Households With Full-Time School-Going Children": "hh_school_children",
    "Households With Seniors Only": "hh_seniors_only",
}

EXPECTED_SEGMENTS = {
    "age": {"all_18_plus", "age_18_39", "age_40_59", "age_60_plus"},
    "household": {"hh_all", "hh_school_children", "hh_seniors_only"},
}
