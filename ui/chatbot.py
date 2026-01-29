import streamlit as st
from core import rag

def show_chat_page():
    # --- HEADER ---
    st.title("🤖 Asisten Cerdas Kantor (Hybrid)")
    st.caption("Bertanya seputar SOP, Kebijakan, dan Data Kantor.")

    # --- INISIALISASI SESSION STATE ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Pastikan mode AI terpilih
    if "ai_mode" not in st.session_state:
        st.session_state.ai_mode = "cloud" # Default

    # --- TAMPILKAN RIWAYAT CHAT ---
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Jika ada sumber (khusus assistant), tampilkan
            if "sources" in message:
                with st.expander("📚 Sumber Referensi"):
                    for src in message["sources"]:
                        st.markdown(f"- 📄 **{src['source']}** (Hal. {src['page']})")
                        st.caption(f"Isi: ...{src['content']}...")

    # --- INPUT USER ---
    if prompt := st.chat_input("Tanyakan sesuatu..."):
        # 1. Tampilkan pesan user
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # 2. Proses Jawaban AI
        with st.chat_message("assistant"):
            with st.spinner(f"Sedang berpikir ({st.session_state.ai_mode})..."):
                
                # Panggil Fungsi RAG
                answer_text, source_docs = rag.process_question(
                    st.session_state.vector_store,
                    prompt,
                    st.session_state.chat_history,
                    st.session_state.ai_mode
                )
                
                # Tampilkan Jawaban Utama
                st.markdown(answer_text)

                # Siapkan data sumber untuk disimpan di history
                saved_sources = []
                
                # --- FITUR PROFESIONAL: TAMPILKAN SUMBER ---
                if source_docs:
                    with st.expander("📚 Lihat Sumber Referensi (Klik Disini)"):
                        for i, doc in enumerate(source_docs):
                            # Ambil metadata (Nama File & Halaman)
                            source_name = doc.metadata.get('source', 'Dokumen Tanpa Nama')
                            page_num = doc.metadata.get('page', '0') # Default 0 kalau tidak terdeteksi
                            
                            # Bersihkan path folder (biar cuma nama file)
                            import os
                            clean_name = os.path.basename(source_name)
                            
                            snippet = doc.page_content[:200].replace("\n", " ") # Ambil cuplikan teks
                            
                            st.markdown(f"**{i+1}. 📄 {clean_name}** (Halaman {page_num})")
                            st.caption(f"matched content: ...{snippet}...")
                            
                            # Simpan ke list untuk history
                            saved_sources.append({
                                "source": clean_name,
                                "page": page_num,
                                "content": snippet
                            })
                else:
                    if "Error" not in answer_text:
                        st.caption("ℹ️ Menjawab berdasarkan pengetahuan umum (tidak ada dokumen relevan).")

                # Simpan ke history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer_text,
                    "sources": saved_sources
                })