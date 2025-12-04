def build_rag_prompt(context_chunks: list, user_query: str) -> str:
    """
    Build final RAG prompt sent to Gemini.
    """

    context = "\n\n".join(context_chunks)

    return f"""
You are a helpful assistant created to answer questions using ONLY the context provided.

--- CONTEXT ---
{context}
--- END CONTEXT ---

User question: {user_query}

Now provide a clear, short, accurate answer based strictly on the context.
"""

