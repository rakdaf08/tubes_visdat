"""
app.py — Entry Point: Dashboard Overview & High-Level KPIs
─────────────────────────────────────────────────────────
Red Sea Crisis: Houthi Conflict & Maritime Trade Impact
"""

import streamlit as st
import pandas as pd

# ── Page config MUST be the very first Streamlit call ─────────────────────
st.set_page_config(
    page_title="Red Sea Crisis Dashboard",
    page_icon="🚢",
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
)
from utils.data_loader import load_data, passage_mean

# ── Apply global styles ───────────────────────────────────────────────────
init_ui()

# ── Load data ─────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()

CRISIS_DATE = pd.Timestamp("2023-11-01")

# ── Sidebar — brand + footer ────
# with st.sidebar:
#     sidebar_brand()
#     sidebar_footer()

# ── Hero header ───────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; padding: 56px 0 48px 0;'>
        <div style='font-size:10px; letter-spacing:4px; color:#3a7eff; font-weight:700;
                    font-family: Plus Jakarta Sans, sans-serif; text-transform:uppercase; margin-bottom:12px;'>
            Analytical Dashboard
        </div>
        <h1 style='font-family: Plus Jakarta Sans, sans-serif; font-size:42px; font-weight:800;
                   color:#ffffff; margin:0; line-height:1; letter-spacing:-1px;'>
            🌊 Red Sea Crisis
        </h1>
        <p style='font-size:15px; color:#3a6080; margin-top:12px; font-weight:400;
                  font-family: Plus Jakarta Sans, sans-serif; max-width:580px;
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
    📊 <strong>Overview:</strong> Across all recorded data, the Middle East region logged
    <strong style='color:#ffffff;'>{total_events:,} conflict events</strong>
    causing <strong style='color:#ff5e5e;'>{total_fatalities:,} fatalities</strong>.
    The Houthi crisis onset in <strong>November 2023</strong> triggered a
    <strong style='color:#ff5e5e;'>{suez_change:+.1f}%</strong> change in
    weekly Suez Canal crossings, while Cape of Good Hope traffic shifted
    <strong style='color:#3ecf6e;'>{cape_change:+.1f}%</strong> —
    evidence of a large-scale rerouting of global maritime trade.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation cards ──────────────────────────────────────────────────────
section_header(
    "Explore the Dashboard",
    "Use the sidebar navigation or the cards below to dive deeper",
)

nav1, nav2 = st.columns(2)

with nav1:
    st.markdown(
        """
        <div class='kpi-card' style='text-align:left; padding:32px 36px; min-height:180px;'>
            <div style='font-size:28px; margin-bottom:10px;'>🌍</div>
            <div style='font-family:Plus Jakarta Sans,sans-serif; font-size:15px; font-weight:700;
                        color:#c0d4ee; margin-bottom:8px;'>Conflict Analysis</div>
            <div style='font-size:12px; color:#4a7aaa; line-height:1.6;'>
                Regional conflict landscape, country-level breakdown, Yemen &amp;
                Houthi deep-dive — attack types, timeline, and word cloud.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav2:
    st.markdown(
        """
        <div class='kpi-card' style='text-align:left; padding:32px 36px; min-height:180px;
                                      border-top-color:#3ecf6e;'>
            <div style='font-size:28px; margin-bottom:10px;'>🚢</div>
            <div style='font-family:Plus Jakarta Sans,sans-serif; font-size:15px; font-weight:700;
                        color:#c0d4ee; margin-bottom:8px;'>Maritime Impact</div>
            <div style='font-size:12px; color:#4a7aaa; line-height:1.6;'>
                Weekly ship crossings, passage traffic shares (pre vs post-crisis),
                quarterly trends, and Conflict–Trade correlation analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────
page_footer()
