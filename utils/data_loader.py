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

    # Filter out peaceful protests to keep focus on armed conflict and maritime disruption
    df_conf = df_conf[~df_conf["SUB_EVENT_TYPE"].isin(["Peaceful protest", "Protest with intervention"])]

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


@st.cache_data
def load_trade_data():
    """Load UK containerised trade flow data through global maritime passages.

    Returns
    -------
    df_monthly : pd.DataFrame
        Monthly TEU volumes by passage and direction (imports + exports combined).
    df_hs2 : pd.DataFrame
        Annual HS2 product volumes by passage for Suez (imports only, top categories).
    """
    trade_candidates = [
        "data/uktradeflowsofcontainerisedproductsthroughglobalmaritimepassages20202024.xlsx",
        "uktradeflowsofcontainerisedproductsthroughglobalmaritimepassages20202024.xlsx",
    ]
    xl = None
    for fname in trade_candidates:
        if os.path.exists(fname):
            xl = pd.read_excel(fname, sheet_name=None)
            break

    if xl is None:
        return pd.DataFrame(), pd.DataFrame()

    # ── Monthly volumes ───────────────────────────────────────────────────
    df_imp = xl.get("1.Monthly Volumes All (Imports)", pd.DataFrame())
    df_exp = xl.get("2.Monthly Volumes All (Exports)", pd.DataFrame())
    df_monthly = pd.concat([df_imp, df_exp], ignore_index=True)
    if not df_monthly.empty:
        df_monthly["TEU"] = pd.to_numeric(df_monthly["TEU"], errors="coerce")
        df_monthly = df_monthly.dropna(subset=["TEU"])
        df_monthly["date"] = pd.to_datetime(
            df_monthly["Year"].astype(str) + "-" + df_monthly["Month"].astype(str) + "-01"
        )
        df_monthly["CRISIS_PHASE"] = df_monthly["date"].apply(
            lambda x: "Post-Crisis" if x >= pd.Timestamp("2023-11-01") else "Pre-Crisis"
        )

    # ── HS2 annual volumes (Imports, all passages) ─────────────────────────
    df_hs2_raw = xl.get("3.Top HS2 Volumes (Imports)", pd.DataFrame())
    df_hs2 = pd.DataFrame()
    if not df_hs2_raw.empty:
        # The sheet has 2 header rows — row index 2 is the real header
        df_hs2 = df_hs2_raw.iloc[2:].copy()
        df_hs2.columns = ["Product Category", "Passage", "2020", "2021", "2022", "2023", "2024"]
        df_hs2 = df_hs2.reset_index(drop=True)
        # Store full name for tooltips
        df_hs2["Full Product Category"] = df_hs2["Product Category"].apply(lambda x: str(x) if pd.notna(x) else x)
        # Clean product labels: keep only the part after the dash
        def shorten_label(label):
            if pd.isna(label):
                return label
            s = str(label)
            # Extract code number + short name (e.g. "84 - Nuclear reactors..." → "84 - Nuclear reactors")
            parts = s.split(" - ", 1)
            if len(parts) == 2:
                code = parts[0].strip()
                desc = parts[1].strip()
                # Shorten description to first ~40 chars
                desc = desc.split(";")[0].strip()
                if len(desc) > 42:
                    desc = desc[:42].rstrip() + "…"
                return f"{code} - {desc}"
            return s[:50]
        df_hs2["Product Category"] = df_hs2["Product Category"].apply(shorten_label)
        for col in ["2020", "2021", "2022", "2023", "2024"]:
            df_hs2[col] = pd.to_numeric(df_hs2[col], errors="coerce")
        df_hs2 = df_hs2.dropna(subset=["Passage"])

    return df_monthly, df_hs2


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
