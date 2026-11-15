"""
auto_sync.py
Watcher otomatis: mendeteksi perubahan file di folder proyek,
lalu otomatis melakukan git add, git commit, dan git push.
Jalankan di terminal: python auto_sync.py
"""

import subprocess
import time
from datetime import datetime

CHECK_INTERVAL_SECONDS = 10  # Cek setiap 10 detik

def has_changes():
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        return bool(res.stdout.strip())
    except Exception as e:
        print(f"[Error cek status] {e}")
        return False

def sync_to_github():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"auto: sinkronisasi berkas pada {now_str}"
    print(f"\n[{now_str}] Terdeteksi perubahan berkas! Memulai proses push...")

    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

        if push_res.returncode == 0:
            print(f"[{now_str}] ✅ Berhasil push ke GitHub! Streamlit Cloud akan terupdate otomatis.")
        else:
            print(f"[{now_str}] ⚠️ Push gagal:\n{push_res.stderr}")
    except Exception as e:
        print(f"[{now_str}] ❌ Gagal sync: {e}")

def main():
    print("=" * 60)
    print("🚀 Auto-Sync Git Berjalan!")
    print(f"Setiap ada file yang Anda simpan/edit, script ini akan")
    print(f"otomatis melakukan git commit dan git push setiap {CHECK_INTERVAL_SECONDS} detik.")
    print("Tekan Ctrl + C di terminal untuk menghentikan.")
    print("=" * 60)

    try:
        while True:
            if has_changes():
                # Tunggu sejenak jika user masih mengetik/menyimpan beberapa file sekaligus
                time.sleep(3)
                sync_to_github()
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[Berhenti] Auto-sync dinonaktifkan.")

if __name__ == "__main__":
    main()
