"""
modules/styles.py — Design system ElectronicSystem Optimizer
Clean, modern, high-contrast UI for Streamlit
"""
import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ══════════════════════════════════════════════════════
   GLOBAL APP SHELL
══════════════════════════════════════════════════════ */
html, body, [data-testid="stApp"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

.block-container {
    padding: 2rem 3rem 4rem !important;
    max-width: 1160px !important;
}

/* ══════════════════════════════════════════════════════
   SIDEBAR — Clean, Light & High Contrast
══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 1px 0 3px rgba(0, 0, 0, 0.02) !important;
}

/* Brand header at top of sidebar */
[data-testid="stSidebar"] > div:first-child::before {
    content: "⚡ Electronic Optimizer";
    display: block;
    font-size: 0.95rem;
    font-weight: 700;
    color: #0f172a;
    padding: 20px 20px 14px;
    letter-spacing: -0.02em;
    border-bottom: 1px solid #f1f5f9;
    margin-bottom: 12px;
    font-family: 'Inter', sans-serif;
}

/* Sidebar Nav */
[data-testid="stSidebarNav"] {
    padding: 0 !important;
}

[data-testid="stSidebarNav"]::before {
    content: "NAVIGASI UTAMA";
    display: block;
    font-size: 0.68rem;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.08em;
    padding: 0 20px 8px;
    text-transform: uppercase;
}

[data-testid="stSidebarNav"] a {
    display: flex !important;
    align-items: center !important;
    padding: 8px 14px !important;
    margin: 3px 10px !important;
    border-radius: 8px !important;
    color: #334155 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: all 0.15s ease !important;
    background: transparent !important;
    border-left: 3px solid transparent !important;
}

[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p {
    color: inherit !important;
    font-weight: inherit !important;
}

[data-testid="stSidebarNav"] a:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border-left: 3px solid #2563eb !important;
    font-weight: 600 !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] span,
[data-testid="stSidebarNav"] a[aria-current="page"] p {
    color: #1d4ed8 !important;
    font-weight: 600 !important;
}

/* Replace "app" label with "🏠 Beranda" */
[data-testid="stSidebarNav"] ul > li:first-child a p {
    font-size: 0 !important;
    color: transparent !important;
    position: relative !important;
    line-height: 1.4 !important;
}
[data-testid="stSidebarNav"] ul > li:first-child a p::before {
    content: "🏠 Beranda";
    font-size: 0.88rem !important;
    color: inherit;
    position: absolute;
    left: 0;
    top: 0;
    white-space: nowrap;
}

/* Sidebar collapse button color */
[data-testid="stSidebarCollapseButton"] button {
    color: #475569 !important;
}

/* ══════════════════════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════════════════════ */
h1 {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: #0f172a !important;
    margin-bottom: 0.35rem !important;
}
h2 {
    font-size: 1.18rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.5rem;
    margin-top: 2rem !important;
}
h3 {
    font-size: 0.98rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
}
p {
    color: #475569 !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
}

/* ══════════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 1.1rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.15s ease;
}
[data-testid="metric-container"]:hover {
    border-color: #93c5fd !important;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.08) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #64748b !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.02em !important;
}

/* ══════════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════════ */
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.25rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"],
.stButton > button:not([kind]) {
    background: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #2563eb !important;
    box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button:not([kind]):hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3) !important;
}
.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
}

/* ══════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════ */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #e2e8f0 !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-baseweb="tab"] {
    padding: 10px 20px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #64748b !important;
    background: transparent !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    transition: color 0.15s ease !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #2563eb !important;
    font-weight: 600 !important;
    border-bottom-color: #2563eb !important;
}
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] { display: none !important; }

/* ══════════════════════════════════════════════════════
   INPUTS & SELECTBOXES
══════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border-color: #cbd5e1 !important;
    background: #ffffff !important;
    color: #0f172a !important;
    font-size: 0.88rem !important;
}

/* ══════════════════════════════════════════════════════
   ALERTS / CALLOUTS
══════════════════════════════════════════════════════ */
[data-testid="stInfo"] {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 8px !important;
    color: #1e40af !important;
}
[data-testid="stSuccess"] {
    background: #f0fdf4 !important;
    border: 1px solid #bbf7d0 !important;
    border-radius: 8px !important;
    color: #166534 !important;
}
[data-testid="stWarning"] {
    background: #fffbeb !important;
    border: 1px solid #fde68a !important;
    border-radius: 8px !important;
    color: #92400e !important;
}
[data-testid="stError"] {
    background: #fef2f2 !important;
    border: 1px solid #fecaca !important;
    border-radius: 8px !important;
    color: #991b1b !important;
}

/* ══════════════════════════════════════════════════════
   CONTAINERS & TABLES
══════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    background: #ffffff !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #0f172a !important;
}

hr {
    border: none !important;
    border-top: 1px solid #e2e8f0 !important;
    margin: 1.5rem 0 !important;
}

/* Step cards on homepage */
.step-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    transition: all 0.15s ease;
}
.step-card:hover {
    border-color: #93c5fd;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.08);
}
.step-num {
    font-size: 0.68rem;
    font-weight: 700;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.step-title {
    font-weight: 700;
    color: #0f172a;
    margin: 4px 0 2px;
    font-size: 0.92rem;
}
.step-desc {
    color: #64748b;
    font-size: 0.82rem;
    line-height: 1.5;
    margin: 0;
}
"""

def inject_css():
    """Inject clean & high-contrast design system."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
