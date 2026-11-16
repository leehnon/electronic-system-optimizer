@echo off
title Menjalankan ElectronicSystem Optimizer
echo ===================================================
echo   Menjalankan ElectronicSystem Parameter Optimizer
echo ===================================================
echo.
cd /d "%~dp0"
echo Membuka aplikasi di browser (http://localhost:8501)...
echo Tekan Ctrl + C di jendela ini untuk mematikan dashboard.
echo.
streamlit run app.py
pause
