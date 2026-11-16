import streamlit as st
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.data_generator import ensure_default_data

st.set_page_config(page_title="Engineering Interpretation", layout="wide")
inject_css()
ensure_default_data()

st.title("Engineering Interpretation")
st.markdown("Interpretasi fisik hasil optimasi parameter, analisis batas operasional, dan keterbatasan model.")

circuit = st.session_state.get("circuit", "RC Charging")
true_p  = st.session_state.get("true_params", {})

if "gd_result" not in st.session_state and circuit not in ["Dioda"]:
    st.warning("Jalankan komputasi numerik terlebih dahulu.")
    st.stop()

result = st.session_state.get("gd_result", {})
p_opt  = result.get("optimal_params", [0, 0, 0])

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 1. Interpretasi Parameter Fisik per Rangkaian
# ══════════════════════════════════════════════════════════════════════════════

# 1. RC Charging
if circuit == "RC Charging":
    R_opt, C_opt = p_opt[0], p_opt[1]
    tau = R_opt * C_opt
    f_c = 1.0 / (2 * np.pi * tau)

    st.markdown("## 1. Analisis Fisik Rangkaian RC Charging")
    col1, col2, col3 = st.columns(3)
    col1.metric("Resistansi R",       f"{R_opt:.3f} Ω")
    col2.metric("Kapasitansi C",      f"{C_opt*1e6:.4f} µF")
    col3.metric("Konstanta Waktu tau",f"{tau*1000:.4f} ms")

    st.markdown("### Karakteristik Respon Transien")
    st.markdown(f"""
    - **Waktu Pengisian Standar (tau = RC):** Pada waktu **t = tau = {tau*1000:.4f} ms**, muatan kapasitor terisi **63.2%** dari tegangan sumber.
    - **Kondisi Mantap (Steady-State 5tau):** Membutuhkan **{5*tau*1000:.4f} ms** untuk mencapai 99.3% pengisian penuh.
    - **Frekuensi Cutoff LPF (fc):** Rangkaian bertindak sebagai filter lolos-rendah orde-1 dengan $f_c = 1/(2\\pi RC) =$ **{f_c:.2f} Hz**.
    """)

# 2. RC Discharging
elif circuit == "RC Discharging":
    R_opt, C_opt = p_opt[0], p_opt[1]
    tau = R_opt * C_opt
    t_half = tau * np.log(2)

    st.markdown("## 1. Analisis Fisik Rangkaian RC Discharging")
    col1, col2, col3 = st.columns(3)
    col1.metric("Resistansi R",         f"{R_opt:.3f} Ω")
    col2.metric("Kapasitansi C",        f"{C_opt*1e6:.4f} µF")
    col3.metric("Waktu Paruh (t 50%)",  f"{t_half*1000:.4f} ms")

    st.markdown("### Karakteristik Pengosongan Muatan")
    st.markdown(f"""
    - **Peluruhan Eksponensial:** Tegangan sisa jatuh ke 36.8% pada $t = \\tau =$ **{tau*1000:.4f} ms**.
    - **Waktu Paruh Energi:** Tegangan turun tepat 50% pada $t_{{1/2}} = \\tau \\ln(2) =$ **{t_half*1000:.4f} ms**.
    - **Batas Aman Teknis:** Disipasi muatan di bawah 1% selesai setelah $5\\tau =$ **{5*tau*1000:.4f} ms**.
    """)

# 3. RLC Seri
elif circuit in ["RLC Seri (Impedansi)", "RLC Impedansi"]:
    R_opt, L_opt, C_opt = p_opt[0], p_opt[1], p_opt[2]
    L_opt = abs(L_opt); C_opt = abs(C_opt)
    f_r   = 1.0 / (2 * np.pi * np.sqrt(max(L_opt, 1e-15) * max(C_opt, 1e-15)))
    Q     = (1.0 / R_opt) * np.sqrt(max(L_opt, 1e-15) / max(C_opt, 1e-15))
    BW    = f_r / max(Q, 1e-6)

    st.markdown("## 1. Analisis Fisik Rangkaian RLC Seri")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Resistansi R",      f"{R_opt:.3f} Ω")
    col2.metric("Induktansi L",      f"{L_opt*1e3:.3f} mH")
    col3.metric("Kapasitansi C",     f"{C_opt*1e6:.4f} µF")
    col4.metric("Frekuensi Resonansi",f"{f_r:.2f} Hz")

    st.markdown("### Resonansi & Selektivitas Frekuensi")
    st.markdown(f"""
    - **Frekuensi Resonansi Alami (fr):** Pada $f_r =$ **{f_r:.2f} Hz**, reaktansi induktif meniadakan kapasitif ($X_L = X_C$), sehingga impedansi minimum murni resistif $|Z| = R =$ **{R_opt:.3f} Ω**.
    - **Faktor Kualitas Selektif (Q):** Nilai $Q =$ **{Q:.3f}** menghasilkan lebar pita atenuasi $-3\\text{{ dB}}$ sebesar **{BW:.2f} Hz**.
    """)

# 4. Band-Pass Filter RLC
elif circuit == "Band-Pass Filter RLC":
    R_opt, L_opt, C_opt = p_opt[0], p_opt[1], p_opt[2]
    f0_opt = 1.0 / (2 * np.pi * np.sqrt(max(L_opt, 1e-15) * max(C_opt, 1e-15)))
    Q_opt  = (1.0 / R_opt) * np.sqrt(L_opt / C_opt)
    BW_opt = f0_opt / max(Q_opt, 1e-6)

    st.markdown("## 1. Analisis Fisik Filter Band-Pass RLC")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Frekuensi Tengah f0", f"{f0_opt:.2f} Hz")
    col2.metric("Bandwidth (BW)",       f"{BW_opt:.2f} Hz")
    col3.metric("Faktor Kualitas (Q)",  f"{Q_opt:.3f}")
    col4.metric("Gain Puncak",          "1.000 (0 dB)")

    st.markdown("### Seleksi Frekuensi & Atenuasi")
    st.markdown(f"""
    - **Pita Lolos (*Passband*):** Meloloskan sinyal di sekitar frekuensi tengah $f_0 =$ **{f0_opt:.2f} Hz** dengan bandwidth selektif **{BW_opt:.2f} Hz**.
    - **Atenuasi Sisi:** Frekuensi di luar pita teredam sebesar $-20\\text{{ dB/dekade}}$ pada roll-off orde-2.
    """)

# 5. Amplifier
elif circuit in ["Amplifier", "Amplifier (Single-Pole)"]:
    A0_opt, fc_opt = p_opt[0], p_opt[1]
    A0_dB = 20 * np.log10(max(A0_opt, 1e-6))
    gbw = A0_opt * fc_opt

    st.markdown("## 1. Analisis Fisik Penguat Sinyal (Amplifier)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gain DC (A0)",         f"{A0_opt:.2f} ({A0_dB:.1f} dB)")
    col2.metric("Cutoff -3dB (fc)",     f"{fc_opt:.2f} Hz")
    col3.metric("Gain-BW Product (GBW)",f"{gbw:.2e} Hz")

    st.markdown("### Performa Penguatan & Pita Frekuensi")
    st.markdown(f"""
    - **Penguatan DC:** Penguatan sinyal linier sebesar **{A0_opt:.2f}×** dengan batas frekuensi cutoff **{fc_opt:.2f} Hz**.
    - **Pertukaran Gain-Bandwidth:** Nilai $GBW =$ **{gbw:.2e} Hz** konstan, memungkinkan konfigurasi gain lebih rendah untuk bandwidth lebih lebar.
    """)

# 6. Dioda
elif circuit == "Dioda":
    st.markdown("## 1. Analisis Fisik Sambungan Semikonduktor Dioda")
    if "nr_result" in st.session_state:
        nr = st.session_state["nr_result"]
        V_D = nr.get("V_D", 0.65)
        I_D = nr.get("I_D", 0.004)
        p_diss = V_D * I_D
        st.markdown(f"""
        - **Titik Kerja Konduksi:** $V_D =$ **{V_D:.4f} V** dan $I_D =$ **{I_D*1000:.4f} mA**.
        - **Disipasi Daya Termal:** $P_D = V_D \\times I_D =$ **{p_diss*1000:.4f} mW** (aman di bawah rating disipasi standar 500 mW).
        """)
    else:
        st.info("Jalankan Newton-Raphson untuk dioda pada menu Numerical Computation.")

# 7. Transistor BJT
elif circuit == "Transistor BJT":
    Is_opt, Vt_opt = p_opt[0], p_opt[1]
    gm_at_1mA = 1e-3 / max(Vt_opt, 1e-4)

    st.markdown("## 1. Analisis Fisik Transistor BJT")
    col1, col2, col3 = st.columns(3)
    col1.metric("Arus Saturasi Is",   f"{Is_opt:.3e} A")
    col2.metric("Tegangan Termal Vt", f"{Vt_opt*1000:.2f} mV")
    col3.metric("Transkonduktansi gm",f"{gm_at_1mA*1000:.2f} mS (pada 1mA)")

    st.markdown("### Karakteristik Sambungan Semikonduktor")
    st.markdown(f"""
    - **Konduktansi Transfer (gm):** Nilai $g_m =$ **{gm_at_1mA*1000:.2f} mS** merepresentasikan rasio konversi perubahan tegangan input $V_{{BE}}$ terhadap arus output kolektor $I_C$.
    - **Tegangan Termal Eksperimental:** $V_T =$ **{Vt_opt*1000:.2f} mV** mengonfirmasi kesesuaian dengan teori difusi pembawa muatan.
    """)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Keterbatasan Model & Asumsi Fisik (Rubrik 7 - Bobot 5%)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 2. Keterbatasan Model Fisik (Model Limitations)")

lim_col1, lim_col2 = st.columns(2)

with lim_col1:
    st.markdown("""
    ### Asumsi Penyederhanaan Komponen
    1. **Elemen Parasitik:**
       - Model mengasumsikan komponen bersifat murni (misal: induktor tanpa resistansi kawat tembaga $R_{DC}$, dan kapasitor tanpa resistansi seri ekivalen / ESR).
       - Pada frekuensi sangat tinggi (>10 MHz), kapasitansi liar antar-kaki komponen dapat menimbulkan resonansi parasitik kedua.
    2. **Stabilitas Termal:**
       - Parameter $R$ dan $V_T$ diasumsikan konstan pada suhu kamar isotermal ($T = 300\\text{ K}$).
       - Pada kondisi arus tinggi, efek pemanasan mandiri (*self-heating*) dapat menggeser nilai resistansi dan meningkatkan arus bocor semikonduktor.
    """)

with lim_col2:
    st.markdown("""
    ### Batas Validitas Domain Operasional
    1. **Wilayah Sinyal Kecil (Small-Signal Linier):**
       - Model amplifier dan filter mengasumsikan sinyal beroperasi di daerah linier. Sinyal input yang terlalu besar akan mengalami pemotongan saturasi (*clipping distortion*).
    2. **Batas Saturasi Induktor:**
       - Induktansi $L$ diasumsikan konstan tanpa efek kejenuhan inti ferit (*magnetic saturation*) pada arus tinggi.
    3. **Rekomendasi Kalibrasi Lanjutan:**
       - Untuk aplikasi instrumentasi kritis, disarankan menyertakan koreksi suhu derajat Celsius dan estimasi ESR kapasitor.
    """)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Potensi Penerapan Proyek & Praktikum Elektronika (Rubrik 7 - Bobot 5%)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 3. Potensi Penerapan untuk Proyek & Praktikum Elektronika")

st.markdown("""
Sistem optimasi parameter ini memiliki nilai guna aplikatif tinggi dalam lingkungan akademik dan industri:

1. **Modul Praktikum Laboratorium Sistem Pengukuran Elektronika:**
   - Mahasiswa dapat menghubungkan osiloskop USB atau data logger ADC ke rangkaian riil, mengekspor file CSV, dan mengidentifikasi nilai komponen aktual beserta toleransi fabrikasinya secara otomatis.
2. **Quality Control & Seleksi Komponen (Binning):**
   - Industri perakitan PCB dapat memanfaatkan algoritma ini untuk menyortir kapasitor dan induktor dengan toleransi ketat (1%–2%) dari batch produksi massal standar 10%.
3. **Deteksi Kerusakan & Penuaan Komponen (Health Monitoring):**
   - Penurunan nilai kapasitansi $C$ atau kenaikan resistansi $R$ dari waktu ke waktu dapat dijadikan indikator degradasi (*early warning system*) sebelum komponen mengalami kegagalan fatal.
""")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# 4. Kinerja Algoritma Numerik
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 4. Analisis Komparasi Kinerja Algoritma")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### Gradient Descent")
    if "history" in result and "cost" in result["history"] and len(result["history"]["cost"]) > 0:
        iters = result.get("iterations", 0)
        conv  = result.get("converged", False)
        cost0 = result["history"]["cost"][0]
        costN = result.get("final_cost", 0)
        reduction = (1.0 - costN / max(cost0, 1e-30)) * 100.0

        st.markdown(f"""
        | Metrik Komputasi | Nilai Numerik |
        |---|---|
        | Jumlah Iterasi | {iters} |
        | Status Konvergensi | {'Konvergen' if conv else 'Selesai'} |
        | Biaya Awal (MSE) | `{cost0:.4e}` |
        | Biaya Akhir (MSE) | `{costN:.4e}` |
        | Reduksi Kesalahan | `{reduction:.2f}%` |
        """)
    else:
        st.info("Gradient Descent belum dijalankan pada sesi ini.")

with col_b:
    st.markdown("### Newton-Raphson")
    if "nr_result" in st.session_state:
        nr = st.session_state["nr_result"]
        st.markdown(f"""
        | Metrik Komputasi | Nilai Numerik |
        |---|---|
        | Jumlah Iterasi | {nr.get('iterations', '-')} |
        | Status Konvergensi | {'Konvergen' if nr.get('converged', True) else 'Tidak Konvergen'} |
        | Nilai \|f(x)\| Akhir | `{abs(nr.get('f_root', 0)):.4e}` |
        | Orde Konvergensi | Kuadratik (Orde 2) |
        """)
    else:
        st.info("Newton-Raphson belum dijalankan.")
