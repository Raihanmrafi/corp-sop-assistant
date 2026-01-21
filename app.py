import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from ui import sidebar, chatbot

# Konfigurasi Halaman (Wajib paling atas)
st.set_page_config(page_title="Office AI Assistant", page_icon="🤖")

def main():
    # --- 1. LOAD CONFIG USER ---
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        st.error("File config.yaml tidak ditemukan. Jalankan langkah pembuatan config dulu.")
        return

    # --- 2. SETUP AUTHENTICATOR ---
    # Membaca konfigurasi dari file yaml
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # --- 3. TAMPILKAN LOGIN FORM ---
    # PERUBAHAN DISINI: Jangan pakai variable = authenticator.login(...)
    # Cukup panggil fungsinya saja.
    authenticator.login(location='main')

    # --- 4. LOGIKA AKSES (PAKAI SESSION STATE) ---
    # Cek status login langsung dari memori session_state
    if st.session_state["authentication_status"]:
        
        # === BERHASIL LOGIN ===
        username = st.session_state["username"]
        name = st.session_state["name"]
        
        # Ambil Role User
        try:
            user_role = config['credentials']['usernames'][username]['roles'][0]
        except:
            user_role = "viewer" # Default jika role tidak ada
            
        # Simpan ke Session State global biar bisa dibaca sidebar.py
        st.session_state.user_role = user_role
        st.session_state.user_name = name
        
        # --- SIDEBAR (Logout & Info) ---
        with st.sidebar:
            st.write(f"👋 Halo, **{name}**")
            st.caption(f"Akses: {user_role.upper()}")
            
            # Tombol Logout
            authenticator.logout(location='sidebar') 
            st.divider()

        # --- TAMPILKAN UI UTAMA ---
        sidebar.show_sidebar()
        chatbot.show_chat_page()

    elif st.session_state["authentication_status"] is False:
        # === PASSWORD SALAH ===
        st.error('Username atau Password salah')
        
    elif st.session_state["authentication_status"] is None:
        # === BELUM LOGIN ===
        st.warning('Silakan login menggunakan akun kantor.')

if __name__ == "__main__":
    main()