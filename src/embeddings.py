"""
embeddings.py
--------------
Generates vector embeddings locally using sentence-transformers
(all-MiniLM-L6-v2 -- small, fast, free, no API key needed).

The model is cached with st.cache_resource so it only loads once per
server session instead of on every rerun.
"""

import streamlit as st
from sentence_transformers import SentenceTransformer


@st.cache_resource(show_spinner=False)
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts):
    """
    Accepts a list of strings (or a single string) and returns
    a numpy array of embeddings.
    """
    if isinstance(texts, str):
        texts = [texts]
    model = load_embedder()
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
