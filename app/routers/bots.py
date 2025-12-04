import logging
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

# services
from app.services.scraper import scrape_page
from app.services.text_processing import process_text_to_chunks
from app.services.embeddings import embed_text
from app.services.vector_store import add_chunks_to_chroma

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", response_model=schemas.BotCreateResponse)
def create_bot(payload: schemas.BotCreateRequest, db: Session = Depends(get_db)):
    """
    Complete pipeline:
    1. Save bot in DB as "processing"
    2. Scrape website
    3. Clean + Chunk the text
    4. Embed chunks
    5. Store into Chroma
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
    # 💥  PIPELINE STARTS  (scrape → chunk → embed → save)
    # -------------------------------------------------------------
    logger.info("Starting bot processing pipeline...")

    try:
        # 1️⃣ SCRAPE TEXT (async)
        scraped_text = scrape_page(website_url)
        if not scraped_text or len(scraped_text) < 50:
            raise Exception("Scraper returned insufficient content.")

        # 2️⃣ CLEAN + CHUNK
        chunks = process_text_to_chunks(scraped_text)
        if len(chunks) == 0:
            raise Exception("No chunks created from scraped content.")

        # 3️⃣ EMBED CHUNKS
        embeddings = embed_text(chunks)

        # 4️⃣ STORE IN CHROMA
        add_chunks_to_chroma(bot_id, chunks, embeddings)

        # 5️⃣ NOW MARK AS READY
        new_bot.status = "ready"
        db.commit()

        logger.info(f"Bot {bot_id} fully generated and ready!")

    except Exception as e:
        logger.exception("Pipeline failed. Marking bot as failed.")
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