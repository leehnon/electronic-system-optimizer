import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.styles import inject_css

st.set_page_config(
    page_title="ElectronicSystem Parameter Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ── Page Header ───────────────────────────────────────────────────────────────
st.title("ElectronicSystem Parameter Optimizer")
st.markdown(
    "Optimasi parameter prototipe elektronika menggunakan metode numerik "
    "**Gradient Descent** dan **Newton-Raphson** — dari data simulasi maupun pengukuran riil."
)

st.divider()

# ── Stat Row ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Metode Numerik",    "GD + NR")
c2.metric("Studi Kasus",       "4 Rangkaian")
c3.metric("Metrik Validasi",   "MSE · RMSE · R²")
c4.metric("Format Output",     "TXT · CSV")

st.markdown("## Tentang Sistem")

col_l, col_r = st.columns([3, 2], gap="large")

with col_l:
    st.markdown("""
    Dashboard ini membantu **identifikasi dan optimasi parameter** komponen elektronika 
    dari data pengukuran atau simulasi. Cocok digunakan untuk:
    """)

    rows = [
        ("🔧", "Karakterisasi Komponen",    "Estimasi nilai R, L, C, A₀, f_c dari data terukur"),
        ("📐", "Fitting Kurva",             "Cocokkan model matematis dengan data eksperimen"),
        ("🔁", "Analisis Frekuensi",        "Temukan frekuensi resonansi RLC dan bandwidth amplifier"),
        ("🔴", "Titik Operasi Nonlinear",   "Solusi numerik rangkaian dioda dan transistor"),
    ]
    for icon, title, desc in rows:
        st.markdown(f"""
        <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;">
            <span style="font-size:1.1rem;margin-top:1px;">{icon}</span>
            <div>
                <span style="font-weight:600;color:#1c2128;font-size:0.875rem;">{title}</span><br>
                <span style="color:#57606a;font-size:0.82rem;">{desc}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_r:
    st.markdown("""
    <div style="background:white;border:1px solid #d0d7de;border-radius:8px;padding:20px 24px;">
        <p style="font-size:0.72rem;font-weight:700;color:#57606a;text-transform:uppercase;
                  letter-spacing:0.08em;margin:0 0 12px;">Stack Teknis</p>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#1c2128;
                    line-height:2;margin:0;">
            Python 3.x<br>
            Streamlit<br>
            NumPy &nbsp;/&nbsp; SciPy<br>
            Plotly<br>
            Pandas
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## Alur Kerja")

steps = [
    ("01", "Data Management",         "Generate atau upload data pengukuran rangkaian elektronika"),
    ("02", "Numerical Computation",   "Jalankan Gradient Descent dan Newton-Raphson"),
    ("03", "Visualization",           "Analisis grafik fitting, konvergensi, dan residual"),
    ("04", "Evaluation",              "Validasi hasil: MSE, R², MAPE, dan sensitivitas parameter"),
    ("05", "Engineering Interp.",     "Interpretasi makna teknik dari parameter yang ditemukan"),
    ("06", "Report",                  "Ekspor hasil optimasi ke file TXT atau CSV"),
]

cols = st.columns(3, gap="small")
for i, (num, title, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="step-card">
            <p class="step-num">Langkah {num}</p>
            <p class="step-title">{title}</p>
            <p class="step-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Rangkaian yang Didukung ────────────────────────────────────────────────────
st.markdown("## Rangkaian yang Didukung")

rc_col, rlc_col, amp_col, diode_col = st.columns(4, gap="small")

circuits = [
    (rc_col,    "#0969da", "RC",        "Charging",     "Parameter: R, C, τ",         "V(t) = Vᵢₙ·(1−e⁻ᵗ/τ)"),
    (rlc_col,   "#1a7f37", "RLC",       "Impedansi",    "Parameter: R, L, C, f_r",    "|Z(f)| vs frekuensi"),
    (amp_col,   "#7d4e00", "Amplifier", "Single-Pole",  "Parameter: A₀, f_cutoff",    "G(f) = A₀/√(1+(f/fc)²)"),
    (diode_col, "#82071e", "Dioda",     "Karakteristik","Parameter: V_D, I_D",         "Model Shockley"),
]

for col, color, ctype, csub, params, formula in circuits:
    with col:
        st.markdown(f"""
        <div style="background:white;border:1px solid #d0d7de;border-radius:8px;
                    padding:16px;text-align:center;height:100%;">
            <div style="width:36px;height:36px;border-radius:8px;background:{color}18;
                        display:flex;align-items:center;justify-content:center;
                        margin:0 auto 10px;border:1px solid {color}40;">
                <span style="font-size:0.75rem;font-weight:700;color:{color};">{ctype}</span>
            </div>
            <p style="font-weight:700;color:#1c2128;font-size:0.9rem;margin:0 0 2px;">{ctype}</p>
            <p style="color:#57606a;font-size:0.75rem;margin:0 0 10px;">{csub}</p>
            <p style="font-size:0.72rem;color:#57606a;margin:0 0 4px;">{params}</p>
            <code style="font-size:0.68rem;color:{color};">{formula}</code>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("ElectronicSystem Parameter Optimizer · Pengujian & Diagnostik")
