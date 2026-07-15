"""
text_chunker.py
----------------
Splits large documents into overlapping word-based chunks so they can be
embedded and stored in a vector index for retrieval (RAG).

Overlap keeps context from being cut off mid-idea between chunks.
"""


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list:
    """
    Splits text into chunks of `chunk_size` words, with `overlap` words
    shared between consecutive chunks.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap

    return chunks
