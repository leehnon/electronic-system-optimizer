@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   ElectronicSystem Optimizer - Quick Push to Git
echo ===================================================
echo.

cd /d "%~dp0"

:: Ambil pesan commit dari argumen, jika kosong gunakan default timestamp
set "COMMIT_MSG=%~1"
if "%COMMIT_MSG%"=="" (
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set dt=%%I
    set "TIMESTAMP=!dt:~0,4!-!dt:~4,2!-!dt:~6,2! !dt:~8,2!:!dt:~10,2!:!dt:~12,2!"
    set "COMMIT_MSG=update: !TIMESTAMP!"
)

echo [1/3] Menambahkan semua perubahan...
git add .

echo [2/3] Menyimpan commit: "%COMMIT_MSG%"...
git commit -m "%COMMIT_MSG%"

echo [3/3] Mendorong (push) ke GitHub...
git push origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ===================================================
    echo   [SUKSES] Berhasil di-push ke GitHub!
    echo   Streamlit Cloud akan otomatis update dalam 1 menit.
    echo ===================================================
) else (
    echo.
    echo [INFO] Tidak ada perubahan baru atau push gagal.
)

echo.
pause
