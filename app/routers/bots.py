import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

from app.services.crawler import crawl_website
from app.services.text_processing import process_text_to_chunks
from app.services.embeddings import embed_text
from app.services.vector_store import add_chunks_to_chroma, reset_chroma_for_bot

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", response_model=schemas.BotCreateResponse)
def create_bot(payload: schemas.BotCreateRequest, db: Session = Depends(get_db)):
    """
    Complete multi-page pipeline:
    1. Save bot in DB as "processing"
    2. Crawl website (multi-page)
    3. Clean + Chunk per page
    4. Embed chunks
    5. Store into Chroma with page_url metadata
    6. Mark bot as READY
    """

    website_url = str(payload.website_url)
    logger.info(f"Bot creation requested for URL: {website_url}")

    # --- check for existing bot ---
    existing_bot = (
        db.query(models.Bot)
        .filter(models.Bot.website_url == website_url)
        .first()
    )
    if existing_bot:
        logger.info(
            f"Bot already exists for URL {website_url}, reusing bot_id={existing_bot.bot_id}"
        )
        chat_url = f"/chat/{existing_bot.bot_id}"
        return schemas.BotCreateResponse(
            bot_id=existing_bot.bot_id,
            chat_url=chat_url,
            status=existing_bot.status,
        )

    # --- create new bot ---
    bot_id = str(uuid.uuid4())
    logger.info(f"Creating new bot with bot_id={bot_id}")

    new_bot = models.Bot(
        bot_id=bot_id,
        website_url=website_url,
        status="processing",
        vector_index_path=f"app/data/chroma/bots/{bot_id}",
    )

    try:
        db.add(new_bot)
        db.commit()
        db.refresh(new_bot)
    except Exception:
        db.rollback()
        logger.exception("Failed to save bot in DB.")
        raise HTTPException(status_code=500, detail="Failed to create bot")

    # -------------------------------------------------------------
    # 💥  PIPELINE STARTS  (crawl → chunk → embed → save)
    # -------------------------------------------------------------
    logger.info("Starting multi-page bot processing pipeline...")

    try:
        # 1️⃣ CRAWL WEBSITE
        page_texts = crawl_website(website_url, max_pages=10)

        if not page_texts:
            raise Exception("No pages found or all pages were empty.")

        logger.info(f"Crawled {len(page_texts)} pages.")

        all_chunks = []
        all_embeddings = []
        all_metadatas = []

        # 2️⃣ FOR EACH PAGE → CHUNK + EMBED + METADATA
        for page_url, text in page_texts.items():
            logger.info(f"Processing page: {page_url}")

            chunks = process_text_to_chunks(text)
            if not chunks:
                logger.warning(f"No chunks created for page: {page_url}")
                continue

            embeddings = embed_text(chunks)

            for c, e in zip(chunks, embeddings):
                chunk_index = len(all_chunks)
                all_chunks.append(c)
                all_embeddings.append(e)
                all_metadatas.append(
                    {
                        "bot_id": bot_id,
                        "page_url": page_url,
                        "chunk_index": chunk_index,
                    }
                )

        if not all_chunks:
            raise Exception("No chunks generated from the entire website.")

        # 3️⃣ STORE IN CHROMA
        logger.info(f"Saving {len(all_chunks)} chunks into Chroma for bot {bot_id}")
        add_chunks_to_chroma(bot_id, all_chunks, all_embeddings, all_metadatas)

        # 4️⃣ MARK BOT READY
        new_bot.status = "ready"
        db.commit()
        logger.info(f"Bot {bot_id} fully generated and READY!")

    except Exception as e:
        logger.exception("Pipeline failed. Marking bot as FAILED.")
        new_bot.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Bot processing failed: {str(e)}")

    # -------------------------------------------------------------
    # 💥  PIPELINE COMPLETED
    # -------------------------------------------------------------

    chat_url = f"/chat/{new_bot.bot_id}"

    return schemas.BotCreateResponse(
        bot_id=new_bot.bot_id,
        chat_url=chat_url,
        status=new_bot.status,
    )

@router.post("/{bot_id}/refresh", response_model=schemas.BotCreateResponse)
def refresh_bot(bot_id: str, db: Session = Depends(get_db)):
    """
    Rebuild an existing bot:
    1. Set status to 'processing'
    2. Delete old vector store
    3. Re-crawl website
    4. Clean + chunk + embed
    5. Store into Chroma
    6. Mark as READY again
    """

    logger.info(f"Refresh requested for bot_id={bot_id}")

    # 1️⃣ Load bot
    bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    website_url = bot.website_url
    logger.info(f"Rebuilding bot for website: {website_url}")

    # Set status to processing
    bot.status = "processing"
    db.commit()
    db.refresh(bot)

    try:
        # 2️⃣ Clear existing Chroma index
        reset_chroma_for_bot(bot_id)

        # 3️⃣ Crawl website again
        page_texts = crawl_website(website_url, max_pages=10)
        if not page_texts:
            raise Exception("No pages found or all pages were empty during refresh.")

        logger.info(f"Re-crawled {len(page_texts)} pages for bot {bot_id}")

        all_chunks = []
        all_embeddings = []
        all_metadatas = []

        # 4️⃣ Clean + chunk + embed per page
        for page_url, text in page_texts.items():
            logger.info(f"[REFRESH] Processing page: {page_url}")

            chunks = process_text_to_chunks(text)
            if not chunks:
                logger.warning(f"[REFRESH] No chunks created for page: {page_url}")
                continue

            embeddings = embed_text(chunks)

            for c, e in zip(chunks, embeddings):
                chunk_index = len(all_chunks)
                all_chunks.append(c)
                all_embeddings.append(e)
                all_metadatas.append(
                    {
                        "bot_id": bot_id,
                        "page_url": page_url,
                        "chunk_index": chunk_index,
                    }
                )

        if not all_chunks:
            raise Exception("No chunks created during refresh for this website.")

        # 5️⃣ Save to Chroma
        add_chunks_to_chroma(bot_id, all_chunks, all_embeddings, all_metadatas)

        # 6️⃣ Mark bot as ready
        bot.status = "ready"
        db.commit()
        db.refresh(bot)

        logger.info(f"Bot {bot_id} successfully refreshed and READY.")

    except Exception as e:
        logger.exception("Refresh pipeline failed. Marking bot as FAILED.")
        bot.status = "failed"
        db.commit()
        db.refresh(bot)
        raise HTTPException(status_code=500, detail=f"Bot refresh failed: {str(e)}")

    # Reuse BotCreateResponse to return status + chat_url
    chat_url = f"/chat/{bot.bot_id}"
    return schemas.BotCreateResponse(
        bot_id=bot.bot_id,
        chat_url=chat_url,
        status=bot.status,
    )