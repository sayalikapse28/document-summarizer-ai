"""
app.py
-------
AI-Powered Document Summarizer & Q&A (RAG-based)

Upload a PDF / DOCX / XLSX / CSV / TXT file -> get an AI-generated summary
-> ask unlimited follow-up questions answered using Retrieval-Augmented
Generation (RAG) grounded in the document's actual content.

Tech stack (all free):
- Streamlit          -> UI + hosting (Streamlit Community Cloud)
- Groq API           -> free-tier LLM inference (Llama 3.3 70B)
- sentence-transformers -> free local embeddings
- FAISS              -> free local vector similarity search
"""

import streamlit as st

from src.document_parser import extract_text
from src.text_chunker import chunk_text
from src.embeddings import embed_texts
from src.vector_store import VectorStore
from src.ai_engine import get_client, summarize_text, answer_question
from src.config import get_api_key

st.set_page_config(page_title="AI Document Summarizer", page_icon="📄", layout="wide")

st.title("📄 AI-Powered Document Summarizer & Q&A")
st.caption(
    "Upload a PDF, Word, Excel, or CSV file — get an instant AI summary "
    "and ask follow-up questions grounded in the document (RAG-powered)."
)

# ---------------------------------------------------------------------
# Sidebar - settings
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.caption("Groq API key is read from Streamlit secrets or environment variables.")
    summary_style = st.selectbox("Summary style", ["concise", "detailed", "executive"])
    st.markdown("---")
    st.markdown("**Supported formats:** PDF, DOCX, XLSX, CSV, TXT")
    st.markdown("---")
    if st.button("🗑️ Clear session"):
        for key in ["doc_text", "vector_store", "chat_history", "summary"]:
            st.session_state.pop(key, None)
        st.rerun()

api_key_input = get_api_key()

# ---------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------
for key, default in [
    ("doc_text", None),
    ("vector_store", None),
    ("chat_history", []),
    ("summary", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------------
# File upload + processing
# ---------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload your document", type=["pdf", "docx", "xlsx", "xls", "csv", "txt"]
)

if uploaded_file and st.button("🔍 Process Document", type="primary"):
    if not api_key_input:
        st.error("Groq API key is missing. Configure GROQ_API_KEY in Streamlit secrets or your environment.")
    else:
        try:
            with st.spinner("Extracting text from document..."):
                text = extract_text(uploaded_file)
                if not text.strip():
                    st.error("Couldn't extract any text from this file. It may be scanned/image-based.")
                    st.stop()
                st.session_state.doc_text = text

            with st.spinner("Building searchable index (embeddings)..."):
                chunks = chunk_text(text)
                embeddings = embed_texts(chunks)
                store = VectorStore(dim=embeddings.shape[1])
                store.add(embeddings, chunks)
                st.session_state.vector_store = store

            with st.spinner("Generating AI summary..."):
                client = get_client(api_key_input)
                st.session_state.summary = summarize_text(client, text, style=summary_style)
                st.session_state.chat_history = []

            st.success("✅ Document processed! See the summary and ask questions below.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# ---------------------------------------------------------------------
# Summary + document stats
# ---------------------------------------------------------------------
if st.session_state.summary:
    word_count = len(st.session_state.doc_text.split())
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📝 Summary")
        st.markdown(st.session_state.summary)
    with col2:
        st.metric("Document word count", f"{word_count:,}")

    st.divider()

    # -------------------------------------------------------------
    # Follow-up Q&A (RAG chat)
    # -------------------------------------------------------------
    st.subheader("💬 Ask follow-up questions")

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])

    question = st.chat_input("Ask something about the document...")
    if question:
        if not api_key_input:
            st.error("Groq API key is missing. Configure GROQ_API_KEY in Streamlit secrets or your environment.")
        else:
            with st.chat_message("user"):
                st.write(question)
            with st.spinner("Thinking..."):
                client = get_client(api_key_input)
                q_embedding = embed_texts([question])[0]
                relevant_chunks = st.session_state.vector_store.search(q_embedding, top_k=4)
                answer = answer_question(
                    client, question, relevant_chunks, st.session_state.chat_history
                )
            with st.chat_message("assistant"):
                st.write(answer)
            st.session_state.chat_history.append({"question": question, "answer": answer})
else:
    st.info("👆 Upload a document and click **Process Document** to get started.")
