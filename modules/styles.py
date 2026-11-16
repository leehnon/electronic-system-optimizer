"""
modules/styles.py
Shared design system untuk ElectronicSystem Parameter Optimizer.
Import di setiap halaman: from modules.styles import inject_css; inject_css()
"""
import streamlit as st

GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"

CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="{GOOGLE_FONTS}">
<style>

/* ══════════════════════════════════════════════════════
   APP SHELL
══════════════════════════════════════════════════════ */
html, body, [data-testid="stApp"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background-color: #f6f8fa !important;
    color: #1c2128 !important;
}}

.block-container {{
    padding: 2.25rem 3rem 5rem !important;
    max-width: 1140px !important;
}}

/* ══════════════════════════════════════════════════════
   SIDEBAR — Dark Professional
══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: #0d1117 !important;
    border-right: 1px solid #21262d !important;
}}

/* Brand header pseudo-element */
[data-testid="stSidebar"] > div:first-child::before {{
    content: "⚡  ESPOptimizer";
    display: block;
    font-size: 0.9rem;
    font-weight: 700;
    color: #e6edf3;
    padding: 22px 20px 14px;
    letter-spacing: -0.01em;
    border-bottom: 1px solid #21262d;
    margin-bottom: 10px;
    font-family: 'Inter', sans-serif;
}}

/* Nav wrapper */
[data-testid="stSidebarNav"] {{
    padding: 2px 0 !important;
}}

/* Nav links */
[data-testid="stSidebarNav"] a {{
    display: flex !important;
    align-items: center !important;
    padding: 7px 16px !important;
    margin: 2px 8px !important;
    border-radius: 6px !important;
    color: #8b949e !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: background 0.1s ease, color 0.1s ease !important;
    background: transparent !important;
    border-left: 2px solid transparent !important;
}}

[data-testid="stSidebarNav"] a:hover {{
    background: #161b22 !important;
    color: #cdd9e5 !important;
}}

[data-testid="stSidebarNav"] a[aria-current="page"] {{
    background: rgba(31,111,235,0.12) !important;
    color: #58a6ff !important;
    border-left: 2px solid #1f6feb !important;
    padding-left: 14px !important;
}}

/* Rename "app" → "Beranda" via CSS trick */
[data-testid="stSidebarNav"] ul > li:first-child a p {{
    font-size: 0 !important;
    color: transparent !important;
    position: relative !important;
    line-height: 1.4 !important;
}}
[data-testid="stSidebarNav"] ul > li:first-child a p::before {{
    content: "🏠  Beranda";
    font-size: 0.84rem !important;
    color: inherit;
    position: absolute;
    left: 0;
    top: 0;
    white-space: nowrap;
}}

/* Sidebar section label */
[data-testid="stSidebarNav"]::before {{
    content: "MENU";
    display: block;
    font-size: 0.65rem;
    font-weight: 700;
    color: #484f58;
    letter-spacing: 0.1em;
    padding: 0 20px 6px;
    text-transform: uppercase;
}}


/* ══════════════════════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════════════════════ */
h1 {{
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: #1c2128 !important;
    margin-bottom: 0.25rem !important;
}}
h2 {{
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #1c2128 !important;
    border-bottom: 1px solid #d0d7de;
    padding-bottom: 0.5rem;
    margin-top: 2rem !important;
}}
h3 {{
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #1c2128 !important;
}}
p {{
    color: #57606a !important;
    font-size: 0.875rem !important;
    line-height: 1.6 !important;
}}

/* ══════════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════════ */
[data-testid="metric-container"] {{
    background: white !important;
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    padding: 1.1rem 1.25rem !important;
    transition: border-color 0.15s;
}}
[data-testid="metric-container"]:hover {{
    border-color: #1f6feb !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #57606a !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: #1c2128 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.02em !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.75rem !important;
    font-weight: 500 !important;
}}

/* ══════════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════════ */
.stButton > button {{
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.1rem !important;
    transition: all 0.12s ease !important;
    border: 1px solid transparent !important;
}}
.stButton > button[kind="primary"],
.stButton > button:not([kind]) {{
    background: #1f6feb !important;
    color: white !important;
    border-color: #1f6feb !important;
}}
.stButton > button[kind="primary"]:hover,
.stButton > button:not([kind]):hover {{
    background: #1a5fc8 !important;
    border-color: #1a5fc8 !important;
}}
.stButton > button[kind="secondary"] {{
    background: white !important;
    color: #1c2128 !important;
    border-color: #d0d7de !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background: #f6f8fa !important;
    border-color: #8c959f !important;
}}

/* ══════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════ */
[data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid #d0d7de !important;
    gap: 0 !important;
    padding: 0 !important;
}}
[data-baseweb="tab"] {{
    padding: 9px 18px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #57606a !important;
    background: transparent !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    color: #1c2128 !important;
    font-weight: 600 !important;
    border-bottom-color: #1f6feb !important;
}}
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {{
    display: none !important;
}}

/* ══════════════════════════════════════════════════════
   FORM INPUTS
══════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {{
    border-radius: 6px !important;
    border-color: #d0d7de !important;
    font-size: 0.875rem !important;
    background: white !important;
}}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {{
    border-color: #1f6feb !important;
    box-shadow: 0 0 0 3px rgba(31,111,235,0.1) !important;
}}
.stSlider [data-testid="stThumbValue"] {{
    font-size: 0.75rem !important;
}}

/* ══════════════════════════════════════════════════════
   ALERTS / CALLOUTS
══════════════════════════════════════════════════════ */
[data-testid="stInfo"] {{
    background: #ddf4ff !important;
    border: 1px solid #54aeff60 !important;
    border-radius: 6px !important;
    color: #0550ae !important;
    font-size: 0.875rem !important;
}}
[data-testid="stSuccess"] {{
    background: #dafbe1 !important;
    border: 1px solid #4ac26b60 !important;
    border-radius: 6px !important;
    color: #1a7f37 !important;
    font-size: 0.875rem !important;
}}
[data-testid="stWarning"] {{
    background: #fff8c5 !important;
    border: 1px solid #d4a72c60 !important;
    border-radius: 6px !important;
    color: #7d4e00 !important;
    font-size: 0.875rem !important;
}}
[data-testid="stError"] {{
    background: #ffebe9 !important;
    border: 1px solid #ff818260 !important;
    border-radius: 6px !important;
    color: #82071e !important;
    font-size: 0.875rem !important;
}}

/* ══════════════════════════════════════════════════════
   DATAFRAME / TABLE
══════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}}

/* ══════════════════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════════════════ */
[data-testid="stExpander"] {{
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    background: white !important;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #1c2128 !important;
}}

/* ══════════════════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════════════════ */
hr {{
    border: none !important;
    border-top: 1px solid #d0d7de !important;
    margin: 1.5rem 0 !important;
}}

/* ══════════════════════════════════════════════════════
   CODE
══════════════════════════════════════════════════════ */
code {{
    font-family: 'JetBrains Mono', 'Consolas', monospace !important;
    font-size: 0.78rem !important;
    background: #f6f8fa !important;
    border: 1px solid #d0d7de !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
    color: #0550ae !important;
}}
pre {{
    background: #f6f8fa !important;
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    padding: 1rem 1.25rem !important;
}}
pre code {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    color: #1c2128 !important;
    font-size: 0.82rem !important;
}}

/* ══════════════════════════════════════════════════════
   CAPTION / FOOTER
══════════════════════════════════════════════════════ */
[data-testid="stCaptionContainer"] {{
    color: #8c959f !important;
    font-size: 0.75rem !important;
}}

/* ══════════════════════════════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════════════════════════════ */

/* Step card */
.step-card {{
    background: white;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.15s, box-shadow 0.15s;
}}
.step-card:hover {{
    border-color: #1f6feb;
    box-shadow: 0 1px 8px rgba(31,111,235,0.1);
}}
.step-num {{
    font-size: 0.65rem;
    font-weight: 700;
    color: #8c959f;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.step-title {{
    font-weight: 700;
    color: #1c2128;
    margin: 4px 0 2px;
    font-size: 0.9rem;
}}
.step-desc {{
    color: #57606a;
    font-size: 0.8rem;
    line-height: 1.5;
    margin: 0;
}}

/* Info chip */
.chip {{
    display: inline-block;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #57606a;
    margin: 2px;
}}
.chip-blue {{
    background: #ddf4ff;
    border-color: #54aeff60;
    color: #0969da;
}}
.chip-green {{
    background: #dafbe1;
    border-color: #4ac26b60;
    color: #1a7f37;
}}

/* ══════════════════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: #d0d7de; border-radius: 10px; }}
::-webkit-scrollbar-thumb:hover {{ background: #8c959f; }}

</style>
"""


def inject_css():
    """Inject design system CSS ke halaman Streamlit saat ini."""
    st.markdown(CSS, unsafe_allow_html=True)
