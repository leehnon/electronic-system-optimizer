import streamlit as st
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.evaluation import evaluate_metrics, parameter_sensitivity, convergence_rate
from modules.visualization import plot_residuals, plot_sensitivity
from modules.data_generator import ensure_default_data

st.set_page_config(page_title="Evaluation", layout="wide")
inject_css()
ensure_default_data()

st.title("Evaluation")
st.markdown("Evaluasi akurasi model dan perbandingan hasil numerik vs referensi.")

if "gd_result" not in st.session_state:
    st.warning("Belum ada hasil komputasi. Jalankan Gradient Descent terlebih dahulu.")
    st.stop()

result  = st.session_state["gd_result"]
circuit = st.session_state.get("circuit", "RC Charging")
df      = st.session_state["data"]
true_p  = st.session_state.get("true_params", {})
p_opt   = result["optimal_params"]

# ── Hitung prediksi ───────────────────────────────────────────────────────────
if circuit == "RC Charging":
    t, V = df["time_s"].values, df["voltage_V"].values
    V_in = float(true_p.get("V_in", 5.0))
    R_opt, C_opt = p_opt
    tau_opt = max(R_opt * C_opt, 1e-15)
    y_pred  = V_in * (1 - np.exp(-t / tau_opt))
    y_true  = V
    param_names = ["R (Ω)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("C")]

elif circuit == "RC Discharging":
    t, V = df["time_s"].values, df["voltage_V"].values
    V0 = float(true_p.get("V0", 5.0))
    R_opt, C_opt = p_opt
    tau_opt = max(R_opt * C_opt, 1e-15)
    y_pred  = V0 * np.exp(-t / tau_opt)
    y_true  = V
    param_names = ["R (Ω)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("C")]

elif circuit in ["RLC Seri (Impedansi)", "RLC Impedansi"]:
    freqs = df["frequency_Hz"].values
    Z     = df["impedance_ohm"].values
    R_opt, L_opt, C_opt = p_opt
    omega  = 2 * np.pi * freqs
    reactance = omega * L_opt - 1.0 / (omega * C_opt)
    y_pred = np.sqrt(R_opt**2 + reactance**2)
    y_true = Z
    param_names = ["R (Ω)", "L (H)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("L"), true_p.get("C")]

elif circuit == "Band-Pass Filter RLC":
    freqs = df["frequency_Hz"].values
    gain  = df["gain_linear"].values
    R_opt, L_opt, C_opt = p_opt
    omega = 2 * np.pi * freqs
    reactance = omega * L_opt - 1.0 / (omega * C_opt)
    y_pred = R_opt / np.sqrt(R_opt**2 + reactance**2)
    y_true = gain
    param_names = ["R (Ω)", "L (H)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("L"), true_p.get("C")]

elif circuit in ["Amplifier", "Amplifier (Single-Pole)"]:
    freqs  = df["frequency_Hz"].values
    G      = df["gain"].values
    A0_opt, fc_opt = p_opt
    y_pred = A0_opt / np.sqrt(1 + (freqs / max(fc_opt, 1e-3))**2)
    y_true = G
    param_names = ["A0", "f_c (Hz)"]
    true_vals = [true_p.get("A0"), true_p.get("f_cutoff")]

elif circuit == "Transistor BJT":
    vbe = df["V_be_V"].values
    ic  = df["I_c_A"].values
    Is_opt, Vt_opt = p_opt
    y_pred = Is_opt * (np.exp(np.clip(vbe / Vt_opt, 0, 40)) - 1)
    y_true = ic
    param_names = ["Is (A)", "Vt (V)"]
    true_vals = [true_p.get("I_s"), true_p.get("V_T")]

else:
    st.info("Evaluasi otomatis tersedia untuk rangkaian dengan hasil fitting terukur.")
    st.stop()

metrics = evaluate_metrics(y_true, y_pred)

# ── Metrik Utama ──────────────────────────────────────────────────────────────
st.markdown("## Metrik Akurasi")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("MSE",           f"{metrics['MSE']:.4e}")
col2.metric("RMSE",          f"{metrics['RMSE']:.4e}")
col3.metric("MAE",           f"{metrics['MAE']:.4e}")
col4.metric("R² (Determinasi)", f"{metrics['R²']:.6f}")
col5.metric("MAPE",          f"{metrics['MAPE (%)']:.3f}%")

r2 = metrics["R²"]
if r2 > 0.99:
    st.success(f"Model sangat akurat: R² = {r2:.6f} (>0.99 — fitting sangat presisi)")
elif r2 > 0.95:
    st.info(f"Model baik: R² = {r2:.6f} (>0.95)")
elif r2 > 0.90:
    st.warning(f"Model cukup: R² = {r2:.6f} (>0.90 — pertimbangkan tuning learning rate)")
else:
    st.error(f"Model kurang optimal: R² = {r2:.6f} — periksa data atau tebakan awal")

st.markdown("---")

# ── Perbandingan Parameter ────────────────────────────────────────────────────
st.markdown("## Perbandingan Parameter: Optimal vs True")
rows = []
for i, name in enumerate(param_names):
    p_true = true_vals[i] if i < len(true_vals) else None
    p_est  = p_opt[i]
    err_pct = abs(p_est - p_true) / abs(p_true) * 100 if (p_true is not None and p_true != 0) else None
    rows.append({
        "Parameter":     name,
        "Nilai True":    f"{p_true:.6e}" if p_true is not None else "N/A",
        "Nilai Optimal": f"{p_est:.6e}",
        "Galat (%)":     f"{err_pct:.4f}%" if err_pct is not None else "N/A",
        "Status":        "Sangat Baik (<1%)" if (err_pct and err_pct < 1) else
                         "Toleransi (<5%)" if (err_pct and err_pct < 5) else
                         "Perlu Tuning" if err_pct else "-"
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.markdown("---")

# ── Konvergensi ───────────────────────────────────────────────────────────────
st.markdown("## Analisis Konvergensi")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Iterasi Total",     result["iterations"])
col_b.metric("Cost Awal",         f"{result['history']['cost'][0]:.4e}")
col_c.metric("Cost Akhir",        f"{result['final_cost']:.4e}")

cr = convergence_rate(result["history"]["cost"])
if cr:
    if cr < 1.0:
        st.success(f"Laju konvergensi rata-rata: {cr:.4f} (< 1 — proses stabil)")
    else:
        st.error(f"Laju konvergensi: {cr:.4f} (≥ 1 — kurangi learning rate)")

st.markdown("---")

# ── Residual Analysis ─────────────────────────────────────────────────────────
st.markdown("## Analisis Residual")
residuals = metrics["Residuals"]
st.markdown(f"""
| Statistik Residual | Nilai |
|---|---|
| Mean Residual | `{np.mean(residuals):.4e}` |
| Std Deviasi Residual | `{np.std(residuals):.4e}` |
| Max Abs Residual | `{np.max(np.abs(residuals)):.4e}` |
| Min Abs Residual | `{np.min(np.abs(residuals)):.4e}` |
""")
st.plotly_chart(plot_residuals(residuals), use_container_width=True)

# ── Sensitivitas ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Sensitivitas Parameter (±5%)")

cost_f = None
if circuit == "RC Charging":
    from modules.gradient_descent import rc_voltage_error
    t_arr, V_arr = df["time_s"].values, df["voltage_V"].values
    V_in_v = float(true_p.get("V_in", 5.0))
    cost_f = lambda p: rc_voltage_error(p, t_arr, V_arr, V_in_v)

elif circuit == "RC Discharging":
    from modules.gradient_descent import rc_discharge_error
    t_arr, V_arr = df["time_s"].values, df["voltage_V"].values
    V0_v = float(true_p.get("V0", 5.0))
    cost_f = lambda p: rc_discharge_error(p, t_arr, V_arr, V0_v)

elif circuit in ["RLC Seri (Impedansi)", "RLC Impedansi"]:
    from modules.gradient_descent import rlc_impedance_error
    cost_f = lambda p: rlc_impedance_error(p, df["frequency_Hz"].values, df["impedance_ohm"].values)

elif circuit == "Band-Pass Filter RLC":
    from modules.gradient_descent import bandpass_filter_error
    cost_f = lambda p: bandpass_filter_error(p, df["frequency_Hz"].values, df["gain_linear"].values)

elif circuit in ["Amplifier", "Amplifier (Single-Pole)"]:
    from modules.gradient_descent import amplifier_gain_error
    cost_f = lambda p: amplifier_gain_error(p, df["frequency_Hz"].values, df["gain"].values)

elif circuit == "Transistor BJT":
    from modules.gradient_descent import bjt_collector_error
    cost_f = lambda p: bjt_collector_error(p, df["V_be_V"].values, df["I_c_A"].values)

if cost_f:
    sens_df = parameter_sensitivity(cost_f, p_opt, param_names)
    st.plotly_chart(plot_sensitivity(sens_df), use_container_width=True)
    st.dataframe(sens_df, use_container_width=True)
