import streamlit as st
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.data_generator import ensure_default_data

st.set_page_config(page_title="Engineering Interpretation", page_icon="💡", layout="wide")
inject_css()
ensure_default_data()

st.title("Engineering Interpretation")
st.markdown("Interpretasi teknik hasil optimasi parameter elektronika.")

circuit = st.session_state.get("circuit", "")
true_p  = st.session_state.get("true_params", {})

if "gd_result" not in st.session_state:
    st.warning("⚠️ Jalankan komputasi numerik terlebih dahulu.")
    st.stop()

result = st.session_state["gd_result"]
p_opt  = result["optimal_params"]
df_data = st.session_state.get("data", None)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Interpretasi per rangkaian
# ══════════════════════════════════════════════════════════════════════════════

if circuit == "RC Charging":
    R_opt, C_opt = p_opt
    tau = R_opt * C_opt
    f_c = 1 / (2 * np.pi * tau)

    st.markdown("## ⚡ Rangkaian RC Charging")

    col1, col2, col3 = st.columns(3)
    col1.metric("R Optimal",         f"{R_opt:.4f} Ω")
    col2.metric("C Optimal",         f"{C_opt*1e6:.4f} µF")
    col3.metric("τ = RC",            f"{tau*1000:.4f} ms")

    st.markdown("### 📖 Interpretasi Teknik")
    st.markdown(f"""
    **Konstanta Waktu (τ = RC)**
    - τ = **{tau*1000:.4f} ms** → kapasitor mencapai **~63.2%** tegangan penuh pada t = τ
    - Pada t = 5τ = **{5*tau*1000:.4f} ms**, kapasitor dianggap **penuh terisi (99.3%)**

    **Frekuensi Cutoff**
    - f_c = 1/(2πRC) = **{f_c:.2f} Hz**
    - Rangkaian RC berfungsi sebagai **Low-Pass Filter** dengan f_c = {f_c:.2f} Hz
    - Sinyal di bawah {f_c:.2f} Hz akan **lolos**, di atas akan **dilemahkan**

    **Aplikasi Teknis**
    - 🔋 Filter daya supply, debounce sinyal digital
    - ⏱️ Timer/osilator sederhana
    - 📡 Coupling dan decoupling sinyal AC/DC

    **Validasi**
    - Bandingkan τ dengan nilai τ_referensi dari datasheet komponen
    - Gunakan osiloskop untuk verifikasi kurva charging aktual
    """)

    st.info(f"💡 **Kesimpulan**: Sistem RC dengan R={R_opt:.2f}Ω dan C={C_opt*1e6:.4f}µF "
            f"memiliki respons transien τ={tau*1000:.4f}ms, cocok untuk aplikasi "
            f"filter dan timer dengan frekuensi cutoff {f_c:.2f} Hz.")

elif circuit == "RLC Impedansi":
    R_opt, L_opt, C_opt = p_opt
    L_opt = abs(L_opt); C_opt = abs(C_opt)
    f_r   = 1/(2*np.pi*np.sqrt(max(L_opt,1e-15)*max(C_opt,1e-15)))
    Q     = (1/R_opt)*np.sqrt(max(L_opt,1e-15)/max(C_opt,1e-15))
    BW    = f_r / max(Q, 1e-6)
    Z_min = R_opt

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("R Optimal", f"{R_opt:.4f} Ω")
    col2.metric("L Optimal", f"{L_opt*1e3:.4f} mH")
    col3.metric("C Optimal", f"{C_opt*1e6:.4f} µF")
    col4.metric("f_r",       f"{f_r:.2f} Hz")

    st.markdown("### 📖 Interpretasi Teknik")
    st.markdown(f"""
    **Frekuensi Resonansi**
    - f_r = **{f_r:.4f} Hz** → pada frekuensi ini |Z| minimum = R = {R_opt:.4f} Ω
    - Di bawah f_r: rangkaian bersifat **kapasitif** (Z didominasi kapasitor)
    - Di atas f_r: rangkaian bersifat **induktif** (Z didominasi induktor)

    **Faktor Kualitas (Q-factor)**
    - Q = **{Q:.4f}** → {'resonansi tajam (Q > 10)' if Q > 10 else 'resonansi sedang' if Q > 1 else 'resonansi lebar (Q < 1)'}
    - Bandwidth = f_r/Q = **{BW:.4f} Hz**

    **Aplikasi Teknis**
    - 📻 Filter bandpass/notch, tuner radio
    - ⚡ Power factor correction
    - 🔊 Crossover speaker, osilator LC

    **Validasi**
    - Ukur impedansi dengan LCR meter atau impedance analyzer
    - Konfirmasi f_r dengan sweep frekuensi pada network analyzer
    """)

    st.info(f"💡 **Kesimpulan**: Rangkaian RLC seri beresonansi pada **{f_r:.2f} Hz** "
            f"dengan Q-factor **{Q:.4f}** dan bandwidth **{BW:.4f} Hz**.")

elif circuit == "Amplifier":
    A0_opt, fc_opt = p_opt
    A0_dB = 20*np.log10(max(A0_opt, 1e-6))
    f_unity = fc_opt * A0_opt  # gain-bandwidth product

    col1,col2,col3 = st.columns(3)
    col1.metric("Gain DC (A0)",       f"{A0_opt:.4f} ({A0_dB:.2f} dB)")
    col2.metric("Frekuensi Cutoff",   f"{fc_opt:.4f} Hz")
    col3.metric("Gain-BW Product",    f"{f_unity:.2f} Hz")

    st.markdown("### 📖 Interpretasi Teknik")
    st.markdown(f"""
    **Gain DC**
    - A0 = **{A0_opt:.4f}** = **{A0_dB:.2f} dB**
    - Pada frekuensi DC (f → 0), sinyal diperkuat {A0_opt:.2f}×

    **Frekuensi Cutoff (−3dB)**
    - f_c = **{fc_opt:.4f} Hz** → pada f = f_c, gain turun menjadi A0/√2 = {A0_opt/np.sqrt(2):.4f} ({A0_dB-3:.2f} dB)
    - Di atas f_c, gain turun **−20 dB/decade** (sistem orde-1)

    **Gain-Bandwidth Product (GBW)**
    - GBW = A0 × f_c = **{f_unity:.2f} Hz**
    - GBW konstan → menambah gain akan mengurangi bandwidth, dan sebaliknya

    **Aplikasi Teknis**
    - 🎵 Amplifier audio, instrumentasi
    - 📡 Front-end RF (bila f_c tinggi)
    - 🔬 Op-amp dalam loop tertutup

    **Validasi**
    - Ukur dengan network analyzer atau bode plotter
    - Bandingkan dengan datasheet transistor/op-amp yang digunakan
    """)
    st.info(f"💡 **Kesimpulan**: Amplifier dengan A0={A0_opt:.4f} ({A0_dB:.2f} dB) "
            f"dan f_c={fc_opt:.4f} Hz, GBW={f_unity:.2f} Hz.")

elif circuit == "Dioda":
    st.markdown("## 🔴 Rangkaian Dioda")
    if "nr_result" in st.session_state:
        nr = st.session_state["nr_result"]
        V_D = nr.get("V_D", 0)
        I_D = nr.get("I_D", 0)
        st.markdown(f"""
        **Titik Operasi Dioda**
        - V_D = **{V_D:.4f} V** (tegangan maju dioda)
        - I_D = **{I_D*1000:.4f} mA** (arus maju dioda)

        **Interpretasi**
        - Dioda silicon umumnya V_D ≈ 0.6–0.7 V pada kondisi ON
        - V_D = {V_D:.4f} V → dioda {'aktif (forward bias)' if V_D > 0.5 else 'mendekati cutoff'}
        - Daya disipasi dioda: P_D = V_D × I_D = **{V_D*I_D*1000:.4f} mW**
        """)
    else:
        st.info("Jalankan Newton-Raphson untuk dioda terlebih dahulu.")

else:
    st.info("Interpretasi teknik akan muncul setelah komputasi selesai.")

st.markdown("---")
st.markdown("## 🔬 Interpretasi Algoritma Numerik")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### Gradient Descent")
    iters = result["iterations"]
    conv  = result["converged"]
    cost0 = result["history"]["cost"][0]
    costN = result["final_cost"]
    reduction = (1 - costN/max(cost0,1e-30))*100

    st.markdown(f"""
    | Metrik | Nilai |
    |---|---|
    | Iterasi | {iters} |
    | Status | {'✅ Konvergen' if conv else '⚠️ Belum konvergen'} |
    | Cost Awal | {cost0:.4e} |
    | Cost Akhir | {costN:.4e} |
    | Reduksi Cost | {reduction:.2f}% |
    """)

with col_b:
    if "nr_result" in st.session_state:
        st.markdown("### Newton-Raphson")
        nr    = st.session_state["nr_result"]
        st.markdown(f"""
        | Metrik | Nilai |
        |---|---|
        | Iterasi | {nr['iterations']} |
        | Status | {'✅ Konvergen' if nr['converged'] else '⚠️ Tidak konvergen'} |
        | \|f(x)\| Akhir | {abs(nr['f_root']):.4e} |
        | Orde Konvergensi | Kuadratik (orde 2) |
        """)
    else:
        st.markdown("### Newton-Raphson")
        st.info("Belum dijalankan.")
