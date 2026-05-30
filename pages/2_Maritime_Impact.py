"""
pages/2_Maritime_Impact.py
─────────────────────────────────────────────
Maritime Impact page — Ship crossing trends, route share analysis,
quarterly comparisons, and Conflict–Trade correlation.

Page-local filter: selected_passages multiselect at the top.
Global filter:     Year Range from sidebar (shared across all pages).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ── Page config — MUST be first Streamlit call ────────────────────────────
st.set_page_config(
    page_title="Maritime Impact · Red Sea Crisis",
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
    chart_title,
)
from utils.data_loader import load_data, passage_mean

# ── Styles ────────────────────────────────────────────────────────────────
init_ui()

# ── Data ──────────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()

PASSAGES = (
    sorted(df_ship["Passage"].unique().tolist()) if "Passage" in df_ship.columns else []
)
CRISIS_DATE = pd.Timestamp("2023-11-01")
DEFAULT_PASSAGES = [
    p for p in ["Bab-Al Mandab Strait", "Suez", "Cape of Good Hope"] if p in PASSAGES
]
if not DEFAULT_PASSAGES:
    DEFAULT_PASSAGES = PASSAGES[:3]


def reset_maritime_filters():
    st.session_state.maritime_passages = DEFAULT_PASSAGES


# ── Sidebar — brand + footer ──────────────
with st.sidebar:
    sidebar_brand()
    st.page_link("Overview.py", label="Overview")
    st.page_link("pages/1_Conflict_Analysis.py", label="Conflict Analysis")
    st.page_link("pages/2_Maritime_Impact.py", label="Maritime Impact")
    sidebar_footer()

# ── Page header ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; margin-bottom: 12px;'>
        <h1 style='font-family: Plus Jakarta Sans, sans-serif; font-size:32px; font-weight:800;
                   color:#ffffff; margin-bottom:0px; padding-bottom:0px; letter-spacing:-0.5px;'>
            Maritime Impact
        </h1>
        <p style='font-size:16px; color:#d9d9d9; margin-top:0px; padding-top:4px;
                  font-family: Plus Jakarta Sans, sans-serif;'>
            Suez Canal traffic decline, Cape of Good Hope surge &amp;
            Conflict–Trade correlation
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Bail early if no passage data ─────────────────────────────────────────
if not PASSAGES:
    st.warning(
        "Data passage tidak ditemukan di kolom 'Passage'. "
        "Periksa nama kolom di file CSV ship-crossings."
    )
    st.stop()

# Pre-compute KPIs used in insight box
suez_pre_v = passage_mean(df_ship, "Suez", "pre")
suez_post_v = passage_mean(df_ship, "Suez", "post")
suez_change = ((suez_post_v - suez_pre_v) / suez_pre_v * 100) if suez_pre_v else 0

cape_pre_v = passage_mean(df_ship, "Cape of Good Hope", "pre")
cape_post_v = passage_mean(df_ship, "Cape of Good Hope", "post")
cape_change = ((cape_post_v - cape_pre_v) / cape_pre_v * 100) if cape_pre_v else 0

# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Route Disruption (Line Chart)
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Maritime Route Disruption",
    "Suez Canal traffic decline vs Cape of Good Hope surge — "
    "direct economic impact of the Red Sea Crisis",
)

col_ms, col_btn = st.columns([8, 1], vertical_alignment="bottom")
with col_ms:
    selected_passages = st.multiselect(
        "Select Passages to Display",
        options=PASSAGES,
        default=DEFAULT_PASSAGES,
        key="maritime_passages",
    )
with col_btn:
    st.button(
        "Reset Filters",
        on_click=reset_maritime_filters,
        key="reset_maritime",
        width="stretch",
    )

# ── Resolve active passages ────────────────────────────────────────────────
active_passages = selected_passages if selected_passages else PASSAGES
ship_plot = df_ship[df_ship["Passage"].isin(active_passages)].copy()

chart_note(
    "Hover across the same week to compare routes. The red marker anchors the Houthi crisis onset so the pre/post shift is visible without changing pages."
)

COLORS_PASSAGE = {
    "Suez": "#ff5e5e",
    "Bab-Al Mandab Strait": "#ffa640",
    "Cape of Good Hope": "#3ecf6e",
    "Hormuz": "#3a9eff",
    "Dover": "#c063e8",
    "Taiwan Strait": "#5ccfff",
}

fig_line = go.Figure()
for passage in active_passages:
    p_data = ship_plot[ship_plot["Passage"] == passage].sort_values("date")
    fig_line.add_trace(
        go.Scatter(
            x=p_data["date"],
            y=p_data["Number of crossings"],
            name=passage,
            mode="lines",
            line=dict(color=COLORS_PASSAGE.get(passage, "#3a9eff"), width=2),
            hovertemplate=(
                f"<b>{passage}</b><br>Week: %{{x|%d %b %Y}}"
                "<br>Crossings: %{y:,}<extra></extra>"
            ),
        )
    )

fig_line.add_shape(CRISIS_LINE)
fig_line.add_annotation(
    x="2023-11-01",
    y=1,
    yref="paper",
    text="     Crisis Onset (Nov 2023)",
    showarrow=False,
    font=dict(color="#ff5e5e", size=11, family="Plus Jakarta Sans"),
    xanchor="left",
    bgcolor="#180404",
    borderpad=4,
)
fig_line.update_layout(
    **PLOTLY_LAYOUT,
    title=chart_title("Weekly Ship Crossings — All Major Passages"),
    height=420,
    xaxis=dict(gridcolor="#152035", title="Week"),
    yaxis=dict(gridcolor="#152035", title="Number of Crossings"),
    hovermode="x unified",
)
st.plotly_chart(fig_line, width="stretch", config=PLOTLY_CONFIG)

# Insight box
if suez_change != 0 and cape_change != 0:
    st.markdown(
        f"""
        <div class='insight-box'>
        <strong>Key Insight:</strong> Following the Houthi crisis onset in November 2023,
        weekly Suez Canal crossings changed by
        <strong style='color:#ff5e5e;'>{suez_change:+.1f}%</strong> on average,
        while Cape of Good Hope traffic shifted by
        <strong style='color:#3ecf6e;'>{cape_change:+.1f}%</strong> —
        confirming a major rerouting of global maritime trade.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Traffic Share Donuts + Quarterly Bar
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Traffic Share: Pre vs Post-Crisis",
    "Distribution of ship crossings between Red Sea routes before and after Nov 2023",
)
chart_note(
    "A 100% stacked comparison makes the route-share shift easier to read than separate donut charts."
)

red_sea_routes = ["Suez", "Bab-Al Mandab Strait", "Cape of Good Hope"]
donut_routes = [r for r in red_sea_routes if r in active_passages]

col_share, col_qbar = st.columns([1, 2])

with col_share:
    share_data = (
        df_ship[df_ship["Passage"].isin(donut_routes)]
        .groupby(["CRISIS_PHASE", "Passage"], as_index=False)["Number of crossings"]
        .sum()
    )
    if not share_data.empty:
        share_data["SHARE"] = share_data.groupby("CRISIS_PHASE")[
            "Number of crossings"
        ].transform(lambda s: s / s.sum() * 100)
        phase_order = ["Pre-Crisis", "Post-Crisis"]
        fig_share = px.bar(
            share_data,
            x="CRISIS_PHASE",
            y="SHARE",
            color="Passage",
            category_orders={"CRISIS_PHASE": phase_order},
            title="Route Share Shift",
            text=share_data["SHARE"].map(lambda v: f"{v:.0f}%"),
            color_discrete_map={
                "Suez": "#ff5e5e",
                "Bab-Al Mandab Strait": "#ffa640",
                "Cape of Good Hope": "#3ecf6e",
            },
        )
        fig_share.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Share: %{y:.1f}%<extra></extra>",
            textposition="inside",
        )
        fig_share.update_layout(
            **{
                **PLOTLY_LAYOUT,
                "margin": dict(l=5, r=5, t=44, b=58),
                "legend": dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.18,
                    xanchor="center",
                    x=0.5,
                    bgcolor="#080e1a",
                    bordercolor="#152035",
                    borderwidth=1,
                    font=dict(size=11),
                ),
            },
            title=chart_title("Route Share Shift"),
            height=320,
            barmode="stack",
            xaxis=dict(title=""),
            yaxis=dict(title="Share of Crossings", ticksuffix="%", range=[0, 100]),
        )
        st.plotly_chart(fig_share, width="stretch", config={**PLOTLY_CONFIG, "displayModeBar": False})
    else:
        st.info("No route-share data for the active passages.")

with col_qbar:
    qbar_data = (
        df_ship[df_ship["Passage"].isin(donut_routes)]
        .groupby(["quarter", "Passage"])["Number of crossings"]
        .sum()
        .reset_index()
        .sort_values("quarter")
    )
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
        title=chart_title("Quarterly Ship Crossings by Route"),
        height=300,
        xaxis=dict(gridcolor="#152035", title="Quarter", tickangle=-45),
        yaxis=dict(gridcolor="#152035", title="Crossings"),
    )
    st.plotly_chart(fig_qbar, width="stretch", config={**PLOTLY_CONFIG, "displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Conflict–Trade Correlation
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Conflict–Trade Correlation",
    "Direct comparison of Yemen conflict intensity vs Suez Canal traffic disruption over time",
)
chart_note(
    "Both series are indexed to the first overlapping month, avoiding the visual distortion that can happen with dual-axis charts."
)

yemen_monthly2 = df_conf[df_conf["COUNTRY"] == "Yemen"].copy()
yemen_monthly2["MONTH_DT"] = yemen_monthly2["WEEK"].dt.to_period("M").dt.to_timestamp()
ym2 = yemen_monthly2.groupby("MONTH_DT")["EVENTS"].sum().reset_index()
ym2.columns = ["month", "yemen_events"]

suez_monthly_df = (
    df_ship[df_ship["Passage"] == "Suez"].copy()
    if "Suez" in df_ship.get("Passage", pd.Series()).values
    else pd.DataFrame()
)

if not suez_monthly_df.empty:
    suez_monthly_df["month"] = pd.to_datetime(suez_monthly_df["month"], errors="coerce")
    sm = suez_monthly_df.groupby("month")["Number of crossings"].mean().reset_index()
    sm.columns = ["month", "suez_crossings"]
    merged = pd.merge(ym2, sm, on="month", how="inner").sort_values("month")

    def to_index(series):
        baseline = series[series > 0].iloc[0] if (series > 0).any() else 1
        return series / baseline * 100

    merged["Yemen conflict events"] = to_index(merged["yemen_events"])
    merged["Suez crossings"] = to_index(merged["suez_crossings"])
    corr_value = merged["yemen_events"].corr(merged["suez_crossings"])
    corr_label = "not enough overlap" if pd.isna(corr_value) else f"{corr_value:.2f}"

    corr_long = merged.melt(
        id_vars=["month", "yemen_events", "suez_crossings"],
        value_vars=["Yemen conflict events", "Suez crossings"],
        var_name="Metric",
        value_name="Index",
    )
    fig_corr = px.line(
        corr_long,
        x="month",
        y="Index",
        color="Metric",
        title="Yemen Conflict Events vs Suez Crossings (Indexed)",
        color_discrete_map={
            "Yemen conflict events": "#ff5e5e",
            "Suez crossings": "#3a9eff",
        },
        custom_data=["yemen_events", "suez_crossings"],
    )
    fig_corr.update_traces(
        line=dict(width=2.5),
        hovertemplate=(
            "<b>%{x|%b %Y}</b><br>%{fullData.name}: %{y:.1f}"
            "<br>Yemen Events: %{customdata[0]:,}"
            "<br>Suez Avg Crossings: %{customdata[1]:.0f}<extra></extra>"
        ),
    )
    if not merged.empty:
        fig_corr.add_shape(
            type="rect",
            x0="2023-11-01",
            x1=str(merged["month"].max()),
            y0=0,
            y1=1,
            yref="paper",
            fillcolor="rgba(255,94,94,0.05)",
            line=dict(color="rgba(255,94,94,0.25)", width=1),
        )
    fig_corr.add_annotation(
        x="2023-11-01",
        y=0.95,
        yref="paper",
        text=" Crisis Zone",
        showarrow=False,
        font=dict(color="#ff5e5e", size=10),
        xanchor="left",
    )
    fig_corr.update_layout(
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
        title=chart_title("Yemen Conflict Events vs Suez Crossings (Indexed)"),
        height=400,
        xaxis=dict(gridcolor="#152035", title="Month"),
        yaxis=dict(gridcolor="#152035", title="Index (first overlapping month = 100)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_corr, width="stretch", config=PLOTLY_CONFIG)
    st.markdown(
        f"""
        <div class='insight-box'>
        <strong>Correlation guide:</strong> The raw monthly correlation between Yemen events
        and Suez crossings is <strong style='color:#ffffff;'>{corr_label}</strong>. Treat this
        as directional context, not proof of causality, because routing decisions are also shaped
        by insurance, carrier policy, and global demand.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Data Suez tidak tersedia untuk chart korelasi.")

# ── Footer ────────────────────────────────────────────────────────────────
page_footer()
