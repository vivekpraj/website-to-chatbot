import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas

from app.services.embeddings import embed_text
from app.services.vector_store import get_chroma_client, get_or_create_collection
from app.services.gemini_client import generate_answer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{bot_id}", response_model=schemas.ChatResponse)
def chat_with_bot(bot_id: str, payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Full RAG pipeline:
    1. Load bot from DB
    2. Embed user query
    3. Search Chroma
    4. Build RAG prompt
    5. Send to Gemini
    6. Return answer
    """

    # 1️⃣ Load bot
    bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    if bot.status != "ready":
        raise HTTPException(status_code=400, detail=f"Bot status is {bot.status}")

    logger.info(f"Chat request to bot {bot_id}: {payload.message}")

    # 2️⃣ Embed user query
    query_embedding = embed_text([payload.message])[0]

    # 3️⃣ Load Chroma collection
    client = get_chroma_client(bot_id)
    collection = get_or_create_collection(client)

    # Retrieve top 3 relevant chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    retrieved_chunks = results["documents"][0]

    logger.info(f"Retrieved {len(retrieved_chunks)} context chunks.")

    # 4️⃣ Build RAG prompt
    context_block = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are a helpful assistant. Use ONLY the context below to answer.

--- CONTEXT ---
{context_block}
--- END CONTEXT ---

User question: {payload.message}

Provide a clear, accurate answer.
"""

    # 5️⃣ Send to Gemini
    answer = generate_answer(prompt)

    # 6️⃣ Return response
    return schemas.ChatResponse(
        answer=answer,
        retrieved_chunks=retrieved_chunks
    )
