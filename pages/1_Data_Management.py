import streamlit as st
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.data_generator import (generate_rc_data, generate_rlc_data,
                                     generate_amplifier_data, generate_diode_data)
from modules.visualization import (plot_rc_charging, plot_rlc_impedance,
                                    plot_amplifier_gain, plot_diode_iv)

st.set_page_config(page_title="Data Management", page_icon="📊", layout="wide")
st.title("📊 Data Management")
st.markdown("Generate atau upload data rangkaian elektronika untuk optimasi parameter.")

# ── Pilih jenis rangkaian ──────────────────────────────────────────────────────
circuit = st.selectbox("🔌 Pilih Jenis Rangkaian",
                        ["RC Charging", "RLC Impedansi", "Amplifier (Single-Pole)", "Dioda"])

st.markdown("---")

# ── Tab: Generate vs Upload ────────────────────────────────────────────────────
tab_gen, tab_upload = st.tabs(["🔧 Generate Data Simulasi", "📂 Upload Data Riil"])

with tab_gen:
    if circuit == "RC Charging":
        st.markdown("### ⚡ Parameter RC Charging")
        c1, c2, c3 = st.columns(3)
        R     = c1.number_input("Resistansi R (Ω)", 100.0, 1e6, 1000.0, step=100.0)
        C     = c2.number_input("Kapasitansi C (µF)", 0.1, 1000.0, 1.0) * 1e-6
        V_in  = c3.number_input("Tegangan Input V_in (V)", 1.0, 50.0, 5.0)
        c4, c5 = st.columns(2)
        n_pts   = c4.slider("Jumlah Titik Data", 20, 500, 100)
        noise   = c5.slider("Noise Std (%)", 0.0, 20.0, 2.0) * V_in / 100

        if st.button("▶ Generate RC Data", type="primary"):
            df = generate_rc_data(R=R, C=C, V_in=V_in, t_max=5*R*C,
                                   n_points=n_pts, noise_std=noise)
            st.session_state["data"]    = df
            st.session_state["circuit"] = "RC Charging"
            st.session_state["true_params"] = {"R": R, "C": C,
                                                "tau": R*C, "V_in": V_in}
            st.success(f"✅ RC Data berhasil digenerate! τ = {R*C:.4f} s")
            st.plotly_chart(plot_rc_charging(df["time_s"], df["voltage_V"],
                                             tau_true=R*C), use_container_width=True)

    elif circuit == "RLC Impedansi":
        st.markdown("### 🔁 Parameter RLC Seri")
        c1, c2, c3 = st.columns(3)
        R    = c1.number_input("Resistansi R (Ω)", 1.0, 1000.0, 10.0)
        L    = c2.number_input("Induktansi L (mH)", 0.1, 1000.0, 10.0) * 1e-3
        C    = c3.number_input("Kapasitansi C (µF)", 0.01, 100.0, 1.0) * 1e-6
        c4, c5 = st.columns(2)
        n_pts = c4.slider("Jumlah Titik Data", 50, 500, 200)
        noise = c5.slider("Noise Std (Ω)", 0.0, 10.0, 0.5)

        f_r = 1 / (2 * np.pi * np.sqrt(L * C))
        st.info(f"🎯 Frekuensi Resonansi: **{f_r:.2f} Hz**")

        if st.button("▶ Generate RLC Data", type="primary"):
            df = generate_rlc_data(R=R, L=L, C=C, n_points=n_pts, noise_std=noise)
            st.session_state["data"]    = df
            st.session_state["circuit"] = "RLC Impedansi"
            st.session_state["true_params"] = {"R": R, "L": L, "C": C, "f_r": f_r}
            st.success(f"✅ RLC Data berhasil digenerate! f_r = {f_r:.2f} Hz")
            st.plotly_chart(plot_rlc_impedance(df["frequency_Hz"], df["impedance_ohm"],
                                               f_resonance=f_r), use_container_width=True)

    elif circuit == "Amplifier (Single-Pole)":
        st.markdown("### 📡 Parameter Amplifier")
        c1, c2 = st.columns(2)
        A0      = c1.number_input("Gain DC (A0)", 1.0, 10000.0, 100.0)
        f_cut   = c2.number_input("Frekuensi Cutoff f_c (Hz)", 10.0, 1e5, 1000.0)
        c3, c4  = st.columns(2)
        n_pts   = c3.slider("Jumlah Titik Data", 50, 500, 150)
        noise   = c4.slider("Noise Std (%)", 0.0, 10.0, 1.0)

        if st.button("▶ Generate Amplifier Data", type="primary"):
            df = generate_amplifier_data(A0=A0, f_cutoff=f_cut, n_points=n_pts,
                                          noise_std=noise/100)
            st.session_state["data"]    = df
            st.session_state["circuit"] = "Amplifier"
            st.session_state["true_params"] = {"A0": A0, "f_cutoff": f_cut}
            st.success(f"✅ Amplifier Data digenerate! A0={A0}, f_c={f_cut} Hz")
            st.plotly_chart(plot_amplifier_gain(df["frequency_Hz"], df["gain"],
                                                f_cutoff=f_cut), use_container_width=True)

    else:  # Dioda
        st.markdown("### 🔴 Parameter Dioda")
        c1, c2 = st.columns(2)
        R_ser = c1.number_input("Resistor Seri R (Ω)", 100.0, 10000.0, 1000.0)
        n_pts = c2.slider("Jumlah Titik Data", 20, 200, 50)

        if st.button("▶ Generate Dioda Data", type="primary"):
            df = generate_diode_data(R=R_ser, n_points=n_pts)
            st.session_state["data"]    = df
            st.session_state["circuit"] = "Dioda"
            st.session_state["true_params"] = {"R": R_ser}
            st.success("✅ Data kurva I-V Dioda berhasil digenerate!")
            st.plotly_chart(plot_diode_iv(df["V_source_V"], df["V_diode_V"],
                                          df["I_diode_A"]), use_container_width=True)

with tab_upload:
    st.markdown("### 📂 Upload File Data Riil (CSV/Excel)")
    uploaded = st.file_uploader("Upload file data", type=["csv", "xlsx"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") \
                 else pd.read_excel(uploaded)
            st.session_state["data"]    = df
            st.session_state["circuit"] = circuit
            st.session_state["true_params"] = {}
            st.success("✅ Data berhasil diupload!")
            st.dataframe(df.head(20))
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")

# ── Tampilkan data yang sudah ada ──────────────────────────────────────────────
if "data" in st.session_state:
    st.markdown("---")
    st.markdown("### 📋 Data Aktif")
    df = st.session_state["data"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Baris", len(df))
    c2.metric("Jumlah Kolom", len(df.columns))
    c3.metric("Rangkaian", st.session_state.get("circuit", "-"))
    st.dataframe(df, use_container_width=True, height=250)

    csv = df.to_csv(index=False)
    st.download_button("⬇ Download Data (CSV)", csv, "data_elektronika.csv", "text/csv")
