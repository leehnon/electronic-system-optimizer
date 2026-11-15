param (
    [string]$msg = "update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  ElectronicSystem Optimizer - Quick Push to Git   " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$status = git status --porcelain
if (-not $status) {
    Write-Host "[INFO] Tidak ada file yang berubah." -ForegroundColor Yellow
    exit
}

Write-Host "[1/3] Menambahkan perubahan (git add .)..." -ForegroundColor Gray
git add .

Write-Host "[2/3] Menyimpan commit: `"$msg`"..." -ForegroundColor Gray
git commit -m "$msg"

Write-Host "[3/3] Mendorong ke GitHub (git push origin main)..." -ForegroundColor Gray
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===================================================" -ForegroundColor Green
    Write-Host "  [SUKSES] Berhasil terkirim ke GitHub!            " -ForegroundColor Green
    Write-Host "  Streamlit Cloud akan otomatis update dalam 1 mnt." -ForegroundColor Green
    Write-Host "===================================================" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Push gagal. Periksa koneksi internet atau repo GitHub." -ForegroundColor Red
}
