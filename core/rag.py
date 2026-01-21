import streamlit as st
import os
import shutil
from pypdf import PdfReader
from typing import List, Tuple, Any

# Library Env
from dotenv import load_dotenv

# --- PERUBAHAN PENTING DISINI (GANTI GROQ JADI OPENROUTER) ---
from langchain_openai import ChatOpenAI 
# -------------------------------------------------------------

# Library LangChain & Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma 
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# Library Local Model
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load Env
load_dotenv()
CHROMA_PATH = "chroma_db_store"

# --- 1. SETUP MODEL ENGINE (HYBRID: OPENROUTER vs LOCAL) ---

@st.cache_resource
def load_cloud_model():
    """Engine 1: OpenRouter (Llama 3.3 Free)"""
    # Ambil key OpenRouter dari .env
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        st.error("⚠️ API Key OpenRouter tidak ditemukan di .env!")
        return None
    
    try:
        # Kita pakai ChatOpenAI tapi diarahkan ke base_url OpenRouter
        llm = ChatOpenAI(
            model="meta-llama/llama-3.3-70b-instruct:free", # Model Gratisan OpenRouter
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,
            max_tokens=1024
        )
        return llm
    except Exception as e:
        st.error(f"Error loading Cloud Model: {e}")
        return None

@st.cache_resource
def load_local_model():
    """Engine 2: Qwen Local (Privasi & Offline)"""
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.1,
            return_full_text=False 
        )
        return HuggingFacePipeline(pipeline=pipe)
    except Exception as e:
        st.error(f"Error loading Local Model: {e}")
        return None

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# --- 2. DOCUMENT PROCESSING ---
def get_pdf_text(pdf_docs: List[Any]) -> str:
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text: str) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    return text_splitter.split_text(text)

# --- 3. DATABASE MANAGEMENT ---
def create_vector_db(text_chunks: List[str]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    embeddings = get_embedding_model()
    vector_store = Chroma.from_texts(
        texts=text_chunks, 
        embedding=embeddings, 
        persist_directory=CHROMA_PATH
    )
    return vector_store

def load_existing_vector_db():
    embeddings = get_embedding_model()
    if os.path.exists(CHROMA_PATH):
        vector_store = Chroma(
            persist_directory=CHROMA_PATH, 
            embedding_function=embeddings
        )
        return vector_store
    return None

# --- 4. RETRIEVAL ENGINE ---
def get_conversational_chain(vector_store, mode="cloud"):
    if mode == "cloud":
        llm = load_cloud_model()
    else:
        llm = load_local_model()

    if llm is None:
        return None

    condense_question_prompt = PromptTemplate.from_template(
        """<|im_start|>system
        Rephrase the follow up question to be a standalone question.
        Chat History: {chat_history}
        Follow Up Input: {question}
        Standalone question:<|im_end|>
        <|im_start|>assistant
        """
    )

    qa_prompt = PromptTemplate.from_template(
        """<|im_start|>system
        Anda adalah Asisten Pintar SOP Kantor.
        INSTRUKSI:
        1. JIKA user menyapa ("Halo", "Pagi"), jawab sopan & tawarkan bantuan. ABAIKAN Context.
        2. JIKA bertanya SOP, jawab HANYA berdasarkan Context.
        
        Context:
        {context}
        <|im_end|>
        <|im_start|>user
        {question}
        <|im_end|>
        <|im_start|>assistant
        """
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        condense_question_prompt=condense_question_prompt,
        combine_docs_chain_kwargs={"prompt": qa_prompt},
        return_source_documents=True,
    )
    return chain

def process_question(vector_store, question: str, chat_history: List[Tuple], mode: str) -> Tuple[str, List[Document]]:
    chain = get_conversational_chain(vector_store, mode)
    if chain is None:
        return "Maaf, model gagal dimuat. Cek API Key.", []

    response = chain.invoke({
        "question": question,
        "chat_history": chat_history
    })
    return response["answer"], response["source_documents"]