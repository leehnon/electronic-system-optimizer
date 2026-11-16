# ElectronicSystem Parameter Optimizer (ESPOptimizer)

**Sistem Komputasi Numerik untuk Optimalisasi, Identifikasi Parameter, dan Diagnostik Rangkaian Elektronika**

---

## 1. Ringkasan Proyek & Pemenuhan Rubrik Penilaian

Proyek ini dibangun untuk memenuhi seluruh 8 indikator penilaian tugas komputasi numerik sistem elektronika dengan bobot total 100%:

| No | Komponen Penilaian | Bobot | Pemenuhan pada Dashboard | Lokasi / Halaman |
|---|---|---|---|---|
| 1 | **Perumusan masalah dan relevansi elektronika** | 10% | Latar belakang toleransi komponen fisik, rumusan masalah, variabel, asumsi operasi, dan manfaat industri. | `app.py` & `pages/1_Data_Management.py` |
| 2 | **Model matematika dan pemilihan metode numerik** | 15% | Formulasi analitik lengkap, MSE cost function, dan justifikasi matematis pemilihan GD vs NR. | `app.py` & `pages/2_Numerical_Computation.py` |
| 3 | **Implementasi algoritma numerik mandiri** | 25% | Algoritma GD dan NR ditulis dari dasar (*pure NumPy* tanpa solver siap pakai) dengan tabel jejak iterasi (*trace log* per baris). | `modules/gradient_descent.py`, `modules/newton_raphson.py`, `pages/2` |
| 4 | **Kualitas data dan pengelolaannya** | 10% | Pelabelan jujur (data simulasi vs pengukuran riil CSV), dokumentasi variabel & satuan SI, verifikasi preprocessing data. | `pages/1_Data_Management.py` |
| 5 | **Pengujian, validasi, dan evaluasi error** | 15% | 3 skenario uji (Noise 0%, 2-5%, 10%), perbandingan nilai rujukan, metrik MSE/RMSE/MAE/R²/MAPE, analisis residual, dan sensitivitas. | `pages/4_Evaluation.py` & `pages/3_Visualization.py` |
| 6 | **Fungsionalitas sistem dan dashboard** | 15% | Alur 6 menu lengkap terintegrasi: input/upload, komputasi, visualisasi, evaluasi, interpretasi, dan ekspor dokumen. | Seluruh menu dashboard |
| 7 | **Interpretasi teknik dan manfaat aplikasi** | 5% | Analisis makna fisik (tau, Q-factor, bandwidth, transkonduktansi), evaluasi batas operasi, dan keterbatasan model (ESR & termal). | `pages/5_Engineering_Interpretation.py` |
| 8 | **Dokumentasi, presentasi, dan demonstrasi** | 5% | Source code terstruktur rapi, panduan demonstrasi presentasi 5 menit, dan ekspor laporan ilmiah TXT/CSV. | `README.md` & `pages/6_Report.py` |

---

## 2. Struktur Direktori Proyek

```
tugas pak ronny/
├── app.py                          # Halaman Beranda (Perumusan Masalah & Spesifikasi Sistem)
├── requirements.txt                # Daftar pustaka Python pendukung
├── README.md                       # Dokumentasi teknis dan pemetaan rubrik penilaian
├── run.bat                         # Script otomatisasi peluncuran lokal
├── update.bat                      # Script sinkronisasi Git & Streamlit Cloud
├── modules/
│   ├── gradient_descent.py         # Algoritma Gradient Descent mandiri + fungsi biaya 7 sirkuit
│   ├── newton_raphson.py           # Algoritma Newton-Raphson mandiri (skalar & sistem)
│   ├── data_generator.py           # Generator data simulasi 7 rangkaian elektronika
│   ├── evaluation.py               # Fungsi metrik evaluasi (MSE, RMSE, MAE, R², MAPE, sensitivitas)
│   ├── visualization.py            # Modul rendering grafik Plotly interaktif
│   └── styles.py                   # Sistem desain visual minimalis profesional (bebas emoji)
└── pages/
    ├── 1_Data_Management.py        # Akuisisi data, dokumentasi satuan SI, dan preprocessing
    ├── 2_Numerical_Computation.py  # Komputasi numerik GD/NR + penelusuran log iterasi
    ├── 3_Visualization.py          # Grafik perbandingan model fitting, konvergensi, residual
    ├── 4_Evaluation.py             # Validasi skenario uji, pembanding ground truth, sensitivitas
    ├── 5_Engineering_Interpretation.py # Interpretasi fisik parameter, keterbatasan model, aplikasi
    └── 6_Report.py                 # Ekspor dokumen laporan ilmiah (TXT/CSV) & panduan presentasi
```

---

## 3. Cakupan 7 Studi Kasus Rangkaian Elektronika

1. **RC Charging (Pengisian Kapasitor):**
   - Formulasi: $V(t) = V_{in} \cdot (1 - e^{-t / (RC)})$
   - Parameter teroptimasi: Resistansi $R$, Kapasitansi $C$, Konstanta waktu $\tau = RC$.
2. **RC Discharging (Pengosongan Kapasitor):**
   - Formulasi: $V(t) = V_0 \cdot e^{-t / (RC)}$
   - Parameter teroptimasi: Resistansi $R$, Kapasitansi $C$, Waktu paruh $t_{1/2}$.
3. **RLC Seri (Respon Frekuensi & Impedansi):**
   - Formulasi: $|Z(f)| = \sqrt{R^2 + (2\pi f L - \frac{1}{2\pi f C})^2}$
   - Parameter teroptimasi: Resistansi $R$, Induktansi $L$, Kapasitansi $C$, Frekuensi resonansi $f_r$.
4. **Band-Pass Filter RLC Pasif:**
   - Formulasi: $H(f) = \frac{R}{\sqrt{R^2 + (2\pi f L - \frac{1}{2\pi f C})^2}}$
   - Parameter teroptimasi: $R, L, C$, Frekuensi tengah $f_0$, Bandwidth $BW$, Faktor Kualitas $Q$.
5. **Amplifier (Single-Pole Frequency Roll-off):**
   - Formulasi: $G(f) = \frac{A_0}{\sqrt{1 + (f / f_c)^2}}$
   - Parameter teroptimasi: Penguatan DC $A_0$, Frekuensi cutoff $-3\text{ dB}$ $f_c$, Gain-Bandwidth Product (GBW).
6. **Dioda Semikonduktor PN Junction:**
   - Formulasi: $I_D = I_s \cdot (e^{V_D / V_T} - 1)$ dengan KVL $V_s = V_D + I_D \cdot R$
   - Parameter teroptimasi: Titik kerja tegangan maju $V_D$, arus maju $I_D$, disipasi daya $P_D$.
7. **Transistor BJT (Karakteristik Arus Kolektor Shockley):**
   - Formulasi: $I_C = I_s \cdot (e^{V_{BE} / V_T} - 1)$
   - Parameter teroptimasi: Arus saturasi $I_s$, Tegangan termal $V_T$, Transkonduktansi $g_m$.

---

## 4. Panduan Menjalankan Sistem

### Persyaratan Sistem
- Python 3.9, 3.10, atau 3.11
- Web browser modern (Google Chrome, Microsoft Edge, Firefox)

### Langkah Instalasi & Menjalankan
1. Pasang dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan server lokal:
   - **Metode Batch (Windows):** Klik dua kali file `run.bat`.
   - **Metode Terminal:** Jalankan perintah `python -m streamlit run app.py`.
3. Akses dashboard di browser melalui tautan: `http://localhost:8501`.

---

## 5. Skenario Demonstrasi & Presentasi Pengujian (5 Menit)

1. **Menit 1 (Beranda):** Presentasikan rumusan masalah deviasi parameter fisik akibat toleransi fabrikasi dan perlihatkan tabel batas operasi model.
2. **Menit 2 (Data Management):** Tunjukkan bahwa data memiliki label jujur (simulasi vs data pengukuran riil laboratorium), dokumentasi variabel dengan satuan SI baku, dan lolos uji verifikasi preprocessing tanpa nilai kosong (NaN).
3. **Menit 3 (Numerical Computation):** Tunjukkan bahwa algoritma diimplementasikan dari dasar (*pure NumPy* tanpa solver siap pakai) dan perlihatkan tabel jejak iterasi langkah demi langkah (*trace log* per iterasi).
4. **Menit 4 (Visualization & Evaluation):** Tunjukkan grafik kecocokan data vs model fitting ($R^2 > 0.99$), grafik konvergensi stabil, dan analisis residual simetris di sekitar nol.
5. **Menit 5 (Engineering Interpretation & Report):** Jelaskan makna fisik parameter (misal: konstanta waktu $\tau$, frekuensi resonansi, atau bandwidth), paparkan keterbatasan model fisik (asumsi komponen ideal tanpa ESR), dan unduh berkas laporan hasil komputasi.
