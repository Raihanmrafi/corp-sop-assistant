# --- MANTRA SAKTI FIX SQLITE (WAJIB PALING ATAS) ---
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("✅ Berhasil menggunakan pysqlite3 (Database Aman)")
except ImportError:
    print("⚠️ pysqlite3 tidak ditemukan, menggunakan sqlite3 bawaan (Beresiko)")
# ---------------------------------------------------

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# --- IMPORT MODULE BUATAN KITA ---
from core import rag 
from ui import sidebar, chatbot

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Office AI Assistant", page_icon="🤖")

# ==========================================
# 2. INISIALISASI MEMORI AI (AUTO-LOAD)
# ==========================================
if "vector_store" not in st.session_state:
    # Kita buat placeholder kosong dulu biar gak error di UI
    st.session_state.vector_store = None
    
    with st.spinner("Sedang menyiapkan otak AI..."):
        try:
            # 1. Load Text dari Folder
            raw_text = rag.load_data_from_folder("data")
            
            # 2. Cek apakah ada teksnya?
            if raw_text and len(raw_text.strip()) > 0:
                text_chunks = rag.get_text_chunks(raw_text)
                
                # 3. Buat Database (Hanya jika ada teks)
                st.session_state.vector_store = rag.create_vector_db(text_chunks)
                print(f"✅ Database System: READY ({len(text_chunks)} chunks loaded)")
            else:
                print("⚠️ Database System: EMPTY (Folder kosong atau PDF tidak terbaca)")
                # Jangan error, biarkan kosong. Nanti user disuruh upload.
                
        except Exception as e:
            # Tampilkan error ASLI ke layar biar ketahuan salahnya dimana
            st.error(f"Terjadi kesalahan fatal saat memuat database: {e}")
            print(f"❌ ERROR DETAIL: {e}")

# Inisialisasi Riwayat Chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# 3. MAIN FUNCTION
# ==========================================
def main():
    # --- A. LOAD CONFIG PASSWORD ---
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        st.error("🚨 File config.yaml hilang! Jalankan script setup credentials dulu.")
        return

    # --- B. SETUP AUTHENTICATOR ---
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # --- C. LOGIN ---
    authenticator.login(location='main')

    if st.session_state["authentication_status"]:
        # === LOGIN BERHASIL ===
        username = st.session_state["username"]
        name = st.session_state["name"]
        
        try:
            user_role = config['credentials']['usernames'][username]['roles'][0]
        except:
            user_role = "viewer"
            
        st.session_state.user_role = user_role
        st.session_state.user_name = name
        
        # Sidebar & Chatbot
        with st.sidebar:
            st.write(f"👋 Halo, **{name}**")
            label_role = "👨‍🍳 ADMIN (HR)" if user_role == 'admin' else "🍴 STAFF (User)"
            st.caption(f"Akses: {label_role}")
            authenticator.logout(location='sidebar') 
            st.divider()

        sidebar.show_sidebar()
        chatbot.show_chat_page()

    elif st.session_state["authentication_status"] is False:
        st.error('Username atau Password salah!')
    elif st.session_state["authentication_status"] is None:
        st.warning('Silakan login menggunakan akun kantor.')

if __name__ == "__main__":
    main()