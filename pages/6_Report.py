import streamlit as st
import numpy as np
import pandas as pd
import io
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.evaluation import evaluate_metrics

st.set_page_config(page_title="Report", page_icon="📄", layout="wide")
st.title("📄 Report — Ekspor Laporan")
st.markdown("Generate dan download laporan hasil optimasi parameter elektronika.")

if "gd_result" not in st.session_state:
    st.warning("⚠️ Jalankan komputasi numerik terlebih dahulu sebelum membuat laporan.")
    st.stop()

result  = st.session_state["gd_result"]
circuit = st.session_state.get("circuit", "")
df_data = st.session_state.get("data", pd.DataFrame())
true_p  = st.session_state.get("true_params", {})
p_opt   = result["optimal_params"]

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── Hitung prediksi ───────────────────────────────────────────────────────────
if circuit == "RC Charging":
    t, V = df_data["time_s"].values, df_data["voltage_V"].values
    V_in = true_p.get("V_in", 5.0)
    R_opt, C_opt = p_opt
    tau_opt = max(R_opt*C_opt, 1e-15)
    y_pred  = V_in * (1 - np.exp(-t/tau_opt))
    y_true  = V
    param_names = ["R (Ω)", "C (F)"]

elif circuit == "RLC Impedansi":
    freqs = df_data["frequency_Hz"].values
    Z     = df_data["impedance_ohm"].values
    R_opt, L_opt, C_opt = p_opt
    omega  = 2*np.pi*freqs
    y_pred = np.sqrt(R_opt**2 + (omega*L_opt - 1/(omega*C_opt))**2)
    y_true = Z
    param_names = ["R (Ω)", "L (H)", "C (F)"]

elif circuit == "Amplifier":
    freqs  = df_data["frequency_Hz"].values
    G      = df_data["gain"].values
    A0_opt, fc_opt = p_opt
    y_pred = A0_opt / np.sqrt(1 + (freqs/max(fc_opt,1e-3))**2)
    y_true = G
    param_names = ["A0", "f_c (Hz)"]
else:
    y_true = y_pred = np.array([0])
    param_names = []

metrics = evaluate_metrics(y_true, y_pred) if len(y_true) > 0 else {}

# ── Preview Laporan ───────────────────────────────────────────────────────────
st.markdown("## 📋 Preview Laporan")

report_text = f"""
╔══════════════════════════════════════════════════════════════════════╗
║          LAPORAN OPTIMASI PARAMETER SISTEM ELEKTRONIKA              ║
║                ElectronicSystem Parameter Optimizer                 ║
╚══════════════════════════════════════════════════════════════════════╝

Tanggal   : {now}
NRP       : 130
Bidang    : Pengujian & Diagnostik
Rangkaian : {circuit}

═══════════════════════════════════════════════════════════════════════
 1. PARAMETER HASIL OPTIMASI (Gradient Descent)
═══════════════════════════════════════════════════════════════════════
"""

for i, name in enumerate(param_names):
    p_true = list(true_p.values())[i] if i < len(true_p) else None
    p_est  = p_opt[i]
    err_pct = abs(p_est-p_true)/abs(p_true)*100 if p_true else None
    report_text += f"\n  {name:<20} = {p_est:.6e}"
    if p_true:
        report_text += f"  (True: {p_true:.6e}, Error: {err_pct:.4f}%)"

report_text += f"""

═══════════════════════════════════════════════════════════════════════
 2. METRIK AKURASI MODEL
═══════════════════════════════════════════════════════════════════════
  MSE              = {metrics.get('MSE', 'N/A'):.4e}
  RMSE             = {metrics.get('RMSE', 'N/A'):.4e}
  MAE              = {metrics.get('MAE', 'N/A'):.4e}
  R²               = {metrics.get('R²', 'N/A'):.6f}
  MAPE             = {metrics.get('MAPE (%)', 'N/A'):.4f}%
  Max Error        = {metrics.get('Max Error', 'N/A'):.4e}

═══════════════════════════════════════════════════════════════════════
 3. INFORMASI KONVERGENSI
═══════════════════════════════════════════════════════════════════════
  Algoritma        : Gradient Descent
  Status           : {'KONVERGEN' if result['converged'] else 'BELUM KONVERGEN'}
  Iterasi          : {result['iterations']}
  Cost Awal        : {result['history']['cost'][0]:.4e}
  Cost Akhir       : {result['final_cost']:.4e}
  Reduksi Cost     : {(1-result['final_cost']/max(result['history']['cost'][0],1e-30))*100:.4f}%

  Newton-Raphson   : {'Tersedia — lihat menu Numerical Computation' if 'nr_result' in st.session_state else 'Tidak dijalankan pada sesi ini'}
"""
if "nr_result" in st.session_state:
    nr = st.session_state["nr_result"]
    report_text += f"""
  NR Status        : {'KONVERGEN' if nr['converged'] else 'TIDAK KONVERGEN'}
  NR Iterasi       : {nr['iterations']}
  NR |f(x)| akhir  : {abs(nr['f_root']):.4e}
"""

report_text += f"""
═══════════════════════════════════════════════════════════════════════
 4. KESIMPULAN & VALIDASI
═══════════════════════════════════════════════════════════════════════
  - Model fitted menghasilkan R² = {metrics.get('R²','N/A'):.6f}
  - {'Model sangat akurat (R² > 0.99)' if metrics.get('R²',0)>0.99 else 'Model perlu peningkatan'}
  - MAPE = {metrics.get('MAPE (%)','N/A'):.4f}% menunjukkan rata-rata persentase error
  - Lakukan validasi dengan alat ukur fisik (osiloskop, LCR meter, dll.)
  - Bandingkan hasil dengan perhitungan manual atau simulasi LTspice/Proteus

═══════════════════════════════════════════════════════════════════════
 Dibuat oleh: ElectronicSystem Parameter Optimizer
═══════════════════════════════════════════════════════════════════════
"""

st.code(report_text, language=None)

st.markdown("---")
st.markdown("## ⬇️ Download Laporan")

col1, col2, col3 = st.columns(3)

# Download teks
with col1:
    st.download_button(
        "📄 Download Laporan (.txt)",
        data=report_text,
        file_name=f"laporan_optimizer_{circuit.lower().replace(' ','_')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Download CSV data
with col2:
    if not df_data.empty:
        df_export = df_data.copy()
        if len(y_pred) == len(df_export):
            df_export["y_fitted"]  = y_pred
            df_export["residual"]  = np.array(y_true) - np.array(y_pred)
        csv_data = df_export.to_csv(index=False)
        st.download_button(
            "📊 Download Data + Residual (.csv)",
            data=csv_data,
            file_name=f"data_hasil_{circuit.lower().replace(' ','_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Download history
with col3:
    hist_df = pd.DataFrame({
        "iterasi": result["history"]["iteration"],
        "cost":    result["history"]["cost"],
        "grad_norm": result["history"].get("gradient_norm", [None]*len(result["history"]["iteration"]))
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
    p_true = list(true_p.values())[i] if i < len(true_p) else "N/A"
    p_est  = p_opt[i]
    err_pct = abs(p_est-p_true)/abs(p_true)*100 if isinstance(p_true, float) else "N/A"
    param_rows.append({
        "Parameter":     name,
        "Nilai Optimal": f"{p_est:.6e}",
        "Nilai True":    f"{p_true:.6e}" if isinstance(p_true, float) else "N/A",
        "Error (%)":     f"{err_pct:.4f}" if isinstance(err_pct, float) else "N/A"
    })
st.dataframe(pd.DataFrame(param_rows), use_container_width=True)

st.success("✅ Laporan siap! Gunakan tombol download di atas untuk menyimpan hasilnya.")
