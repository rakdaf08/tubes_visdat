import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Red Sea Crisis Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background-color: #060b14;
        color: #d0dced;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #080e1a;
        border-right: 1px solid #152035;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {
        color: #6a8aa8;
        font-size: 12px;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(145deg, #0b1628 0%, #0d1e38 100%);
        border: 1px solid #162840;
        border-top: 2px solid #1e4a8a;
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, #3a7eff55, transparent);
    }
    .kpi-label {
        font-family: 'Syne', sans-serif;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #4a7aaa;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-family: 'Syne', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
        letter-spacing: -0.5px;
    }
    .kpi-delta {
        font-size: 11px;
        margin-top: 6px;
        font-weight: 500;
    }
    .kpi-delta.negative { color: #ff5e5e; }
    .kpi-delta.positive { color: #3ecf6e; }
    .kpi-delta.neutral  { color: #5a8aaa; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, rgba(13,26,50,0.9), transparent);
        border-left: 3px solid #3a7eff;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin: 28px 0 16px 0;
    }
    .section-header h2 {
        margin: 0;
        font-family: 'Syne', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #c0d4ee;
        letter-spacing: 0.3px;
    }
    .section-header p {
        margin: 4px 0 0 0;
        font-size: 11px;
        color: #3a6080;
    }

    /* Streamlit selectbox / multiselect / slider labels */
    .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label {
        color: #5a8aaa !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #060b14;
        border-bottom: 1px solid #152035;
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #080e1a;
        color: #3a6080;
        border-radius: 6px 6px 0 0;
        border: 1px solid #152035;
        border-bottom: none;
        font-family: 'Syne', sans-serif;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0b1628 !important;
        color: #3a9eff !important;
        border-color: #1e3a6a !important;
    }

    hr { border-color: #152035; }

    .caption-text {
        font-size: 10px;
        color: #2a4a6a;
        text-align: center;
        margin-top: 4px;
        font-style: italic;
    }

    /* Hero title */
    .hero-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        color: #3a6080;
        letter-spacing: 0.3px;
    }

    /* insight box */
    .insight-box {
        background: #0b1628;
        border: 1px solid #152840;
        border-left: 3px solid #3a9eff;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 12px;
        color: #6a9ac8;
        line-height: 1.6;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0b1628",
    plot_bgcolor="#0b1628",
    font=dict(family="DM Sans", color="#b0c4de", size=12),
    title_font=dict(family="Syne", size=14, color="#d0dced"),
    legend=dict(
        bgcolor="#080e1a",
        bordercolor="#152035",
        borderwidth=1,
        font=dict(size=11),
    ),
    margin=dict(l=10, r=10, t=44, b=10),
    colorway=["#3a9eff", "#ff5e5e", "#3ecf6e", "#ffa640", "#c063e8", "#5ccfff"],
)

CRISIS_LINE = dict(
    type="line",
    x0="2023-11-01", x1="2023-11-01",
    y0=0, y1=1, yref="paper",
    line=dict(color="#ff5e5e", width=1.5, dash="dot"),
)

# ─────────────────────────────────────────────
# DATA LOADING — flexible filename detection
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    # ── Conflict data ─────────────────────────
    conflict_candidates = [
        "conflict_data.xlsx",
        "Middle-east-conflict-data.xlsx",
        "middle-east-conflict-data.xlsx",
        "conflict.xlsx",
        "sources/Middle-east-conflict-data.xlsx",
        "sources/middle-east-conflict-data.xlsx",
        "sources/conflict_data.xlsx",
    ]
    df_conf = None
    for fname in conflict_candidates:
        if os.path.exists(fname):
            df_conf = pd.read_excel(fname)
            break
    if df_conf is None:
        st.error("❌ File konflik tidak ditemukan. Pastikan salah satu dari file berikut ada di folder yang sama dengan app.py atau di folder `sources/`:\n- `Middle-east-conflict-data.xlsx`\n- `conflict_data.xlsx`")
        st.stop()

    df_conf["WEEK"] = pd.to_datetime(df_conf["WEEK"], errors="coerce")
    df_conf = df_conf.dropna(subset=["WEEK"])
    df_conf["YEAR"] = df_conf["WEEK"].dt.year
    df_conf["MONTH"] = df_conf["WEEK"].dt.to_period("M").astype(str)
    df_conf["CRISIS_PHASE"] = df_conf["WEEK"].apply(
        lambda x: "Post-Crisis (Nov 2023+)" if x >= pd.Timestamp("2023-11-01") else "Pre-Crisis"
    )

    # ── Ship crossings ────────────────────────
    ship_candidates = [
        "ship_crossings.csv",
        "upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv",
        "weeklyshipcrossings.csv",
        "ship_data.csv",
        "sources/upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv",
        "sources/ship_crossings.csv",
    ]
    df_ship = None
    for fname in ship_candidates:
        if os.path.exists(fname):
            df_ship = pd.read_csv(fname)
            break
    if df_ship is None:
        st.error("❌ File ship crossings tidak ditemukan. Pastikan salah satu dari file berikut ada di folder yang sama dengan app.py atau di folder `sources/`:\n- `upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv`\n- `ship_crossings.csv`")
        st.stop()

    # Detect date column (might be named differently)
    date_col = None
    for c in df_ship.columns:
        if "week" in c.lower() or "date" in c.lower():
            date_col = c
            break
    if date_col is None:
        date_col = df_ship.columns[0]

    df_ship["date"] = pd.to_datetime(df_ship[date_col], dayfirst=True, errors="coerce")
    df_ship = df_ship.dropna(subset=["date"])

    # Detect crossing count column
    cross_col = None
    for c in df_ship.columns:
        if "crossing" in c.lower() or "number" in c.lower() or "count" in c.lower():
            cross_col = c
            break
    if cross_col is None:
        # Fallback: pick first numeric column that isn't date
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

    # ── GeoJSON ───────────────────────────────
    geojson = None
    geo_candidates = [
        "shipping_lanes.geojson",
        "Shipping_Lanes_v1.geojson",
        "shipping_lanes_v1.geojson",
        "shipping.geojson",
        "sources/shipping_lanes/Shipping_Lanes_v1.geojson",
        "sources/Shipping_Lanes_v1.geojson",
    ]
    for fname in geo_candidates:
        if os.path.exists(fname):
            with open(fname) as f:
                geojson = json.load(f)
            break

    return df_conf, df_ship, geojson

df_conf, df_ship, geojson = load_data()

CRISIS_DATE = pd.Timestamp("2023-11-01")
COUNTRIES = sorted(df_conf["COUNTRY"].unique().tolist())
EVENT_TYPES = sorted(df_conf["EVENT_TYPE"].unique().tolist())
PASSAGES = sorted(df_ship["Passage"].unique().tolist()) if "Passage" in df_ship.columns else []

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 12px 0 8px 0;'>
        <div style='font-family: Syne, sans-serif; font-size: 18px; font-weight: 800; color: #ffffff;'>🌊 Red Sea Crisis</div>
        <div style='font-size: 11px; color: #3a6080; margin-top: 4px;'>Analytical Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🎛️ Global Filters")

    year_min = int(df_conf["YEAR"].min())
    year_max = int(df_conf["YEAR"].max())
    year_range = st.slider(
        "Year Range",
        min_value=year_min,
        max_value=year_max,
        value=(2020, year_max),
        step=1,
    )

    st.markdown("### 🌍 Conflict Filters")

    default_countries = [c for c in ["Yemen", "Israel", "Palestine", "Lebanon"] if c in COUNTRIES]
    selected_countries = st.multiselect(
        "Countries",
        options=COUNTRIES,
        default=default_countries if default_countries else COUNTRIES[:4],
    )
    selected_events = st.multiselect(
        "Event Types",
        options=EVENT_TYPES,
        default=EVENT_TYPES,
    )

    st.markdown("### 🛳️ Maritime Filters")
    default_passages = [p for p in ["Bab-Al Mandab Strait", "Suez", "Cape of Good Hope"] if p in PASSAGES]
    selected_passages = st.multiselect(
        "Passages",
        options=PASSAGES,
        default=default_passages if default_passages else PASSAGES[:3],
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px; color:#2a4a6a; line-height:1.8;'>
    📅 Conflict data: 2015–2026<br>
    🚢 Ship data: Jan 2022–Apr 2024<br>
    🔴 Crisis onset: Nov 2023<br><br>
    <strong style='color:#3a6080;'>Sources:</strong><br>
    ACLED · UNCTAD Maritime Data
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
active_countries = selected_countries if selected_countries else COUNTRIES
active_events = selected_events if selected_events else EVENT_TYPES
active_passages = selected_passages if selected_passages else PASSAGES

conf_filtered = df_conf[
    (df_conf["YEAR"] >= year_range[0]) &
    (df_conf["YEAR"] <= year_range[1]) &
    (df_conf["COUNTRY"].isin(active_countries)) &
    (df_conf["EVENT_TYPE"].isin(active_events))
]

ship_filtered = df_ship[df_ship["Passage"].isin(active_passages)] if PASSAGES else df_ship

yemen_all = df_conf[df_conf["COUNTRY"] == "Yemen"]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 36px 0 28px 0;'>
    <div style='font-size:10px; letter-spacing:4px; color:#3a7eff; font-weight:700;
                font-family: Syne, sans-serif; text-transform:uppercase; margin-bottom:12px;'>
        Analytical Dashboard
    </div>
    <h1 style='font-family: Syne, sans-serif; font-size:42px; font-weight:800;
               color:#ffffff; margin:0; line-height:1; letter-spacing:-1px;'>
        🌊 Red Sea Crisis
    </h1>
    <p style='font-size:15px; color:#3a6080; margin-top:12px; font-weight:400;
              font-family: DM Sans, sans-serif; max-width:580px; margin-left:auto; margin-right:auto;'>
        Houthi Conflict &amp; Its Impact on Global Maritime Trade
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
total_events = int(conf_filtered["EVENTS"].sum())
total_fatalities = int(conf_filtered["FATALITIES"].sum())

suez_pre  = df_ship[(df_ship["Passage"] == "Suez") & (df_ship["date"] < CRISIS_DATE)]["Number of crossings"].mean() if "Suez" in df_ship.get("Passage", pd.Series()).values else 0
suez_post = df_ship[(df_ship["Passage"] == "Suez") & (df_ship["date"] >= CRISIS_DATE)]["Number of crossings"].mean() if "Suez" in df_ship.get("Passage", pd.Series()).values else 0

# Safer passage lookup
def passage_mean(passage, phase):
    if "Passage" not in df_ship.columns:
        return 0
    mask = (df_ship["Passage"] == passage)
    if phase == "pre":
        mask &= (df_ship["date"] < CRISIS_DATE)
    else:
        mask &= (df_ship["date"] >= CRISIS_DATE)
    val = df_ship.loc[mask, "Number of crossings"].mean()
    return val if not pd.isna(val) else 0

suez_pre_v  = passage_mean("Suez", "pre")
suez_post_v = passage_mean("Suez", "post")
suez_change = ((suez_post_v - suez_pre_v) / suez_pre_v * 100) if suez_pre_v else 0

cape_pre_v  = passage_mean("Cape of Good Hope", "pre")
cape_post_v = passage_mean("Cape of Good Hope", "post")
cape_change = ((cape_post_v - cape_pre_v) / cape_pre_v * 100) if cape_pre_v else 0

bab_pre_v  = passage_mean("Bab-Al Mandab Strait", "pre")
bab_post_v = passage_mean("Bab-Al Mandab Strait", "post")
bab_change = ((bab_post_v - bab_pre_v) / bab_pre_v * 100) if bab_pre_v else 0

yemen_post_events = int(df_conf[(df_conf["COUNTRY"] == "Yemen") & (df_conf["WEEK"] >= CRISIS_DATE)]["EVENTS"].sum())

k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, delta_text, delta_type):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-delta {delta_type}'>{delta_text}</div>
    </div>
    """, unsafe_allow_html=True)

kpi(k1, "Conflict Events", f"{total_events:,}", f"{year_range[0]}–{year_range[1]} filtered", "neutral")
kpi(k2, "Total Fatalities", f"{total_fatalities:,}", "Filtered selection", "negative")
kpi(k3, "Yemen Post-Crisis", f"{yemen_post_events:,}", "Events since Nov 2023", "negative")
kpi(k4, "Suez Traffic Change", f"{suez_change:+.1f}%", "Post vs Pre-Crisis avg/week", "negative" if suez_change < 0 else "positive")
kpi(k5, "Cape of Good Hope", f"{cape_change:+.1f}%", "Post vs Pre-Crisis avg/week", "positive" if cape_change > 0 else "negative")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🌍  Regional Conflict Overview",
    "🎯  Yemen & Houthi Deep-Dive",
    "🚢  Maritime Impact",
])

# ══════════════════════════════════════════════
# TAB 1 — REGIONAL CONFLICT
# ══════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class='section-header'>
        <h2>Regional Conflict Landscape</h2>
        <p>Middle East conflict intensity across countries — Yemen as epicentre of the Red Sea Crisis</p>
    </div>
    """, unsafe_allow_html=True)

    col_map, col_bar = st.columns([3, 2])

    # --- Interactive Map ---
    with col_map:
        # Group by country + centroid
        lat_col = next((c for c in df_conf.columns if "lat" in c.lower()), None)
        lon_col = next((c for c in df_conf.columns if "lon" in c.lower() or "lng" in c.lower()), None)

        if lat_col and lon_col:
            map_data = conf_filtered.groupby(["COUNTRY", lat_col, lon_col], as_index=False).agg(
                EVENTS=("EVENTS", "sum"),
                FATALITIES=("FATALITIES", "sum"),
            )
            map_data = map_data.rename(columns={lat_col: "LAT", lon_col: "LON"})
            map_data = map_data.dropna(subset=["LAT", "LON"])

            fig_map = px.scatter_mapbox(
                map_data,
                lat="LAT", lon="LON",
                size="EVENTS",
                color="FATALITIES",
                hover_name="COUNTRY",
                hover_data={"EVENTS": True, "FATALITIES": True, "LAT": False, "LON": False},
                color_continuous_scale="Reds",
                size_max=25,
                opacity=0.6,
                zoom=3.5,
                center={"lat": 24, "lon": 42},
                mapbox_style="carto-darkmatter",
                title="Conflict Intensity by Country",
            )

            # Add shipping lanes if available
            if geojson:
                for feat in geojson.get("features", []):
                    try:
                        geom = feat["geometry"]
                        coords_list = geom["coordinates"]
                        lane_type = feat.get("properties", {}).get("Type", "Minor")
                        color = "#3a9eff" if lane_type == "Major" else "#1a4a7a"
                        width = 2 if lane_type == "Major" else 1

                        # Handle both LineString and MultiLineString
                        if geom["type"] == "LineString":
                            coords_list = [coords_list]
                        elif geom["type"] == "MultiLineString":
                            pass  # already a list of lines

                        for line in coords_list:
                            lons = [c[0] for c in line]
                            lats = [c[1] for c in line]
                            fig_map.add_trace(go.Scattermapbox(
                                lon=lons, lat=lats,
                                mode="lines",
                                line=dict(color=color, width=width),
                                hoverinfo="skip",
                                showlegend=False,
                                opacity=0.6,
                            ))
                    except Exception:
                        continue

            fig_map.update_layout(
                **PLOTLY_LAYOUT,
                height=450,
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Fatalities",
                        font=dict(color="#6a9ac8")
                    ),
                    tickfont=dict(color="#6a9ac8", size=10),
                    bgcolor="#080e1a",
                    bordercolor="#152035",
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.markdown("<p class='caption-text'>Blue lines = major shipping lanes · Bubble size = events · Color = fatalities</p>", unsafe_allow_html=True)
        else:
            st.warning("Kolom koordinat tidak ditemukan di data konflik.")

    # --- Bar Chart: Events by Country ---
    with col_bar:
        bar_data = conf_filtered.groupby("COUNTRY", as_index=False).agg(
            EVENTS=("EVENTS", "sum"),
            FATALITIES=("FATALITIES", "sum"),
        ).sort_values("EVENTS", ascending=True)

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=bar_data["COUNTRY"],
            x=bar_data["EVENTS"],
            orientation="h",
            marker=dict(
                color=bar_data["EVENTS"],
                colorscale=[
                    [0, "#0d2040"],
                    [0.5, "#1a5a9e"],
                    [1, "#3a9eff"],
                ],
                line=dict(color="#0b1628", width=0.5),
            ),
            customdata=bar_data["FATALITIES"],
            hovertemplate="<b>%{y}</b><br>Events: %{x:,}<br>Fatalities: %{customdata:,}<extra></extra>",
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            title="Total Conflict Events by Country",
            height=450,
            xaxis=dict(gridcolor="#152035", title="Events"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Event Type Breakdown ---
    st.markdown("""
    <div class='section-header'>
        <h2>Conflict Composition</h2>
        <p>Distribution of conflict types across the filtered selection</p>
    </div>
    """, unsafe_allow_html=True)

    col_pie, col_line = st.columns([1, 2])

    with col_pie:
        pie_data = conf_filtered.groupby("EVENT_TYPE")["EVENTS"].sum().reset_index()
        fig_pie = px.pie(
            pie_data,
            names="EVENT_TYPE",
            values="EVENTS",
            title="Events by Type",
            hole=0.48,
            color_discrete_sequence=["#3a9eff", "#ff5e5e", "#3ecf6e", "#ffa640", "#c063e8", "#5ccfff"],
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            textfont_size=10,
            hovertemplate="<b>%{label}</b><br>Events: %{value:,}<br>Share: %{percent}<extra></extra>",
        )
        fig_pie.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_line:
        trend_data = conf_filtered.copy()
        trend_data["MONTH_DT"] = pd.to_datetime(trend_data["MONTH"], errors="coerce")
        monthly = trend_data.groupby(["MONTH_DT", "COUNTRY"])["EVENTS"].sum().reset_index()
        monthly = monthly.sort_values("MONTH_DT")

        fig_trend = px.line(
            monthly,
            x="MONTH_DT",
            y="EVENTS",
            color="COUNTRY",
            title="Monthly Conflict Events by Country",
            labels={"MONTH_DT": "Month", "EVENTS": "Events"},
        )
        fig_trend.add_shape(CRISIS_LINE)
        fig_trend.add_annotation(
            x="2023-11-01", y=1, yref="paper",
            text="Crisis Onset", showarrow=False,
            font=dict(color="#ff5e5e", size=10),
            xanchor="left", yanchor="top",
        )
        fig_trend.update_traces(line=dict(width=1.8))
        fig_trend.update_layout(
            **PLOTLY_LAYOUT,
            height=360,
            xaxis=dict(gridcolor="#152035"),
            yaxis=dict(gridcolor="#152035"),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — YEMEN DEEP DIVE
# ══════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class='section-header'>
        <h2>Yemen & Houthi Activity Deep-Dive</h2>
        <p>Granular analysis of conflict sub-types — drone strikes, missile attacks, armed clashes</p>
    </div>
    """, unsafe_allow_html=True)

    yemen_filtered = df_conf[
        (df_conf["COUNTRY"] == "Yemen") &
        (df_conf["YEAR"] >= year_range[0]) &
        (df_conf["YEAR"] <= year_range[1])
    ]

    col_a, col_b = st.columns(2)

    with col_a:
        sub_data = yemen_filtered.groupby("SUB_EVENT_TYPE")["EVENTS"].sum().reset_index()
        sub_data = sub_data.sort_values("EVENTS", ascending=False).head(10)
        fig_sub = px.pie(
            sub_data,
            names="SUB_EVENT_TYPE",
            values="EVENTS",
            title="Yemen: Attack Types Distribution (Top 10)",
            hole=0.42,
            color_discrete_sequence=[
                "#ff5e5e", "#ff8c42", "#ffc844", "#ffee70",
                "#3ecf6e", "#3a9eff", "#5ccfff", "#c063e8",
                "#ff7eb6", "#a8daff",
            ],
        )
        fig_sub.update_traces(
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Events: %{value:,}<br>%{percent}<extra></extra>",
        )
        fig_sub.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig_sub, use_container_width=True)

    with col_b:
        sub_bar = sub_data.sort_values("EVENTS", ascending=True)
        fig_sub_bar = go.Figure(go.Bar(
            y=sub_bar["SUB_EVENT_TYPE"],
            x=sub_bar["EVENTS"],
            orientation="h",
            marker=dict(
                color=sub_bar["EVENTS"],
                colorscale=[
                    [0, "#200808"],
                    [0.5, "#8a2020"],
                    [1, "#ff5e5e"],
                ],
                line=dict(color="#0b1628", width=0.5),
            ),
            hovertemplate="<b>%{y}</b><br>Events: %{x:,}<extra></extra>",
        ))
        fig_sub_bar.update_layout(
            **PLOTLY_LAYOUT,
            title="Yemen: Top 10 Attack Methods",
            height=400,
            xaxis=dict(gridcolor="#152035", title="Total Events"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            showlegend=False,
        )
        st.plotly_chart(fig_sub_bar, use_container_width=True)

    # --- Timeline: Yemen monthly events & fatalities ---
    st.markdown("""
    <div class='section-header'>
        <h2>Conflict Timeline</h2>
        <p>Monthly events and fatalities in Yemen — before and after the Red Sea Crisis onset</p>
    </div>
    """, unsafe_allow_html=True)

    yemen_monthly = yemen_filtered.copy()
    yemen_monthly["MONTH_DT"] = pd.to_datetime(yemen_monthly["MONTH"], errors="coerce")
    ym = yemen_monthly.groupby("MONTH_DT").agg(
        EVENTS=("EVENTS", "sum"),
        FATALITIES=("FATALITIES", "sum"),
    ).reset_index()

    fig_timeline = make_subplots(specs=[[{"secondary_y": True}]])
    fig_timeline.add_trace(
        go.Bar(x=ym["MONTH_DT"], y=ym["EVENTS"], name="Events",
               marker_color="#3a9eff", opacity=0.65,
               hovertemplate="<b>%{x|%b %Y}</b><br>Events: %{y:,}<extra></extra>"),
        secondary_y=False,
    )
    fig_timeline.add_trace(
        go.Scatter(x=ym["MONTH_DT"], y=ym["FATALITIES"], name="Fatalities",
                   line=dict(color="#ff5e5e", width=2.5),
                   hovertemplate="<b>%{x|%b %Y}</b><br>Fatalities: %{y:,}<extra></extra>"),
        secondary_y=True,
    )
    fig_timeline.add_shape(
        type="line", x0="2023-11-01", x1="2023-11-01",
        y0=0, y1=1, yref="paper",
        line=dict(color="#ff5e5e", width=1.5, dash="dot"),
    )
    fig_timeline.add_shape(
        type="rect",
        x0="2023-11-01", x1=str(ym["MONTH_DT"].max()),
        y0=0, y1=1, yref="paper",
        fillcolor="rgba(255,94,94,0.04)",
        line=dict(color="rgba(255,94,94,0.2)", width=1),
    )
    fig_timeline.add_annotation(
        x="2023-11-01", y=0.97, yref="paper",
        text="  🔴 Houthi Crisis Onset", showarrow=False,
        font=dict(color="#ff5e5e", size=11, family="Syne"),
        xanchor="left", bgcolor="#1a0808", borderpad=4,
    )
    fig_timeline.update_layout(
        **PLOTLY_LAYOUT,
        title="Yemen Monthly Conflict Events & Fatalities",
        height=380,
        xaxis=dict(gridcolor="#152035"),
        yaxis=dict(gridcolor="#152035", title="Events"),
        yaxis2=dict(title="Fatalities", gridcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    # --- Word Cloud ---
    st.markdown("""
    <div class='section-header'>
        <h2>Attack Type Word Cloud</h2>
        <p>Visual frequency map of conflict sub-event types and disorder categories in Yemen</p>
    </div>
    """, unsafe_allow_html=True)

    col_wc, col_wc_info = st.columns([3, 1])

    with col_wc:
        wc_freq = yemen_filtered.groupby("SUB_EVENT_TYPE")["EVENTS"].sum().to_dict()
        # Also include EVENT_TYPE with lower weight for variety
        wc_freq2 = yemen_filtered.groupby("EVENT_TYPE")["EVENTS"].sum().to_dict()
        wc_combined = {**wc_freq, **{k: v // 4 for k, v in wc_freq2.items()}}
        # Add DISORDER_TYPE if available
        if "DISORDER_TYPE" in yemen_filtered.columns:
            wc_freq3 = yemen_filtered.groupby("DISORDER_TYPE")["EVENTS"].sum().to_dict()
            wc_combined.update({k: v // 6 for k, v in wc_freq3.items()})

        # Remove empty/NaN keys
        wc_combined = {str(k): int(v) for k, v in wc_combined.items() if k and str(k).strip()}

        wc = WordCloud(
            width=900, height=380,
            background_color="#0b1628",
            colormap="YlOrRd",
            max_words=70,
            prefer_horizontal=0.65,
            relative_scaling=0.5,
            min_font_size=11,
            max_font_size=95,
        ).generate_from_frequencies(wc_combined)

        fig_wc, ax_wc = plt.subplots(figsize=(11, 4))
        ax_wc.imshow(wc, interpolation="bilinear")
        ax_wc.axis("off")
        fig_wc.patch.set_facecolor("#0b1628")
        plt.tight_layout(pad=0)
        st.pyplot(fig_wc, use_container_width=True)

    with col_wc_info:
        st.markdown("""
        <div style='padding:14px; background:#0b1628; border:1px solid #152840;
                    border-radius:8px; margin-top:8px;'>
        <div style='font-family:Syne,sans-serif; font-size:10px; color:#3a9eff;
                    font-weight:700; letter-spacing:1px; text-transform:uppercase;
                    margin-bottom:12px;'>Top Attack Types</div>
        """, unsafe_allow_html=True)

        top5 = sorted(wc_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        total_wc = sum(wc_freq.values()) or 1
        for i, (k, v) in enumerate(top5):
            pct = v / total_wc * 100
            st.markdown(f"""
            <div style='margin-bottom:12px;'>
                <div style='font-size:11px; color:#c0d4ee; font-weight:500;'>{k}</div>
                <div style='background:#152035; border-radius:3px; height:5px; margin-top:5px;'>
                    <div style='background:#ff5e5e; width:{min(pct,100):.0f}%; height:5px; border-radius:3px;'></div>
                </div>
                <div style='font-size:10px; color:#3a6080; margin-top:3px;'>{v:,} events ({pct:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — MARITIME IMPACT
# ══════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class='section-header'>
        <h2>Maritime Route Disruption</h2>
        <p>Suez Canal traffic decline vs Cape of Good Hope surge — direct economic impact of the Red Sea Crisis</p>
    </div>
    """, unsafe_allow_html=True)

    if PASSAGES:
        passages_to_plot = active_passages if active_passages else PASSAGES
        ship_plot = df_ship[df_ship["Passage"].isin(passages_to_plot)].copy()

        # ── Line Chart: all passages ──────────
        colors_passage = {
            "Suez": "#ff5e5e",
            "Bab-Al Mandab Strait": "#ffa640",
            "Cape of Good Hope": "#3ecf6e",
            "Hormuz": "#3a9eff",
            "Dover": "#c063e8",
            "Taiwan Strait": "#5ccfff",
        }

        fig_line = go.Figure()
        for passage in passages_to_plot:
            p_data = ship_plot[ship_plot["Passage"] == passage].sort_values("date")
            fig_line.add_trace(go.Scatter(
                x=p_data["date"],
                y=p_data["Number of crossings"],
                name=passage,
                mode="lines",
                line=dict(color=colors_passage.get(passage, "#3a9eff"), width=2),
                hovertemplate=f"<b>{passage}</b><br>Week: %{{x|%d %b %Y}}<br>Crossings: %{{y:,}}<extra></extra>",
            ))

        fig_line.add_shape(CRISIS_LINE)
        fig_line.add_annotation(
            x="2023-11-01", y=1, yref="paper",
            text="  🔴 Crisis Onset (Nov 2023)", showarrow=False,
            font=dict(color="#ff5e5e", size=11, family="Syne"),
            xanchor="left", bgcolor="#180404", borderpad=4,
        )
        fig_line.update_layout(
            **PLOTLY_LAYOUT,
            title="Weekly Ship Crossings — All Major Passages",
            height=420,
            xaxis=dict(gridcolor="#152035", title="Week"),
            yaxis=dict(gridcolor="#152035", title="Number of Crossings"),
            hovermode="x unified",
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # ── Insight box ──────────────────────
        if suez_change != 0 and cape_change != 0:
            st.markdown(f"""
            <div class='insight-box'>
            📊 <strong>Key Insight:</strong> Following the Houthi crisis onset in November 2023,
            weekly Suez Canal crossings changed by <strong style='color:#ff5e5e;'>{suez_change:+.1f}%</strong>
            on average, while Cape of Good Hope traffic shifted by
            <strong style='color:#3ecf6e;'>{cape_change:+.1f}%</strong> —
            confirming a major rerouting of global maritime trade.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Donut charts + Quarterly bar ──────
        red_sea_routes = ["Suez", "Bab-Al Mandab Strait", "Cape of Good Hope"]
        donut_routes = [r for r in red_sea_routes if r in passages_to_plot]

        col_donut1, col_donut2, col_qbar = st.columns([1, 1, 2])
        crisis_phases = ["Pre-Crisis", "Post-Crisis"]

        for idx, (phase, col) in enumerate(zip(crisis_phases, [col_donut1, col_donut2])):
            with col:
                donut_data = df_ship[
                    (df_ship["Passage"].isin(donut_routes)) &
                    (df_ship["CRISIS_PHASE"] == phase)
                ].groupby("Passage")["Number of crossings"].sum().reset_index()

                if not donut_data.empty:
                    fig_donut = px.pie(
                        donut_data,
                        names="Passage",
                        values="Number of crossings",
                        title=f"Traffic Share — {phase}",
                        hole=0.52,
                        color_discrete_map={
                            "Suez": "#ff5e5e",
                            "Bab-Al Mandab Strait": "#ffa640",
                            "Cape of Good Hope": "#3ecf6e",
                        },
                    )
                    fig_donut.update_traces(
                        textinfo="percent+label",
                        textfont_size=10,
                        hovertemplate="<b>%{label}</b><br>Total: %{value:,}<br>%{percent}<extra></extra>",
                    )
                    fig_donut.update_layout(
                        **{**PLOTLY_LAYOUT, "margin": dict(l=5, r=5, t=44, b=5)},
                        height=300,
                        showlegend=False,
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)

        with col_qbar:
            qbar_data = df_ship[df_ship["Passage"].isin(donut_routes)].groupby(
                ["quarter", "Passage"]
            )["Number of crossings"].sum().reset_index()
            qbar_data = qbar_data.sort_values("quarter")

            fig_qbar = px.bar(
                qbar_data,
                x="quarter",
                y="Number of crossings",
                color="Passage",
                title="Quarterly Ship Crossings by Route",
                barmode="group",
                color_discrete_map={
                    "Suez": "#ff5e5e",
                    "Bab-Al Mandab Strait": "#ffa640",
                    "Cape of Good Hope": "#3ecf6e",
                },
            )
            fig_qbar.update_layout(
                **{**PLOTLY_LAYOUT, "margin": dict(l=5, r=5, t=44, b=60)},
                height=300,
                xaxis=dict(gridcolor="#152035", title="Quarter", tickangle=-45),
                yaxis=dict(gridcolor="#152035", title="Crossings"),
            )
            st.plotly_chart(fig_qbar, use_container_width=True)

        # ── Correlation chart ─────────────────
        st.markdown("""
        <div class='section-header'>
            <h2>Conflict–Trade Correlation</h2>
            <p>Direct comparison of Yemen conflict intensity vs Suez Canal traffic disruption over time</p>
        </div>
        """, unsafe_allow_html=True)

        yemen_monthly2 = df_conf[df_conf["COUNTRY"] == "Yemen"].copy()
        yemen_monthly2["MONTH_DT"] = yemen_monthly2["WEEK"].dt.to_period("M").dt.to_timestamp()
        ym2 = yemen_monthly2.groupby("MONTH_DT")["EVENTS"].sum().reset_index()
        ym2.columns = ["month", "yemen_events"]

        suez_monthly = df_ship[df_ship["Passage"] == "Suez"].copy() if "Suez" in df_ship.get("Passage", pd.Series()).values else pd.DataFrame()

        if not suez_monthly.empty:
            suez_monthly["month"] = pd.to_datetime(suez_monthly["month"], errors="coerce")
            sm = suez_monthly.groupby("month")["Number of crossings"].mean().reset_index()
            sm.columns = ["month", "suez_crossings"]
            merged = pd.merge(ym2, sm, on="month", how="inner").sort_values("month")

            fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
            fig_corr.add_trace(
                go.Bar(x=merged["month"], y=merged["yemen_events"], name="Yemen Events",
                       marker_color="#ff5e5e", opacity=0.55,
                       hovertemplate="<b>%{x|%b %Y}</b><br>Yemen Events: %{y:,}<extra></extra>"),
                secondary_y=False,
            )
            fig_corr.add_trace(
                go.Scatter(x=merged["month"], y=merged["suez_crossings"], name="Suez Crossings",
                           line=dict(color="#3a9eff", width=2.5),
                           hovertemplate="<b>%{x|%b %Y}</b><br>Suez Avg Crossings: %{y:.0f}<extra></extra>"),
                secondary_y=True,
            )
            fig_corr.add_shape(
                type="rect",
                x0="2023-11-01", x1=str(merged["month"].max()),
                y0=0, y1=1, yref="paper",
                fillcolor="rgba(255,94,94,0.05)",
                line=dict(color="rgba(255,94,94,0.25)", width=1),
            )
            fig_corr.add_annotation(
                x="2023-11-01", y=0.95, yref="paper",
                text=" Crisis Zone", showarrow=False,
                font=dict(color="#ff5e5e", size=10),
                xanchor="left",
            )
            fig_corr.update_layout(
                **PLOTLY_LAYOUT,
                title="Yemen Conflict Events vs Suez Canal Weekly Crossings",
                height=400,
                xaxis=dict(gridcolor="#152035"),
                yaxis=dict(gridcolor="#152035", title="Yemen Events"),
                yaxis2=dict(title="Suez Avg Crossings/Week", gridcolor="rgba(0,0,0,0)"),
                hovermode="x unified",
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Data Suez tidak tersedia untuk chart korelasi.")
    else:
        st.warning("Data passage tidak ditemukan di kolom 'Passage'. Cek nama kolom di file CSV.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; padding:20px 0; color:#1e3a5a; font-size:11px; line-height:2.2;'>
    <strong style='font-family:Syne,sans-serif; color:#3a7eff; font-size:13px; letter-spacing:0.5px;'>
        Red Sea Crisis: Houthi Conflict &amp; Maritime Trade Impact
    </strong><br>
    Data Sources: ACLED (Armed Conflict Location &amp; Event Data Project) · UNCTAD Maritime Trade Data<br>
    Dashboard built with Streamlit · Plotly · WordCloud · Python
</div>
""", unsafe_allow_html=True)
