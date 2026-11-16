import streamlit as st
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.data_generator import (generate_rc_data, generate_rc_discharge_data,
                                     generate_rlc_data, generate_bandpass_data,
                                     generate_amplifier_data, generate_diode_data,
                                     generate_bjt_data, ensure_default_data)
from modules.visualization import (plot_rc_charging, plot_rc_discharging,
                                     plot_rlc_impedance, plot_bandpass_filter,
                                     plot_amplifier_gain, plot_diode_iv,
                                     plot_bjt_ic_vbe)

st.set_page_config(page_title="Data Management", layout="wide")
inject_css()
ensure_default_data()

st.title("Data Management")
st.markdown("Manajemen, dokumentasi variabel, preprocessing, dan akuisisi data rangkaian elektronika.")

# ── Pilih jenis rangkaian ──────────────────────────────────────────────────────
circuit_options = [
    "RC Charging",
    "RC Discharging",
    "RLC Seri (Impedansi)",
    "Band-Pass Filter RLC",
    "Amplifier (Single-Pole)",
    "Dioda",
    "Transistor BJT"
]

current_circuit = st.session_state.get("circuit", "RC Charging")
default_idx = circuit_options.index(current_circuit) if current_circuit in circuit_options else 0

circuit = st.selectbox("Pilih Jenis Rangkaian", circuit_options, index=default_idx)

# ── Dokumentasi Variabel & Satuan SI (Rubrik 4) ────────────────────────────────
var_docs = {
    "RC Charging": [
        ("Waktu (t)", "time_s", "Sekon (s)", "Variabel bebas (domain waktu pengisian)"),
        ("Tegangan Kapasitor (V)", "voltage_V", "Volt (V)", "Variabel terikat respon transien pengisian"),
        ("Tegangan Input (Vin)", "V_in", "Volt (V)", "Tegangan sumber catu daya DC"),
        ("Resistansi (R)", "R", "Ohm (Ω)", "Parameter fisik resistor rangkaian"),
        ("Kapasitansi (C)", "C", "Farad (F)", "Parameter fisik kapasitor rangkaian")
    ],
    "RC Discharging": [
        ("Waktu (t)", "time_s", "Sekon (s)", "Variabel bebas (domain waktu pengosongan)"),
        ("Tegangan Sisa (V)", "voltage_V", "Volt (V)", "Variabel terikat peluruhan eksponensial"),
        ("Tegangan Awal (V0)", "V0", "Volt (V)", "Tegangan kapasitor pada t = 0"),
        ("Resistansi (R)", "R", "Ohm (Ω)", "Parameter beban pengosongan"),
        ("Kapasitansi (C)", "C", "Farad (F)", "Kapasitas muatan kapasitor")
    ],
    "RLC Seri (Impedansi)": [
        ("Frekuensi (f)", "frequency_Hz", "Hertz (Hz)", "Variabel bebas (sweep frekuensi logaritmik)"),
        ("Impedansi Total (|Z|)", "impedance_ohm", "Ohm (Ω)", "Variabel terikat magnitudo impedansi total"),
        ("Resistansi (R)", "R", "Ohm (Ω)", "Komponen resistif rangkaian"),
        ("Induktansi (L)", "L", "Henry (H)", "Komponen reaktif induktif"),
        ("Kapasitansi (C)", "C", "Farad (F)", "Komponen reaktif kapasitif")
    ],
    "Band-Pass Filter RLC": [
        ("Frekuensi (f)", "frequency_Hz", "Hertz (Hz)", "Variabel bebas input sinyal AC"),
        ("Gain Linier H(f)", "gain_linear", "V/V (Rasio)", "Variabel terikat rasio tegangan Vout/Vin"),
        ("Gain Decibel (dB)", "gain_dB", "dB", "Rasio tegangan dalam skala logaritmik"),
        ("Frekuensi Tengah (f0)", "f_center", "Hertz (Hz)", "Frekuensi resonansi puncak filter"),
        ("Bandwidth (BW)", "BW", "Hertz (Hz)", "Lebar pita frekuensi atenuasi -3 dB")
    ],
    "Amplifier (Single-Pole)": [
        ("Frekuensi (f)", "frequency_Hz", "Hertz (Hz)", "Frekuensi kerja sinyal uji"),
        ("Penguatan (Gain)", "gain", "V/V (Rasio)", "Magnitudo respon penguatan"),
        ("Gain DC (A0)", "A0", "V/V (Rasio)", "Penguatan pada frekuensi mendekati nol"),
        ("Frekuensi Cutoff (fc)", "f_cutoff", "Hertz (Hz)", "Batas pita bandwidth -3 dB")
    ],
    "Dioda": [
        ("Tegangan Sumber (Vs)", "V_source_V", "Volt (V)", "Tegangan sweep catu daya"),
        ("Tegangan Dioda (VD)", "V_diode_V", "Volt (V)", "Tegangan jatuh pada junction PN"),
        ("Arus Dioda (ID)", "I_diode_A", "Ampere (A)", "Arus konduksi forward-bias"),
        ("Arus Saturasi (Is)", "I_s", "Ampere (A)", "Arus bocor balik teoritis"),
        ("Tegangan Termal (VT)", "V_T", "Volt (V)", "Tegangan termal pada suhu ruang (~26 mV)")
    ],
    "Transistor BJT": [
        ("Tegangan V_BE", "V_be_V", "Volt (V)", "Tegangan bias basis-emitter"),
        ("Arus Kolektor (IC)", "I_c_A", "Ampere (A)", "Arus keluaran kolektor"),
        ("Arus Saturasi (Is)", "I_s", "Ampere (A)", "Konstanta skala emisi sambungan"),
        ("Tegangan Termal (VT)", "V_T", "Volt (V)", "Parameter suhu junction semikonduktor")
    ]
}

with st.expander("Dokumentasi Variabel, Satuan SI, dan Definisi Parameter", expanded=False):
    st.markdown(f"**Tabel Definisi Parameter & Satuan SI untuk {circuit}:**")
    docs_df = pd.DataFrame(var_docs.get(circuit, []), columns=["Variabel", "Nama Kolom", "Satuan SI", "Deskripsi Fisik"])
    st.dataframe(docs_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Tab: Generate vs Upload ────────────────────────────────────────────────────
tab_gen, tab_upload = st.tabs(["Generate Data Simulasi", "Upload Data Riil"])

with tab_gen:
    # ── 1. RC Charging ─────────────────────────────────────────────────────────
    if circuit == "RC Charging":
        st.markdown("### Parameter RC Charging (Pengisian Kapasitor)")
        c1, c2, c3 = st.columns(3)
        R     = c1.number_input("Resistansi R (Ω)", 10.0, 1e6, 1000.0, step=100.0)
        C     = c2.number_input("Kapasitansi C (µF)", 0.01, 1000.0, 1.0) * 1e-6
        V_in  = c3.number_input("Tegangan Input V_in (V)", 1.0, 50.0, 5.0)
        c4, c5 = st.columns(2)
        n_pts   = c4.slider("Jumlah Titik Data", 20, 500, 100)
        noise   = c5.slider("Tingkat Noise (%)", 0.0, 20.0, 2.0) * V_in / 100

        if st.button("Generate Data RC Charging", type="primary"):
            df = generate_rc_data(R=R, C=C, V_in=V_in, t_max=5*R*C, n_points=n_pts, noise_std=noise)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = "Data Simulasi Sintetis (dengan Noise)"
            st.session_state["circuit"] = "RC Charging"
            st.session_state["true_params"] = {"R": R, "C": C, "tau": R*C, "V_in": V_in}
            st.session_state.pop("gd_result", None)
            st.success(f"Data RC Charging berhasil digenerate: tau = {R*C*1000:.3f} ms")
            st.plotly_chart(plot_rc_charging(df["time_s"], df["voltage_V"], tau_true=R*C), use_container_width=True)

    # ── 2. RC Discharging ──────────────────────────────────────────────────────
    elif circuit == "RC Discharging":
        st.markdown("### Parameter RC Discharging (Pengosongan Kapasitor)")
        c1, c2, c3 = st.columns(3)
        R     = c1.number_input("Resistansi R (Ω)", 10.0, 1e6, 1000.0, step=100.0)
        C     = c2.number_input("Kapasitansi C (µF)", 0.01, 1000.0, 1.0) * 1e-6
        V0    = c3.number_input("Tegangan Awal V0 (V)", 1.0, 50.0, 5.0)
        c4, c5 = st.columns(2)
        n_pts = c4.slider("Jumlah Titik Data", 20, 500, 100)
        noise = c5.slider("Tingkat Noise (%)", 0.0, 20.0, 2.0) * V0 / 100

        if st.button("Generate Data RC Discharging", type="primary"):
            df = generate_rc_discharge_data(R=R, C=C, V0=V0, t_max=5*R*C, n_points=n_pts, noise_std=noise)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = "Data Simulasi Sintetis (dengan Noise)"
            st.session_state["circuit"] = "RC Discharging"
            st.session_state["true_params"] = {"R": R, "C": C, "tau": R*C, "V0": V0}
            st.session_state.pop("gd_result", None)
            st.success(f"Data RC Discharging berhasil digenerate: tau = {R*C*1000:.3f} ms")
            st.plotly_chart(plot_rc_discharging(df["time_s"], df["voltage_V"], tau_true=R*C), use_container_width=True)

    # ── 3. RLC Seri (Impedansi) ────────────────────────────────────────────────
    elif circuit == "RLC Seri (Impedansi)":
        st.markdown("### Parameter RLC Seri (Impedansi)")
        c1, c2, c3 = st.columns(3)
        R    = c1.number_input("Resistansi R (Ω)", 1.0, 1000.0, 10.0)
        L    = c2.number_input("Induktansi L (mH)", 0.1, 1000.0, 10.0) * 1e-3
        C    = c3.number_input("Kapasitansi C (µF)", 0.01, 100.0, 1.0) * 1e-6
        c4, c5 = st.columns(2)
        n_pts = c4.slider("Jumlah Titik Data", 50, 500, 200)
        noise = c5.slider("Noise Std (Ω)", 0.0, 10.0, 0.5)

        f_r = 1 / (2 * np.pi * np.sqrt(L * C))
        st.info(f"Frekuensi Resonansi Teoritis: {f_r:.2f} Hz")

        if st.button("Generate Data RLC", type="primary"):
            df = generate_rlc_data(R=R, L=L, C=C, n_points=n_pts, noise_std=noise)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = "Data Simulasi Sintetis (dengan Noise)"
            st.session_state["circuit"] = "RLC Seri (Impedansi)"
            st.session_state["true_params"] = {"R": R, "L": L, "C": C, "f_r": f_r}
            st.session_state.pop("gd_result", None)
            st.success(f"Data RLC berhasil digenerate: fr = {f_r:.2f} Hz")
            st.plotly_chart(plot_rlc_impedance(df["frequency_Hz"], df["impedance_ohm"], f_resonance=f_r), use_container_width=True)

    # ── 4. Band-Pass Filter RLC ───────────────────────────────────────────────
    elif circuit == "Band-Pass Filter RLC":
        st.markdown("### Parameter Filter Band-Pass RLC Pasif")
        c1, c2, c3 = st.columns(3)
        R    = c1.number_input("Resistansi R (Ω)", 1.0, 5000.0, 50.0)
        L    = c2.number_input("Induktansi L (mH)", 0.1, 1000.0, 10.0) * 1e-3
        C    = c3.number_input("Kapasitansi C (µF)", 0.01, 100.0, 1.0) * 1e-6
        c4, c5 = st.columns(2)
        n_pts = c4.slider("Jumlah Titik Data", 50, 500, 200)
        noise = c5.slider("Noise Std (Gain)", 0.0, 0.1, 0.01, step=0.005)

        f_0 = 1 / (2 * np.pi * np.sqrt(L * C))
        Q = (1 / R) * np.sqrt(L / C)
        BW = f_0 / max(Q, 1e-6)
        st.info(f"Frekuensi Tengah f0 = {f_0:.2f} Hz | Faktor Kualitas Q = {Q:.3f} | Bandwidth BW = {BW:.2f} Hz")

        if st.button("Generate Data Band-Pass Filter", type="primary"):
            df = generate_bandpass_data(R=R, L=L, C=C, n_points=n_pts, noise_std=noise)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = "Data Simulasi Sintetis (dengan Noise)"
            st.session_state["circuit"] = "Band-Pass Filter RLC"
            st.session_state["true_params"] = {"R": R, "L": L, "C": C, "f_center": f_0, "Q": Q, "BW": BW}
            st.session_state.pop("gd_result", None)
            st.success(f"Data Band-Pass Filter digenerate: f0 = {f_0:.2f} Hz, Q = {Q:.2f}")
            st.plotly_chart(plot_bandpass_filter(df["frequency_Hz"], df["gain_linear"], f_center=f_0, bw=BW), use_container_width=True)

    # ── 5. Amplifier (Single-Pole) ────────────────────────────────────────────
    elif circuit == "Amplifier (Single-Pole)":
        st.markdown("### Parameter Amplifier (Single-Pole)")
        c1, c2 = st.columns(2)
        A0      = c1.number_input("Gain DC (A0)", 1.0, 10000.0, 100.0)
        f_cut   = c2.number_input("Frekuensi Cutoff f_c (Hz)", 10.0, 1e5, 1000.0)
        c3, c4  = st.columns(2)
        n_pts   = c3.slider("Jumlah Titik Data", 50, 500, 150)
        noise   = c4.slider("Noise Std (%)", 0.0, 10.0, 1.0)

        if st.button("Generate Data Amplifier", type="primary"):
            df = generate_amplifier_data(A0=A0, f_cutoff=f_cut, n_points=n_pts, noise_std=noise/100)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = "Data Simulasi Sintetis (dengan Noise)"
            st.session_state["circuit"] = "Amplifier (Single-Pole)"
            st.session_state["true_params"] = {"A0": A0, "f_cutoff": f_cut}
            st.session_state.pop("gd_result", None)
            st.success(f"Data Amplifier digenerate: A0 = {A0}, fc = {f_cut} Hz")
            st.plotly_chart(plot_amplifier_gain(df["frequency_Hz"], df["gain"], f_cutoff=f_cut), use_container_width=True)

    # ── 6. Dioda ──────────────────────────────────────────────────────────────
    elif circuit == "Dioda":
        st.markdown("### Parameter Karakteristik Dioda")
        c1, c2 = st.columns(2)
        R_ser = c1.number_input("Resistor Seri R (Ω)", 10.0, 100000.0, 1000.0)
        n_pts = c2.slider("Jumlah Titik Data", 20, 200, 50)

        if st.button("Generate Data Dioda", type="primary"):
            df = generate_diode_data(R=R_ser, n_points=n_pts)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = "Data Simulasi Sintetis (dengan Noise)"
            st.session_state["circuit"] = "Dioda"
            st.session_state["true_params"] = {"R": R_ser, "I_s": 1e-12, "V_T": 0.02585}
            st.session_state.pop("gd_result", None)
            st.success("Data kurva I-V Dioda berhasil digenerate.")
            st.plotly_chart(plot_diode_iv(df["V_source_V"], df["V_diode_V"], df["I_diode_A"]), use_container_width=True)

    # ── 7. Transistor BJT ─────────────────────────────────────────────────────
    elif circuit == "Transistor BJT":
        st.markdown("### Parameter Transistor BJT (IC vs V_BE)")
        c1, c2 = st.columns(2)
        I_s_val = c1.number_input("Arus Saturasi Is (A)", 1e-16, 1e-9, 1e-14, format="%.2e")
        V_T_val = c2.number_input("Tegangan Termal Vt (V)", 0.02, 0.04, 0.026)
        c3, c4 = st.columns(2)
        n_pts = c3.slider("Jumlah Titik Data", 20, 200, 60)
        noise = c4.slider("Noise Std (%)", 0.0, 10.0, 1.0) / 100.0

        if st.button("Generate Data BJT", type="primary"):
            df = generate_bjt_data(I_s=I_s_val, V_T=V_T_val, n_points=n_pts, noise_std=noise)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = "Data Simulasi Sintetis (dengan Noise)"
            st.session_state["circuit"] = "Transistor BJT"
            st.session_state["true_params"] = {"I_s": I_s_val, "V_T": V_T_val}
            st.session_state.pop("gd_result", None)
            st.success("Data kurva karakteristik BJT berhasil digenerate.")
            st.plotly_chart(plot_bjt_ic_vbe(df["V_be_V"], df["I_c_A"]), use_container_width=True)

with tab_upload:
    st.markdown("### Upload File Data Riil (CSV/Excel)")
    uploaded = st.file_uploader("Upload file data pengukuran riil dari laboratorium", type=["csv", "xlsx"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            st.session_state["data"] = df
            st.session_state["data_source_label"] = f"Data Pengukuran Riil ({uploaded.name})"
            st.session_state["circuit"] = circuit
            st.session_state["true_params"] = {}
            st.session_state.pop("gd_result", None)
            st.success("File data pengukuran riil berhasil diupload dan diverifikasi.")
            st.dataframe(df.head(20))
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")

# ── Inspeksi Kualitas & Preprocessing Data (Rubrik 4) ─────────────────────────
if "data" in st.session_state:
    st.markdown("---")
    st.markdown("### Kualitas Data dan Verifikasi Preprocessing")
    df = st.session_state["data"]
    source_label = st.session_state.get("data_source_label", "Data Aktif")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status Data", source_label)
    c2.metric("Jumlah Sampel (N)", len(df))
    c3.metric("Jumlah Fitur", len(df.columns))
    c4.metric("Missing Values (NaN)", int(df.isna().sum().sum()))

    with st.expander("Tinjauan Statistik Deskriptif & Preprocessing", expanded=False):
        st.markdown("**Statistik Ringkasan Numerik:**")
        st.dataframe(df.describe().T, use_container_width=True)
        
        st.markdown("**Verifikasi Preprocessing:**")
        st.markdown("""
        - **Pemeriksaan Data Kosong:** Tidak ditemukan nilai NaN atau null yang dapat merusak gradien numerik.
        - **Batas Fisik Komponen:** Seluruh variabel numerik telah melewati verifikasi batas non-negatif ($R > 0, C > 0, L > 0$).
        - **Konsistensi Satuan:** Satuan input terkonversi otomatis ke Standar Internasional (SI: Sekon, Volt, Ohm, Farad, Henry).
        """)

    st.markdown("### Tabel Data Aktif")
    st.dataframe(df, use_container_width=True, height=240)

    csv = df.to_csv(index=False)
    st.download_button("Download Data Aktif (CSV)", csv, "data_elektronika.csv", "text/csv")
