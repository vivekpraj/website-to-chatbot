import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas

from app.services.embeddings import embed_text
from app.services.rag import build_rag_prompt
from app.services.gemini_client import generate_answer
from app.services.vector_store import retrieve_chunks

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{bot_id}", response_model=schemas.ChatResponse)
def chat_with_bot(bot_id: str, payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Full RAG flow + METRICS UPDATE
    """

    logger.info(f"Chat request received for bot {bot_id}: {payload.message}")

    # 1️⃣ Load bot
    bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bot.status != "ready":
        raise HTTPException(status_code=400, detail=f"Bot status is {bot.status}")

    # =====================================
    # 📊 METRICS UPDATE (Stage 1 Analytics)
    # =====================================
    bot.message_count += 1
    bot.last_used_at = datetime.utcnow()
    db.commit()

    # 2️⃣ Embed user question
    query_vec = embed_text([payload.message])[0]

    # 3️⃣ Retrieve relevant chunks
    chunks, metadatas = retrieve_chunks(bot_id, query_vec, top_k=3)
    if not chunks:
        logger.warning(f"No chunks retrieved from Chroma for bot {bot_id}")
        raise HTTPException(status_code=500, detail="No chunks retrieved from vector database")

    logger.info(f"Retrieved {len(chunks)} chunks for RAG context.")

    # 4️⃣ Build prompt
    prompt = build_rag_prompt(chunks, payload.message)

    # 5️⃣ Generate answer
    answer = generate_answer(prompt)

    # 6️⃣ Format source chunks
    source_chunks = []
    for text, meta in zip(chunks, metadatas):
        source_chunks.append(
            schemas.SourceChunk(
                text=text,
                page_url=meta.get("page_url") if meta else None
            )
        )

    return schemas.ChatResponse(
        answer=answer,
        source_chunks=source_chunks,
    )
