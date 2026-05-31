"""
pages/3_Economic_Impact.py
─────────────────────────────────────────────
Economic Impact page — UK containerised trade flow analysis.

Layout:
  1. KPI row: total TEU imports/exports through Suez pre vs post crisis
  2. Section 1 — Monthly TEU Volume Trend (Suez vs Cape of Good Hope)
  3. Section 2 — Route Share Donut (all passages, all-time)
  4. Section 3 — Top Import Product Categories through Suez (HS2 annual bar)
  5. Section 4 — Year-over-Year TEU Change (Suez, indexed area chart)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# ── Page config — MUST be first Streamlit call ────────────────────────────
st.set_page_config(
    page_title="Economic Impact · Red Sea Crisis",
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
    chart_note,
    chart_title,
    kpi,
)
from utils.data_loader import load_data, load_trade_data

# ── Styles ────────────────────────────────────────────────────────────────
init_ui()

# ── Data ──────────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()
df_monthly, df_hs2 = load_trade_data()

CRISIS_DATE = pd.Timestamp("2023-11-01")

# ── Sidebar — brand + nav + footer ───────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    sidebar_footer()

# ── Page header ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; margin-bottom: 32px;'>
        <h1 style='font-family: Plus Jakarta Sans, sans-serif; font-size:32px; font-weight:800;
                   color:#ffffff; margin-bottom:0px; padding-bottom:0px; letter-spacing:-0.5px;'>
            Economic Impact
        </h1>
        <p style='font-size:16px; color:#d9d9d9; margin-top:0px; padding-top:4px;
                  font-family: Plus Jakarta Sans, sans-serif;'>
            UK containerised trade flows through global maritime passages &amp; the cost of rerouting
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Bail if no trade data ─────────────────────────────────────────────────
if df_monthly.empty:
    st.error(
        "❌ Trade flow data not found. Ensure the UK trade Excel file exists in the `data/` folder."
    )
    st.stop()

# ── KPI Computation ───────────────────────────────────────────────────────
COLORS_PASSAGE = {
    "Suez": "#ff5e5e",
    "Bab-Al Mandab Strait": "#ffa640",
    "Cape of Good Hope": "#3ecf6e",
    "Hormuz": "#3a9eff",
    "Dover": "#c063e8",
    "Taiwan Strait": "#5ccfff",
}

suez_monthly = df_monthly[df_monthly["Passage"] == "Suez"].copy()
cape_monthly = df_monthly[df_monthly["Passage"] == "Cape of Good Hope"].copy()

suez_pre_teu = suez_monthly[suez_monthly["date"] < CRISIS_DATE]["TEU"].sum()
suez_post_teu = suez_monthly[suez_monthly["date"] >= CRISIS_DATE]["TEU"].sum()
suez_teu_chg = (
    ((suez_post_teu - suez_pre_teu) / suez_pre_teu * 100) if suez_pre_teu else 0
)

cape_pre_teu = cape_monthly[cape_monthly["date"] < CRISIS_DATE]["TEU"].sum()
cape_post_teu = cape_monthly[cape_monthly["date"] >= CRISIS_DATE]["TEU"].sum()
cape_teu_chg = (
    ((cape_post_teu - cape_pre_teu) / cape_pre_teu * 100) if cape_pre_teu else 0
)

total_suez_teu = suez_monthly["TEU"].sum()
total_cape_teu = cape_monthly["TEU"].sum()

# ── KPI Cards ─────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
kpi(
    k1,
    "Suez Pre-Crisis TEU",
    f"{suez_pre_teu:,.0f}",
    "Total TEU (imports+exports)",
    "neutral",
)
kpi(
    k2,
    "Suez Post-Crisis TEU",
    f"{suez_post_teu:,.0f}",
    f"Change: {suez_teu_chg:+.1f}%",
    "negative" if suez_teu_chg < 0 else "positive",
)
kpi(
    k3,
    "Cape Pre-Crisis TEU",
    f"{cape_pre_teu:,.0f}",
    "Total TEU (imports+exports)",
    "neutral",
)
kpi(
    k4,
    "Cape Post-Crisis TEU",
    f"{cape_post_teu:,.0f}",
    f"Change: {cape_teu_chg:+.1f}%",
    "positive" if cape_teu_chg > 0 else "negative",
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Insight box ───────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class='insight-box'>
        <strong>Key Insight:</strong> Since the Houthi crisis onset in November 2023, UK containerised
        trade through the <strong style='color:#ff5e5e;'>Suez Canal</strong> changed by
        <strong style='color:#ff5e5e;'>{suez_teu_chg:+.1f}%</strong> in total TEU volume,
        while trade routed via the
        <strong style='color:#3ecf6e;'>Cape of Good Hope</strong> shifted by
        <strong style='color:#3ecf6e;'>{cape_teu_chg:+.1f}%</strong> —
        adding thousands of nautical miles and significant fuel costs to each voyage.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Monthly TEU Trend
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Monthly TEU Volume Trend",
    "UK containerised trade flows (imports + exports) through key passages — Suez decline vs Cape surge",
)
chart_note(
    "TEU = Twenty-foot Equivalent Unit, the standard measure of containerised cargo volume. "
    "The red dotted line marks the Houthi crisis onset in November 2023."
)

# Page-local passage filter for TEU trend
trend_passages = ["Suez", "Cape of Good Hope", "Hormuz", "Dover"]
available_trend = [p for p in trend_passages if p in df_monthly["Passage"].unique()]
ECO_YEAR_MIN = int(df_monthly["Year"].min())
ECO_YEAR_MAX = int(df_monthly["Year"].max())

with st.container(border=True):
    st.markdown(
        "<div class='filter-bar-label'>Chart Filters — Monthly TEU Trend</div>",
        unsafe_allow_html=True,
    )
    col_yr, col_ms, col_dir = st.columns([2, 3, 1])
    with col_yr:
        eco_year_range = st.slider(
            "Year Range",
            min_value=ECO_YEAR_MIN,
            max_value=ECO_YEAR_MAX,
            value=(ECO_YEAR_MIN, ECO_YEAR_MAX),
            step=1,
            key="eco_year_range",
        )
    with col_ms:
        sel_passages = st.multiselect(
            "Passages to Display",
            options=sorted(df_monthly["Passage"].unique().tolist()),
            default=available_trend,
            key="eco_passages",
        )
    with col_dir:
        sel_direction = st.selectbox(
            "Trade Direction",
            options=["Both", "import", "export"],
            index=0,
            key="eco_direction",
        )

active_passages_eco = sel_passages if sel_passages else available_trend
trend_df = df_monthly[
    (df_monthly["Passage"].isin(active_passages_eco))
    & (df_monthly["Year"] >= eco_year_range[0])
    & (df_monthly["Year"] <= eco_year_range[1])
].copy()
if sel_direction != "Both":
    trend_df = trend_df[trend_df["Direction"] == sel_direction]

trend_agg = (
    trend_df.groupby(["date", "Passage"])["TEU"].sum().reset_index().sort_values("date")
)

fig_teu = go.Figure()
for passage in active_passages_eco:
    p_data = trend_agg[trend_agg["Passage"] == passage]
    fig_teu.add_trace(
        go.Scatter(
            x=p_data["date"],
            y=p_data["TEU"],
            name=passage,
            mode="lines",
            line=dict(color=COLORS_PASSAGE.get(passage, "#3a9eff"), width=2.2),
            hovertemplate=(
                f"<b>{passage}</b><br>Month: %{{x|%b %Y}}"
                "<br>TEU: %{y:,.0f}<extra></extra>"
            ),
        )
    )

fig_teu.add_shape(CRISIS_LINE)
fig_teu.add_annotation(
    x="2023-11-01",
    y=1,
    yref="paper",
    text="  Crisis Onset (Nov 2023)",
    showarrow=False,
    font=dict(color="#ff5e5e", size=11, family="Plus Jakarta Sans"),
    xanchor="left",
    bgcolor="#180404",
    borderpad=4,
)
fig_teu.update_layout(
    **{
        **PLOTLY_LAYOUT,
        "legend": dict(
            orientation="h",
            yanchor="bottom",
            y=0.98,
            xanchor="right",
            x=1,
            bgcolor="#080e1a",
            bordercolor="#152035",
            borderwidth=1,
            font=dict(size=11),
        ),
    },
    title=chart_title("Monthly TEU Volume by Maritime Passage"),
    height=420,
    xaxis=dict(gridcolor="#152035", title="Month"),
    yaxis=dict(gridcolor="#152035", title="TEU (Twenty-foot Equivalent Units)"),
    hovermode="x unified",
)
st.plotly_chart(fig_teu, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Route Share Donut + YoY Change
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Trade Route Distribution & Year-over-Year Change",
    "Share of total UK containerised cargo by passage — and how each route's volume changed year-on-year",
)

col_notes_donut, col_notes_yoy = st.columns([1, 2])
with col_notes_donut:
    chart_note(
        "Donut shows total TEU share across all years. Hover each segment for volume."
    )
with col_notes_yoy:
    chart_note(
        "Year-over-year % change in total TEU per passage. Bars below zero indicate cargo volume decline."
    )

col_donut, col_yoy = st.columns([1, 2])

with col_donut:
    donut_agg = (
        df_monthly.groupby("Passage")["TEU"]
        .sum()
        .reset_index()
        .sort_values("TEU", ascending=False)
    )
    fig_donut = go.Figure(
        go.Pie(
            labels=donut_agg["Passage"],
            values=donut_agg["TEU"],
            hole=0.55,
            marker=dict(
                colors=[COLORS_PASSAGE.get(p, "#3a9eff") for p in donut_agg["Passage"]],
                line=dict(color="#080e1a", width=2),
            ),
            hovertemplate="<b>%{label}</b><br>TEU: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
            textfont=dict(family="Plus Jakarta Sans", size=11, color="#ffffff"),
            textposition="inside",
        )
    )
    fig_donut.add_annotation(
        text="Total TEU<br>by Route",
        x=0.5,
        y=0.5,
        font=dict(family="Plus Jakarta Sans", size=11, color="#d0e6ff"),
        showarrow=False,
    )
    fig_donut.update_layout(
        **{
            **PLOTLY_LAYOUT,
            "legend": dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
                font=dict(size=10),
            ),
            "margin": dict(l=10, r=120, t=52, b=10),
        },
        title=chart_title("All-Time TEU Share by Passage"),
        height=360,
        showlegend=True,
    )
    st.plotly_chart(
        fig_donut,
        use_container_width=True,
        config={**PLOTLY_CONFIG, "displayModeBar": False},
    )

with col_yoy:
    # Annual totals per passage
    yoy_df = (
        df_monthly.groupby(["Year", "Passage"])["TEU"]
        .sum()
        .reset_index()
        .sort_values(["Passage", "Year"])
    )
    yoy_df["TEU_prev"] = yoy_df.groupby("Passage")["TEU"].shift(1)
    yoy_df["YoY_pct"] = (yoy_df["TEU"] - yoy_df["TEU_prev"]) / yoy_df["TEU_prev"] * 100
    yoy_df = yoy_df.dropna(subset=["YoY_pct"])
    yoy_df["color"] = yoy_df["Passage"].map(COLORS_PASSAGE).fillna("#3a9eff")

    fig_yoy = px.bar(
        yoy_df,
        x="Year",
        y="YoY_pct",
        color="Passage",
        barmode="group",
        color_discrete_map=COLORS_PASSAGE,
        title="Year-over-Year TEU Change by Passage",
        labels={"YoY_pct": "YoY Change (%)", "Year": "Year"},
    )
    fig_yoy.add_hline(
        y=0,
        line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot"),
    )
    fig_yoy.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Change: %{y:+.1f}%<extra></extra>"
    )
    fig_yoy.update_layout(
        **{
            **PLOTLY_LAYOUT,
            "legend": dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
                bgcolor="#080e1a",
                bordercolor="#152035",
                borderwidth=1,
                font=dict(size=11),
            ),
            "margin": dict(l=10, r=10, t=52, b=70),
        },
        title=chart_title("Year-over-Year TEU Change by Passage"),
        height=360,
        xaxis=dict(gridcolor="#152035", title="Year", dtick=1),
        yaxis=dict(gridcolor="#152035", title="YoY Change (%)", ticksuffix="%"),
    )
    st.plotly_chart(
        fig_yoy,
        use_container_width=True,
        config={**PLOTLY_CONFIG, "displayModeBar": False},
    )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Top Import Product Categories through Suez
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Top Import Product Categories through Suez",
    "What UK goods flow through the Suez Canal — annual volumes by HS2 product category (TEU)",
)
chart_note(
    "Each bar represents the annual TEU volume for that product category through the Suez Canal. "
    "Use the passage selector to compare across routes."
)

if not df_hs2.empty:
    # Passage selector for the HS2 chart
    hs2_passages = sorted(df_hs2["Passage"].dropna().unique().tolist())
    with st.container(border=True):
        st.markdown(
            "<div class='filter-bar-label'>Passage for Product Analysis</div>",
            unsafe_allow_html=True,
        )
        sel_hs2_passage = st.selectbox(
            "Select Passage",
            options=hs2_passages,
            index=hs2_passages.index("Suez") if "Suez" in hs2_passages else 0,
            key="eco_hs2_passage",
        )

    hs2_filtered = df_hs2[df_hs2["Passage"] == sel_hs2_passage].copy()
    year_cols = [
        c for c in ["2020", "2021", "2022", "2023", "2024"] if c in hs2_filtered.columns
    ]

    if not hs2_filtered.empty and year_cols:
        hs2_filtered["Total TEU"] = hs2_filtered[year_cols].sum(axis=1)
        hs2_sorted = hs2_filtered.nlargest(10, "Total TEU").sort_values("Total TEU")

        # Melt for grouped bar (one bar per year per product)
        hs2_melt = hs2_sorted.melt(
            id_vars=["Product Category"],
            value_vars=year_cols,
            var_name="Year",
            value_name="TEU",
        )
        hs2_melt = hs2_melt.dropna(subset=["TEU"])

        YEAR_COLORS = {
            "2020": "#1a3a5c",
            "2021": "#1f5494",
            "2022": "#2878cc",
            "2023": "#3a9eff",
            "2024": "#7dc9ff",
        }

        fig_hs2 = px.bar(
            hs2_melt,
            y="Product Category",
            x="TEU",
            color="Year",
            orientation="h",
            barmode="group",
            color_discrete_map=YEAR_COLORS,
            title=f"Top 10 Import Categories through {sel_hs2_passage} (TEU)",
            labels={"TEU": "TEU Volume", "Product Category": ""},
        )
        fig_hs2.update_traces(
            hovertemplate="<b>%{y}</b><br>Year: %{fullData.name}<br>TEU: %{x:,.0f}<extra></extra>"
        )
        fig_hs2.update_layout(
            **{
                **PLOTLY_LAYOUT,
                "legend": dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1,
                    xanchor="right",
                    x=1,
                    bgcolor="#080e1a",
                    bordercolor="#152035",
                    borderwidth=1,
                    font=dict(size=11),
                ),
                "margin": dict(l=10, r=10, t=52, b=10),
            },
            title=chart_title(
                f"Top 10 Import Categories through {sel_hs2_passage} (TEU)"
            ),
            height=480,
            xaxis=dict(gridcolor="#152035", title="TEU Volume"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", automargin=True),
        )
        st.plotly_chart(
            fig_hs2,
            use_container_width=True,
            config={**PLOTLY_CONFIG, "displayModeBar": False},
        )
    else:
        st.info(f"No product data available for {sel_hs2_passage}.")
else:
    st.info("Product category data not available.")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Pre vs Post Crisis Comparison (Stacked bar)
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Pre vs Post-Crisis Trade Volume",
    "How the Houthi crisis reshaped UK cargo volumes through each maritime passage",
)
chart_note(
    "Pre-Crisis = Jan 2020 – Oct 2023 · Post-Crisis = Nov 2023 – Dec 2024. "
    "Compare the absolute shift in TEU volume for each route."
)

phase_agg = df_monthly.groupby(["CRISIS_PHASE", "Passage"])["TEU"].sum().reset_index()
phase_agg["CRISIS_PHASE"] = pd.Categorical(
    phase_agg["CRISIS_PHASE"], categories=["Pre-Crisis", "Post-Crisis"], ordered=True
)
phase_agg = phase_agg.sort_values(["CRISIS_PHASE", "Passage"])

fig_phase = px.bar(
    phase_agg,
    x="Passage",
    y="TEU",
    color="CRISIS_PHASE",
    barmode="group",
    color_discrete_map={
        "Pre-Crisis": "#1a3a5c",
        "Post-Crisis": "#ff5e5e",
    },
    title="Total TEU Volume: Pre vs Post-Crisis by Passage",
    labels={"TEU": "Total TEU", "Passage": ""},
)
fig_phase.update_traces(
    hovertemplate="<b>%{x}</b><br>Phase: %{fullData.name}<br>TEU: %{y:,.0f}<extra></extra>"
)
fig_phase.update_layout(
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
    title=chart_title("Total TEU Volume: Pre vs Post-Crisis by Passage"),
    height=380,
    xaxis=dict(gridcolor="rgba(0,0,0,0)", title=""),
    yaxis=dict(gridcolor="#152035", title="Total TEU"),
)
st.plotly_chart(
    fig_phase,
    use_container_width=True,
    config={**PLOTLY_CONFIG, "displayModeBar": False},
)

# ── Footer ────────────────────────────────────────────────────────────────
page_footer()
