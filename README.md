# 🤖 Multi-PDF RAG Chatbot

A fully local, privacy-first AI chatbot that lets you upload multiple PDFs and chat with them using natural language — powered by Llama 3.2 via Ollama. No API key needed, no data leaves your machine.

## ✨ Features

- 📂 **Multi-PDF Support** — Upload up to 5 PDFs simultaneously
- 🧠 **RAG Pipeline** — Retrieval Augmented Generation using Chroma vector store
- 💬 **Conversation Memory** — Remembers previous questions in the session
- 📄 **Source Highlighting** — Shows exactly which page the answer came from
- 📊 **Confidence Scoring** — Tells you how confident the model is in each answer
- 📥 **Chat History Export** — Download your full conversation as a text file
- 🎨 **Beautiful Dark UI** — Clean Streamlit interface with gradient design
- 👤 **Personalised Experience** — Greets you by name with a daily quote
- 🔒 **100% Local** — No API key, no internet required after setup

## 🛠️ Tech Stack

- **Python** — Core language
- **LangChain** — RAG pipeline orchestration
- **Chroma** — Vector store for document embeddings
- **Ollama + Llama 3.2** — Local LLM, runs entirely on your machine
- **PyMuPDF (fitz)** — PDF text extraction
- **Streamlit** — Interactive web UI

## 🚀 How to Run

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com) installed

### 1. Clone the repo
```bash
git clone https://github.com/hitishanathwani/pdf-chatbot-nlp.git
cd pdf-chatbot-nlp
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull the Llama model
```bash
ollama pull llama3.2
```

### 4. Run the app
```bash
streamlit run app.py
```

### 5. Open in browser
Go to `http://localhost:8501`

## 📸 Screenshots

> Upload your PDFs → Ask questions → Get answers with source citations

## 👩‍💻 Author
**Hitisha Nathwani**
[LinkedIn](https://linkedin.com/in/hitishanathwani) • [GitHub](https://github.com/hitishanathwani)