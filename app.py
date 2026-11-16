import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.styles import inject_css
from modules.data_generator import ensure_default_data

st.set_page_config(
    page_title="ElectronicSystem Parameter Optimizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()
ensure_default_data()

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
c2.metric("Studi Kasus",       "7 Rangkaian")
c3.metric("Metrik Validasi",   "MSE · RMSE · R²")
c4.metric("Format Output",     "TXT · CSV")

st.markdown("## Tentang Sistem")

col_l, col_r = st.columns([3, 2], gap="large")

with col_l:
    st.markdown("""
    Dashboard ini dirancang untuk **identifikasi dan optimasi parameter** komponen elektronika 
    dari data pengukuran atau simulasi:
    """)

    rows = [
        ("Karakterisasi Komponen",    "Estimasi nilai R, L, C, A0, fc, Is dari data terukur"),
        ("Fitting Kurva & Transien",  "Pencocokan model matematis respon transien pengisian dan pengosongan"),
        ("Analisis Respon Frekuensi", "Penentuan frekuensi resonansi RLC, bandwidth, dan faktor kualitas Q"),
        ("Titik Operasi Nonlinear",   "Solusi numerik rangkaian semikonduktor dioda dan transistor BJT"),
    ]
    for title, desc in rows:
        st.markdown(f"""
        <div style="margin-bottom:14px;border-left:3px solid #2563eb;padding-left:12px;">
            <span style="font-weight:600;color:#0f172a;font-size:0.875rem;">{title}</span><br>
            <span style="color:#57606a;font-size:0.82rem;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

with col_r:
    st.markdown("""
    <div style="background:white;border:1px solid #d0d7de;border-radius:8px;padding:20px 24px;">
        <p style="font-size:0.72rem;font-weight:700;color:#57606a;text-transform:uppercase;
                  letter-spacing:0.08em;margin:0 0 12px;">Spesifikasi Teknis</p>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#1c2128;
                    line-height:2;margin:0;">
            Python 3.x<br>
            Streamlit Framework<br>
            NumPy & SciPy Computing<br>
            Plotly Visualization Engine<br>
            Pandas Data Structures
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## Alur Kerja Sistem")

steps = [
    ("01", "Data Management",         "Generate atau upload data pengukuran rangkaian elektronika"),
    ("02", "Numerical Computation",   "Jalankan algoritma Gradient Descent dan Newton-Raphson"),
    ("03", "Visualization",           "Analisis grafik fitting model, konvergensi, dan residual"),
    ("04", "Evaluation",              "Validasi akurasi numerik: MSE, RMSE, R², MAPE, dan sensitivitas"),
    ("05", "Engineering Interp.",     "Interpretasi makna teknik dan fisik dari parameter teroptimasi"),
    ("06", "Report",                  "Ekspor laporan komputasi ke format dokumen TXT dan CSV"),
]

cols = st.columns(3, gap="small")
for i, (num, title, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="step-card">
            <p class="step-num">Tahap {num}</p>
            <p class="step-title">{title}</p>
            <p class="step-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Rangkaian yang Didukung (7 Rangkaian) ──────────────────────────────────────
st.markdown("## 7 Rangkaian Elektronika yang Didukung")

row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4, gap="small")
circuits_row1 = [
    (row1_c1, "#0969da", "RC Charging",    "Transien Pengisian", "Parameter: R, C, tau",    "V(t) = Vin·(1-exp(-t/tau))"),
    (row1_c2, "#0284c7", "RC Discharge",   "Transien Pengosongan","Parameter: R, C, tau",    "V(t) = V0·exp(-t/tau)"),
    (row1_c3, "#1a7f37", "RLC Seri",       "Respon Frekuensi",   "Parameter: R, L, C, fr",  "|Z(f)| vs Frekuensi"),
    (row1_c4, "#7c3aed", "Band-Pass RLC",  "Filter Selektif",    "Parameter: f0, BW, Q",    "H(f) = R / |Z(f)|"),
]

for col, color, ctype, csub, params, formula in circuits_row1:
    with col:
        st.markdown(f"""
        <div style="background:white;border:1px solid #d0d7de;border-radius:8px;
                    padding:16px;text-align:center;height:100%;margin-bottom:10px;">
            <p style="font-weight:700;color:#1c2128;font-size:0.88rem;margin:0 0 2px;">{ctype}</p>
            <p style="color:#57606a;font-size:0.75rem;margin:0 0 10px;">{csub}</p>
            <p style="font-size:0.72rem;color:#57606a;margin:0 0 4px;">{params}</p>
            <code style="font-size:0.68rem;color:{color};">{formula}</code>
        </div>
        """, unsafe_allow_html=True)

row2_c1, row2_c2, row2_c3 = st.columns(3, gap="small")
circuits_row2 = [
    (row2_c1, "#b45309", "Amplifier",      "Single-Pole Roll-off","Parameter: A0, f_cutoff", "G(f) = A0/sqrt(1+(f/fc)²)"),
    (row2_c2, "#dc2626", "Dioda PN",       "Karakteristik I-V",   "Parameter: VD, ID",       "ID = Is·(exp(VD/VT)-1)"),
    (row2_c3, "#ea580c", "Transistor BJT", "Karakteristik Transfer","Parameter: Is, VT, gm",  "IC = Is·(exp(VBE/VT)-1)"),
]

for col, color, ctype, csub, params, formula in circuits_row2:
    with col:
        st.markdown(f"""
        <div style="background:white;border:1px solid #d0d7de;border-radius:8px;
                    padding:16px;text-align:center;height:100%;">
            <p style="font-weight:700;color:#1c2128;font-size:0.88rem;margin:0 0 2px;">{ctype}</p>
            <p style="color:#57606a;font-size:0.75rem;margin:0 0 10px;">{csub}</p>
            <p style="font-size:0.72rem;color:#57606a;margin:0 0 4px;">{params}</p>
            <code style="font-size:0.68rem;color:{color};">{formula}</code>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("ElectronicSystem Parameter Optimizer · Pengujian & Diagnostik Sistem Elektronika")
