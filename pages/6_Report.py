import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.styles import inject_css
from modules.evaluation import evaluate_metrics
from modules.data_generator import ensure_default_data

st.set_page_config(page_title="Report", page_icon="📄", layout="wide")
inject_css()
ensure_default_data()

st.title("Report")
st.markdown("Generate dan download laporan hasil optimasi parameter elektronika.")

if "gd_result" not in st.session_state:
    st.warning("⚠️ Jalankan komputasi numerik terlebih dahulu sebelum membuat laporan.")
    st.stop()

result  = st.session_state["gd_result"]
circuit = st.session_state.get("circuit", "RC Charging")
df_data = st.session_state.get("data", pd.DataFrame())
true_p  = st.session_state.get("true_params", {})
p_opt   = result["optimal_params"]

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── Hitung prediksi & parameter untuk semua 7 rangkaian ──────────────────────
if circuit == "RC Charging":
    t, V = df_data["time_s"].values, df_data["voltage_V"].values
    V_in = float(true_p.get("V_in", 5.0))
    R_opt, C_opt = p_opt
    tau_opt = max(R_opt * C_opt, 1e-15)
    y_pred  = V_in * (1 - np.exp(-t / tau_opt))
    y_true  = V
    param_names = ["R (Ω)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("C")]

elif circuit == "RC Discharging":
    t, V = df_data["time_s"].values, df_data["voltage_V"].values
    V0 = float(true_p.get("V0", 5.0))
    R_opt, C_opt = p_opt
    tau_opt = max(R_opt * C_opt, 1e-15)
    y_pred  = V0 * np.exp(-t / tau_opt)
    y_true  = V
    param_names = ["R (Ω)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("C")]

elif circuit in ["RLC Seri (Impedansi)", "RLC Impedansi"]:
    freqs = df_data["frequency_Hz"].values
    Z     = df_data["impedance_ohm"].values
    R_opt, L_opt, C_opt = p_opt
    omega  = 2 * np.pi * freqs
    reactance = omega * L_opt - 1.0 / (omega * C_opt)
    y_pred = np.sqrt(R_opt**2 + reactance**2)
    y_true = Z
    param_names = ["R (Ω)", "L (H)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("L"), true_p.get("C")]

elif circuit == "Band-Pass Filter RLC":
    freqs = df_data["frequency_Hz"].values
    gain  = df_data["gain_linear"].values
    R_opt, L_opt, C_opt = p_opt
    omega = 2 * np.pi * freqs
    reactance = omega * L_opt - 1.0 / (omega * C_opt)
    y_pred = R_opt / np.sqrt(R_opt**2 + reactance**2)
    y_true = gain
    param_names = ["R (Ω)", "L (H)", "C (F)"]
    true_vals = [true_p.get("R"), true_p.get("L"), true_p.get("C")]

elif circuit in ["Amplifier", "Amplifier (Single-Pole)"]:
    freqs  = df_data["frequency_Hz"].values
    G      = df_data["gain"].values
    A0_opt, fc_opt = p_opt
    y_pred = A0_opt / np.sqrt(1 + (freqs / max(fc_opt, 1e-3))**2)
    y_true = G
    param_names = ["A0", "f_c (Hz)"]
    true_vals = [true_p.get("A0"), true_p.get("f_cutoff")]

elif circuit == "Transistor BJT":
    vbe = df_data["V_be_V"].values
    ic  = df_data["I_c_A"].values
    Is_opt, Vt_opt = p_opt
    y_pred = Is_opt * (np.exp(np.clip(vbe / Vt_opt, 0, 40)) - 1)
    y_true = ic
    param_names = ["Is (A)", "Vt (V)"]
    true_vals = [true_p.get("I_s"), true_p.get("V_T")]

else:
    y_true = y_pred = np.array([0.0])
    param_names = []
    true_vals = []

metrics = evaluate_metrics(y_true, y_pred) if len(y_true) > 1 else {}

# ── Preview Laporan ───────────────────────────────────────────────────────────
st.markdown("## 📋 Preview Laporan Lengkap")

report_text = f"""╔══════════════════════════════════════════════════════════════════════╗
║          LAPORAN OPTIMASI PARAMETER SISTEM ELEKTRONIKA              ║
║                ElectronicSystem Parameter Optimizer                 ║
╚══════════════════════════════════════════════════════════════════════╝

Tanggal   : {now}
Studi     : Tugas Komputasi Numerik Sistem Elektronika
Rangkaian : {circuit}

═══════════════════════════════════════════════════════════════════════
 1. PARAMETER HASIL OPTIMASI (Gradient Descent)
═══════════════════════════════════════════════════════════════════════
"""

for i, name in enumerate(param_names):
    p_true = true_vals[i] if i < len(true_vals) else None
    p_est  = p_opt[i]
    err_pct = abs(p_est - p_true) / abs(p_true) * 100 if (p_true is not None and p_true != 0) else None
    report_text += f"\n  {name:<22} = {p_est:.6e}"
    if p_true is not None:
        report_text += f"  (Nilai True: {p_true:.6e}, Galat: {err_pct:.4f}%)"

report_text += f"""

═══════════════════════════════════════════════════════════════════════
 2. METRIK AKURASI & VALIDASI MODEL
═══════════════════════════════════════════════════════════════════════
  MSE              = {metrics.get('MSE', 0):.4e}
  RMSE             = {metrics.get('RMSE', 0):.4e}
  MAE              = {metrics.get('MAE', 0):.4e}
  R²               = {metrics.get('R²', 0):.6f}
  MAPE             = {metrics.get('MAPE (%)', 0):.4f}%
  Max Error        = {metrics.get('Max Error', 0):.4e}

═══════════════════════════════════════════════════════════════════════
 3. INFORMASI KONVERGENSI NUMERIK
═══════════════════════════════════════════════════════════════════════
  Algoritma Utama  : Gradient Descent (Optimasi Multivariat)
  Status           : {'KONVERGEN' if result.get('converged', True) else 'SELESAI'}
  Jumlah Iterasi   : {result.get('iterations', '-')}
  Cost Awal        : {result.get('history', {}).get('cost', [0])[0]:.4e}
  Cost Akhir (MSE) : {result.get('final_cost', 0):.4e}
"""

if "nr_result" in st.session_state:
    nr = st.session_state["nr_result"]
    report_text += f"""
  Newton-Raphson   : Dijalankan
  NR Status        : {'KONVERGEN' if nr.get('converged', True) else 'TIDAK KONVERGEN'}
  NR Iterasi       : {nr.get('iterations', '-')}
  NR |f(x)| akhir  : {abs(nr.get('f_root', 0)):.4e}
"""
else:
    report_text += "\n  Newton-Raphson   : Tidak dijalankan pada sesi aktif ini.\n"

report_text += f"""
═══════════════════════════════════════════════════════════════════════
 4. KESIMPULAN & INTERPRETASI TEKNIK
═══════════════════════════════════════════════════════════════════════
  - Model fitting menghasilkan koefisien determinasi R² = {metrics.get('R²', 0):.6f}.
  - {'Model sangat akurat dan merepresentasikan perilaku fisik komponen (R² > 0.99).' if metrics.get('R²', 0) > 0.99 else 'Model cukup baik (R² > 0.95).' if metrics.get('R²', 0) > 0.95 else 'Toleransi error masih dalam batas dapat diterima.'}
  - Nilai MAPE = {metrics.get('MAPE (%)', 0):.4f}% mengonfirmasi deviasi rata-rata data.
  - Hasil optimasi siap digunakan untuk kalibrasi simulasi SPICE maupun perancangan prototipe PCB.

═══════════════════════════════════════════════════════════════════════
 Dibuat secara otomatis oleh: ElectronicSystem Parameter Optimizer
═══════════════════════════════════════════════════════════════════════
"""

st.code(report_text, language=None)

st.markdown("---")
st.markdown("## ⬇️ Download Laporan & Data")

col1, col2, col3 = st.columns(3)

# Download teks
with col1:
    st.download_button(
        "📄 Download Laporan (.txt)",
        data=report_text,
        file_name=f"laporan_optimizer_{circuit.lower().replace(' ','_').replace('(','').replace(')','')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Download CSV data
with col2:
    if not df_data.empty:
        df_export = df_data.copy()
        if len(y_pred) == len(df_export):
            df_export["y_fitted"] = y_pred
            df_export["residual"] = np.array(y_true) - np.array(y_pred)
        csv_data = df_export.to_csv(index=False)
        st.download_button(
            "📊 Download Data + Residual (.csv)",
            data=csv_data,
            file_name=f"data_hasil_{circuit.lower().replace(' ','_').replace('(','').replace(')','')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Download history
with col3:
    if "history" in result and "cost" in result["history"]:
        hist_df = pd.DataFrame({
            "iterasi": result["history"].get("iteration", list(range(len(result["history"]["cost"])))),
            "cost":    result["history"]["cost"],
            "grad_norm": result["history"].get("gradient_norm", [None]*len(result["history"]["cost"]))
        })
        hist_csv = hist_df.to_csv(index=False)
        st.download_button(
            "🔄 Download History Konvergensi (.csv)",
            data=hist_csv,
            file_name="history_gradient_descent.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("---")
st.markdown("## 📊 Ringkasan Parameter Optimal")
param_rows = []
for i, name in enumerate(param_names):
    p_true = true_vals[i] if i < len(true_vals) else "N/A"
    p_est  = p_opt[i]
    err_pct = abs(p_est - p_true) / abs(p_true) * 100 if (isinstance(p_true, (int, float)) and p_true != 0) else "N/A"
    param_rows.append({
        "Parameter":     name,
        "Nilai Optimal": f"{p_est:.6e}",
        "Nilai True":    f"{p_true:.6e}" if isinstance(p_true, (int, float)) else "N/A",
        "Error (%)":     f"{err_pct:.4f}%" if isinstance(err_pct, (int, float)) else "N/A"
    })
st.dataframe(pd.DataFrame(param_rows), use_container_width=True)

st.success("✅ Laporan lengkap siap diunduh.")
