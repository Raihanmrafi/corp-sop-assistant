import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load Environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print("--- DIAGNOSA KONEKSI GOOGLE ---")

# 2. Cek apakah API Key terbaca?
if not api_key:
    print("❌ MERAH: API Key tidak ditemukan di .env!")
    exit()
else:
    # Tampilkan 5 huruf awal kunci untuk memastikan ini kunci BARU kamu
    print(f"✅ HIJAU: API Key terbaca (Depan: {api_key[:5]}...)")

# 3. Konfigurasi Google
genai.configure(api_key=api_key)

print("\nSedang menghubungi server Google untuk meminta daftar model...")

try:
    # 4. Minta daftar model yang tersedia buat akun ini
    models = list(genai.list_models())
    
    print(f"✅ KONEKSI BERHASIL! Ditemukan {len(models)} model.")
    print("Daftar model yang diizinkan untuk kuncimu:")
    
    found_gemini = False
    for m in models:
        # Hanya tampilkan model yang bisa generate text
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
            if "gemini" in m.name:
                found_gemini = True
    
    if found_gemini:
        print("\n✅ KESIMPULAN: Akunmu sehat. Masalahnya ada di kodingan LangChain.")
    else:
        print("\n⚠️ PERINGATAN: Kunci valid, tapi Google tidak memberi akses ke model Gemini (Mungkin masalah Region/Project).")

except Exception as e:
    print(f"\n❌ ERROR FATAL: {e}")
    print("Kemungkinan API Key salah atau diblokir.")

print("\n-------------------------------")