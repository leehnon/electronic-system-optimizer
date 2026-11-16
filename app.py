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

# ── Header Aplikasi ────────────────────────────────────────────────────────────
st.title("ElectronicSystem Parameter Optimizer")
st.markdown(
    "Sistem Komputasi Numerik untuk Identifikasi, Optimasi Parameter, dan Diagnostik "
    "Rangkaian Elektronika Berbasis **Gradient Descent** dan **Newton-Raphson**."
)

st.divider()

# ── Metrik Utama Sistem ───────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Metode Numerik",    "GD + NR (Scratch)")
c2.metric("Studi Kasus",       "7 Rangkaian")
c3.metric("Metrik Validasi",   "MSE · RMSE · R² · MAPE")
c4.metric("Format Dokumen",    "TXT · CSV · Trace Log")

st.markdown("---")

# ── Bagian 1: Perumusan Masalah & Relevansi Elektronika (Rubrik 1 - Bobot 10%) ──
st.markdown("## 1. Perumusan Masalah dan Relevansi Sistem Elektronika")

col_prob_l, col_prob_r = st.columns([3, 2], gap="large")

with col_prob_l:
    st.markdown("""
    ### Latar Belakang & Rumusan Masalah
    Pada praktikum dan industri elektronika, nilai komponen riil (resistor, induktor, kapasitor, 
    dan semikonduktor) sering kali mengalami deviasi dari label nominal akibat **toleransi fabrikasi (5%–20%)**, 
    pengaruh suhu operasional, dan penuaan komponen. 

    Pengukuran langsung sering kali terdistorsi oleh noise instrumen dan kapasitansi kabel ukur. 
    Oleh karena itu, diperlukan **metode numerik deterministik** untuk merekonstruksi nilai parameter 
    komponen fisik yang sebenarnya dari data respon transien maupun frekuensi yang diamati.
    
    ### Tujuan Optimasi
    1. Mengestimasi parameter fisik ($R, L, C, A_0, f_c, I_s, V_T$) secara presisi dari kurva respon eksperimental.
    2. Menghitung titik kerja nonlinear (*Q-point*) dan frekuensi batas resonansi/cutoff secara eksak.
    3. Memberikan validasi akurasi kuantitatif berbasis metrik statistik standar industri ($R^2 > 0.95$).
    """)

with col_prob_r:
    st.markdown("""
    <div style="background:white;border:1px solid #d0d7de;border-radius:8px;padding:20px 24px;">
        <p style="font-size:0.75rem;font-weight:700;color:#0f172a;text-transform:uppercase;
                  letter-spacing:0.06em;margin:0 0 10px;">Batas Operasi & Asumsi Model</p>
        <ul style="font-size:0.82rem;color:#475569;margin:0;padding-left:18px;line-height:1.7;">
            <li><b>Suhu Lingkungan:</b> T = 300 K (Tegangan termal VT ≈ 25.85–26 mV).</li>
            <li><b>Domain Sinyal:</b> Sinyal kecil (small-signal) linier untuk rangkaian filter dan amplifier.</li>
            <li><b>Resistansi Parasitik:</b> Kapasitor dan induktor dimodelkan ideal (ESR rendah).</li>
            <li><b>Batas Frekuensi:</b> 10 Hz hingga 1 MHz (menghindari efek parasitik frekuensi ultra-tinggi).</li>
            <li><b>Batas Daya:</b> Beroperasi di bawah batas disipasi termal komponen.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Bagian 2: Model Matematika & Alasan Pemilihan Metode (Rubrik 2 - Bobot 15%) ─
st.markdown("## 2. Pemilihan Metode Numerik dan Kesesuaian Masalah")

col_m1, col_m2 = st.columns(2, gap="medium")

with col_m1:
    st.markdown("""
    <div style="background:white;border:1px solid #d0d7de;border-radius:8px;padding:18px 22px;height:100%;">
        <span style="font-size:0.75rem;font-weight:700;color:#2563eb;text-transform:uppercase;">Metode 1: Optimasi Multivariat</span>
        <h3 style="margin:6px 0 10px;color:#0f172a;">Gradient Descent (First-Order Optimization)</h3>
        <p style="font-size:0.83rem;color:#475569;line-height:1.6;">
            <b>Alasan Pemilihan:</b> Sangat sesuai untuk estimasi parameter kontinu simultan 
            (seperti R dan C sekaligus, atau R, L, dan C bersamaan) pada data kurva terukur. 
            Algoritma meminimalkan fungsi biaya Mean Squared Error (MSE) secara stabil melalui penurunan gradien.
        </p>
        <div style="background:#f8fafc;padding:10px 14px;border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#0f172a;">
            θ(k+1) = θ(k) - α · ∇f(θ(k))
        </div>
        <p style="font-size:0.78rem;color:#64748b;margin-top:8px;">
            Gradien numerik dihitung via skema <i>Finite Differences</i> independen tanpa library solver eksternal.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
    <div style="background:white;border:1px solid #d0d7de;border-radius:8px;padding:18px 22px;height:100%;">
        <span style="font-size:0.75rem;font-weight:700;color:#16a34a;text-transform:uppercase;">Metode 2: Penyelesaian Akar Non-Linear</span>
        <h3 style="margin:6px 0 10px;color:#0f172a;">Newton-Raphson (Second-Order Convergence)</h3>
        <p style="font-size:0.83rem;color:#475569;line-height:1.6;">
            <b>Alasan Pemilihan:</b> Sangat ideal untuk persamaan rangkaian transenden yang sulit diselesaikan secara analitik tertutup, 
            seperti persamaan dioda Shockley dan penentuan titik bias tegangan basis-emitter BJT. Memiliki laju konvergensi kuadratik (orde 2).
        </p>
        <div style="background:#f8fafc;padding:10px 14px;border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#0f172a;">
            x(k+1) = x(k) - f(x(k)) / f'(x(k))
        </div>
        <p style="font-size:0.78rem;color:#64748b;margin-top:8px;">
            Menyelesaikan titik kerja dengan toleransi presisi tinggi |f(x)| < 1e-8 dalam waktu di bawah 10 iterasi.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Bagian 3: Alur Kerja Sistem ───────────────────────────────────────────────
st.markdown("## 3. Alur Kerja Sistem Komputasi")

steps = [
    ("Tahap 1", "Data Management",         "Generate data simulasi dengan noise terukur atau upload CSV hasil uji lab"),
    ("Tahap 2", "Numerical Computation",   "Jalankan algoritma GD & NR murni dengan penelusuran log iterasi langkah demi langkah"),
    ("Tahap 3", "Visualization",           "Inspeksi grafik data vs model fitted, respon frekuensi, dan residual"),
    ("Tahap 4", "Evaluation",              "Uji validitas kuantitatif: MSE, RMSE, MAE, R², MAPE, dan indeks sensitivitas ±5%"),
    ("Tahap 5", "Engineering Interp.",     "Interpretasi parameter fisik rangkaian, konstanta waktu, dan batas keterbatasan model"),
    ("Tahap 6", "Report Generation",       "Generate dan unduh laporan ilmiah komprehensif, CSV data, dan trace history numerik"),
]

cols = st.columns(3, gap="small")
for i, (num, title, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="step-card">
            <p class="step-num">{num}</p>
            <p class="step-title">{title}</p>
            <p class="step-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Bagian 4: Rangkaian yang Didukung (Rubrik 1 & 7) ───────────────────────────
st.markdown("## 4. Cakupan 7 Studi Kasus Rangkaian Elektronika")

row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4, gap="small")
circuits_row1 = [
    (row1_c1, "#0969da", "RC Charging",    "Transien Pengisian", "Variabel: R, C, tau",    "V(t) = Vin·(1-exp(-t/tau))"),
    (row1_c2, "#0284c7", "RC Discharge",   "Transien Pengosongan","Variabel: R, C, tau",    "V(t) = V0·exp(-t/tau)"),
    (row1_c3, "#1a7f37", "RLC Seri",       "Respon Frekuensi",   "Variabel: R, L, C, fr",  "|Z(f)| vs Frekuensi"),
    (row1_c4, "#7c3aed", "Band-Pass RLC",  "Filter Frekuensi",   "Variabel: f0, BW, Q",    "H(f) = R / |Z(f)|"),
]

for col, color, ctype, csub, params, formula in circuits_row1:
    with col:
        st.markdown(f"""
        <div style="background:white;border:1px solid #d0d7de;border-radius:8px;
                    padding:16px;text-align:center;height:100%;margin-bottom:10px;">
            <p style="font-weight:700;color:#1c2128;font-size:0.88rem;margin:0 0 2px;">{ctype}</p>
            <p style="color:#57606a;font-size:0.75rem;margin:0 0 8px;">{csub}</p>
            <p style="font-size:0.72rem;color:#57606a;margin:0 0 4px;">{params}</p>
            <code style="font-size:0.68rem;color:{color};">{formula}</code>
        </div>
        """, unsafe_allow_html=True)

row2_c1, row2_c2, row2_c3 = st.columns(3, gap="small")
circuits_row2 = [
    (row2_c1, "#b45309", "Amplifier",      "Single-Pole Roll-off","Variabel: A0, f_cutoff", "G(f) = A0/sqrt(1+(f/fc)²)"),
    (row2_c2, "#dc2626", "Dioda PN",       "Karakteristik I-V",   "Variabel: VD, ID, PD",    "ID = Is·(exp(VD/VT)-1)"),
    (row2_c3, "#ea580c", "Transistor BJT", "Karakteristik Transfer","Variabel: Is, VT, gm",   "IC = Is·(exp(VBE/VT)-1)"),
]

for col, color, ctype, csub, params, formula in circuits_row2:
    with col:
        st.markdown(f"""
        <div style="background:white;border:1px solid #d0d7de;border-radius:8px;
                    padding:16px;text-align:center;height:100%;">
            <p style="font-weight:700;color:#1c2128;font-size:0.88rem;margin:0 0 2px;">{ctype}</p>
            <p style="color:#57606a;font-size:0.75rem;margin:0 0 8px;">{csub}</p>
            <p style="font-size:0.72rem;color:#57606a;margin:0 0 4px;">{params}</p>
            <code style="font-size:0.68rem;color:{color};">{formula}</code>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("ElectronicSystem Parameter Optimizer · Standar Penilaian Komputasi Numerik Sistem Elektronika")
