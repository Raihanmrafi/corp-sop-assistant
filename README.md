# 🏢 OfficeDocAI: Intelligent Office Assistant

**OfficeDocAI** is a secure, hybrid Retrieval-Augmented Generation (RAG) system designed to streamline internal knowledge sharing. It allows employees to chat naturally with company documents (SOPs, Policies, etc.) using either powerful Cloud AI or private Local AI.

Built with **Streamlit**, **LangChain**, and **Docker**, this application prioritizes security by using an in-memory vector database (FAISS), ensuring that sensitive embeddings are never persisted to the disk.

---

## 🚀 Key Features

### 🧠 Hybrid AI Engine
* **Cloud Mode:** Integration with OpenRouter (DeepSeek, Llama 3.3) for high-intelligence reasoning.
* **Local Mode:** Support for local models (like Qwen) for fully offline, private, and cost-free operation.
* **Seamless Switching:** Toggle between Cloud and Local engines instantly from the sidebar.

### 🔒 Enterprise-Grade Security
* **RAM-Only Database:** Uses **FAISS** in-memory vector store. No physical vector database files are created, eliminating "file lock" errors and ensuring data privacy.
* **Role-Based Access Control (RBAC):**
    * **Admin (HR):** Full access to upload, delete, and manage documents.
    * **Staff (User):** Read-only access to chat with the assistant.
* **Secure Configuration:** Credentials and API keys are managed via environment variables and ignored in version control.

### 🛠️ Robust Architecture
* **System Monitor:** Real-time debugging panel to verify file indexing and character counts.
* **Dockerized:** Fully containerized for "Build once, run anywhere" portability.
* **Auto-Healing:** Automatic database re-indexing upon system restart or update.

---

## 🏗️ Tech Stack

* **Frontend:** Streamlit
* **Orchestration:** LangChain
* **Vector Store:** FAISS (Facebook AI Similarity Search) - CPU Version
* **Models:** DeepSeek R1 / Llama 3.3 (Cloud) & Qwen 2.5 (Local)
* **Containerization:** Docker
* **Auth:** Streamlit-Authenticator

---

## ⚙️ Installation & Setup

Follow these steps to deploy the application locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/Raihanmrafi/corp-sop-assistant.git](https://github.com/Raihanmrafi/corp-sop-assistant.git)
cd corp-sop-assistant
