"""
Overview page — Dashboard Overview & High-Level KPIs
─────────────────────────────────────────────────────────
Red Sea Crisis: Houthi Conflict & Maritime Trade Impact
"""

import streamlit as st
import pandas as pd

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
    filter_summary,
)
from utils.data_loader import load_data, passage_mean

# ── Apply global styles ───────────────────────────────────────────────────
init_ui()

# ── Load data ─────────────────────────────────────────────────────────────
df_conf, df_ship, geojson = load_data()

CRISIS_DATE = pd.Timestamp("2023-11-01")
conf_min = df_conf["WEEK"].min().strftime("%b %Y")
conf_max = df_conf["WEEK"].max().strftime("%b %Y")
ship_min = df_ship["date"].min().strftime("%b %Y")
ship_max = df_ship["date"].max().strftime("%b %Y")

# ── Sidebar — brand + footer ────
with st.sidebar:
    sidebar_brand()
    st.page_link("Overview.py", label="Overview")
    st.page_link("pages/1_Conflict_Analysis.py", label="Conflict Analysis")
    st.page_link("pages/2_Maritime_Impact.py", label="Maritime Impact")
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
        <strong style='color:#3ecf6e;'>{cape_change:+.1f}%</strong>, which is an
        evidence of a large-scale rerouting of global maritime trade.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

col_spacer1, col_nav1, col_nav2, col_spacer2 = st.columns([2, 2, 2, 2])
with col_nav1:
    st.page_link("pages/1_Conflict_Analysis.py", label="Go to Conflict Analysis", use_container_width=True)
with col_nav2:
    st.page_link("pages/2_Maritime_Impact.py", label="Go to Maritime Impact", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────
page_footer()
