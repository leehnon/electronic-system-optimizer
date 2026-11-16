@echo off
title Menjalankan ElectronicSystem Optimizer
echo ===================================================
echo   Menjalankan ElectronicSystem Parameter Optimizer
echo ===================================================
echo.
cd /d "%~dp0"

:: Bersihkan sesi lama jika port 8501 masih menggantung
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501" ^| findstr "LISTENING"') do (
    echo Menutup sesi lama pada port 8501 (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo Membuka aplikasi di browser (http://localhost:8501)...
echo Tekan Ctrl + C di jendela ini jika ingin mematikan dashboard.
echo.
timeout /t 1 /nobreak >nul
start http://localhost:8501
python -m streamlit run app.py
pause
