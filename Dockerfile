# 1. Gunakan Python versi stabil (Bookworm = Debian 12 Stable)
# 'slim' biar ringan, 'bookworm' biar stabil gak berubah-ubah
FROM python:3.10-slim-bookworm

# 2. Set folder kerja di dalam container
WORKDIR /app

# 3. Install tool dasar linux (HAPUS software-properties-common)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy file requirements dulu (biar cache berjalan efisien)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy seluruh kode aplikasi ke dalam container
COPY . .

# 7. Trik Config Template (Supaya tidak error saat start)
RUN if [ ! -f config.yaml ]; then cp config.template.yaml config.yaml; fi

# 8. Buka port 8501 (Port Streamlit)
EXPOSE 8501

# 9. Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 10. Jalankan aplikasi
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]