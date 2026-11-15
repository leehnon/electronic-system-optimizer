# ⚡ ElectronicSystem Parameter Optimizer

**Sistem Optimalisasi Parameter Prototipe Elektronika | Pengujian & Diagnostik**

---

## 📋 Deskripsi Proyek

Sistem dashboard interaktif berbasis **Python + Streamlit** untuk mengoptimasi parameter
prototipe elektronika menggunakan metode numerik **Gradient Descent** dan **Newton-Raphson**.

---

## 🗂️ Struktur Project

```
tugas pak ronny/
├── app.py                          ← Halaman utama (Overview)
├── requirements.txt                ← Dependensi Python
├── README.md
├── modules/
│   ├── gradient_descent.py         ← Algoritma Gradient Descent + fungsi biaya
│   ├── newton_raphson.py           ← Algoritma Newton-Raphson (skalar & sistem)
│   ├── data_generator.py           ← Generator data simulasi RC/RLC/Amplifier/Dioda
│   ├── evaluation.py               ← Metrik akurasi & analisis sensitivitas
│   └── visualization.py            ← Grafik Plotly interaktif
└── pages/
    ├── 1_Data_Management.py        ← Generate/upload data elektronika
    ├── 2_Numerical_Computation.py  ← Jalankan GD & NR
    ├── 3_Visualization.py          ← Grafik fitting, konvergensi, residual
    ├── 4_Evaluation.py             ← MSE, RMSE, R², sensitivitas
    ├── 5_Engineering_Interpretation.py ← Interpretasi teknik hasil
    └── 6_Report.py                 ← Ekspor laporan TXT/CSV
```

---

## 🚀 Cara Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Jalankan aplikasi
```bash
streamlit run app.py
```

### 3. Buka browser
Aplikasi akan terbuka otomatis di `http://localhost:8501`

---

## 🔢 Algoritma yang Diimplementasikan

| Algoritma | Penggunaan |
|---|---|
| **Gradient Descent** | Optimasi parameter (R, L, C, A0, f_c) dengan minimasi MSE |
| **Newton-Raphson** | Titik operasi dioda, frekuensi resonansi, konstanta waktu RC |
| **Finite Difference** | Aproksimasi gradien numerik |

---

## 🔌 Studi Kasus Rangkaian

| Rangkaian | Parameter yang Dioptimasi | Data |
|---|---|---|
| **RC Charging** | R, C (dan τ=RC) | V(t) = V_in(1−e^{−t/τ}) |
| **RLC Impedansi** | R, L, C, f_resonansi | \|Z(f)\| vs frekuensi |
| **Amplifier** | A0 (gain DC), f_cutoff | G(f) = A0/√(1+(f/fc)²) |
| **Dioda** | V_D, I_D (titik operasi) | Model Shockley |

---

## 📊 Menu Dashboard

1. **Data Management** — Generate atau upload data elektronika
2. **Numerical Computation** — Jalankan Gradient Descent & Newton-Raphson
3. **Visualization** — Grafik interaktif fitting, konvergensi, residual, sensitivitas
4. **Evaluation** — MSE, RMSE, R², MAPE, analisis sensitivitas parameter
5. **Engineering Interpretation** — Interpretasi teknik (τ, f_r, Q-factor, GBW, dll.)
6. **Report** — Ekspor laporan TXT dan data CSV

---

## ✅ Panduan Validasi

- Bandingkan hasil numerik dengan **perhitungan manual**
- Verifikasi dengan **simulator** (LTspice, Proteus, MATLAB/Simulink)
- Ukur dengan **alat ukur fisik** (osiloskop, LCR meter, impedance analyzer)
- Perhatikan metrik: **R² > 0.99** = model sangat akurat, **MAPE < 1%** = error sangat kecil
