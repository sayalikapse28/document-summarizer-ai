# 📄 AI-Powered Document Summarizer & Q&A

An AI application that lets you upload a document (PDF, Word, Excel, or CSV)
and instantly get an AI-generated summary, then ask unlimited follow-up
questions answered using **Retrieval-Augmented Generation (RAG)** grounded
in the document's actual content.

**Live demo:** https://document-summarizer-ai-mjtejtkr2jjrkfjqwv5lgf.streamlit.app/

## Features

- 📁 Multi-format support: PDF, DOCX, XLSX/XLS, CSV, TXT
- 🧠 AI summarization with 3 styles: concise, detailed, executive
- 💬 Follow-up Q&A chat grounded in the document (not hallucinated)
- 🔍 RAG pipeline: chunking → local embeddings → FAISS similarity search → LLM answer
- ⚡ Fast inference via Groq's free-tier LLM API (Llama 3.3 70B)
- 🆓 Built entirely with free/open-source tools — no paid API required

## Tech Stack

| Component        | Tool                                   |
|-------------------|-----------------------------------------|
| UI & hosting       | Streamlit / Streamlit Community Cloud  |
| LLM inference      | Groq API (Llama 3.3 70B, free tier)    |
| Embeddings         | sentence-transformers (all-MiniLM-L6-v2, local) |
| Vector search       | FAISS (local, in-memory)               |
| Document parsing   | pypdf, python-docx, pandas/openpyxl    |

## Architecture

```
Upload file
    │
    ▼
document_parser.py  → extract raw text (per file type)
    │
    ▼
text_chunker.py      → split into overlapping chunks
    │
    ▼
embeddings.py         → embed chunks locally (sentence-transformers)
    │
    ▼
vector_store.py       → store in FAISS index
    │
    ├──► ai_engine.summarize_text()   → one-shot summary of full doc
    │
    └──► User asks a question
              │
              ▼
         embed the question
              │
              ▼
         FAISS retrieves top-k relevant chunks
              │
              ▼
         ai_engine.answer_question() → LLM answers using retrieved context only
```

## Project Structure

```
document-summarizer-ai/
├── app.py                        # Streamlit UI + orchestration
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml                # theme
│   └── secrets.toml.example       # template for API key
└── src/
    ├── __init__.py
    ├── document_parser.py         # PDF/DOCX/XLSX/CSV/TXT text extraction
    ├── text_chunker.py            # chunking with overlap
    ├── embeddings.py              # sentence-transformers wrapper
    ├── vector_store.py            # FAISS wrapper
    ├── ai_engine.py                # Groq LLM calls (summarize + Q&A)
    └── config.py                  # API key resolution
```

## Run Locally

```bash
git clone https://github.com/<your-username>/document-summarizer-ai.git
cd document-summarizer-ai
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Get a **free** Groq API key at https://console.groq.com, then either:

- paste it into the sidebar text field at runtime, or
- create `.streamlit/secrets.toml` (copy from `secrets.toml.example`) with:
  ```toml
  GROQ_API_KEY = "your-key-here"
  ```

Run the app:

```bash
streamlit run app.py
```

Open http://localhost:8501

## Deploy for Free (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io → **New app**.
3. Select your repo, branch `main`, main file `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your-key-here"
   ```
5. Click **Deploy**. You'll get a public URL like:
   `https://<your-app-name>.streamlit.app`

## Future Improvements

- Multi-document comparison / cross-document Q&A
- Persistent vector store (e.g., Chroma/Pinecone) for large document libraries
- OCR support for scanned PDFs (e.g., Tesseract)
- Export summary + chat transcript as PDF/DOCX
- User authentication and saved chat history per user

## License

MIT
