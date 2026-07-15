"""
config.py
----------
Resolves the Groq API key from Streamlit secrets (used in deployment)
or environment variables (used for local dev), so users don't have to
paste it in manually every time if it's already configured.
"""

import os
import streamlit as st


def get_api_key() -> str:
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "")
