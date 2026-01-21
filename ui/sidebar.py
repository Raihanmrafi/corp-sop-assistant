import streamlit as st
from core import rag

def show_sidebar():
    with st.sidebar:
        # --- LOGIKA RBAC (ROLE BASED ACCESS CONTROL) ---
        # Cek apakah user adalah ADMIN?
        user_role = st.session_state.get('user_role', 'viewer')
        
        if user_role == 'admin':
            st.header("🔐 Panel Admin (HR)")
            st.info("Anda memiliki akses untuk menambah pengetahuan AI.")
            
            # --- FITUR UPLOAD (HANYA MUNCUL JIKA ADMIN) ---
            st.subheader("📂 Update Knowledge Base")
            pdf_docs = st.file_uploader(
                "Upload SOP Baru (PDF)", 
                accept_multiple_files=True,
                type=['pdf']
            )

            if st.button("Proses & Update Database"):
                if not pdf_docs:
                    st.error("File belum dipilih.")
                else:
                    with st.spinner("Mengupdate otak AI..."):
                        raw_text = rag.get_pdf_text(pdf_docs)
                        text_chunks = rag.get_text_chunks(raw_text)
                        vector_store = rag.create_vector_db(text_chunks)
                        st.session_state.vector_store = vector_store
                        st.success("✅ Database berhasil diperbarui!")
            st.divider()
            
        else:
            # TAMPILAN UNTUK STAFF BIASA
            st.header("⚙️ Konfigurasi")
            st.info(f"Mode: **Staff View**\n\nAnda hanya dapat bertanya. Untuk update dokumen, hubungi HR.")
        
        # --- FITUR UMUM (SEMUA BISA AKSES) ---
        # Pilihan Cloud/Local tetap bisa diakses semua orang (atau mau dibatasi juga boleh)
        st.header("🤖 Pilihan Mesin AI")
        mode_pilihan = st.radio(
            "Engine:",
            ["🚀 Cloud (OpenRouter)", "🔒 Local (Qwen)"],
            index=0
        )
        
        if "Cloud" in mode_pilihan:
            st.session_state.ai_mode = "cloud"
        else:
            st.session_state.ai_mode = "local"