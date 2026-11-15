import streamlit as st

st.set_page_config(
    page_title="ElectronicSystem Parameter Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #0d4f8b 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.9rem; }
    .main-header p  { color: #d0e8ff; margin: 6px 0 0; font-size: 0.95rem; }

    .info-card {
        background: #f0f6ff;
        color: #1e293b;
        border-left: 4px solid #1f77b4;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 10px 0;
    }
    .metric-card {
        background: white;
        color: #1e293b;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .metric-card h2 { color: #1f77b4; margin: 0; font-size: 1.8rem; }
    .metric-card p  { color: #475569; margin: 4px 0 0; font-size: 0.85rem; font-weight: 500; }

    /* Navigasi sidebar */
    [data-testid="stSidebarNav"] span {
        font-weight: 600;
        font-size: 0.95rem;
    }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚡ ElectronicSystem Parameter Optimizer</h1>
    <p>Sistem Optimalisasi Parameter Prototipe Elektronika</p>
</div>
""", unsafe_allow_html=True)

# ── Overview Cards ────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div class="metric-card">
        <h2>🔁</h2><p>Gradient Descent</p></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class="metric-card">
        <h2>📐</h2><p>Newton-Raphson</p></div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="metric-card">
        <h2>📊</h2><p>4 Jenis Rangkaian</p></div>""", unsafe_allow_html=True)
with col4:
    st.markdown("""<div class="metric-card">
        <h2>✅</h2><p>Validasi Numerik</p></div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Deskripsi Proyek ──────────────────────────────────────────────────────────
st.markdown("## 📋 Deskripsi Proyek")

col_l, col_r = st.columns([3, 2])
with col_l:
    st.markdown("""
    **ElectronicSystem Parameter Optimizer** adalah sistem berbasis dashboard interaktif untuk:

    - 🔧 **Mengoptimasi parameter** rangkaian elektronika (R, L, C, Gain, frekuensi cutoff)
    - 📈 **Menerapkan algoritma numerik**: Gradient Descent & Newton-Raphson
    - 🧪 **Studi kasus terapan**: RC charging, RLC impedansi, Amplifier, Dioda
    - 📉 **Visualisasi** konvergensi, residual, dan perbandingan model vs data
    - 📋 **Laporan** otomatis hasil optimasi

    > Proyek ini memenuhi persyaratan tugas mata kuliah Pengujian & Diagnostik.
    """)

with col_r:
    st.markdown("""
    <div class="info-card">
    <strong>Informasi Proyek</strong><br><br>
    🏷️ <b>Bidang:</b> Pengujian & Diagnostik<br>
    🔢 <b>Algoritma:</b> Gradient Descent, Newton-Raphson, Simulasi<br>
    📦 <b>Sumber Data:</b> Simulasi / Riil Percobaan
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Navigasi ──────────────────────────────────────────────────────────────────
st.markdown("## 🗺️ Navigasi Menu")

menu_items = [
    ("📊", "1 - Data Management",        "Kelola dan generate data rangkaian elektronika"),
    ("🔢", "2 - Numerical Computation",  "Jalankan Gradient Descent & Newton-Raphson"),
    ("📈", "3 - Visualization",          "Grafik interaktif hasil fitting & konvergensi"),
    ("✅", "4 - Evaluation",             "Hitung MSE, RMSE, R², sensitivitas parameter"),
    ("💡", "5 - Engineering Interp.",    "Interpretasi teknik hasil optimasi"),
    ("📄", "6 - Report",                 "Export laporan PDF / CSV"),
]

cols = st.columns(3)
for i, (icon, title, desc) in enumerate(menu_items):
    with cols[i % 3]:
        st.markdown(f"""
        <div style="background:#f8faff;border:1px solid #d0e0f0;border-radius:10px;
                    padding:16px;margin:8px 0;text-align:center;">
            <span style="font-size:2rem;">{icon}</span>
            <p style="font-weight:700;color:#1f77b4;margin:8px 0 4px;">{title}</p>
            <p style="color:#666;font-size:0.85rem;margin:0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<p style="text-align:center;color:#999;font-size:0.82rem;">
⚡ ElectronicSystem Parameter Optimizer
</p>
""", unsafe_allow_html=True)
