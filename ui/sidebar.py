import streamlit as st
import os
import gc
from core import rag
from pypdf import PdfReader

def show_sidebar():
    with st.sidebar:
        # --- 1. MONITOR SISTEM (DEBUG) 🕵️‍♂️ ---
        st.header("🔍 Monitor Sistem (Debug)")
        
        folder_path = "data"
        if not os.path.exists(folder_path):
            st.error("❌ Folder 'data' hilang!")
        else:
            files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
            st.write(f"📂 File Terdeteksi: **{len(files)}**")
            
            if len(files) > 0:
                with st.expander("Lihat Detail File"):
                    total_chars = 0
                    for f in files:
                        try:
                            f_path = os.path.join(folder_path, f)
                            reader = PdfReader(f_path)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text() or ""
                            chars = len(text)
                            total_chars += chars
                            icon = "✅" if chars > 100 else "⚠️"
                            st.text(f"{icon} {f}\n   ({chars} huruf)")
                        except: pass
                    st.write(f"**Total Karakter: {total_chars}**")

        st.divider()

        # --- 2. PANEL ADMIN (KHUSUS HR) ---
        user_role = st.session_state.get('user_role', 'viewer')
        
        if user_role == 'admin':
            st.header("🔐 Panel Admin")
            uploaded_files = st.file_uploader("Upload PDF", accept_multiple_files=True, type=['pdf'])
            
            if st.button("🔄 Update Database"):
                with st.spinner("Mengganti mesin ke FAISS & Re-Indexing..."):
                    # Simpan file
                    if uploaded_files:
                        if not os.path.exists("data"): os.makedirs("data")
                        for pdf in uploaded_files:
                            with open(os.path.join("data", pdf.name), "wb") as f:
                                f.write(pdf.getbuffer())
                    
                    # Reset Total
                    rag.load_data_from_folder.clear()
                    rag.create_vector_db.clear()
                    if "vector_store" in st.session_state:
                        del st.session_state["vector_store"]
                    gc.collect()
                    st.rerun()
            st.divider()

        # --- 3. PILIHAN MODEL (INI YANG KEMARIN HILANG) 🤖 ---
        st.header("🤖 Model AI")
        mode_pilihan = st.radio(
            "Pilih Otak AI:",
            ["🚀 Cloud (Llama 3.3)", "🔒 Local (Qwen)"],
            index=0,
            help="Gunakan 'Local' jika Cloud error 401/429"
        )
        
        if "Cloud" in mode_pilihan:
            st.session_state.ai_mode = "cloud"
        else:
            st.session_state.ai_mode = "local"
            
        # Status Database
        st.divider()
        if st.session_state.get("vector_store") is not None:
            st.success("✅ DATABASE SIAP")
        else:
            st.warning("⚠️ DATABASE BELUM SIAP")