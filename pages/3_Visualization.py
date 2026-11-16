import streamlit as st
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.visualization import (plot_rc_charging, plot_rlc_impedance, plot_amplifier_gain,
                                    plot_convergence, plot_newton_raphson_convergence,
                                    plot_residuals, plot_sensitivity, plot_diode_iv)
from modules.evaluation import evaluate_metrics, parameter_sensitivity, convergence_rate

st.set_page_config(page_title="Visualization", page_icon="📈", layout="wide")
inject_css()
st.title("Visualization")
st.markdown("Grafik interaktif hasil optimasi parameter elektronika.")

has_gd = "gd_result" in st.session_state
has_nr = "nr_result" in st.session_state
has_data = "data" in st.session_state

if not has_data:
    st.warning("⚠️ Belum ada data! Silakan ke menu **Data Management** terlebih dahulu.")
    st.stop()

circuit = st.session_state.get("circuit", "")
df      = st.session_state["data"]
true_p  = st.session_state.get("true_params", {})

tab1, tab2, tab3, tab4 = st.tabs(["📊 Data & Fitting", "🔄 Konvergensi",
                                   "📉 Residual", "🎛️ Sensitivitas"])

# ── Tab 1: Data & Fitting ─────────────────────────────────────────────────────
with tab1:
    st.markdown("### 📊 Perbandingan Data vs Model Optimal")
    if has_gd:
        result = st.session_state["gd_result"]
        p_opt  = result["optimal_params"]

        if circuit == "RC Charging":
            t   = df["time_s"].values
            V   = df["voltage_V"].values
            V_in = true_p.get("V_in", 5.0)
            R_opt, C_opt = p_opt
            tau_opt = R_opt * C_opt
            V_fitted = V_in * (1 - np.exp(-t / max(tau_opt, 1e-15)))
            st.plotly_chart(plot_rc_charging(t, V, V_fitted,
                                             tau_true=true_p.get("tau"),
                                             tau_fitted=tau_opt),
                            use_container_width=True)
            metrics = evaluate_metrics(V, V_fitted)
            st.session_state["metrics"] = metrics
            st.session_state["y_true"]  = V
            st.session_state["y_pred"]  = V_fitted

        elif circuit == "RLC Impedansi":
            freqs = df["frequency_Hz"].values
            Z     = df["impedance_ohm"].values
            R_opt, L_opt, C_opt = p_opt
            omega  = 2*np.pi*freqs
            Z_fitted = np.sqrt(R_opt**2 + (omega*L_opt - 1/(omega*C_opt))**2)
            f_r = 1/(2*np.pi*np.sqrt(max(L_opt,1e-15)*max(C_opt,1e-15)))
            st.plotly_chart(plot_rlc_impedance(freqs, Z, Z_fitted, f_r),
                            use_container_width=True)
            metrics = evaluate_metrics(Z, Z_fitted)
            st.session_state["metrics"] = metrics
            st.session_state["y_true"]  = Z
            st.session_state["y_pred"]  = Z_fitted

        elif circuit == "Amplifier":
            freqs  = df["frequency_Hz"].values
            G      = df["gain"].values
            A0_opt, fc_opt = p_opt
            G_fitted = A0_opt / np.sqrt(1 + (freqs/max(fc_opt,1e-3))**2)
            st.plotly_chart(plot_amplifier_gain(freqs, G, G_fitted, fc_opt),
                            use_container_width=True)
            metrics = evaluate_metrics(G, G_fitted)
            st.session_state["metrics"] = metrics
            st.session_state["y_true"]  = G
            st.session_state["y_pred"]  = G_fitted
    else:
        if circuit == "Dioda":
            st.plotly_chart(plot_diode_iv(df["V_source_V"], df["V_diode_V"],
                                          df["I_diode_A"]), use_container_width=True)
        else:
            st.info("💡 Jalankan Gradient Descent terlebih dahulu di menu **Numerical Computation**.")

# ── Tab 2: Konvergensi ────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔄 Grafik Konvergensi Algoritma")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Gradient Descent")
        if has_gd:
            st.plotly_chart(plot_convergence(st.session_state["gd_result"]["history"]),
                            use_container_width=True)
            cr = convergence_rate(st.session_state["gd_result"]["history"]["cost"])
            if cr: st.metric("Rata-rata Rasio Konvergensi", f"{cr:.4f}")
        else:
            st.info("Belum ada hasil Gradient Descent.")

    with col_b:
        st.markdown("#### Newton-Raphson")
        if has_nr:
            st.plotly_chart(plot_newton_raphson_convergence(
                st.session_state["nr_result"]["history"]), use_container_width=True)
        else:
            st.info("Belum ada hasil Newton-Raphson.")

# ── Tab 3: Residual ───────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📉 Analisis Residual")
    if "metrics" in st.session_state:
        metrics = st.session_state["metrics"]
        residuals = metrics["Residuals"]

        col1,col2,col3,col4,col5 = st.columns(5)
        col1.metric("MSE",  f"{metrics['MSE']:.4e}")
        col2.metric("RMSE", f"{metrics['RMSE']:.4e}")
        col3.metric("MAE",  f"{metrics['MAE']:.4e}")
        col4.metric("R²",   f"{metrics['R²']:.6f}")
        col5.metric("MAPE", f"{metrics['MAPE (%)']:.3f}%")

        st.plotly_chart(plot_residuals(residuals), use_container_width=True)
    else:
        st.info("💡 Jalankan fitting terlebih dahulu untuk melihat residual.")

# ── Tab 4: Sensitivitas ───────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🎛️ Analisis Sensitivitas Parameter")
    if has_gd:
        result  = st.session_state["gd_result"]
        p_opt   = result["optimal_params"]
        circuit = st.session_state.get("circuit", "")

        if circuit == "RC Charging":
            from modules.gradient_descent import rc_voltage_error
            t, V = df["time_s"].values, df["voltage_V"].values
            V_in = true_p.get("V_in", 5.0)
            cost_f = lambda p: rc_voltage_error(p, t, V, V_in)
            names  = ["R (Ω)", "C (F)"]
        elif circuit == "RLC Impedansi":
            from modules.gradient_descent import rlc_impedance_error
            freqs = df["frequency_Hz"].values
            Z     = df["impedance_ohm"].values
            cost_f = lambda p: rlc_impedance_error(p, freqs, Z)
            names  = ["R (Ω)", "L (H)", "C (F)"]
        elif circuit == "Amplifier":
            from modules.gradient_descent import amplifier_gain_error
            freqs = df["frequency_Hz"].values
            G     = df["gain"].values
            cost_f = lambda p: amplifier_gain_error(p, freqs, G)
            names  = ["A0 (gain)", "f_c (Hz)"]
        else:
            cost_f = None; names = []

        if cost_f:
            perturb = st.slider("Perturbasi Parameter (%)", 1, 20, 5) / 100
            sens_df = parameter_sensitivity(cost_f, p_opt, names, perturb)
            st.plotly_chart(plot_sensitivity(sens_df), use_container_width=True)
            st.dataframe(sens_df.style.format({
                col: "{:.4e}" for col in sens_df.columns if col != "Parameter"
            }), use_container_width=True)
    else:
        st.info("💡 Jalankan Gradient Descent terlebih dahulu.")
