import streamlit as st
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.gradient_descent import (gradient_descent,
    rc_voltage_error, rc_voltage_grad,
    rc_discharge_error, rc_discharge_grad,
    rlc_impedance_error, rlc_impedance_grad,
    bandpass_filter_error, bandpass_filter_grad,
    amplifier_gain_error, amplifier_gain_grad,
    bjt_collector_error, bjt_collector_grad)
from modules.newton_raphson import (newton_raphson_scalar,
    find_diode_operating_point, find_rlc_resonance, find_rc_time_constant,
    find_rc_discharge_constant, find_bjt_vbe_bias, find_bandpass_cutoff)
from modules.visualization import (plot_convergence, plot_newton_raphson_convergence,
                                    plot_rc_charging, plot_rc_discharging,
                                    plot_rlc_impedance, plot_bandpass_filter,
                                    plot_amplifier_gain, plot_bjt_ic_vbe)
from modules.data_generator import ensure_default_data

st.set_page_config(page_title="Numerical Computation", layout="wide")
inject_css()
ensure_default_data()

st.title("Numerical Computation")

if "data" not in st.session_state:
    st.warning("Belum ada data. Silakan generate atau upload data di menu Data Management terlebih dahulu.")
    st.stop()

circuit = st.session_state.get("circuit", "RC Charging")
df      = st.session_state["data"]
true_p  = st.session_state.get("true_params", {})

st.info(f"Rangkaian aktif: {circuit}")
st.markdown("---")

# ── Tab algoritma ──────────────────────────────────────────────────────────────
tab_gd, tab_nr = st.tabs(["Gradient Descent", "Newton-Raphson"])

# ══════════════════════════════════════════════════════════════════════════════
# GRADIENT DESCENT
# ══════════════════════════════════════════════════════════════════════════════
with tab_gd:
    st.markdown("### Gradient Descent — Optimasi Parameter")

    with st.expander("Teori Gradient Descent", expanded=False):
        st.markdown(r"""
        **Gradient Descent** adalah algoritma iteratif untuk mencari minimum fungsi biaya:

        $$\theta_{k+1} = \theta_k - \alpha \cdot \nabla f(\theta_k)$$

        - $\theta$: vektor parameter (R, L, C, dll.)
        - $\alpha$: learning rate (laju belajar)
        - $\nabla f$: gradien fungsi biaya (dihitung numerik via finite differences)

        **Fungsi biaya** yang digunakan adalah **MSE (Mean Squared Error)**:
        $$f(\theta) = \frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i(\theta))^2$$
        """)

    # 1. RC Charging
    if circuit == "RC Charging":
        st.markdown("**Parameter tebakan awal untuk RC Charging:**")
        c1, c2 = st.columns(2)
        R_init = c1.number_input("R awal (Ω)", 10.0, 1e6, float(true_p.get("R", 1000.0) * 1.25),
                                  help="Tebakan awal R")
        C_init = c2.number_input("C awal (µF)", 0.01, 1000.0,
                                  float(true_p.get("C", 1e-6) * 1e6 * 0.75)) * 1e-6
        c3, c4 = st.columns(2)
        lr       = c3.number_input("Learning Rate (alpha)", 1e-12, 1.0, 1e-6, format="%.2e")
        max_iter = c4.number_input("Maks. Iterasi", 10, 5000, 500)

        if st.button("Jalankan Gradient Descent (RC Charging)", type="primary"):
            t   = df["time_s"].values
            V   = df["voltage_V"].values
            V_in = float(true_p.get("V_in", 5.0))

            cost_f = lambda p: rc_voltage_error(p, t, V, V_in)
            grad_f = lambda p: rc_voltage_grad(p, t, V, V_in)

            with st.spinner("Mengoptimasi parameter RC..."):
                result = gradient_descent(cost_f, grad_f, params_init=[R_init, C_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            R_opt, C_opt = result["optimal_params"]
            tau_opt = R_opt * C_opt
            tau_true = true_p.get("tau", None)

            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'Konvergen' if result['converged'] else 'Selesai'} dalam {result['iterations']} iterasi")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R Optimal", f"{R_opt:.2f} Ω")
            col2.metric("C Optimal", f"{C_opt*1e6:.4f} µF")
            col3.metric("tau Optimal", f"{tau_opt*1000:.4f} ms")
            col4.metric("Final MSE", f"{result['final_cost']:.4e}")

            V_fitted = V_in * (1 - np.exp(-t / max(tau_opt, 1e-15)))
            st.plotly_chart(plot_rc_charging(t, V, V_fitted, tau_true=tau_true, tau_fitted=tau_opt),
                            use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    # 2. RC Discharging
    elif circuit == "RC Discharging":
        st.markdown("**Parameter tebakan awal untuk RC Discharging:**")
        c1, c2 = st.columns(2)
        R_init = c1.number_input("R awal (Ω)", 10.0, 1e6, float(true_p.get("R", 1000.0) * 1.25))
        C_init = c2.number_input("C awal (µF)", 0.01, 1000.0,
                                  float(true_p.get("C", 1e-6) * 1e6 * 0.75)) * 1e-6
        c3, c4 = st.columns(2)
        lr       = c3.number_input("Learning Rate (alpha)", 1e-12, 1.0, 1e-6, format="%.2e")
        max_iter = c4.number_input("Maks. Iterasi", 10, 5000, 500)

        if st.button("Jalankan Gradient Descent (RC Discharging)", type="primary"):
            t  = df["time_s"].values
            V  = df["voltage_V"].values
            V0 = float(true_p.get("V0", 5.0))

            cost_f = lambda p: rc_discharge_error(p, t, V, V0)
            grad_f = lambda p: rc_discharge_grad(p, t, V, V0)

            with st.spinner("Mengoptimasi parameter RC Discharging..."):
                result = gradient_descent(cost_f, grad_f, params_init=[R_init, C_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            R_opt, C_opt = result["optimal_params"]
            tau_opt = R_opt * C_opt
            tau_true = true_p.get("tau", None)

            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'Konvergen' if result['converged'] else 'Selesai'} dalam {result['iterations']} iterasi")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R Optimal", f"{R_opt:.2f} Ω")
            col2.metric("C Optimal", f"{C_opt*1e6:.4f} µF")
            col3.metric("tau Optimal", f"{tau_opt*1000:.4f} ms")
            col4.metric("Final MSE", f"{result['final_cost']:.4e}")

            V_fitted = V0 * np.exp(-t / max(tau_opt, 1e-15))
            st.plotly_chart(plot_rc_discharging(t, V, V_fitted, tau_true=tau_true, tau_fitted=tau_opt),
                            use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    # 3. RLC Seri
    elif circuit == "RLC Seri (Impedansi)":
        st.markdown("**Parameter tebakan awal untuk RLC Seri:**")
        c1, c2, c3 = st.columns(3)
        R_init = c1.number_input("R awal (Ω)", 1.0, 1000.0, float(true_p.get("R", 10.0) * 1.2))
        L_init = c2.number_input("L awal (mH)", 0.1, 1000.0, float(true_p.get("L", 0.01) * 1e3 * 0.8)) * 1e-3
        C_init = c3.number_input("C awal (µF)", 0.01, 1000.0, float(true_p.get("C", 1e-6) * 1e6 * 1.3)) * 1e-6
        c4, c5 = st.columns(2)
        lr       = c4.number_input("Learning Rate (alpha)", 1e-14, 1e-3, 1e-10, format="%.2e")
        max_iter = c5.number_input("Maks. Iterasi", 10, 5000, 1000)

        if st.button("Jalankan Gradient Descent (RLC)", type="primary"):
            freqs = df["frequency_Hz"].values
            Z     = df["impedance_ohm"].values

            cost_f = lambda p: rlc_impedance_error(p, freqs, Z)
            grad_f = lambda p: rlc_impedance_grad(p, freqs, Z)

            with st.spinner("Menjalankan Gradient Descent RLC..."):
                result = gradient_descent(cost_f, grad_f, params_init=[R_init, L_init, C_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            R_opt, L_opt, C_opt = result["optimal_params"]
            f_r_opt = 1.0 / (2 * np.pi * np.sqrt(max(L_opt, 1e-15) * max(C_opt, 1e-15)))

            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'Konvergen' if result['converged'] else 'Selesai'} dalam {result['iterations']} iterasi")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R Optimal", f"{R_opt:.3f} Ω")
            col2.metric("L Optimal", f"{L_opt*1e3:.3f} mH")
            col3.metric("C Optimal", f"{C_opt*1e6:.4f} µF")
            col4.metric("fr Optimal", f"{f_r_opt:.2f} Hz")

            omega = 2 * np.pi * freqs
            Z_fitted = np.sqrt(R_opt**2 + (omega * L_opt - 1.0 / (omega * C_opt))**2)
            st.plotly_chart(plot_rlc_impedance(freqs, Z, Z_fitted, f_r_opt), use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    # 4. Band-Pass Filter RLC
    elif circuit == "Band-Pass Filter RLC":
        st.markdown("**Parameter tebakan awal untuk Band-Pass Filter:**")
        c1, c2, c3 = st.columns(3)
        R_init = c1.number_input("R awal (Ω)", 1.0, 5000.0, float(true_p.get("R", 50.0) * 1.2))
        L_init = c2.number_input("L awal (mH)", 0.1, 1000.0, float(true_p.get("L", 0.01) * 1e3 * 0.85)) * 1e-3
        C_init = c3.number_input("C awal (µF)", 0.01, 100.0, float(true_p.get("C", 1e-6) * 1e6 * 1.15)) * 1e-6
        c4, c5 = st.columns(2)
        lr       = c4.number_input("Learning Rate (alpha)", 1e-12, 1e-2, 1e-7, format="%.2e")
        max_iter = c5.number_input("Maks. Iterasi", 10, 5000, 1000)

        if st.button("Jalankan Gradient Descent (Band-Pass Filter)", type="primary"):
            freqs = df["frequency_Hz"].values
            gain  = df["gain_linear"].values

            cost_f = lambda p: bandpass_filter_error(p, freqs, gain)
            grad_f = lambda p: bandpass_filter_grad(p, freqs, gain)

            with st.spinner("Mengoptimasi respons Band-Pass Filter..."):
                result = gradient_descent(cost_f, grad_f, params_init=[R_init, L_init, C_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            R_opt, L_opt, C_opt = result["optimal_params"]
            f0_opt = 1.0 / (2 * np.pi * np.sqrt(max(L_opt, 1e-15) * max(C_opt, 1e-15)))
            Q_opt = (1.0 / R_opt) * np.sqrt(L_opt / C_opt)
            BW_opt = f0_opt / max(Q_opt, 1e-6)

            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'Konvergen' if result['converged'] else 'Selesai'} dalam {result['iterations']} iterasi")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R Optimal", f"{R_opt:.2f} Ω")
            col2.metric("f0 Optimal", f"{f0_opt:.2f} Hz")
            col3.metric("Q Factor", f"{Q_opt:.3f}")
            col4.metric("Bandwidth", f"{BW_opt:.2f} Hz")

            omega = 2 * np.pi * freqs
            reactance = omega * L_opt - 1.0 / (omega * C_opt)
            H_fitted = R_opt / np.sqrt(R_opt**2 + reactance**2)
            st.plotly_chart(plot_bandpass_filter(freqs, gain, H_fitted, f_center=f0_opt, bw=BW_opt),
                            use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    # 5. Amplifier
    elif circuit in ["Amplifier", "Amplifier (Single-Pole)"]:
        st.markdown("**Parameter tebakan awal untuk Amplifier:**")
        c1, c2 = st.columns(2)
        A0_init = c1.number_input("A0 awal", 1.0, 10000.0, float(true_p.get("A0", 100.0) * 0.8))
        fc_init = c2.number_input("f_c awal (Hz)", 10.0, 1e5, float(true_p.get("f_cutoff", 1000.0) * 1.3))
        c3, c4  = st.columns(2)
        lr       = c3.number_input("Learning Rate (alpha)", 1e-10, 10.0, 0.01, format="%.4f")
        max_iter = c4.number_input("Maks. Iterasi", 10, 5000, 1000)

        if st.button("Jalankan Gradient Descent (Amplifier)", type="primary"):
            freqs = df["frequency_Hz"].values
            G     = df["gain"].values

            cost_f = lambda p: amplifier_gain_error(p, freqs, G)
            grad_f = lambda p: amplifier_gain_grad(p, freqs, G)

            with st.spinner("Mengoptimasi parameter Amplifier..."):
                result = gradient_descent(cost_f, grad_f, params_init=[A0_init, fc_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            A0_opt, fc_opt = result["optimal_params"]
            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = "Amplifier (Single-Pole)"

            st.success(f"{'Konvergen' if result['converged'] else 'Selesai'} dalam {result['iterations']} iterasi")
            col1, col2, col3 = st.columns(3)
            col1.metric("A0 Optimal", f"{A0_opt:.3f}")
            col2.metric("fc Optimal", f"{fc_opt:.2f} Hz")
            col3.metric("Final MSE", f"{result['final_cost']:.4e}")

            G_fitted = A0_opt / np.sqrt(1 + (freqs / max(fc_opt, 1e-3))**2)
            st.plotly_chart(plot_amplifier_gain(freqs, G, G_fitted, fc_opt), use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    # 6. Dioda
    elif circuit == "Dioda":
        st.info("Karakteristik titik kerja Dioda diselesaikan menggunakan tab Newton-Raphson.")

    # 7. Transistor BJT
    elif circuit == "Transistor BJT":
        st.markdown("**Parameter tebakan awal untuk Karakteristik BJT:**")
        c1, c2 = st.columns(2)
        Is_init = c1.number_input("Is awal (A)", 1e-18, 1e-8, float(true_p.get("I_s", 1e-14) * 2.0), format="%.2e")
        Vt_init = c2.number_input("Vt awal (V)", 0.01, 0.06, float(true_p.get("V_T", 0.026) * 1.1), format="%.4f")
        c3, c4 = st.columns(2)
        lr       = c3.number_input("Learning Rate (alpha)", 1e-12, 1e-1, 1e-4, format="%.2e")
        max_iter = c4.number_input("Maks. Iterasi", 10, 5000, 800)

        if st.button("Jalankan Gradient Descent (BJT)", type="primary"):
            vbe = df["V_be_V"].values
            ic  = df["I_c_A"].values

            cost_f = lambda p: bjt_collector_error(p, vbe, ic)
            grad_f = lambda p: bjt_collector_grad(p, vbe, ic)

            with st.spinner("Mengestimasi parameter BJT Shockley..."):
                result = gradient_descent(cost_f, grad_f, params_init=[Is_init, Vt_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            Is_opt, Vt_opt = result["optimal_params"]
            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'Konvergen' if result['converged'] else 'Selesai'} dalam {result['iterations']} iterasi")
            col1, col2, col3 = st.columns(3)
            col1.metric("Is Optimal", f"{Is_opt:.3e} A")
            col2.metric("Vt Optimal", f"{Vt_opt*1000:.2f} mV")
            col3.metric("Final MSE", f"{result['final_cost']:.4e}")

            ic_fitted = Is_opt * (np.exp(np.clip(vbe / Vt_opt, 0, 40)) - 1)
            st.plotly_chart(plot_bjt_ic_vbe(vbe, ic, ic_fitted), use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# NEWTON-RAPHSON
# ══════════════════════════════════════════════════════════════════════════════
with tab_nr:
    st.markdown("### Newton-Raphson — Penyelesaian Persamaan Nonlinear")

    with st.expander("Teori Newton-Raphson", expanded=False):
        st.markdown(r"""
        **Newton-Raphson** adalah metode iteratif untuk mencari akar persamaan nonlinear $f(x) = 0$:

        $$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}$$

        Metode ini memiliki konvergensi **kuadratik** (orde 2) di dekat akar, sehingga sangat
        cepat untuk menghitung titik bias semikonduktor, frekuensi cut-off, dan konstanta waktu transien.
        """)

    nr_options = [
        "Titik Operasi Dioda (V_D & I_D)",
        "Titik Bias Transistor BJT (V_BE untuk target I_C)",
        "Frekuensi Cutoff Band-Pass Filter (-3 dB)",
        "Frekuensi Resonansi RLC",
        "Konstanta Waktu RC Charging",
        "Konstanta Waktu RC Discharging",
        "Persamaan Kustom f(x) = 0"
    ]
    nr_mode = st.selectbox("Pilih Aplikasi Newton-Raphson:", nr_options)

    # 1. Dioda
    if nr_mode == "Titik Operasi Dioda (V_D & I_D)":
        st.markdown("**Cari V_D dan I_D pada titik kerja rangkaian dioda:**")
        c1, c2 = st.columns(2)
        V_s = c1.number_input("Tegangan Sumber V_s (V)", 0.1, 50.0, 5.0)
        R   = c2.number_input("Resistor Seri R (Ω)", 10.0, 100000.0, 1000.0)
        c3, c4 = st.columns(2)
        I_s = c3.number_input("Arus Saturasi I_s (A)", 1e-15, 1e-8, 1e-12, format="%.2e")
        V_T = c4.number_input("Tegangan Termal V_T (V)", 0.02, 0.04, 0.02585)

        if st.button("Jalankan Newton-Raphson (Dioda)", type="primary"):
            result = find_diode_operating_point(V_s, R, I_s, V_T)
            st.session_state["nr_result"] = result

            st.success(f"{'Konvergen' if result['converged'] else 'Selesai'} dalam {result['iterations']} iterasi")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("VD (Tegangan Dioda)", f"{result['V_D']:.4f} V")
            col2.metric("ID (Arus Dioda)", f"{result['I_D']*1000:.4f} mA")
            col3.metric("|f(x)| Akhir", f"{abs(result['f_root']):.2e}")
            col4.metric("Iterasi", result["iterations"])

            st.plotly_chart(plot_newton_raphson_convergence(result["history"]), use_container_width=True)

    # 2. BJT Bias
    elif nr_mode == "Titik Bias Transistor BJT (V_BE untuk target I_C)":
        st.markdown("**Cari tegangan basis V_BE untuk mencapai target arus kolektor I_C:**")
        c1, c2 = st.columns(2)
        target_ic = c1.number_input("Target Arus Kolektor I_C (mA)", 0.01, 500.0, 2.0) * 1e-3
        Is_bjt    = c2.number_input("Arus Saturasi Is (A)", 1e-16, 1e-9, 1e-14, format="%.2e")
        Vt_bjt    = st.number_input("Tegangan Termal Vt (V)", 0.02, 0.04, 0.026)

        if st.button("Selesaikan Bias BJT (Newton-Raphson)", type="primary"):
            res = find_bjt_vbe_bias(target_ic, Is_bjt, Vt_bjt)
            st.session_state["nr_result"] = res
            st.success(f"Konvergen: V_BE yang dibutuhkan = {res['V_BE']:.4f} V")
            col1, col2, col3 = st.columns(3)
            col1.metric("V_BE Diperlukan", f"{res['V_BE']:.4f} V")
            col2.metric("Target I_C", f"{target_ic*1000:.2f} mA")
            col3.metric("Iterasi", res["iterations"])
            st.plotly_chart(plot_newton_raphson_convergence(res["history"]), use_container_width=True)

    # 3. Bandpass Cutoff
    elif nr_mode == "Frekuensi Cutoff Band-Pass Filter (-3 dB)":
        st.markdown("**Cari frekuensi batas atas (f_c2) atau batas bawah (f_c1) pada level -3 dB:**")
        c1, c2, c3 = st.columns(3)
        R_bp = c1.number_input("Resistor R (Ω)", 1.0, 5000.0, 50.0)
        L_bp = c2.number_input("Induktor L (mH)", 0.1, 1000.0, 10.0) * 1e-3
        C_bp = c3.number_input("Kapasitor C (µF)", 0.01, 100.0, 1.0) * 1e-6
        side = st.radio("Pilih Sisi Cutoff:", ["low (f_c1)", "high (f_c2)"], horizontal=True)

        if st.button("Cari Frekuensi Cutoff -3dB", type="primary"):
            res = find_bandpass_cutoff(R_bp, L_bp, C_bp, side="low" if "low" in side else "high")
            st.session_state["nr_result"] = res
            st.success(f"Frekuensi Cutoff {side} = {res['f_cutoff']:.2f} Hz (Pusat: {res['f_center']:.2f} Hz)")
            col1, col2 = st.columns(2)
            col1.metric("f_cutoff (-3 dB)", f"{res['f_cutoff']:.2f} Hz")
            col2.metric("Iterasi NR", res["iterations"])
            st.plotly_chart(plot_newton_raphson_convergence(res["history"]), use_container_width=True)

    # 4. RLC Resonansi
    elif nr_mode == "Frekuensi Resonansi RLC":
        st.markdown("**Hitung frekuensi resonansi dan cari L optimal:**")
        c1, c2, c3 = st.columns(3)
        L_val = c1.number_input("Induktansi L (mH)", 0.1, 1000.0, 10.0) * 1e-3
        C_val = c2.number_input("Kapasitansi C (µF)", 0.01, 100.0, 1.0) * 1e-6
        f_tgt = c3.number_input("Target Frekuensi (Hz, opsional)", 0.0, 1e6, 0.0)

        if st.button("Hitung Resonansi RLC", type="primary"):
            result = find_rlc_resonance(L_val, C_val, target_freq=f_tgt if f_tgt > 0 else None)
            st.success(f"Frekuensi resonansi: {result['resonance_freq_Hz']:.4f} Hz")
            col1, col2 = st.columns(2)
            col1.metric("fr (Hz)", f"{result['resonance_freq_Hz']:.4f}")
            col2.metric("omega_r (rad/s)", f"{result['resonance_omega']:.4f}")
            if f_tgt > 0 and "optimal_L_for_target_freq" in result:
                st.metric("L Optimal untuk target fr", f"{result['optimal_L_for_target_freq']*1e3:.4f} mH")

    # 5. RC Charging Time Constant
    elif nr_mode == "Konstanta Waktu RC Charging":
        st.markdown("**Cari konstanta waktu tau dari titik pengukuran charging:**")
        c1, c2, c3 = st.columns(3)
        V_in_nr = c1.number_input("V_in (V)", 1.0, 50.0, 5.0)
        V_t_nr  = c2.number_input("V terukur pada waktu t (V)", 0.01, 49.9, 3.16)
        t_nr    = c3.number_input("Waktu t (ms)", 0.001, 1000.0, 1.0) * 1e-3

        if st.button("Cari Konstanta Waktu tau (Charging)", type="primary"):
            if V_t_nr >= V_in_nr:
                st.error("V terukur harus < V_in!")
            else:
                result = find_rc_time_constant(V_in_nr, V_t_nr, t_nr)
                if result:
                    st.session_state["nr_result"] = result
                    st.success(f"tau = RC = {result['root']*1000:.4f} ms")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("tau (ms)", f"{result['root']*1000:.4f}")
                    col2.metric("|f(tau)|", f"{abs(result['f_root']):.2e}")
                    col3.metric("Iterasi", result["iterations"])
                    st.plotly_chart(plot_newton_raphson_convergence(result["history"]), use_container_width=True)

    # 6. RC Discharging Time Constant
    elif nr_mode == "Konstanta Waktu RC Discharging":
        st.markdown("**Cari konstanta waktu tau dari titik pengosongan (discharging):**")
        c1, c2, c3 = st.columns(3)
        V0_nr   = c1.number_input("Tegangan Awal V0 (V)", 1.0, 50.0, 5.0)
        Vt_dis  = c2.number_input("V terukur saat discharging (V)", 0.01, 49.9, 1.84)
        t_dis   = c3.number_input("Waktu t (ms)", 0.001, 1000.0, 1.0) * 1e-3

        if st.button("Cari Konstanta Waktu tau (Discharging)", type="primary"):
            result = find_rc_discharge_constant(V0_nr, Vt_dis, t_dis)
            if result:
                st.session_state["nr_result"] = result
                st.success(f"tau = RC = {result['root']*1000:.4f} ms")
                col1, col2, col3 = st.columns(3)
                col1.metric("tau (ms)", f"{result['root']*1000:.4f}")
                col2.metric("|f(tau)|", f"{abs(result['f_root']):.2e}")
                col3.metric("Iterasi", result["iterations"])
                st.plotly_chart(plot_newton_raphson_convergence(result["history"]), use_container_width=True)

    # 7. Persamaan Kustom
    else:
        st.markdown("**Masukkan persamaan kustom f(x) = 0:**")
        st.markdown("> Gunakan sintaks Python. Variabel: `x`. Contoh: `x**3 - 2*x - 5`")
        expr = st.text_input("f(x) =", value="x**3 - 2*x - 5")
        c1, c2 = st.columns(2)
        x0_custom  = c1.number_input("Tebakan Awal x0", -1e6, 1e6, 2.0)
        eps_custom = c2.number_input("Epsilon FD", 1e-10, 1e-3, 1e-7, format="%.2e")

        if st.button("Selesaikan f(x) = 0", type="primary"):
            try:
                f = lambda x: eval(expr, {"x": x, "np": np, "__builtins__": {}})
                df_num = lambda x: (f(x + eps_custom) - f(x)) / eps_custom
                result = newton_raphson_scalar(f, df_num, x0_custom)
                st.session_state["nr_result"] = result
                st.success(f"Akar ditemukan: x = {result['root']:.8f}, f(x) = {result['f_root']:.4e}")
                st.plotly_chart(plot_newton_raphson_convergence(result["history"]), use_container_width=True)
            except Exception as e:
                st.error(f"Error pada ekspresi: {e}")
