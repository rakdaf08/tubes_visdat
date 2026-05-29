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
    page_icon="🚢",
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
from utils.data_loader import load_data, passage_mean

# ── Styles ────────────────────────────────────────────────────────────────
init_ui()

# ── Data ──────────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()

PASSAGES = (
    sorted(df_ship["Passage"].unique().tolist()) if "Passage" in df_ship.columns else []
)
CRISIS_DATE = pd.Timestamp("2023-11-01")

# ── Sidebar — brand + footer ──────────────
# with st.sidebar:
#     sidebar_brand()
#     sidebar_footer()

# ── Page header ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='padding: 28px 0 8px 0;'>
        <div style='font-size:10px; letter-spacing:4px; color:#3ecf6e; font-weight:700;
                    font-family: Plus Jakarta Sans, sans-serif; text-transform:uppercase; margin-bottom:10px;'>
            Trade & Shipping
        </div>
        <h1 style='font-family: Plus Jakarta Sans, sans-serif; font-size:32px; font-weight:800;
                   color:#ffffff; margin:0; line-height:1.1; letter-spacing:-0.5px;'>
            🚢 Maritime Impact
        </h1>
        <p style='font-size:13px; color:#3a6080; margin-top:8px;
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

# ── Page-local filter bar ─────────────────────────────────────────────────
st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
st.markdown(
    "<div class='filter-bar-label'>🛳️ Page Filters — Maritime Passages</div>",
    unsafe_allow_html=True,
)

default_passages = [
    p for p in ["Bab-Al Mandab Strait", "Suez", "Cape of Good Hope"] if p in PASSAGES
]
selected_passages = st.multiselect(
    "Select Passages to Display",
    options=PASSAGES,
    default=default_passages if default_passages else PASSAGES[:3],
    key="maritime_passages",
)

st.markdown("</div>", unsafe_allow_html=True)

# ── Resolve active passages ────────────────────────────────────────────────
active_passages = selected_passages if selected_passages else PASSAGES
ship_plot = df_ship[df_ship["Passage"].isin(active_passages)].copy()

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
    text="  🔴 Crisis Onset (Nov 2023)",
    showarrow=False,
    font=dict(color="#ff5e5e", size=11, family="Plus Jakarta Sans"),
    xanchor="left",
    bgcolor="#180404",
    borderpad=4,
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

# Insight box
if suez_change != 0 and cape_change != 0:
    st.markdown(
        f"""
        <div class='insight-box'>
        📊 <strong>Key Insight:</strong> Following the Houthi crisis onset in November 2023,
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

red_sea_routes = ["Suez", "Bab-Al Mandab Strait", "Cape of Good Hope"]
donut_routes = [r for r in red_sea_routes if r in active_passages]

col_donut1, col_donut2, col_qbar = st.columns([1, 1, 2])
crisis_phases = ["Pre-Crisis", "Post-Crisis"]

for phase, col in zip(crisis_phases, [col_donut1, col_donut2]):
    with col:
        donut_data = (
            df_ship[
                (df_ship["Passage"].isin(donut_routes))
                & (df_ship["CRISIS_PHASE"] == phase)
            ]
            .groupby("Passage")["Number of crossings"]
            .sum()
            .reset_index()
        )

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
        else:
            st.info(f"No data for {phase}.")

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
        height=300,
        xaxis=dict(gridcolor="#152035", title="Quarter", tickangle=-45),
        yaxis=dict(gridcolor="#152035", title="Crossings"),
    )
    st.plotly_chart(fig_qbar, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Conflict–Trade Correlation
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Conflict–Trade Correlation",
    "Direct comparison of Yemen conflict intensity vs Suez Canal traffic disruption over time",
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

    fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
    fig_corr.add_trace(
        go.Bar(
            x=merged["month"],
            y=merged["yemen_events"],
            name="Yemen Events",
            marker_color="#ff5e5e",
            opacity=0.55,
            hovertemplate="<b>%{x|%b %Y}</b><br>Yemen Events: %{y:,}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_corr.add_trace(
        go.Scatter(
            x=merged["month"],
            y=merged["suez_crossings"],
            name="Suez Crossings",
            line=dict(color="#3a9eff", width=2.5),
            hovertemplate="<b>%{x|%b %Y}</b><br>Suez Avg Crossings: %{y:.0f}<extra></extra>",
        ),
        secondary_y=True,
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

# ── Footer ────────────────────────────────────────────────────────────────
page_footer()
