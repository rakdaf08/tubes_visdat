"""
Overview page — Dashboard Overview & High-Level KPIs
─────────────────────────────────────────────────────────
Red Sea Crisis: Houthi Conflict & Maritime Trade Impact
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config MUST be the very first Streamlit call ─────────────────────
st.set_page_config(
    page_title="Red Sea Crisis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui import (
    init_ui,
    sidebar_brand,
    sidebar_footer,
    kpi,
    page_footer,
    section_header,
    chart_note,
    chart_title,
    PLOTLY_LAYOUT,
    PLOTLY_CONFIG,
    CRISIS_LINE,
)
from utils.data_loader import load_data, passage_mean

# ── Apply global styles ───────────────────────────────────────────────────
init_ui()

# ── Load data ─────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()

CRISIS_DATE = pd.Timestamp("2023-11-01")

# ── Sidebar — brand + nav + footer ───────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    sidebar_footer()

# ── Hero header ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; padding: 56px 0 48px 0;'>
        <div style='font-size:12px; letter-spacing:4px; color:#85AEF0; font-weight:700;
                    font-family: Plus Jakarta Sans, sans-serif; text-transform:uppercase; margin-bottom:12px;'>
            Analytical Dashboard
        </div>
        <div style='font-family: Plus Jakarta Sans, sans-serif; font-size:42px; font-weight:800;
                   color:#ffffff; margin:0; line-height:1; letter-spacing:-1px;'>
            Red Sea Crisis
        </div>
        <p style='font-size:24px; color:#fafafa; margin-top:12px; font-weight:700;
                  font-family: Plus Jakarta Sans, sans-serif; max-width:720px;
                  margin-left:auto; margin-right:auto;'>
            Houthi Conflict &amp; Its Impact on Global Maritime Trade
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI computations (all-time, no year filter on overview) ───────────────
total_events = int(df_conf["EVENTS"].sum())
total_fatalities = int(df_conf["FATALITIES"].sum())

suez_pre_v = passage_mean(df_ship, "Suez", "pre")
suez_post_v = passage_mean(df_ship, "Suez", "post")
suez_change = ((suez_post_v - suez_pre_v) / suez_pre_v * 100) if suez_pre_v else 0

cape_pre_v = passage_mean(df_ship, "Cape of Good Hope", "pre")
cape_post_v = passage_mean(df_ship, "Cape of Good Hope", "post")
cape_change = ((cape_post_v - cape_pre_v) / cape_pre_v * 100) if cape_pre_v else 0

yemen_post_events = int(
    df_conf[(df_conf["COUNTRY"] == "Yemen") & (df_conf["WEEK"] >= CRISIS_DATE)][
        "EVENTS"
    ].sum()
)

# ── KPI Cards ─────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

kpi(k1, "Conflict Events", f"{total_events:,}", "All-time total", "neutral")
kpi(k2, "Total Fatalities", f"{total_fatalities:,}", "All-time total", "negative")
kpi(
    k3,
    "Yemen Post-Crisis",
    f"{yemen_post_events:,}",
    "Events since Nov 2023",
    "negative",
)
kpi(
    k4,
    "Suez Traffic Change",
    f"{suez_change:+.1f}%",
    "Post vs Pre-Crisis avg/week",
    "negative" if suez_change < 0 else "positive",
)
kpi(
    k5,
    "Cape of Good Hope",
    f"{cape_change:+.1f}%",
    "Post vs Pre-Crisis avg/week",
    "positive" if cape_change > 0 else "negative",
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Crisis summary narrative ───────────────────────────────────────────────
st.markdown(
    f"""
    <div class='insight-box'>
        Across all recorded data, the Middle East region logged
        <strong style='color:#ffffff;'>{total_events:,} conflict events</strong>
        causing <strong style='color:#ff5e5e;'>{total_fatalities:,} fatalities</strong>.
        The Houthi crisis onset in <strong style='color:#ffffff;'>November 2023</strong> triggered a
        <strong style='color:#ff5e5e;'>{suez_change:+.1f}%</strong> change in
        weekly Suez Canal crossings, while Cape of Good Hope traffic shifted
        <strong style='color:#3ecf6e;'>{cape_change:+.1f}%</strong> — evidence of
        a large-scale rerouting of global maritime trade.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# HERO CHART — Dual sparkline: Yemen Events vs Suez Crossings (Indexed)
# ══════════════════════════════════════════════════════════════════════════
section_header(
    "Crisis at a Glance",
    "Yemen conflict escalation vs Suez Canal traffic disruption — indexed to pre-crisis baseline",
)
chart_note(
    "Both series are indexed to 100 at their first overlapping month. "
    "Divergence after the red line marks the Houthi crisis impact on global shipping."
)

col_spark, col_donut = st.columns([3, 2])

with col_spark:
    yemen_m = df_conf[df_conf["COUNTRY"] == "Yemen"].copy()
    yemen_m["MONTH_DT"] = yemen_m["WEEK"].dt.to_period("M").dt.to_timestamp()
    ym = yemen_m.groupby("MONTH_DT")["EVENTS"].sum().reset_index()
    ym.columns = ["month", "yemen_events"]

    suez_df = df_ship[df_ship["Passage"] == "Suez"].copy() if "Passage" in df_ship.columns else pd.DataFrame()

    if not suez_df.empty:
        suez_df["month"] = pd.to_datetime(suez_df["month"] + "-01", errors="coerce")
        sm = suez_df.groupby("month")["Number of crossings"].mean().reset_index()
        sm.columns = ["month", "suez_crossings"]
        merged = pd.merge(ym, sm, on="month", how="inner").sort_values("month")

        def to_index(s, month_col):
            mask = month_col == pd.Timestamp("2023-10-01")
            if mask.any() and s[mask].iloc[0] > 0:
                baseline = s[mask].iloc[0]
            else:
                baseline = s[s > 0].iloc[0] if (s > 0).any() else 1
            return s / baseline * 100

        merged["Yemen Conflict Events"] = to_index(merged["yemen_events"], merged["month"])
        merged["Suez Canal Crossings"] = to_index(merged["suez_crossings"], merged["month"])

        corr_long = merged.melt(
            id_vars=["month", "yemen_events", "suez_crossings"],
            value_vars=["Yemen Conflict Events", "Suez Canal Crossings"],
            var_name="Metric",
            value_name="Index",
        )
        fig_spark = px.line(
            corr_long,
            x="month",
            y="Index",
            color="Metric",
            color_discrete_map={
                "Yemen Conflict Events": "#ff5e5e",
                "Suez Canal Crossings": "#3a9eff",
            },
        )
        fig_spark.add_shape(CRISIS_LINE)
        fig_spark.add_annotation(
            x="2023-11-01",
            y=1,
            yref="paper",
            text="  Crisis Onset",
            showarrow=False,
            font=dict(color="#ff5e5e", size=10, family="Plus Jakarta Sans"),
            xanchor="left",
            bgcolor="#180404",
            borderpad=3,
        )
        fig_spark.update_traces(line=dict(width=2.2))
        fig_spark.update_layout(
            **{
                **PLOTLY_LAYOUT,
                "legend": dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    bgcolor="#080e1a",
                    bordercolor="#152035",
                    borderwidth=1,
                    font=dict(size=11),
                ),
            },
            title=chart_title("Yemen Events vs Suez Crossings (Indexed)"),
            height=360,
            xaxis=dict(gridcolor="#152035", title=""),
            yaxis=dict(gridcolor="#152035", title="Index (baseline = 100)"),
            hovermode="x unified",
        )
        st.plotly_chart(fig_spark, use_container_width=True, config={**PLOTLY_CONFIG, "displayModeBar": False})
    else:
        st.info("Suez crossing data not available.")

with col_donut:
    red_sea_routes = ["Suez", "Bab-Al Mandab Strait", "Cape of Good Hope"]
    COLORS_PASSAGE = {
        "Suez": "#ff5e5e",
        "Bab-Al Mandab Strait": "#ffa640",
        "Cape of Good Hope": "#3ecf6e",
    }

    donut_data = (
        df_ship[df_ship["Passage"].isin(red_sea_routes)]
        .groupby("Passage", as_index=False)["Number of crossings"]
        .sum()
    ) if "Passage" in df_ship.columns else pd.DataFrame()

    if not donut_data.empty:
        fig_donut = go.Figure(
            go.Pie(
                labels=donut_data["Passage"],
                values=donut_data["Number of crossings"],
                hole=0.55,
                marker=dict(
                    colors=[COLORS_PASSAGE.get(p, "#3a9eff") for p in donut_data["Passage"]],
                    line=dict(color="#080e1a", width=2),
                ),
                hovertemplate="<b>%{label}</b><br>Crossings: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
                textfont=dict(family="Plus Jakarta Sans", size=12, color="#ffffff"),
            )
        )
        fig_donut.add_annotation(
            text="All-Time<br>Route Share",
            x=0.5,
            y=0.5,
            font=dict(family="Plus Jakarta Sans", size=12, color="#d0e6ff"),
            showarrow=False,
        )
        fig_donut.update_layout(
            **{
                **PLOTLY_LAYOUT,
                "legend": dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.05,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
            },
            title=chart_title("Ship Crossings by Route"),
            height=360,
            showlegend=True,
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={**PLOTLY_CONFIG, "displayModeBar": False})
    else:
        st.info("Route data not available.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation buttons ─────────────────────────────────────────────────────
col_spacer1, col_nav1, col_nav2, col_nav3, col_spacer2 = st.columns([1, 2, 2, 2, 1])
with col_nav1:
    st.page_link("pages/1_Conflict_Analysis.py", label="Go to Conflict Analysis", use_container_width=True)
with col_nav2:
    st.page_link("pages/2_Maritime_Impact.py", label="Go to Maritime Impact", use_container_width=True)
with col_nav3:
    st.page_link("pages/3_Economic_Impact.py", label="Go to Economic Impact", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────
page_footer()
