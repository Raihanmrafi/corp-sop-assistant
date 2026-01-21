import streamlit as st
from core import rag

def show_chat_page():
    st.title("🤖 Asisten Cerdas Kantor (Hybrid)")

    # 1. Inisialisasi History Tampilan (UI)
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # 2. Inisialisasi History Logika (Untuk Otak AI)
    if "chat_history_memory" not in st.session_state:
        st.session_state.chat_history_memory = []

    # Tampilkan Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Sumber Referensi"):
                    for source in message["sources"]:
                        st.markdown(f"- {source}")

    # Input User
    if prompt := st.chat_input("Tanyakan sesuatu..."):
        # Tampilkan pesan user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if st.session_state.vector_store is not None:
            with st.chat_message("assistant"):
                
                # --- AMBIL MODE YANG DIPILIH DARI SIDEBAR ---
                current_mode = st.session_state.get("ai_mode", "cloud") # Default cloud kalau belum pilih
                
                with st.spinner(f"Sedang berpikir ({current_mode.upper()} Mode)..."):
                    
                    # --- PROSES PERTANYAAN DENGAN MODE TERTENTU ---
                    answer_text, source_docs = rag.process_question(
                        st.session_state.vector_store, 
                        prompt,
                        st.session_state.chat_history_memory,
                        mode=current_mode # <--- INI TAMBAHAN PENTINGNYA
                    )
                    
                    # Format Sumber
                    unique_sources = set()
                    for doc in source_docs:
                        page_num = doc.metadata.get('page', 0) + 1 
                        unique_sources.add(f"Halaman {page_num}")
                    formatted_sources = sorted(list(unique_sources))

                    # Tampilkan Jawaban
                    st.markdown(answer_text)
                    if formatted_sources:
                        with st.expander("📚 Sumber Referensi"):
                            for src in formatted_sources:
                                st.markdown(f"- **{src}**")
            
            # --- SIMPAN KE MEMORI ---
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer_text,
                "sources": formatted_sources
            })
            
            st.session_state.chat_history_memory.append((prompt, answer_text))

        else:
            st.warning("⚠️ Silakan upload dokumen PDF terlebih dahulu di sidebar.")