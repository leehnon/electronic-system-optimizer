import streamlit as st
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.evaluation import evaluate_metrics, parameter_sensitivity, convergence_rate
from modules.visualization import plot_residuals, plot_sensitivity

st.set_page_config(page_title="Evaluation", page_icon="✅", layout="wide")
st.title("✅ Evaluation — Validasi & Metrik Numerik")
st.markdown("Evaluasi akurasi model dan perbandingan hasil numerik vs referensi.")

if "gd_result" not in st.session_state:
    st.warning("⚠️ Belum ada hasil komputasi. Jalankan Gradient Descent terlebih dahulu.")
    st.stop()

result  = st.session_state["gd_result"]
circuit = st.session_state.get("circuit", "")
df      = st.session_state["data"]
true_p  = st.session_state.get("true_params", {})
p_opt   = result["optimal_params"]

# ── Hitung prediksi ───────────────────────────────────────────────────────────
if circuit == "RC Charging":
    t, V = df["time_s"].values, df["voltage_V"].values
    V_in = true_p.get("V_in", 5.0)
    R_opt, C_opt = p_opt
    tau_opt = max(R_opt*C_opt, 1e-15)
    y_pred  = V_in * (1 - np.exp(-t/tau_opt))
    y_true  = V
    param_names = ["R (Ω)", "C (F)"]

elif circuit == "RLC Impedansi":
    freqs = df["frequency_Hz"].values
    Z     = df["impedance_ohm"].values
    R_opt, L_opt, C_opt = p_opt
    omega  = 2*np.pi*freqs
    y_pred = np.sqrt(R_opt**2 + (omega*L_opt - 1/(omega*C_opt))**2)
    y_true = Z
    param_names = ["R (Ω)", "L (H)", "C (F)"]

elif circuit == "Amplifier":
    freqs  = df["frequency_Hz"].values
    G      = df["gain"].values
    A0_opt, fc_opt = p_opt
    y_pred = A0_opt / np.sqrt(1 + (freqs/max(fc_opt,1e-3))**2)
    y_true = G
    param_names = ["A0", "f_c (Hz)"]

else:
    st.info("Evaluasi otomatis tersedia untuk RC, RLC, dan Amplifier.")
    st.stop()

metrics = evaluate_metrics(y_true, y_pred)

# ── Metrik Utama ──────────────────────────────────────────────────────────────
st.markdown("## 📊 Metrik Akurasi")
col1,col2,col3,col4,col5 = st.columns(5)
col1.metric("MSE",           f"{metrics['MSE']:.4e}")
col2.metric("RMSE",          f"{metrics['RMSE']:.4e}")
col3.metric("MAE",           f"{metrics['MAE']:.4e}")
col4.metric("R² (Koefisien Determinasi)", f"{metrics['R²']:.6f}")
col5.metric("MAPE",          f"{metrics['MAPE (%)']:.3f}%")

r2 = metrics["R²"]
if r2 > 0.99:
    st.success(f"🎯 Model sangat baik! R² = {r2:.6f} (>0.99 — fitting sangat akurat)")
elif r2 > 0.95:
    st.info(f"✅ Model baik. R² = {r2:.6f} (>0.95)")
elif r2 > 0.90:
    st.warning(f"⚠️ Model cukup. R² = {r2:.6f} (>0.90 — pertimbangkan tuning hyperparameter)")
else:
    st.error(f"❌ Model kurang baik. R² = {r2:.6f} — coba ubah learning rate atau tebakan awal")

st.markdown("---")

# ── Perbandingan Parameter ────────────────────────────────────────────────────
st.markdown("## 🔍 Perbandingan Parameter: Optimal vs True")
rows = []
for i, name in enumerate(param_names):
    p_true = list(true_p.values())[i] if i < len(true_p) else None
    p_est  = p_opt[i]
    err_pct = abs(p_est - p_true)/abs(p_true)*100 if p_true else None
    rows.append({
        "Parameter":        name,
        "Nilai True":       f"{p_true:.6e}" if p_true else "N/A",
        "Nilai Optimal":    f"{p_est:.6e}",
        "Error (%)":        f"{err_pct:.4f}%" if err_pct is not None else "N/A",
        "Status":           "✅ Baik (<1%)" if err_pct and err_pct<1 else
                            "⚠️ Toleransi" if err_pct and err_pct<5 else
                            "❌ Perlu tuning" if err_pct else "—"
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.markdown("---")

# ── Konvergensi ───────────────────────────────────────────────────────────────
st.markdown("## 🔄 Analisis Konvergensi")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Iterasi Total",     result["iterations"])
col_b.metric("Cost Awal",         f"{result['history']['cost'][0]:.4e}")
col_c.metric("Cost Akhir",        f"{result['final_cost']:.4e}")

cr = convergence_rate(result["history"]["cost"])
if cr:
    if cr < 1.0:
        st.success(f"✅ Laju konvergensi rata-rata: **{cr:.4f}** (< 1 → konvergen)")
    else:
        st.error(f"❌ Laju konvergensi: **{cr:.4f}** (≥ 1 → perlu turunkan learning rate)")

st.markdown("---")

# ── Residual Analysis ─────────────────────────────────────────────────────────
st.markdown("## 📉 Analisis Residual")
residuals = metrics["Residuals"]
st.markdown(f"""
| Statistik | Nilai |
|---|---|
| Mean Residual | `{np.mean(residuals):.4e}` |
| Std Residual | `{np.std(residuals):.4e}` |
| Max |Residual| | `{np.max(np.abs(residuals)):.4e}` |
| Min |Residual| | `{np.min(np.abs(residuals)):.4e}` |
""")
st.plotly_chart(plot_residuals(residuals), use_container_width=True)

# ── Sensitivitas ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🎛️ Sensitivitas Parameter (±5%)")

if circuit == "RC Charging":
    from modules.gradient_descent import rc_voltage_error
    t_arr, V_arr = df["time_s"].values, df["voltage_V"].values
    V_in_v = true_p.get("V_in", 5.0)
    cost_f  = lambda p: rc_voltage_error(p, t_arr, V_arr, V_in_v)
elif circuit == "RLC Impedansi":
    from modules.gradient_descent import rlc_impedance_error
    cost_f = lambda p: rlc_impedance_error(p, df["frequency_Hz"].values, df["impedance_ohm"].values)
else:
    from modules.gradient_descent import amplifier_gain_error
    cost_f = lambda p: amplifier_gain_error(p, df["frequency_Hz"].values, df["gain"].values)

sens_df = parameter_sensitivity(cost_f, p_opt, param_names)
st.plotly_chart(plot_sensitivity(sens_df), use_container_width=True)
st.dataframe(sens_df, use_container_width=True)
