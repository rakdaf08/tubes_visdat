"""
pages/1_Conflict_Analysis.py
─────────────────────────────────────────────
Conflict Analysis page — Regional Landscape + Yemen Deep-Dive.

Layout (top-to-bottom, no tabs):
  1. Page-local filter bar (Countries, Event Types)
  2. Macro view  — Regional Conflict Landscape (Map + Bar)
  3. Macro view  — Conflict Composition (Pie + Trend line)
  ── divider ──
  4. Micro view  — Yemen Attack Types (Pie + Bar)
  5. Micro view  — Yemen Conflict Timeline
  6. Micro view  — Attack Type Word Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# ── Page config — MUST be first Streamlit call ────────────────────────────
st.set_page_config(
    page_title="Conflict Analysis · Red Sea Crisis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui import (
    init_ui,
    sidebar_brand,
    sidebar_footer,
    section_header,
    page_footer,
    PLOTLY_LAYOUT,
    CRISIS_LINE,
)
from utils.data_loader import load_data

# ── Styles ────────────────────────────────────────────────────────────────
init_ui()

# ── Data ──────────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()

COUNTRIES = sorted(df_conf["COUNTRY"].unique().tolist())
EVENT_TYPES = sorted(df_conf["EVENT_TYPE"].unique().tolist())

# ── Sidebar — brand + footer ──────────────
# with st.sidebar:
#     sidebar_brand()
#     sidebar_footer()

# ── Page header ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='padding: 28px 0 8px 0;'>
        <div style='font-size:10px; letter-spacing:4px; color:#3a7eff; font-weight:700;
                    font-family: Plus Jakarta Sans, sans-serif; text-transform:uppercase; margin-bottom:10px;'>
            Deep Analysis
        </div>
        <h1 style='font-family: Plus Jakarta Sans, sans-serif; font-size:32px; font-weight:800;
                   color:#ffffff; margin:0; line-height:1.1; letter-spacing:-0.5px;'>
            🌍 Conflict Analysis
        </h1>
        <p style='font-size:13px; color:#3a6080; margin-top:8px;
                  font-family: Plus Jakarta Sans, sans-serif;'>
            Regional conflict landscape &amp; Yemen · Houthi deep-dive
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Page-local filter bar (ıncludes year range + country + event type) ──────
st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
st.markdown(
    "<div class='filter-bar-label'>🌍 Page Filters — Conflict Analysis</div>",
    unsafe_allow_html=True,
)

# Year range — full width
year_min = int(df_conf["YEAR"].min())
year_max = int(df_conf["YEAR"].max())
year_range = st.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(2020, year_max),
    step=1,
    key="conflict_year_range",
)

# Countries + Event types
fc1, fc2 = st.columns(2)

with fc1:
    default_countries = [
        c for c in ["Yemen", "Israel", "Palestine", "Lebanon"] if c in COUNTRIES
    ]
    selected_countries = st.multiselect(
        "Countries",
        options=COUNTRIES,
        default=default_countries if default_countries else COUNTRIES[:4],
        key="conflict_countries",
    )

with fc2:
    selected_events = st.multiselect(
        "Event Types",
        options=EVENT_TYPES,
        default=EVENT_TYPES,
        key="conflict_events",
    )

st.markdown("</div>", unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────
active_countries = selected_countries if selected_countries else COUNTRIES
active_events = selected_events if selected_events else EVENT_TYPES

conf_filtered = df_conf[
    (df_conf["YEAR"] >= year_range[0])
    & (df_conf["YEAR"] <= year_range[1])
    & (df_conf["COUNTRY"].isin(active_countries))
    & (df_conf["EVENT_TYPE"].isin(active_events))
]

# ══════════════════════════════════════════════════════════════════════════
# MACRO VIEW — Regional Conflict Landscape
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Regional Conflict Landscape",
    "Middle East conflict intensity across countries — Yemen as epicentre of the Red Sea Crisis",
)

col_map, col_bar = st.columns([3, 2])

# ── Interactive scatter-map ───────────────────────────────────────────────
with col_map:
    lat_col = next((c for c in df_conf.columns if "latitude" in c.lower()), None)
    lon_col = next(
        (c for c in df_conf.columns if "longitude" in c.lower()), None
    )

    if lat_col and lon_col:
        map_data = conf_filtered.groupby(
            ["COUNTRY", lat_col, lon_col], as_index=False
        ).agg(EVENTS=("EVENTS", "sum"), FATALITIES=("FATALITIES", "sum"))
        map_data = map_data.rename(columns={lat_col: "LAT", lon_col: "LON"})
        map_data = map_data.dropna(subset=["LAT", "LON"])

        fig_map = px.scatter_mapbox(
            map_data,
            lat="LAT",
            lon="LON",
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

        if geojson:
            for feat in geojson.get("features", []):
                try:
                    geom = feat["geometry"]
                    coords_raw = geom["coordinates"]
                    lane_type = feat.get("properties", {}).get("Type", "Minor")
                    color = "#3a9eff" if lane_type == "Major" else "#1a4a7a"
                    width = 2 if lane_type == "Major" else 1
                    lines = [coords_raw] if geom["type"] == "LineString" else coords_raw
                    for line in lines:
                        fig_map.add_trace(
                            go.Scattermapbox(
                                lon=[c[0] for c in line],
                                lat=[c[1] for c in line],
                                mode="lines",
                                line=dict(color=color, width=width),
                                hoverinfo="skip",
                                showlegend=False,
                                opacity=0.6,
                            )
                        )
                except Exception:
                    continue

        fig_map.update_layout(
            **PLOTLY_LAYOUT,
            height=450,
            coloraxis_colorbar=dict(
                title=dict(text="Fatalities", font=dict(color="#6a9ac8")),
                tickfont=dict(color="#6a9ac8", size=10),
                bgcolor="#080e1a",
                bordercolor="#152035",
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown(
            "<p class='caption-text'>Blue lines = major shipping lanes · "
            "Bubble size = events · Color = fatalities</p>",
            unsafe_allow_html=True,
        )
    else:
        st.warning("Kolom koordinat tidak ditemukan di data konflik.")

# ── Bar chart: events by country ──────────────────────────────────────────
with col_bar:
    bar_data = (
        conf_filtered.groupby("COUNTRY", as_index=False)
        .agg(EVENTS=("EVENTS", "sum"), FATALITIES=("FATALITIES", "sum"))
        .sort_values("EVENTS", ascending=True)
    )

    fig_bar = go.Figure(
        go.Bar(
            y=bar_data["COUNTRY"],
            x=bar_data["EVENTS"],
            orientation="h",
            marker=dict(
                color=bar_data["EVENTS"],
                colorscale=[[0, "#0d2040"], [0.5, "#1a5a9e"], [1, "#3a9eff"]],
                line=dict(color="#0b1628", width=0.5),
            ),
            customdata=bar_data["FATALITIES"],
            hovertemplate="<b>%{y}</b><br>Events: %{x:,}<br>Fatalities: %{customdata:,}<extra></extra>",
        )
    )
    fig_bar.update_layout(
        **PLOTLY_LAYOUT,
        title="Total Conflict Events by Country",
        height=450,
        xaxis=dict(gridcolor="#152035", title="Events"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Conflict Composition ──────────────────────────────────────────────────
section_header(
    "Conflict Composition",
    "Distribution of conflict types across the filtered selection",
)

col_pie, col_line = st.columns([1, 2])

with col_pie:
    pie_data = conf_filtered.groupby("EVENT_TYPE")["EVENTS"].sum().reset_index()
    fig_pie = px.pie(
        pie_data,
        names="EVENT_TYPE",
        values="EVENTS",
        title="Events by Type",
        hole=0.48,
        color_discrete_sequence=[
            "#3a9eff",
            "#ff5e5e",
            "#3ecf6e",
            "#ffa640",
            "#c063e8",
            "#5ccfff",
        ],
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
    monthly = (
        trend_data.groupby(["MONTH_DT", "COUNTRY"])["EVENTS"]
        .sum()
        .reset_index()
        .sort_values("MONTH_DT")
    )

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
        x="2023-11-01",
        y=1,
        yref="paper",
        text="Crisis Onset",
        showarrow=False,
        font=dict(color="#ff5e5e", size=10),
        xanchor="left",
        yanchor="top",
    )
    fig_trend.update_traces(line=dict(width=1.8))
    fig_trend.update_layout(
        **PLOTLY_LAYOUT,
        height=360,
        xaxis=dict(gridcolor="#152035"),
        yaxis=dict(gridcolor="#152035"),
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# MICRO VIEW — Yemen & Houthi Deep-Dive
# ══════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)

section_header(
    "🎯 Zooming In: Yemen & Houthi Deep-Dive",
    "Granular analysis of conflict sub-types — drone strikes, missile attacks, armed clashes",
    variant="deep-dive",
)

# Yemen-specific slice (uses year range only, not country/event filters,
# because this section is always about Yemen)
yemen_filtered = df_conf[
    (df_conf["COUNTRY"] == "Yemen")
    & (df_conf["YEAR"] >= year_range[0])
    & (df_conf["YEAR"] <= year_range[1])
]

if yemen_filtered.empty:
    st.warning("No Yemen data available for the selected year range.")
else:
    # ── Attack Types ──────────────────────────────────────────────────────
    sub_data = (
        yemen_filtered.groupby("SUB_EVENT_TYPE")["EVENTS"]
        .sum()
        .reset_index()
        .sort_values("EVENTS", ascending=False)
        .head(10)
    )

    col_a, col_b = st.columns(2)

    with col_a:
        fig_sub = px.pie(
            sub_data,
            names="SUB_EVENT_TYPE",
            values="EVENTS",
            title="Yemen: Attack Types Distribution (Top 10)",
            hole=0.42,
            color_discrete_sequence=[
                "#ff5e5e",
                "#ff8c42",
                "#ffc844",
                "#ffee70",
                "#3ecf6e",
                "#3a9eff",
                "#5ccfff",
                "#c063e8",
                "#ff7eb6",
                "#a8daff",
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
        fig_sub_bar = go.Figure(
            go.Bar(
                y=sub_bar["SUB_EVENT_TYPE"],
                x=sub_bar["EVENTS"],
                orientation="h",
                marker=dict(
                    color=sub_bar["EVENTS"],
                    colorscale=[[0, "#200808"], [0.5, "#8a2020"], [1, "#ff5e5e"]],
                    line=dict(color="#0b1628", width=0.5),
                ),
                hovertemplate="<b>%{y}</b><br>Events: %{x:,}<extra></extra>",
            )
        )
        fig_sub_bar.update_layout(
            **PLOTLY_LAYOUT,
            title="Yemen: Top 10 Attack Methods",
            height=400,
            xaxis=dict(gridcolor="#152035", title="Total Events"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            showlegend=False,
        )
        st.plotly_chart(fig_sub_bar, use_container_width=True)

    # ── Timeline ──────────────────────────────────────────────────────────
    section_header(
        "Conflict Timeline",
        "Monthly events and fatalities in Yemen — before and after the Red Sea Crisis onset",
    )

    yemen_monthly = yemen_filtered.copy()
    yemen_monthly["MONTH_DT"] = pd.to_datetime(yemen_monthly["MONTH"], errors="coerce")
    ym = (
        yemen_monthly.groupby("MONTH_DT")
        .agg(EVENTS=("EVENTS", "sum"), FATALITIES=("FATALITIES", "sum"))
        .reset_index()
    )

    fig_timeline = make_subplots(specs=[[{"secondary_y": True}]])
    fig_timeline.add_trace(
        go.Bar(
            x=ym["MONTH_DT"],
            y=ym["EVENTS"],
            name="Events",
            marker_color="#3a9eff",
            opacity=0.65,
            hovertemplate="<b>%{x|%b %Y}</b><br>Events: %{y:,}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_timeline.add_trace(
        go.Scatter(
            x=ym["MONTH_DT"],
            y=ym["FATALITIES"],
            name="Fatalities",
            line=dict(color="#ff5e5e", width=2.5),
            hovertemplate="<b>%{x|%b %Y}</b><br>Fatalities: %{y:,}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig_timeline.add_shape(
        type="line",
        x0="2023-11-01",
        x1="2023-11-01",
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#ff5e5e", width=1.5, dash="dot"),
    )
    if not ym.empty:
        fig_timeline.add_shape(
            type="rect",
            x0="2023-11-01",
            x1=str(ym["MONTH_DT"].max()),
            y0=0,
            y1=1,
            yref="paper",
            fillcolor="rgba(255,94,94,0.04)",
            line=dict(color="rgba(255,94,94,0.2)", width=1),
        )
    fig_timeline.add_annotation(
        x="2023-11-01",
        y=0.97,
        yref="paper",
        text="  🔴 Houthi Crisis Onset",
        showarrow=False,
        font=dict(color="#ff5e5e", size=11, family="Plus Jakarta Sans"),
        xanchor="left",
        bgcolor="#1a0808",
        borderpad=4,
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

    # ── Word Cloud ────────────────────────────────────────────────────────
    section_header(
        "Attack Type Word Cloud",
        "Visual frequency map of conflict sub-event types and disorder categories in Yemen",
    )

    col_wc, col_wc_info = st.columns([3, 1])

    wc_freq = yemen_filtered.groupby("SUB_EVENT_TYPE")["EVENTS"].sum().to_dict()
    wc_freq2 = yemen_filtered.groupby("EVENT_TYPE")["EVENTS"].sum().to_dict()
    wc_combined = {**wc_freq, **{k: v // 4 for k, v in wc_freq2.items()}}

    if "DISORDER_TYPE" in yemen_filtered.columns:
        wc_freq3 = yemen_filtered.groupby("DISORDER_TYPE")["EVENTS"].sum().to_dict()
        wc_combined.update({k: v // 6 for k, v in wc_freq3.items()})

    wc_combined = {
        str(k): int(v) for k, v in wc_combined.items() if k and str(k).strip()
    }

    with col_wc:
        if wc_combined:
            wc = WordCloud(
                width=900,
                height=380,
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
        else:
            st.info("No sub-event data available for the word cloud.")

    with col_wc_info:
        st.markdown(
            """
            <div style='padding:14px; background:#0b1628; border:1px solid #152840;
                        border-radius:8px; margin-top:8px;'>
            <div style='font-family:Plus Jakarta Sans,sans-serif; font-size:10px; color:#3a9eff;
                        font-weight:700; letter-spacing:1px; text-transform:uppercase;
                        margin-bottom:12px;'>Top Attack Types</div>
            """,
            unsafe_allow_html=True,
        )

        top5 = sorted(wc_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        total_wc = sum(wc_freq.values()) or 1
        for k, v in top5:
            pct = v / total_wc * 100
            st.markdown(
                f"""
                <div style='margin-bottom:12px;'>
                    <div style='font-size:11px; color:#c0d4ee; font-weight:500;'>{k}</div>
                    <div style='background:#152035; border-radius:3px; height:5px; margin-top:5px;'>
                        <div style='background:#ff5e5e; width:{min(pct, 100):.0f}%;
                                    height:5px; border-radius:3px;'></div>
                    </div>
                    <div style='font-size:10px; color:#3a6080; margin-top:3px;'>
                        {v:,} events ({pct:.1f}%)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────
page_footer()
