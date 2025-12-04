def build_rag_prompt(context_chunks: list, user_query: str) -> str:
    """
    Build the final RAG prompt to send to Gemini.
    """

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful AI assistant. Use ONLY the context below to answer.

--- CONTEXT ---
{context}
--- END CONTEXT ---

User question: {user_query}

Provide a clear, accurate answer.
"""

    return prompt
