"""
utils/data_loader.py
─────────────────────────────────────────────
Centralised data-loading layer for the Red Sea Crisis Dashboard.
All DataFrames are cached with @st.cache_data so they are loaded
only once regardless of which page calls load_data().
"""

import os
import json
import warnings

import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")


@st.cache_data
def load_data():
    """Load, validate, and pre-process all source datasets.

    Returns
    -------
    df_conf : pd.DataFrame
        Conflict events data (ACLED).
    df_ship : pd.DataFrame
        Weekly ship crossings data (UNCTAD).
    geojson : dict | None
        Shipping-lane GeoJSON feature collection, or None if not found.
    """
    # ── Conflict data ─────────────────────────────────────────────────────
    conflict_candidates = [
        "conflict_data.xlsx",
        "Middle-east-conflict-data.xlsx",
        "middle-east-conflict-data.xlsx",
        "conflict.xlsx",
        "sources/Middle-east-conflict-data.xlsx",
        "sources/middle-east-conflict-data.xlsx",
        "sources/conflict_data.xlsx",
        "data/Middle-east-conflict-data.xlsx",
        "data/middle-east-conflict-data.xlsx",
        "data/conflict_data.xlsx",
    ]
    df_conf = None
    for fname in conflict_candidates:
        if os.path.exists(fname):
            df_conf = pd.read_excel(fname)
            break

    if df_conf is None:
        st.error(
            "❌ File konflik tidak ditemukan. Pastikan salah satu dari file berikut "
            "ada di folder yang sama dengan main.py atau di folder `data/` / `sources/`:\n"
            "- `Middle-east-conflict-data.xlsx`\n- `conflict_data.xlsx`"
        )
        st.stop()

    df_conf["WEEK"] = pd.to_datetime(df_conf["WEEK"], errors="coerce")
    df_conf = df_conf.dropna(subset=["WEEK"])
    df_conf["YEAR"] = df_conf["WEEK"].dt.year
    df_conf["MONTH"] = df_conf["WEEK"].dt.to_period("M").astype(str)
    df_conf["CRISIS_PHASE"] = df_conf["WEEK"].apply(
        lambda x: "Post-Crisis (Nov 2023+)" if x >= pd.Timestamp("2023-11-01") else "Pre-Crisis"
    )

    # ── Ship crossings ────────────────────────────────────────────────────
    ship_candidates = [
        "ship_crossings.csv",
        "upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv",
        "weeklyshipcrossings.csv",
        "ship_data.csv",
        "sources/upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv",
        "sources/ship_crossings.csv",
        "data/upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv",
        "data/ship_crossings.csv",
    ]
    df_ship = None
    for fname in ship_candidates:
        if os.path.exists(fname):
            df_ship = pd.read_csv(fname)
            break

    if df_ship is None:
        st.error(
            "❌ File ship crossings tidak ditemukan. Pastikan salah satu dari file berikut "
            "ada di folder yang sama dengan main.py atau di folder `data/` / `sources/`:\n"
            "- `upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv`\n"
            "- `ship_crossings.csv`"
        )
        st.stop()

    # Detect date column (may be named differently across dataset versions)
    date_col = next(
        (c for c in df_ship.columns if "week" in c.lower() or "date" in c.lower()),
        df_ship.columns[0],
    )
    df_ship["date"] = pd.to_datetime(df_ship[date_col], dayfirst=True, errors="coerce")
    df_ship = df_ship.dropna(subset=["date"])

    # Detect crossing-count column
    cross_col = next(
        (c for c in df_ship.columns if any(k in c.lower() for k in ("crossing", "number", "count"))),
        None,
    )
    if cross_col is None:
        numeric_cols = df_ship.select_dtypes(include="number").columns.tolist()
        cross_col = numeric_cols[0] if numeric_cols else df_ship.columns[1]

    if cross_col != "Number of crossings":
        df_ship = df_ship.rename(columns={cross_col: "Number of crossings"})

    df_ship["month"] = df_ship["date"].dt.to_period("M").astype(str)
    df_ship["quarter"] = df_ship["date"].dt.to_period("Q").astype(str)
    df_ship["year"] = df_ship["date"].dt.year
    df_ship["CRISIS_PHASE"] = df_ship["date"].apply(
        lambda x: "Post-Crisis" if x >= pd.Timestamp("2023-11-01") else "Pre-Crisis"
    )

    # ── GeoJSON (shipping lanes, optional) ────────────────────────────────
    geojson = None
    geo_candidates = [
        "shipping_lanes.geojson",
        "Shipping_Lanes_v1.geojson",
        "shipping_lanes_v1.geojson",
        "shipping.geojson",
        "sources/shipping_lanes/Shipping_Lanes_v1.geojson",
        "sources/Shipping_Lanes_v1.geojson",
        "data/shipping_lanes/Shipping_Lanes_v1.geojson",
        "data/Shipping_Lanes_v1.geojson",
    ]
    for fname in geo_candidates:
        if os.path.exists(fname):
            with open(fname) as f:
                geojson = json.load(f)
            break

    return df_conf, df_ship, geojson


def passage_mean(df_ship: pd.DataFrame, passage: str, phase: str) -> float:
    """Return the mean weekly crossings for a passage in a given phase.

    Parameters
    ----------
    df_ship : pd.DataFrame  Full (unfiltered) ship-crossings DataFrame.
    passage : str           Passage name, e.g. ``"Suez"``.
    phase   : str           ``"pre"`` or ``"post"``.

    Returns
    -------
    float  Mean crossings, or 0 if data is unavailable.
    """
    CRISIS_DATE = pd.Timestamp("2023-11-01")
    if "Passage" not in df_ship.columns:
        return 0.0
    mask = df_ship["Passage"] == passage
    if phase == "pre":
        mask &= df_ship["date"] < CRISIS_DATE
    else:
        mask &= df_ship["date"] >= CRISIS_DATE
    val = df_ship.loc[mask, "Number of crossings"].mean()
    return float(val) if not pd.isna(val) else 0.0
