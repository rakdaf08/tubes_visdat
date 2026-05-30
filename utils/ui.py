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
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#ffffff", size=13),
    title_font=dict(family="Plus Jakarta Sans", size=15, color="#ffffff"),
    legend=dict(
        bgcolor="rgba(11, 22, 40, 0.8)",
        bordercolor="rgba(255, 255, 255, 0.2)",
        borderwidth=1,
        font=dict(size=11, color="#ffffff"),
    ),
    margin=dict(l=10, r=10, t=52, b=10),
    colorway=["#5cb8ff", "#E50303", "#3ecf6e", "#ffbc40", "#d186f8", "#5ccfff"],
    hoverlabel=dict(
        bgcolor="rgba(11, 22, 40, 0.95)",
        bordercolor="#5cb8ff",
        font=dict(family="Plus Jakarta Sans", size=12, color="#ffffff"),
    ),
)


def chart_title(text: str, t: int = 16, l: int = 16) -> dict:
    """Return a Plotly-compatible title dict with consistent padding.

    Use in place of a bare title string so the padding is never overridden:
        fig.update_layout(title=chart_title("My Title"), ...)
    """
    return dict(text=text, pad=dict(t=t, l=l))


PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

CRISIS_LINE = dict(
    type="line",
    x0="2023-11-01",
    x1="2023-11-01",
    y0=0,
    y1=1,
    yref="paper",
    line=dict(color="#E50303", width=1.5, dash="dot"),
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
_CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(to bottom right, #2A1B87, #060816) !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
    }
    
    .stApp > header {
        background-color: transparent !important;
    }

    /* Hide header anchors */
    .stMarkdown a.header-anchor {
        display: none !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(6, 8, 22, 0.6) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {
        color: #85AEF0 !important;
        font-size: 13px;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* KPI Cards */
    .kpi-card {
        background: rgba(11, 22, 40, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 24px 28px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .kpi-label {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #9cc4e8;
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
        font-size: 12px;
        margin-top: 6px;
        font-weight: 600;
    }
    .kpi-delta.negative { color: #ff5e5e; }
    .kpi-delta.positive { color: #5ceb8a; }
    .kpi-delta.neutral  { color: #9cc4e8; }

    /* Section headers */
    .section-header {
        margin: 32px 0 32px 0;
    }
    .section-header h2 {
        margin-bottom: 4px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        padding: 0px;
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .section-header p {
        margin: 0 0 0 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 16px;
        color: #d0e6ff;
    }

    /* Deep-dive divider */
    .deep-dive-divider {
    }
    .deep-dive-divider h2 { color: #ffffff; }

    /* Widget labels */
    .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label {
        color: #9cc4e8 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(6, 8, 22, 0.4);
        color: #d0e6ff;
        border-radius: 6px 6px 0 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: none;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.3px;
        padding: 12px 24px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(42, 27, 135, 0.6) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }

    hr { border-color: rgba(255, 255, 255, 0.1); }

    .caption-text {
        font-size: 12px;
        color: #9cc4e8;
        text-align: center;
        margin-top: 4px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 400;

    }

    /* Hero title */
    .hero-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14px;
        color: #d0e6ff;
        letter-spacing: 0.3px;
    }

    /* Insight box */
    .insight-box {
        background: rgba(11, 22, 40, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 20px 24px;
        font-size: 14px;
        color: #e0f0ff;
        line-height: 1.6;
        margin-top: 8px;
        margin-bottom: 16px;
    }

    /* Page filter bar */
    .filter-bar {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: rgba(6, 8, 22, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 24px 28px 16px 28px;
        margin-bottom: 24px;
    }
    .filter-bar-label {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #fafafa;
        margin-bottom: 10px;
    }
    .filter-summary {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 10px 0 2px 0;
    }
    .filter-pill {
        background: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 999px;
        color: #ffffff;
        display: inline-flex;
        font-size: 13px;
        font-weight: 600;
        line-height: 1;
        padding: 8px 10px;
        white-space: nowrap;
    }
    .chart-helper {
        color: #9cc4e8;
        font-size: 13px;
        line-height: 1.55;
        margin: -6px 0 12px 0;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    [data-testid="stPageLink"] a {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        min-height: 44px;
        display: flex !important;
        align-items: center !important;
        padding-left: 12px;
        padding-right: 12px;
    }
    .main [data-testid="stPageLink"] a {
        border-radius: 9999px !important;
    }
    .stButton > button:hover,
    [data-testid="stPageLink"] a:hover {
        border-color: #85AEF0 !important;
        background: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }
    [data-testid="stPageLink"] a[data-active="true"],
    [data-testid="stPageLink"] a[aria-current="page"] {
        background: rgba(133, 174, 240, 0.25) !important;
        border: 1px solid #85AEF0 !important;
        border-left: 5px solid #85AEF0 !important;
        color: #ffffff !important;
    }

    [data-testid="stPageLink"] a::before {
        content: "";
        display: inline-block;
        width: 18px;
        height: 18px;
        background-size: contain;
        background-repeat: no-repeat;
        margin-right: 12px;
        flex-shrink: 0;
    }
    [data-testid="stPageLink"] a::after {
        content: "";
        display: inline-block;
        width: 14px;
        height: 14px;
        background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHZpZXdCb3g9IjAgMCA5MCA5MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CjxyZWN0IHdpZHRoPSI5MCIgaGVpZ2h0PSI5MCIgZmlsbD0idXJsKCNwYXR0ZXJuMF8yMDFfNikiLz4KPGRlZnM+CjxwYXR0ZXJuIGlkPSJwYXR0ZXJuMF8yMDFfNiIgcGF0dGVybkNvbnRlbnRVbml0cz0ib2JqZWN0Qm91bmRpbmdCb3giIHdpZHRoPSIxIiBoZWlnaHQ9IjEiPgo8dXNlIHhsaW5rOmhyZWY9IiNpbWFnZTBfMjAxXzYiIHRyYW5zZm9ybT0ic2NhbGUoMC4wMTExMTExKSIvPgo8L3BhdHRlcm4+CjxpbWFnZSBpZD0iaW1hZ2UwXzIwMV82IiB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHByZXNlcnZlQXNwZWN0UmF0aW89Im5vbmUiIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBRm9BQUFCYUNBWUFBQUE0cUVFQ0FBQUFDWEJJV1hNQUFBc1RBQUFMRXdFQW1wd1lBQUFCSTBsRVFWUjRuTzNhUVU0VVFSaUEwZEVGb09Ia2JGZ1lFM1RESFZ3QWQzS2hVWUhsWnliMHlqalRFTG9MR2Q4N1FIWGxXM1NxcS8vTkJnQUFBQUFBQUFBQUFBNUw5YTc2VlAycXZsWm4xZkZMNyt2ZzlCRDVUMWRpTDZoNlUvMzhTMml4bDFiOTJCRmE3Q1ZWNTN0Q2k3MlViY1FwcHRocnE0NnFMek94YjZxVDFUZHo2Qko3SExFSEVuc2dzUWNTZXlDeEJ4TDdOY2F1M2xjZnErOHppekgvQmJrN2RuVXhzd0NQOTNsWDVMZlYzUk1XWXIvYmJWT2hYeXEwVjhmaUx1YittMzJvdmkzLzNQL0t0V1BlTXpoTER5RHlBQ0lQSVBJQUlnOGc4Z0FpRHlEeUFDTC9Xd00wSWovSGRQVWc4cHFtbTh2dGJadklBMExmNzRsczNtNHAxYVhJQTFTblUrejdhU2g5TzhZcjhwclQvNnN0RGdBQUFBQUFBQUFBc0ZuVGI3Q2FVU2ROVGFkUEFBQUFBRWxGVGtTdVFtQ0MiLz4KPC9kZWZzPgo8L3N2Zz4K");
        background-size: contain;
        background-repeat: no-repeat;
        margin-left: auto;
        flex-shrink: 0;
        opacity: 0.6;
    }

    [data-testid="stPageLink"] a:not([href*="Conflict_Analysis"]):not([href*="Maritime_Impact"])::before {
        background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHZpZXdCb3g9IjAgMCA5MCA5MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CjxyZWN0IHdpZHRoPSI5MCIgaGVpZ2h0PSI5MCIgZmlsbD0idXJsKCNwYXR0ZXJuMF8yMDFfMykiLz4KPGRlZnM+CjxwYXR0ZXJuIGlkPSJwYXR0ZXJuMF8yMDFfMyIgcGF0dGVybkNvbnRlbnRVbml0cz0ib2JqZWN0Qm91bmRpbmdCb3giIHdpZHRoPSIxIiBoZWlnaHQ9IjEiPgo8dXNlIHhsaW5rOmhyZWY9IiNpbWFnZTBfMjAxXzMiIHRyYW5zZm9ybT0ic2NhbGUoMC4wMTExMTExKSIvPgo8L3BhdHRlcm4+CjxpbWFnZSBpZD0iaW1hZ2UwXzIwMV8zIiB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHByZXNlcnZlQXNwZWN0UmF0aW89Im5vbmUiIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBRm9BQUFCYUNBWUFBQUE0cUVFQ0FBQUFDWEJJV1hNQUFBc1RBQUFMRXdFQW1wd1lBQUFEZzBsRVFWUjRuTzJjVFdvVVFSU0FteXhpZENPdWpERnJSUThnNkFVa2lrZlFFNmdieGNSVmRHR1dJa1p4NGhtTU4xQndZY1NWRW5IakR5aEVVQkIvRU9NMGlwOFVVeEZOdXJxN2FycGZkOWU4RDVvTVlhcnExZGRWcjZzbW1Vb1NSVkVVUlZHNkJURFdkQXhSQTJ3SGJnQmY3TFZvZnRkMFhORUJYR01yVjV1T0t6cUE5eG1pUHpRZFYzVGdvT200b2dNVkxRTXhpUVoyQURmdFUxMEo0N05kSGJsWFJFQXZzSEpsS3oyWDVERmdQYU9BRXNiM3pNMlZpaFlTcmFtamNtNFZiWE1YYlVKWHd2Z0VYQy85OFVCZ0l5TlA0a3ZUQVhjVkZTMkVpaFpDUlF1aG9vVlEwVUtvYUNGVXRCQXF1cGcrTUF0TTJzdThUdkZFUlJkTG5zbHdNSWNuS3RxTkdiVW5IQTUyNDRtSzlwUnNIVXpoaVlvdW1TNDJPYmlJSnlyYVgvS01mWjhYS3Jwa3VyQjlQd3I4SUFBVkxTRFpvS0twWDNLWFJmY3pOaEg5TnVYa0dFU25XU013WU5TSmpPU3VpazRMMXJkbHhZaEs3cHJvdEVoT1NVSGlrcnNrT2kwanVZU29SaVIzUlhUcUl6bEhXR09TbXhDZGVxNFcra1dyZ3BJckJySFZSVnRFejNwMHNGOVNUbFh2cVUyeXdVUHgzNkNHWWJLR2FaNkdwSmFjdG1zaEpMREtSZnVLQzdreEpldXBEV25SY3pWTzg3NVBQcGRJRi8vaTQzZ2p3R0dvNnVFMlZQM1NrcHNRTFRITjA0cDJqNTBYWGVVR3BPN1BRem92V21LYTkrMWZxL2ZZYTA0NlhiUkZkR3VuZVl5aVd6bk5ZeFhkdW1rZXMram9VZEZDcUdnaFZMUVFLbG9JRlMyRWloWkNSUXVob2xzcytwdFVjQkh4TlVUMDQ2YWo3aUNQUWtTZmJUcnFEbkk2UlBRMjRHblRrWGVJSjhDNHQyZ3JlMXBsbDVhOE4wanlwcEY5eHVRZmZVRCtoM0d4WXRKRjhFaHVBbUFDZUVzMmI4d056eWd6RHJ4MmxGblRZNDh6QU03ajVtUk91Vk01NWM2NXlvMGt3RTdnbzBQV2F0NHA2UGE4UHBNalhTZDI3Wkx0VFlzQkZuSkc1YkVTNVkvbmxMOGkwNHVXdytCcndPYlV3eXdlZU5SenoxR0hPWjF5T2hsMWdOczVvL0d3UnoySGdOK09lcGFTVVFiWUQveDB5TGtUVU4reW82NWZ3TUZrVkFIdTVvZzVFRkRmdnB3YnQ1eU1JdVJQOWQ0UTlTN2g1a2d5S2pEWWFacnZ0THh6eURBUHhxbWFIcTVydHUwdG01K29ZSENhNzMzeVdhaDV1WWhkb1V3a3NVTHhRU09WYkRBS05rQWJYRWhpQlhoZTBQblZDdHQ2SnRWVzY2RDR2MGJYSzJ4clhhcXQxZ0c4S3VqOGl5NjIxVHFBeXdXZG4rOWlXMjFkZGF3NE92Nnd5cytQSmR0cUpRd0VYQUplMm04Qm1KL3pkWFJjc2kxRlVaU2tldjRBaFZ1Q3dWc3hJZ2NBQUFBQVNVVk9SSzVDWUlJPSIvPgo8L2RlZnM+Cjwvc3ZnPgo=");
    }
    [data-testid="stPageLink"] a[href*="Conflict_Analysis"]::before {
        background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHZpZXdCb3g9IjAgMCA5MCA5MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CjxyZWN0IHdpZHRoPSI5MCIgaGVpZ2h0PSI5MCIgZmlsbD0idXJsKCNwYXR0ZXJuMF8yMDFfNCkiLz4KPGRlZnM+CjxwYXR0ZXJuIGlkPSJwYXR0ZXJuMF8yMDFfNCIgcGF0dGVybkNvbnRlbnRVbml0cz0ib2JqZWN0Qm91bmRpbmdCb3giIHdpZHRoPSIxIiBoZWlnaHQ9IjEiPgo8dXNlIHhsaW5rOmhyZWY9IiNpbWFnZTBfMjAxXzQiIHRyYW5zZm9ybT0ic2NhbGUoMC4wMTExMTExKSIvPgo8L3BhdHRlcm4+CjxpbWFnZSBpZD0iaW1hZ2UwXzIwMV80IiB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHByZXNlcnZlQXNwZWN0UmF0aW89Im5vbmUiIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBRm9BQUFCYUNBWUFBQUE0cUVFQ0FBQUFDWEJJV1hNQUFBc1RBQUFMRXdFQW1wd1lBQUFDMjBsRVFWUjRuTzNkdTQ4TlVRREg4ZU10b1JFYVVmQUhJTkdKZUN5RlVJakdQNkVRaFlJb1JJTW9XS0pRK2grUUhZMUVTeStLUmVJWmlWZkVyRXV5MmErYzdCU2J5OTU3ejl6em1udCtuM28yT2VlYms4bVp1VE96eG9pSWlJaEl4b0N0d0MzZ0hmQVd1QVNzU2oydWlRRnNBcTRCYy96cll1cnhkUjZ3d1lZRXZyTzhWNm5IMlZuQVd1QU04SW5oM3FRZWJ5Y0JwNERYak81MjZqRjNDckFIZUlLYlg4QzIxR1B2QkdDelhaWEFQTzZ1cGg1LzlvRFZ3RG5nQisxOHM3dVIxUFBJR3JBTGVNWjRMcVNlUjdhQU5jQjU0TStZa1QvYXJWL3ErV1FKMkFzOHg0L1RxZWVUSldESE1sZDFiYnkwKyt6VWM4b1djQlRvZVFoOU12VmNTb2o5T1BVY1NvZzlEK3hPUGY1c0FJZUE0ME9PT2RZaTl0MTRzOGdjc0IvNDJXemZUbmhjMmZidTNaWjRNOGwvSmRkTDR2ejJ1TExQeHB0Sk4xWnlQeDhyKzZsK1JURURJL3VJYmY5MnB5a2R3eU9QRy91eUtSMXdZTVRJYldPL0FOYVprdUVlMlRXMnZWemZaMG9HVFBYdExseU5zaHZaYmtwRys1WHN2TEtMaGIvSWloMHhzbUpIakt6WUVTUFQ3REFPbTFLaHlPR2h5T0doeU9HaHlPRUJCeFY1Y2lJZk1hVkNrY05Ea2NORGthTkZyaFY1QVB1ckEzQzllYUl5VjdXOWIyMDYvaExOQS9JMjEvV1ZyTWloS1hJRWloeUJJa2VneUJFb2NnU0tITzlpcENKdmRhY3ZSaXhnbXJ6Vm5ZOXNBVi9KVnowUmtUc1Flc3BNaW94UEhRdG1ralE3amh2QVovS3lrTHBOZHV4VDhnb2RiNHM0cTlEaFR6MzNQVWUyRkRwQ1pFdWhJMFMyRkxvNUo4OHcyQ3pqS1R2MGlDdjVFYkIrek4xSXVhRmRJcHZGNDFjb2RPRElsa0tIT1NmUDlMOTFxdENPZ0R1dWtTMkZkZ0NzSFBLMXJmOUd0aFRhUFhUUE5iS0gwTzlOYVlCN3JwRTloTDVpU2dOc2JHTDNtc2R1cDBmNTNBTHRRejhzK29OK05wenI4YlNMWFBZM00xemhIcnBhdWcrWE1LRXJSUTRmdWxMazhLRXJSUTRmdWxKa1Q0QXZ5MFRXN3NJbkZoOWxVT1JJdDFkdk5tOTBmYkQvWHFQb2l4RVJFUkVSNDhOZnRLQ2VHWkpmaWtZQUFBQUFTVVZPUks1Q1lJST0iLz4KPC9kZWZzPgo8L3N2Zz4K");
    }
    [data-testid="stPageLink"] a[href*="Maritime_Impact"]::before {
        background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHZpZXdCb3g9IjAgMCA5MCA5MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CjxyZWN0IHdpZHRoPSI5MCIgaGVpZ2h0PSI5MCIgZmlsbD0idXJsKCNwYXR0ZXJuMF8yMDFfNSkiLz4KPGRlZnM+CjxwYXR0ZXJuIGlkPSJwYXR0ZXJuMF8yMDFfNSIgcGF0dGVybkNvbnRlbnRVbml0cz0ib2JqZWN0Qm91bmRpbmdCb3giIHdpZHRoPSIxIiBoZWlnaHQ9IjEiPgo8dXNlIHhsaW5rOmhyZWY9IiNpbWFnZTBfMjAxXzUiIHRyYW5zZm9ybT0ic2NhbGUoMC4wMTExMTExKSIvPgo8L3BhdHRlcm4+CjxpbWFnZSBpZD0iaW1hZ2UwXzIwMV81IiB3aWR0aD0iOTAiIGhlaWdodD0iOTAiIHByZXNlcnZlQXNwZWN0UmF0aW89Im5vbmUiIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBRm9BQUFCYUNBWUFBQUE0cUVFQ0FBQUFDWEJJV1hNQUFBc1RBQUFMRXdFQW1wd1lBQUFEY0VsRVFWUjRuTzJkVFc4TlVSaUFSNUd5RVI4SlZSYlNwS2tVcTRhRUJlb0hpRDlRU1Rjc1NDeUkraWkxcXdoRktKTHlBMWlJRlJzaEVUc1NTUnQwb1EyU1Zva2dQcUpObzQ4YzNrV1Q5dDdPekoxenpqMHo3NU9jcEpuT3ZQZDluM3N6TStlY3VlZEdrYUlvaXFJbzJRTFUrTTRoMXdDTGdhdkFOMmxYekRiZmVlVU80Qkl6NmZHZFYrNEF4bVlSL2RGM1hybURFdmpPSzNlb2FFZW9hRWVvYUVlb2FFZW9hSXNTYlJBVkdSWHRDQlh0Q0JYdENCWHRDQlh0Q0llZXU2SWk0MGp5NmFqb09KQjh5bmVOVllGbHlaMis2NnNhVkxJakxFays2aXIvWUxCaE9WSm1vcUlkb2FJZG9hSWRvYUlkb2FJZG9hSWRvYUlkb2FJZGtXZlJ3RmJnSHZEWmU0MVpKMkN3WWkxWlRmT0FDMWdrVFZMK2s4Z1lNLzV0bzY1cXF0RTdRQjN3UzBYbjROT3NvcU4vb2wrcWFNc0F6VEVjVFpqeGNxQmVXb2RzUzBKL1ZHU0FyaGlTT21ZNXpzaE93dkdveUJEdnRMRzZ4QVUwTGxQQXVuSkpLUCtwbjhYTkd1THpkSzUzV3lsOTZqaEdmQTZxNkhoTXlEazV6Y1Z3RWxpcG91MXp2NnhrRlowWmJTcmFQcitCSlNyYVByZm5sS3lpTTJHUGlyYlBWNkEycnVnWERoTEtLMzJ4Skl2b1E3NnpEWmhkU1VTdkFNWjlaeHdnbzhEODJLSkY5bDNmV1FkSThwVjJnTjIrc3c2UXpXbEVMd0ErK000OElONllHZlhFb2tYMmVkL1pCOFNaVkpKRjlBYmYyUWRFYzJyUkl2dVo3d29DNEhsRmtrWDBBZDlWQk1EaExFUXYxM3Zxc3Z3QjFsWXNXbVRmS2Y5YWhlWnhKcEpGOUZLWi9UVTl4azFBTy9CUVpublRNZ1U4QWZZREc0Rmw4anJtNzMzeXZ4RGk3OHhNZEprM1lEMXdFUmhKa09DSTZVR1pZL01lMzhvU3hzQTI0Q1R3QUhnTi9KRDJ5c3lmQVNka241cWl4VmNVUmJHOHd2bDFtYUl4SzV6ZkJGb3lqTjhpTWI5SUN6RituNnliYlFiaHpnSUwwd1M2VWVMcTJ3OGNBWnBTeEd5U1l3ZktYTjBIQW83ZkhhVUkralBHTGM5NzRKYmNYMjhCVmdHTHBOWEp0bmJaeCt5YmxORGlqNmI1eHRMM0ZJa1huZEUwbitqTHZyTU9rRlNuamxyNUhwNE9MTTJOZWRMMG5KbWRTaXg2bW5EejJHb25NRVQyREp1aFJtbkRBY1lmRWpjekhseXZSTGpwcnJZQ3ZjQzdDcElia3hqYnAzZHJKZjRPNEZxSm54cXBsdmh2NVlkOVdwMTB5NEVHWUs4TXRKZ3hnVUhnazV4cUp1WGUxVXhjUHBMQzI0REdCUEViNVpoZWlURWtNU2NkeEIrWFdnYWx0aDZwdFNHMU1FVlJGRVZSRkVWUmxLaEsrUXNPS2tJWldHaDJnUUFBQUFCSlJVNUVya0pnZ2c9PSIvPgo8L2RlZnM+Cjwvc3ZnPgo=");
    }
    .sidebar-nav-link {
        align-items: center;
        background: rgba(11, 22, 40, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #ffffff !important;
        display: flex;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 8px;
        min-height: 40px;
        padding: 0 12px;
        text-decoration: none !important;
    }
    .sidebar-nav-link:hover {
        border-color: #5cb8ff;
        background: rgba(42, 27, 135, 0.6);
        color: #ffffff !important;
    }
    /* Plotly charts rounded corners */
    [data-testid="stPlotlyChart"] {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        background: rgba(11, 22, 40, 0.4) !important;
    }
    [data-testid="stPlotlyChart"] iframe {
        border-radius: 8px !important;
    }
    @media (max-width: 900px) {
        .kpi-card {
            padding: 18px 16px;
        }
        .kpi-value {
            font-size: 22px;
        }
        .section-header {
            padding: 14px 16px;
        }
        .filter-bar {
            padding: 18px 16px 12px 16px;
        }
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
                        font-weight: 800; color: #ffffff;'>Red Sea Crisis</div>
            <div style='font-size: 11px; color: #85AEF0; margin-top: 4px;'>
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
        <div style='font-size:11px; color:#85AEF0; line-height:1.8; opacity: 80%;'>
        Conflict data: 2015–2026<br>
        Ship data: Jan 2022–Apr 2024<br>
        Crisis onset: Nov 2023<br><br>
        <strong style='color:#fafafa;'>Sources:</strong><br>
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


def filter_summary(items: list[tuple[str, str]]) -> None:
    """Render compact chips that explain the currently active filters."""
    chips = "".join(
        f"<span class='filter-pill'>{label}: {value}</span>" for label, value in items
    )
    st.markdown(f"<div class='filter-summary'>{chips}</div>", unsafe_allow_html=True)


def chart_note(text: str) -> None:
    """Render a small chart-reading note below a section title."""
    st.markdown(f"<div class='chart-helper'>{text}</div>", unsafe_allow_html=True)


def page_footer() -> None:
    """Render the shared footer at the bottom of each page."""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; padding:20px 0; color:#d9d9d9;
                    font-size:11px; line-height:2.2;'>
            <strong style='font-family:Plus Jakarta Sans,sans-serif; color:#85AEF0;
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
