"""
Centralized data loader for the GTD dataset.

Every page should call `load_data()` from here instead of reading the
CSV independently — this keeps caching, encoding, and column-cleanup
consistent across the whole app.
"""

import streamlit as st
import pandas as pd

DATA_PATH = "data/globalterrorism.csv"

REQUIRED_COLUMNS = [
    "iyear", "country_txt", "region_txt", "city",
    "latitude", "longitude",
    "attacktype1_txt", "weaptype1_txt", "targtype1_txt",
    "gname", "success", "suicide", "nkill", "nwound",
]


@st.cache_data(show_spinner="Loading Global Terrorism Database...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="latin1", low_memory=False)

    # Fill numeric NaNs that break sums/metrics across pages
    for col in ("nkill", "nwound"):
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Warn (once, in-app) rather than crash if the schema drifted
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.warning(
            f"Dataset is missing expected columns: {missing}. "
            "Some charts/pages may not render correctly."
        )

    return df


@st.cache_data
def apply_global_filters(
    df: pd.DataFrame,
    years=None,
    countries=None,
    regions=None,
) -> pd.DataFrame:
    """Shared filter logic so every page slices data the same way."""
    out = df
    if years:
        out = out[out["iyear"].isin(years)]
    if countries:
        out = out[out["country_txt"].isin(countries)]
    if regions:
        out = out[out["region_txt"].isin(regions)]
    return out
