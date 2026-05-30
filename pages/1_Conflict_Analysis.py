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
    PLOTLY_CONFIG,
    CRISIS_LINE,
    filter_summary,
    chart_note,
)
from utils.data_loader import load_data

# ── Styles ────────────────────────────────────────────────────────────────
init_ui()

# ── Data ──────────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()

COUNTRIES = sorted(df_conf["COUNTRY"].unique().tolist())
EVENT_TYPES = sorted(df_conf["EVENT_TYPE"].unique().tolist())
YEAR_MIN = int(df_conf["YEAR"].min())
YEAR_MAX = int(df_conf["YEAR"].max())
DEFAULT_YEAR_RANGE = (max(2020, YEAR_MIN), YEAR_MAX)
DEFAULT_COUNTRIES = [
    c for c in ["Yemen", "Israel", "Palestine", "Lebanon"] if c in COUNTRIES
]
if not DEFAULT_COUNTRIES:
    DEFAULT_COUNTRIES = COUNTRIES[:4]


def reset_conflict_filters():
    st.session_state.conflict_year_range = DEFAULT_YEAR_RANGE
    st.session_state.conflict_countries = DEFAULT_COUNTRIES
    st.session_state.conflict_events = EVENT_TYPES

# ── Sidebar — brand + footer ──────────────
with st.sidebar:
    sidebar_brand()
    st.page_link("main.py", label="Overview", icon="🌊")
    st.page_link("pages/1_Conflict_Analysis.py", label="Conflict Analysis", icon="🌍")
    st.page_link("pages/2_Maritime_Impact.py", label="Maritime Impact", icon="🚢")
    sidebar_footer()

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

# ── Page-local filters (includes year range + country + event type) ──────
filter_title, filter_reset = st.columns([4, 1])
with filter_title:
    st.markdown(
        "<div class='filter-bar-label'>🌍 Page Filters — Conflict Analysis</div>",
        unsafe_allow_html=True,
    )
with filter_reset:
    st.button("Reset Filters", on_click=reset_conflict_filters, key="reset_conflict")

# Year range — full width
year_range = st.slider(
    "Year Range",
    min_value=YEAR_MIN,
    max_value=YEAR_MAX,
    value=DEFAULT_YEAR_RANGE,
    step=1,
    key="conflict_year_range",
)

# Countries + Event types
fc1, fc2 = st.columns(2)

with fc1:
    selected_countries = st.multiselect(
        "Countries",
        options=COUNTRIES,
        default=DEFAULT_COUNTRIES,
        key="conflict_countries",
    )

with fc2:
    selected_events = st.multiselect(
        "Event Types",
        options=EVENT_TYPES,
        default=EVENT_TYPES,
        key="conflict_events",
    )

filter_summary(
    [
        ("Years", f"{year_range[0]} - {year_range[1]}"),
        ("Countries", f"{len(selected_countries) or len(COUNTRIES)} selected"),
        ("Event types", f"{len(selected_events) or len(EVENT_TYPES)} selected"),
    ]
)

# ── Apply filters ─────────────────────────────────────────────────────────
active_countries = selected_countries if selected_countries else COUNTRIES
active_events = selected_events if selected_events else EVENT_TYPES

conf_filtered = df_conf[
    (df_conf["YEAR"] >= year_range[0])
    & (df_conf["YEAR"] <= year_range[1])
    & (df_conf["COUNTRY"].isin(active_countries))
    & (df_conf["EVENT_TYPE"].isin(active_events))
]

if conf_filtered.empty:
    st.warning("No conflict records match the active filters. Try widening the year, country, or event-type selection.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# MACRO VIEW — Regional Conflict Landscape
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Regional Conflict Landscape",
    "Middle East conflict intensity across countries — Yemen as epicentre of the Red Sea Crisis",
)
chart_note(
    "Use the map for spatial context, then read the bar chart for exact country ranking. Bubble size shows event volume; color intensity shows fatalities."
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

        fig_map = px.scatter_map(
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
            map_style="carto-darkmatter",
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
                            go.Scattermap(
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
        # fig_map.update_layout(margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig_map, width="stretch", config=PLOTLY_CONFIG)
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
    st.plotly_chart(fig_bar, width="stretch", config=PLOTLY_CONFIG)

# ── Conflict Composition ──────────────────────────────────────────────────
section_header(
    "Conflict Composition",
    "Distribution of conflict types across the filtered selection",
)
chart_note(
    "Bars are used here instead of a pie chart so users can compare event categories precisely, especially when values are close."
)

col_type, col_line = st.columns([1, 2])

with col_type:
    type_data = (
        conf_filtered.groupby("EVENT_TYPE", as_index=False)["EVENTS"]
        .sum()
        .sort_values("EVENTS", ascending=True)
    )
    fig_type = go.Figure(
        go.Bar(
            y=type_data["EVENT_TYPE"],
            x=type_data["EVENTS"],
            orientation="h",
            marker=dict(
                color=type_data["EVENTS"],
                colorscale=[[0, "#10213a"], [0.55, "#1f6fb8"], [1, "#3a9eff"]],
                line=dict(color="#0b1628", width=0.5),
            ),
            text=type_data["EVENTS"],
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Events: %{x:,}<extra></extra>",
        )
    )
    fig_type.update_layout(
        **{**PLOTLY_LAYOUT, "margin": dict(l=10, r=72, t=44, b=10)},
        title="Events by Type",
        height=360,
        xaxis=dict(
            gridcolor="#152035",
            title="Events",
            range=[0, max(type_data["EVENTS"]) * 1.18],
        ),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", title=""),
        showlegend=False,
    )
    st.plotly_chart(fig_type, width="stretch", config=PLOTLY_CONFIG)

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
    st.plotly_chart(fig_trend, width="stretch", config=PLOTLY_CONFIG)


# ══════════════════════════════════════════════════════════════════════════
# MICRO VIEW — Yemen & Houthi Deep-Dive
# ══════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)

section_header(
    "🎯 Zooming In: Yemen & Houthi Deep-Dive",
    "Granular analysis of conflict sub-types — drone strikes, missile attacks, armed clashes",
    variant="deep-dive",
)
chart_note(
    "This section intentionally stays focused on Yemen and only follows the selected year range, so the deep-dive remains comparable across filter changes."
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
        pareto_data = sub_data.copy()
        pareto_data["SHARE"] = pareto_data["EVENTS"] / pareto_data["EVENTS"].sum() * 100
        pareto_data["CUM_SHARE"] = pareto_data["SHARE"].cumsum()
        fig_sub = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sub.add_trace(
            go.Bar(
                x=pareto_data["SUB_EVENT_TYPE"],
                y=pareto_data["EVENTS"],
                name="Events",
                marker_color="#ff5e5e",
                opacity=0.72,
                hovertemplate="<b>%{x}</b><br>Events: %{y:,}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_sub.add_trace(
            go.Scatter(
                x=pareto_data["SUB_EVENT_TYPE"],
                y=pareto_data["CUM_SHARE"],
                name="Cumulative share",
                mode="lines+markers",
                line=dict(color="#3ecf6e", width=2),
                marker=dict(size=6),
                hovertemplate="<b>%{x}</b><br>Cumulative share: %{y:.1f}%<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_sub.update_layout(
            **{
                **PLOTLY_LAYOUT,
                "legend": dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="#080e1a",
                    bordercolor="#152035",
                    borderwidth=1,
                    font=dict(size=11),
                ),
            },
            title="Yemen: Top Attack Types and Cumulative Share",
            height=400,
            xaxis=dict(gridcolor="#152035", tickangle=-35, title=""),
            yaxis=dict(gridcolor="#152035", title="Events"),
            yaxis2=dict(title="Cumulative Share", range=[0, 105], ticksuffix="%"),
        )
        st.plotly_chart(fig_sub, width="stretch", config=PLOTLY_CONFIG)

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
        st.plotly_chart(fig_sub_bar, width="stretch", config=PLOTLY_CONFIG)

    # ── Timeline ──────────────────────────────────────────────────────────
    section_header(
        "Conflict Timeline",
        "Monthly events and fatalities in Yemen — before and after the Red Sea Crisis onset",
    )
    chart_note(
        "The shaded region marks the post-crisis period. Hover along the timeline to compare events and fatalities for the same month."
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
    st.plotly_chart(fig_timeline, width="stretch", config=PLOTLY_CONFIG)

    # ── Word Cloud ────────────────────────────────────────────────────────
    section_header(
        "Attack Type Word Cloud",
        "Visual frequency map of conflict sub-event types and disorder categories in Yemen",
    )
    chart_note(
        "Use the word cloud as a quick texture view, then rely on the ranked list for exact top attack types."
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
            st.pyplot(fig_wc, width="stretch")
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
