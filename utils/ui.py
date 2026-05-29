"""
utils/ui.py
─────────────────────────────────────────────
Shared UI primitives for the Red Sea Crisis Dashboard.

Call ``init_ui()`` at the top of every page (after set_page_config) to
inject the global CSS and font imports into the current page.
"""

import streamlit as st


# ─────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0b1628",
    plot_bgcolor="#0b1628",
    font=dict(family="Plus Jakarta Sans", color="#b0c4de", size=12),
    title_font=dict(family="Plus Jakarta Sans", size=14, color="#d0dced"),
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
    x0="2023-11-01",
    x1="2023-11-01",
    y0=0,
    y1=1,
    yref="paper",
    line=dict(color="#ff5e5e", width=1.5, dash="dot"),
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
_CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
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
        border-radius: 16px;
        padding: 24px 28px;
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
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #4a7aaa;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
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
        padding: 16px 24px;
        border-radius: 0 12px 12px 0;
        margin: 32px 0 20px 0;
    }
    .section-header h2 {
        margin: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
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

    /* Deep-dive divider */
    .deep-dive-divider {
        border-left: 3px solid #ff5e5e;
        background: linear-gradient(90deg, rgba(50,10,10,0.85), transparent);
    }
    .deep-dive-divider h2 { color: #ffa0a0; }

    /* Widget labels */
    .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label {
        color: #5a8aaa !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
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
        border-radius: 12px 12px 0 0;
        border: 1px solid #152035;
        border-bottom: none;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        padding: 12px 24px;
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
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14px;
        color: #3a6080;
        letter-spacing: 0.3px;
    }

    /* Insight box */
    .insight-box {
        background: #0b1628;
        border: 1px solid #152840;
        border-left: 3px solid #3a9eff;
        border-radius: 12px;
        padding: 20px 24px;
        font-size: 12px;
        color: #6a9ac8;
        line-height: 1.6;
        margin-top: 8px;
    }

    /* Page filter bar */
    .filter-bar {
        background: #080e1a;
        border: 1px solid #152035;
        border-radius: 12px;
        padding: 24px 28px 16px 28px;
        margin-bottom: 24px;
    }
    .filter-bar-label {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #3a7eff;
        margin-bottom: 10px;
    }
    /* Plotly charts rounded corners */
    [data-testid="stPlotlyChart"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #152840 !important;
    }
    [data-testid="stPlotlyChart"] iframe {
        border-radius: 12px !important;
    }


</style>
"""


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────
def init_ui() -> None:
    """Inject global CSS + fonts.  Call this once per page, right after
    ``st.set_page_config``."""
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Render the brand logo / title block inside the sidebar."""
    st.markdown(
        """
        <div style='padding: 12px 0 8px 0;'>
            <div style='font-family: Plus Jakarta Sans, sans-serif; font-size: 18px;
                        font-weight: 800; color: #ffffff;'>🌊 Red Sea Crisis</div>
            <div style='font-size: 11px; color: #3a6080; margin-top: 4px;'>
                Analytical Dashboard
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")


def sidebar_footer() -> None:
    """Render the data-sources footnote at the bottom of the sidebar."""
    st.markdown("---")
    st.markdown(
        """
        <div style='font-size:11px; color:#2a4a6a; line-height:1.8;'>
        📅 Conflict data: 2015–2026<br>
        🚢 Ship data: Jan 2022–Apr 2024<br>
        🔴 Crisis onset: Nov 2023<br><br>
        <strong style='color:#3a6080;'>Sources:</strong><br>
        ACLED · UNCTAD Maritime Data
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(col, label: str, value: str, delta_text: str, delta_type: str) -> None:
    """Render a single KPI card inside *col* (a Streamlit column object).

    Parameters
    ----------
    col        : st.columns element to render into.
    label      : Short uppercase label shown above the value.
    value      : Pre-formatted value string, e.g. ``"1,234"`` or ``"-32.1%"``.
    delta_text : Supporting text shown below the value.
    delta_type : One of ``"positive"``, ``"negative"``, ``"neutral"``.
    """
    col.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-delta {delta_type}'>{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "", variant: str = "default") -> None:
    """Render a styled section header.

    Parameters
    ----------
    title    : Bold heading text.
    subtitle : Optional smaller description.
    variant  : ``"default"`` (blue accent) or ``"deep-dive"`` (red accent).
    """
    extra_class = "deep-dive-divider" if variant == "deep-dive" else ""
    st.markdown(
        f"""
        <div class='section-header {extra_class}'>
            <h2>{title}</h2>
            {"<p>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_footer() -> None:
    """Render the shared footer at the bottom of each page."""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; padding:20px 0; color:#1e3a5a;
                    font-size:11px; line-height:2.2;'>
            <strong style='font-family:Plus Jakarta Sans,sans-serif; color:#3a7eff;
                           font-size:13px; letter-spacing:0.5px;'>
                Red Sea Crisis: Houthi Conflict &amp; Maritime Trade Impact
            </strong><br>
            Data Sources: ACLED (Armed Conflict Location &amp; Event Data Project)
            · UNCTAD Maritime Trade Data<br>
            Dashboard built with Streamlit · Plotly · WordCloud · Python
        </div>
        """,
        unsafe_allow_html=True,
    )
