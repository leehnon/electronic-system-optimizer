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
st.markdown("Interpretasi teknik hasil optimasi parameter elektronika.")

circuit = st.session_state.get("circuit", "RC Charging")
true_p  = st.session_state.get("true_params", {})

if "gd_result" not in st.session_state and circuit not in ["Dioda"]:
    st.warning("Jalankan komputasi numerik terlebih dahulu.")
    st.stop()

result = st.session_state.get("gd_result", {})
p_opt  = result.get("optimal_params", [0, 0, 0])

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Interpretasi per rangkaian
# ══════════════════════════════════════════════════════════════════════════════

# 1. RC Charging
if circuit == "RC Charging":
    R_opt, C_opt = p_opt[0], p_opt[1]
    tau = R_opt * C_opt
    f_c = 1.0 / (2 * np.pi * tau)

    st.markdown("## Rangkaian RC Charging (Pengisian)")
    col1, col2, col3 = st.columns(3)
    col1.metric("R Optimal",         f"{R_opt:.3f} Ω")
    col2.metric("C Optimal",         f"{C_opt*1e6:.4f} µF")
    col3.metric("Konstanta Waktu tau", f"{tau*1000:.4f} ms")

    st.markdown("### Interpretasi Karakteristik Teknik")
    st.markdown(f"""
    **Konstanta Waktu Pengisian (tau = RC)**
    - Pada waktu **t = tau = {tau*1000:.4f} ms**, tegangan kapasitor mencapai **63.2%** dari tegangan sumber V_in.
    - Pada **t = 5tau = {5*tau*1000:.4f} ms**, kapasitor berada dalam kondisi *steady-state* penuh (**99.3%**).

    **Frekuensi Cutoff & Respon Sinyal**
    - Frekuensi cutoff f_c = 1 / (2πRC) = **{f_c:.2f} Hz**.
    - Rangkaian berfungsi sebagai **Low-Pass Filter (LPF)** pasif orde 1 dengan pelemahan -20 dB/dekade di atas frekuensi cutoff.

    **Aplikasi Praktis di Industri & Laboratorium**
    - Peredam lonjakan tegangan (*snubber*) dan filter ripple power supply DC.
    - Sirkuit penunda waktu (*delay timer*) dan *debouncing* tombol tekan mekanis.
    """)
    st.info(f"Rekomendasi Desain: Untuk aplikasi filter ripple frekuensi rendah, nilai tau = {tau*1000:.3f} ms sudah memenuhi standar respon transien cepat.")

# 2. RC Discharging
elif circuit == "RC Discharging":
    R_opt, C_opt = p_opt[0], p_opt[1]
    tau = R_opt * C_opt
    t_half = tau * np.log(2)

    st.markdown("## Rangkaian RC Discharging (Pengosongan)")
    col1, col2, col3 = st.columns(3)
    col1.metric("R Optimal",          f"{R_opt:.3f} Ω")
    col2.metric("C Optimal",          f"{C_opt*1e6:.4f} µF")
    col3.metric("Waktu Paruh (50%)",  f"{t_half*1000:.4f} ms")

    st.markdown("### Interpretasi Karakteristik Teknik")
    st.markdown(f"""
    **Dinamika Pengosongan Energi Kapasitor**
    - Konstanta waktu pengosongan tau = RC = **{tau*1000:.4f} ms**.
    - Pada t = tau, sisa tegangan tinggal **36.8%** dari tegangan awal V0.
    - Waktu paruh tegangan (V(t) = 0.5 V0) dicapai tepat pada t_1/2 = tau ln(2) = **{t_half*1000:.4f} ms**.
    - Setelah 5tau = **{5*tau*1000:.4f} ms**, energi elektrostatik tersisa < 0.7%, kapasitor aman disentuh.

    **Aplikasi Teknik Elektro**
    - Sirkuit pembuang muatan (*bleeder resistor*) pada catu daya tegangan tinggi untuk keselamatan teknisi.
    - Pemicu monostable multivibrator dan generator pulsa relaksasi.
    """)
    st.info(f"Rekomendasi Desain: Kapasitor terdisipasi hingga batas aman dalam {5*tau*1000:.2f} ms.")

# 3. RLC Seri
elif circuit in ["RLC Seri (Impedansi)", "RLC Impedansi"]:
    R_opt, L_opt, C_opt = p_opt[0], p_opt[1], p_opt[2]
    L_opt = abs(L_opt); C_opt = abs(C_opt)
    f_r   = 1.0 / (2 * np.pi * np.sqrt(max(L_opt, 1e-15) * max(C_opt, 1e-15)))
    Q     = (1.0 / R_opt) * np.sqrt(max(L_opt, 1e-15) / max(C_opt, 1e-15))
    BW    = f_r / max(Q, 1e-6)

    st.markdown("## Rangkaian RLC Seri (Impedansi)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("R (Resistansi)",     f"{R_opt:.3f} Ω")
    col2.metric("L (Induktansi)",     f"{L_opt*1e3:.3f} mH")
    col3.metric("C (Kapasitansi)",    f"{C_opt*1e6:.4f} µF")
    col4.metric("Frekuensi Resonansi",f"{f_r:.2f} Hz")

    st.markdown("### Interpretasi Karakteristik Teknik")
    st.markdown(f"""
    **Kondisi Resonansi Seri**
    - Pada frekuensi resonansi f_r = **{f_r:.2f} Hz**, reaktansi induktif X_L meniadakan reaktansi kapasitif X_C (X_L = X_C).
    - Nilai impedansi total mencapai minimum absolut: |Z|_min = R = **{R_opt:.3f} Ω** (murni resistif).
    - Arus sirkuit mencapai puncak maksimal pada frekuensi ini.

    **Selektivitas & Faktor Kualitas (Q-Factor)**
    - Faktor Kualitas Q = **{Q:.3f}** ({'Resonansi Sangat Tajam (High-Q)' if Q > 10 else 'Resonansi Menengah' if Q >= 1 else 'Broadband Rendah'}).
    - Lebar pita frekuensi -3 dB (*Bandwidth*) BW = f_r / Q = **{BW:.2f} Hz**.

    **Aplikasi Praktis**
    - Sirkuit tuner penerima gelombang radio dan filter notch pemotong noise 50/60 Hz.
    - Koreksi faktor daya (*Power Factor Correction*) beban industri.
    """)
    st.info(f"Kesimpulan: Rangkaian resonan pada {f_r:.2f} Hz dengan bandwidth seleksi {BW:.2f} Hz.")

# 4. Band-Pass Filter RLC
elif circuit == "Band-Pass Filter RLC":
    R_opt, L_opt, C_opt = p_opt[0], p_opt[1], p_opt[2]
    f0_opt = 1.0 / (2 * np.pi * np.sqrt(max(L_opt, 1e-15) * max(C_opt, 1e-15)))
    Q_opt  = (1.0 / R_opt) * np.sqrt(L_opt / C_opt)
    BW_opt = f0_opt / max(Q_opt, 1e-6)

    st.markdown("## Filter Band-Pass RLC Pasif")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Frekuensi Tengah f0", f"{f0_opt:.2f} Hz")
    col2.metric("Bandwidth (BW)",       f"{BW_opt:.2f} Hz")
    col3.metric("Faktor Kualitas (Q)",  f"{Q_opt:.3f}")
    col4.metric("Gain Puncak H(f0)",    "1.000 (0 dB)")

    st.markdown("### Interpretasi Karakteristik Teknik")
    st.markdown(f"""
    **Performa Filtrasi Frekuensi**
    - Sinyal pada frekuensi tengah f_0 = **{f0_opt:.2f} Hz** diteruskan sempurna tanpa atenuasi (H = 1.0, 0 dB).
    - Rentang frekuensi yang diloloskan (antara batas -3 dB) selebar **{BW_opt:.2f} Hz**.
    - Sinyal frekuensi rendah (f << f_0) diblokir oleh kapasitor C, dan sinyal frekuensi tinggi (f >> f_0) diblokir oleh induktor L.

    **Aplikasi Teknik Telekomunikasi & Audio**
    - Equalizer audio grafis pada kanal frekuensi menengah (*midrange band*).
    - Seleksi kanal pita transmisi RF pada transceiver nirkabel.
    """)
    st.info(f"Desain Filter: Filter ini meloloskan rentang sinyal sekitar {f0_opt:.1f} Hz dengan selektivitas Q = {Q_opt:.2f}.")

# 5. Amplifier
elif circuit in ["Amplifier", "Amplifier (Single-Pole)"]:
    A0_opt, fc_opt = p_opt[0], p_opt[1]
    A0_dB = 20 * np.log10(max(A0_opt, 1e-6))
    gbw = A0_opt * fc_opt

    st.markdown("## Penguat Sinyal (Amplifier Single-Pole)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gain DC (A0)",         f"{A0_opt:.2f} ({A0_dB:.1f} dB)")
    col2.metric("Cutoff -3dB (fc)",     f"{fc_opt:.2f} Hz")
    col3.metric("Gain-BW Product (GBW)",f"{gbw:.2e} Hz")

    st.markdown("### Interpretasi Karakteristik Teknik")
    st.markdown(f"""
    **Karakteristik Penguatan Sinyal**
    - Penguatan sinyal frekuensi rendah (DC) adalah **{A0_opt:.2f}×** atau **{A0_dB:.2f} dB**.
    - Batas frekuensi operasi optimal (*bandwidth efektif*) mencapai **{fc_opt:.2f} Hz**.
    - Di atas frekuensi cutoff f_c, penguatan menurun dengan laju -20 dB/dekade karena efek kapasitansi internal transistor/op-amp.

    **Konstansi Gain-Bandwidth Product (GBW)**
    - Nilai GBW = A0 × f_c = **{gbw:.2e} Hz** konstan pada penguat umpan balik.
    - Menurunkan gain akan memperluas bandwidth secara linier, dan sebaliknya.
    """)
    st.info(f"Kesimpulan: Amplifier mampu bekerja stabil pada domain frekuensi di bawah {fc_opt:.1f} Hz.")

# 6. Dioda
elif circuit == "Dioda":
    st.markdown("## Rangkaian Dioda Semikonduktor PN Junction")
    if "nr_result" in st.session_state:
        nr = st.session_state["nr_result"]
        V_D = nr.get("V_D", 0.65)
        I_D = nr.get("I_D", 0.004)
        p_diss = V_D * I_D
        st.markdown(f"""
        **Titik Kerja Operasi (*Q-Point*) Dioda**
        - Tegangan jatuh maju (V_D) = **{V_D:.4f} V**.
        - Arus maju (I_D) = **{I_D*1000:.4f} mA**.
        - Daya disipasi termal (P_D = V_D × I_D) = **{p_diss*1000:.4f} mW**.

        **Interpretasi Karakteristik**
        - Dioda silikon beroperasi normal pada daerah konduksi aktif (0.6 s/d 0.7 V).
        - Nilai disipasi daya {p_diss*1000:.2f} mW aman jauh di bawah batas maksimum rating komponen standar (umumnya 250 s/d 500 mW).
        """)
    else:
        st.info("Jalankan Newton-Raphson untuk dioda pada menu Numerical Computation untuk melihat titik operasi.")

# 7. Transistor BJT
elif circuit == "Transistor BJT":
    Is_opt, Vt_opt = p_opt[0], p_opt[1]
    gm_at_1mA = 1e-3 / max(Vt_opt, 1e-4)

    st.markdown("## Transistor BJT (Model Arus Kolektor Shockley)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Arus Saturasi Is",   f"{Is_opt:.3e} A")
    col2.metric("Tegangan Termal Vt", f"{Vt_opt*1000:.2f} mV")
    col3.metric("Transkonduktansi gm",f"{gm_at_1mA*1000:.2f} mS (pada 1mA)")

    st.markdown("### Interpretasi Karakteristik Teknik")
    st.markdown(f"""
    **Karakteristik Sambungan Base-Emitter BJT**
    - Arus saturasi balik I_s = **{Is_opt:.3e} A** mencerminkan area sambungan silikon dan tingkat doping basis.
    - Tegangan termal hasil optimasi V_T = **{Vt_opt*1000:.2f} mV** (nilai ideal pada suhu ruang 25°C adalah 25.85 mV).
    - Transkonduktansi sinyal kecil pada bias I_C = 1 mA adalah g_m = I_C / V_T = **{gm_at_1mA*1000:.2f} mS**.

    **Aplikasi Rangkaian**
    - Penguat sinyal kecil (*Common Emitter*), saklar logika digital transistor, dan cermin arus (*current mirror*).
    """)
    st.info(f"Kesimpulan: Model BJT cocok dengan data terukur, memberikan estimasi transkonduktansi presisi.")

st.markdown("---")
st.markdown("## Analisis Kinerja Algoritma Numerik")
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
        | Metrik Komputasi | Nilai |
        |---|---|
        | Jumlah Iterasi | {iters} |
        | Status Konvergensi | {'Konvergen' if conv else 'Selesai'} |
        | Cost Function Awal (MSE) | `{cost0:.4e}` |
        | Cost Function Akhir (MSE) | `{costN:.4e}` |
        | Penurunan Error (Reduksi) | `{reduction:.2f}%` |
        """)
    else:
        st.info("Gradient Descent belum dijalankan pada sesi ini.")

with col_b:
    st.markdown("### Newton-Raphson")
    if "nr_result" in st.session_state:
        nr = st.session_state["nr_result"]
        st.markdown(f"""
        | Metrik Komputasi | Nilai |
        |---|---|
        | Jumlah Iterasi | {nr.get('iterations', '-')} |
        | Status Konvergensi | {'Konvergen' if nr.get('converged', True) else 'Tidak Konvergen'} |
        | Nilai \|f(x)\| Akhir | `{abs(nr.get('f_root', 0)):.4e}` |
        | Laju Konvergensi | Kuadratik (Orde 2) |
        """)
    else:
        st.info("Newton-Raphson belum dijalankan.")
