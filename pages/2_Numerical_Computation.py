import streamlit as st
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.gradient_descent import (gradient_descent,
    rlc_impedance_error, rlc_impedance_grad,
    rc_voltage_error,   rc_voltage_grad,
    amplifier_gain_error, amplifier_gain_grad)
from modules.newton_raphson import (newton_raphson_scalar,
    find_diode_operating_point, find_rlc_resonance, find_rc_time_constant)
from modules.visualization import (plot_convergence, plot_newton_raphson_convergence,
                                    plot_rc_charging, plot_rlc_impedance, plot_amplifier_gain)
from modules.data_generator import ensure_default_data

st.set_page_config(page_title="Numerical Computation", page_icon="🔢", layout="wide")
inject_css()
ensure_default_data()

st.title("Numerical Computation")

if "data" not in st.session_state:
    st.warning("⚠️ Belum ada data! Silakan generate atau upload data di menu **Data Management** dulu.")
    st.stop()

circuit = st.session_state.get("circuit", "RC Charging")
df      = st.session_state["data"]
true_p  = st.session_state.get("true_params", {})

st.info(f"📌 Rangkaian aktif: **{circuit}**")
st.markdown("---")

# ── Tab algoritma ──────────────────────────────────────────────────────────────
tab_gd, tab_nr = st.tabs(["🔁 Gradient Descent", "📐 Newton-Raphson"])

# ══════════════════════════════════════════════════════════════════════════════
# GRADIENT DESCENT
# ══════════════════════════════════════════════════════════════════════════════
with tab_gd:
    st.markdown("### 🔁 Gradient Descent — Optimasi Parameter")

    with st.expander("📖 Teori Gradient Descent", expanded=False):
        st.markdown(r"""
        **Gradient Descent** adalah algoritma iteratif untuk mencari minimum fungsi biaya:

        $$\theta_{k+1} = \theta_k - \alpha \cdot \nabla f(\theta_k)$$

        - $\theta$: vektor parameter (R, L, C, dll.)
        - $\alpha$: learning rate (laju belajar)
        - $\nabla f$: gradien fungsi biaya (dihitung numerik)

        **Fungsi biaya** yang digunakan adalah **MSE (Mean Squared Error)**:
        $$f(\theta) = \frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i(\theta))^2$$
        """)

    if circuit == "RC Charging":
        st.markdown("**Parameter awal untuk RC Charging:**")
        c1, c2 = st.columns(2)
        R_init = c1.number_input("R awal (Ω)", 100.0, 1e6, true_p.get("R", 1000.0) * 1.3,
                                  help="Tebakan awal R (berbeda dari nilai asli)")
        C_init = c2.number_input("C awal (µF)", 0.1, 1000.0,
                                  true_p.get("C", 1e-6) * 1e6 * 0.7) * 1e-6
        c3, c4 = st.columns(2)
        lr       = c3.number_input("Learning Rate (α)", 1e-10, 1.0, 1e-6, format="%.2e")
        max_iter = c4.number_input("Maks. Iterasi", 10, 5000, 1000)
        tol      = st.number_input("Toleransi Konvergensi", 1e-12, 1e-3, 1e-7, format="%.2e")

        if st.button("▶ Jalankan Gradient Descent (RC)", type="primary"):
            t   = df["time_s"].values
            V   = df["voltage_V"].values
            V_in = true_p.get("V_in", 5.0)

            cost_f = lambda p: rc_voltage_error(p, t, V, V_in)
            grad_f = lambda p: rc_voltage_grad(p, t, V, V_in)

            with st.spinner("Menjalankan Gradient Descent..."):
                result = gradient_descent(cost_f, grad_f,
                                          params_init=[R_init, C_init],
                                          learning_rate=lr,
                                          max_iter=int(max_iter), tol=tol)

            R_opt, C_opt = result["optimal_params"]
            tau_opt = R_opt * C_opt
            tau_true = true_p.get("tau", None)

            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'✅ Konvergen' if result['converged'] else '⚠️ Belum konvergen'} "
                       f"dalam **{result['iterations']}** iterasi")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R Optimal", f"{R_opt:.2f} Ω",
                        f"{(R_opt/true_p.get('R',R_opt)-1)*100:.1f}% error" if true_p.get("R") else "")
            col2.metric("C Optimal", f"{C_opt*1e6:.4f} µF",
                        f"{(C_opt/true_p.get('C',C_opt)-1)*100:.1f}% error" if true_p.get("C") else "")
            col3.metric("τ Optimal", f"{tau_opt:.5f} s")
            col4.metric("Final Cost (MSE)", f"{result['final_cost']:.4e}")

            # Grafik perbandingan
            V_fitted = V_in * (1 - np.exp(-t / max(tau_opt, 1e-15)))
            st.plotly_chart(plot_rc_charging(t, V, V_fitted,
                                             tau_true=tau_true, tau_fitted=tau_opt),
                            use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    elif circuit == "RLC Impedansi":
        st.markdown("**Parameter awal untuk RLC:**")
        c1, c2, c3 = st.columns(3)
        R_init = c1.number_input("R awal (Ω)", 1.0, 1000.0, true_p.get("R", 10.0)*1.2)
        L_init = c2.number_input("L awal (mH)", 0.1, 1000.0,
                                  true_p.get("L", 0.01)*1e3*0.8) * 1e-3
        C_init = c3.number_input("C awal (µF)", 0.01, 100.0,
                                  true_p.get("C", 1e-6)*1e6*1.3) * 1e-6
        c4, c5 = st.columns(2)
        lr       = c4.number_input("Learning Rate (α)", 1e-14, 1e-3, 1e-10, format="%.2e")
        max_iter = c5.number_input("Maks. Iterasi", 10, 5000, 2000)

        if st.button("▶ Jalankan Gradient Descent (RLC)", type="primary"):
            freqs = df["frequency_Hz"].values
            Z     = df["impedance_ohm"].values

            cost_f = lambda p: rlc_impedance_error(p, freqs, Z)
            grad_f = lambda p: rlc_impedance_grad(p, freqs, Z)

            with st.spinner("Menjalankan Gradient Descent..."):
                result = gradient_descent(cost_f, grad_f,
                                          params_init=[R_init, L_init, C_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            R_opt, L_opt, C_opt = result["optimal_params"]
            f_r_opt = 1/(2*np.pi*np.sqrt(max(L_opt,1e-15)*max(C_opt,1e-15)))

            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'✅ Konvergen' if result['converged'] else '⚠️ Belum konvergen'} "
                       f"dalam **{result['iterations']}** iterasi")
            col1,col2,col3,col4 = st.columns(4)
            col1.metric("R Optimal", f"{R_opt:.3f} Ω")
            col2.metric("L Optimal", f"{L_opt*1e3:.3f} mH")
            col3.metric("C Optimal", f"{C_opt*1e6:.4f} µF")
            col4.metric("f_r Optimal", f"{f_r_opt:.2f} Hz")

            omega = 2*np.pi*freqs
            Z_fitted = np.sqrt(R_opt**2 + (omega*L_opt - 1/(omega*C_opt))**2)
            st.plotly_chart(plot_rlc_impedance(freqs, Z, Z_fitted, f_r_opt),
                            use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    elif circuit == "Amplifier":
        st.markdown("**Parameter awal untuk Amplifier:**")
        c1, c2 = st.columns(2)
        A0_init = c1.number_input("A0 awal", 1.0, 10000.0, true_p.get("A0", 100.0)*0.8)
        fc_init = c2.number_input("f_c awal (Hz)", 10.0, 1e5, true_p.get("f_cutoff",1000.0)*1.3)
        c3, c4  = st.columns(2)
        lr       = c3.number_input("Learning Rate (α)", 1e-10, 10.0, 0.01, format="%.4f")
        max_iter = c4.number_input("Maks. Iterasi", 10, 5000, 1000)

        if st.button("▶ Jalankan Gradient Descent (Amplifier)", type="primary"):
            freqs = df["frequency_Hz"].values
            G     = df["gain"].values

            cost_f = lambda p: amplifier_gain_error(p, freqs, G)
            grad_f = lambda p: amplifier_gain_grad(p, freqs, G)

            with st.spinner("Menjalankan Gradient Descent..."):
                result = gradient_descent(cost_f, grad_f,
                                          params_init=[A0_init, fc_init],
                                          learning_rate=lr, max_iter=int(max_iter))

            A0_opt, fc_opt = result["optimal_params"]
            st.session_state["gd_result"]  = result
            st.session_state["gd_circuit"] = circuit

            st.success(f"{'✅ Konvergen' if result['converged'] else '⚠️ Belum konvergen'} "
                       f"dalam **{result['iterations']}** iterasi")
            col1,col2,col3 = st.columns(3)
            col1.metric("A0 Optimal", f"{A0_opt:.3f}")
            col2.metric("f_c Optimal", f"{fc_opt:.2f} Hz")
            col3.metric("Final MSE", f"{result['final_cost']:.4e}")

            G_fitted = A0_opt / np.sqrt(1 + (freqs / max(fc_opt,1e-3))**2)
            st.plotly_chart(plot_amplifier_gain(freqs, G, G_fitted, fc_opt),
                            use_container_width=True)
            st.plotly_chart(plot_convergence(result["history"]), use_container_width=True)

    else:
        st.info("💡 Untuk rangkaian Dioda, gunakan tab **Newton-Raphson**.")

# ══════════════════════════════════════════════════════════════════════════════
# NEWTON-RAPHSON
# ══════════════════════════════════════════════════════════════════════════════
with tab_nr:
    st.markdown("### 📐 Newton-Raphson — Penyelesaian Persamaan Nonlinear")

    with st.expander("📖 Teori Newton-Raphson", expanded=False):
        st.markdown(r"""
        **Newton-Raphson** adalah metode iteratif untuk mencari akar persamaan $f(x) = 0$:

        $$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}$$

        Metode ini memiliki konvergensi **kuadratik** (orde 2) di dekat akar, sehingga sangat
        cepat untuk persamaan nonlinear rangkaian elektronika.
        """)

    nr_mode = st.selectbox("Pilih Aplikasi Newton-Raphson:", [
        "Titik Operasi Dioda",
        "Frekuensi Resonansi RLC",
        "Konstanta Waktu RC (dari titik pengukuran)",
        "Persamaan Kustom f(x) = 0"
    ])

    if nr_mode == "Titik Operasi Dioda":
        st.markdown("**Cari V_D dan I_D pada titik operasi dioda:**")
        c1, c2 = st.columns(2)
        V_s = c1.number_input("Tegangan Sumber V_s (V)", 0.1, 20.0, 5.0)
        R   = c2.number_input("Resistor Seri R (Ω)", 10.0, 100000.0, 1000.0)
        c3, c4 = st.columns(2)
        I_s = c3.number_input("Arus Saturasi I_s (A)", 1e-15, 1e-9, 1e-12, format="%.2e")
        V_T = c4.number_input("Tegangan Termal V_T (V)", 0.02, 0.04, 0.02585)

        if st.button("▶ Jalankan Newton-Raphson (Dioda)", type="primary"):
            with st.spinner("Menghitung..."):
                result = find_diode_operating_point(V_s, R, I_s, V_T)
            st.session_state["nr_result"] = result

            st.success(f"{'✅ Konvergen' if result['converged'] else '⚠️ Belum konvergen'} "
                       f"dalam **{result['iterations']}** iterasi")
            col1,col2,col3,col4 = st.columns(4)
            col1.metric("V_D (Tegangan Dioda)", f"{result['V_D']:.4f} V")
            col2.metric("I_D (Arus Dioda)", f"{result['I_D']*1000:.4f} mA")
            col3.metric("|f(x)| Akhir", f"{abs(result['f_root']):.2e}")
            col4.metric("Iterasi", result["iterations"])

            st.plotly_chart(plot_newton_raphson_convergence(result["history"]),
                            use_container_width=True)

    elif nr_mode == "Frekuensi Resonansi RLC":
        st.markdown("**Hitung frekuensi resonansi dan cari L optimal:**")
        c1, c2, c3 = st.columns(3)
        L_val = c1.number_input("Induktansi L (mH)", 0.1, 1000.0, 10.0) * 1e-3
        C_val = c2.number_input("Kapasitansi C (µF)", 0.01, 100.0, 1.0) * 1e-6
        f_tgt = c3.number_input("Target Frekuensi (Hz, opsional)", 0.0, 1e6, 0.0)

        if st.button("▶ Hitung Resonansi RLC", type="primary"):
            result = find_rlc_resonance(L_val, C_val,
                                         target_freq=f_tgt if f_tgt > 0 else None)
            st.success(f"✅ Frekuensi resonansi: **{result['resonance_freq_Hz']:.4f} Hz**")
            col1,col2 = st.columns(2)
            col1.metric("f_r (Hz)", f"{result['resonance_freq_Hz']:.4f}")
            col2.metric("ω_r (rad/s)", f"{result['resonance_omega']:.4f}")
            if f_tgt > 0 and "optimal_L_for_target_freq" in result:
                L_opt = result["optimal_L_for_target_freq"]
                st.metric("L Optimal untuk target f_r", f"{L_opt*1e3:.4f} mH")

    elif nr_mode == "Konstanta Waktu RC (dari titik pengukuran)":
        st.markdown("**Cari τ = RC dari satu titik pengukuran:**")
        c1,c2,c3 = st.columns(3)
        V_in_nr = c1.number_input("V_in (V)", 1.0, 50.0, 5.0)
        V_t_nr  = c2.number_input("V terukur pada t (V)", 0.01, 49.9, 3.16)
        t_nr    = c3.number_input("Waktu pengukuran t (ms)", 0.001, 1000.0, 1.0) * 1e-3

        if st.button("▶ Cari Konstanta Waktu τ", type="primary"):
            if V_t_nr >= V_in_nr:
                st.error("V terukur harus < V_in!")
            else:
                result = find_rc_time_constant(V_in_nr, V_t_nr, t_nr)
                if result:
                    st.success(f"✅ τ = RC = **{result['root']*1000:.4f} ms**")
                    col1,col2,col3 = st.columns(3)
                    col1.metric("τ (ms)", f"{result['root']*1000:.4f}")
                    col2.metric("|f(τ)|", f"{abs(result['f_root']):.2e}")
                    col3.metric("Iterasi", result["iterations"])
                    st.plotly_chart(plot_newton_raphson_convergence(result["history"]),
                                    use_container_width=True)

    else:  # Kustom
        st.markdown("**Masukkan persamaan kustom f(x) = 0:**")
        st.markdown("> Gunakan sintaks Python. Variabel: `x`. Contoh: `x**3 - 2*x - 5`")
        expr = st.text_input("f(x) =", value="x**3 - 2*x - 5")
        c1,c2 = st.columns(2)
        x0_custom = c1.number_input("Tebakan Awal x₀", -1e6, 1e6, 2.0)
        eps_custom = c2.number_input("Epsilon FD (untuk f')", 1e-10, 1e-3, 1e-7, format="%.2e")

        if st.button("▶ Selesaikan f(x) = 0", type="primary"):
            try:
                f  = lambda x: eval(expr, {"x": x, "np": np, "__builtins__": {}})
                df_num = lambda x: (f(x + eps_custom) - f(x)) / eps_custom
                result = newton_raphson_scalar(f, df_num, x0_custom)
                st.success(f"✅ Akar ditemukan: x = **{result['root']:.8f}**, "
                           f"f(x) = {result['f_root']:.4e}")
                st.session_state["nr_result"] = result
                st.plotly_chart(plot_newton_raphson_convergence(result["history"]),
                                use_container_width=True)
            except Exception as e:
                st.error(f"Error pada ekspresi: {e}")
