# 1. Gunakan Python versi stabil (Slim biar ringan)
FROM python:3.10-slim

# 2. Set folder kerja di dalam container
WORKDIR /app

# 3. Install tool dasar linux (penting untuk library AI seperti chroma/numpy)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy file requirements dulu (biar cache berjalan efisien)
COPY requirements.txt .

# 5. Install Python dependencies
# --no-cache-dir biar ukuran image tidak bengkak
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy seluruh kode aplikasi ke dalam container
COPY . .

# 7. (PENTING) Handle File yang di-Ignore
# Karena config.yaml dan .env tidak ikut di-push ke GitHub, 
# aplikasi akan error kalau file ini tidak ada.
# Solusi sementara: Kita copy file example (kalau ada) atau biarkan kosong.
# Nanti saat RUN, kita akan inject isinya.
# --- BARU! ---
# Jika config.yaml tidak ada, copy dari template lalu ganti namanya jadi config.yaml
# Ini trik supaya aplikasi tidak crash saat pertama kali dijalankan di server
RUN if [ ! -f config.yaml ]; then cp config.template.yaml config.yaml; fi
# -------------

# 8. Buka port 8501 (Port Streamlit)
EXPOSE 8501

# 9. Perintah pengecekan kesehatan (Healthcheck)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 10. Perintah untuk menjalankan aplikasi
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]