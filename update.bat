@echo off
cd /d "%~dp0"
title Update GitHub - ElectronicSystem Optimizer
echo ===================================================
echo   Mengirimkan Pembaruan ke GitHub ^& Streamlit Cloud
echo ===================================================
echo.

echo [1/3] Menyiapkan berkas (git add)...
git add .

echo [2/3] Menyimpan perubahan (git commit)...
git commit -m "update: perbaikan tampilan sidebar terang dan auto-load data default"

echo [3/3] Mengirimkan ke GitHub (git push origin main)...
git push origin main

echo.
echo ===================================================
echo   Selesai! Periksa pesan di atas.
echo   Jika muncul 'main -> main', berarti BERHASIL!
echo ===================================================
echo.
pause
