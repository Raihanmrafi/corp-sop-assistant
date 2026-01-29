import streamlit as st
import os
from typing import List, Tuple, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI 
from langchain_text_splitters import RecursiveCharacterTextSplitter
# KITA GANTI CHROMA DENGAN FAISS
from langchain_community.vectorstores import FAISS 
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from pypdf import PdfReader
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

load_dotenv()

# --- SETUP MODEL (SAMA SEPERTI SEBELUMNYA) ---
@st.cache_resource
def load_cloud_model():
    """Engine 1: OpenRouter (TNG Tech DeepSeek R1T2 Chimera Free)"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Cek API Key
    if not api_key: 
        print("❌ API Key OpenRouter tidak valid/kosong.")
        return None
        
    try:
        llm = ChatOpenAI(
            # --- INI ID YANG BENAR DARI REFERENSI ABANG ---
            model="tngtech/deepseek-r1t2-chimera:free", 
            # ----------------------------------------------
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,
            max_tokens=1024
        )
        return llm
    except: return None

@st.cache_resource
def load_local_model():
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512, temperature=0.3, return_full_text=False)
        return HuggingFacePipeline(pipeline=pipe)
    except: return None

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# --- PROSES DOKUMEN ---
@st.cache_resource(show_spinner=False)
def load_data_from_folder(folder_path="data"):
    text = ""
    if not os.path.exists(folder_path): os.makedirs(folder_path); return ""
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    for filename in files:
        try:
            reader = PdfReader(os.path.join(folder_path, filename))
            for page in reader.pages: text += page.extract_text() or ""
        except: pass      
    return text

def get_text_chunks(text: str) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    return text_splitter.split_text(text)

# --- DATABASE ENGINE BARU: FAISS (ANTI ERROR SQLITE) ---
@st.cache_resource(show_spinner=False)
def create_vector_db(_text_chunks: List[str]):
    if not _text_chunks: return None
    print(f"💾 Membuat Database FAISS ({len(_text_chunks)} pecahan)...")
    embeddings = get_embedding_model()
    try:
        # FAISS berjalan murni di RAM, sangat cepat & stabil
        vector_store = FAISS.from_texts(texts=_text_chunks, embedding=embeddings)
        return vector_store
    except Exception as e:
        print(f"❌ Error FAISS: {e}")
        return None

# --- CHAT ENGINE ---
def process_question(vector_store, question: str, chat_history: List[Tuple], mode: str) -> Tuple[str, List[Document]]:
    if vector_store is None: return "⚠️ Database kosong. Upload dokumen dulu.", []
    
    # Pilih Model sesuai Sidebar
    llm = load_cloud_model() if mode == "cloud" else load_local_model()
    if llm is None: return "❌ Model AI gagal dimuat.", []

    # Prompt Template
    qa_prompt = PromptTemplate.from_template(
        """<|im_start|>system
        Jawab pertanyaan berdasarkan Context berikut.
        Context:
        {context}
        <|im_end|>
        <|im_start|>user
        {question}
        <|im_end|>
        <|im_start|>assistant
        """
    )
    condense_prompt = PromptTemplate.from_template("<|im_start|>user\nRephrase: {question}\n<|im_end|>\n<|im_start|>assistant")

    try:
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
            condense_question_prompt=condense_prompt,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            return_source_documents=True,
        )
        response = chain.invoke({"question": question, "chat_history": chat_history})
        return response["answer"], response["source_documents"]
    except Exception as e:
        return f"Error: {e}", []