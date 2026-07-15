"""
ai_engine.py
-------------
Wraps calls to the Groq API (https://console.groq.com) which offers a
generous FREE tier for fast LLM inference (Llama 3.3 70B).

Two capabilities:
1. summarize_text()   -> single-shot document summarization
2. answer_question()  -> RAG-style Q&A grounded in retrieved chunks
"""

from groq import Groq

MODEL_NAME = "llama-3.3-70b-versatile"

STYLE_PROMPTS = {
    "concise": "Provide a concise summary in 5-7 bullet points.",
    "detailed": "Provide a detailed, well-structured summary covering all key sections and important details.",
    "executive": "Provide a short executive summary (3-4 sentences) suitable for a business audience.",
}


def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def summarize_text(client: Groq, text: str, style: str = "concise") -> str:
    instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["concise"])

    # Guard against extremely large documents exceeding context limits.
    max_chars = 15000
    truncated = text[:max_chars]
    note = "\n\n[Note: document was truncated for summarization due to length.]" if len(text) > max_chars else ""

    prompt = f"""You are an expert document summarizer.
{instruction}

Document:
\"\"\"{truncated}\"\"\"

Summary:"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800,
    )
    return response.choices[0].message.content + note


def answer_question(client: Groq, question: str, context_chunks: list, chat_history: list = None) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant context found."

    history_text = ""
    if chat_history:
        for turn in chat_history[-4:]:
            history_text += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    prompt = f"""You are a helpful assistant answering questions about a specific document.
Use ONLY the context provided below to answer. If the answer isn't in the context,
say you don't have enough information rather than guessing.

Context from the document:
{context}

Previous conversation (for reference):
{history_text}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    return response.choices[0].message.content
