import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

# services
from app.services.crawler import crawl_website        # ⬅️ NEW
from app.services.text_processing import process_text_to_chunks
from app.services.embeddings import embed_text
from app.services.vector_store import add_chunks_to_chroma

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", response_model=schemas.BotCreateResponse)
def create_bot(payload: schemas.BotCreateRequest, db: Session = Depends(get_db)):
    """
    Multi-page pipeline:
    1. Save bot in database
    2. Crawl website for up to N pages
    3. Chunk each page separately
    4. Embed all chunks
    5. Store in ChromaDB with page_url metadata
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
    # 💥  MULTI-PAGE PIPELINE STARTS
    # -------------------------------------------------------------
    logger.info("Starting multi-page bot processing pipeline...")

    try:
        # 1️⃣ Crawl website → returns dict: {url: html_text}
        logger.info("Crawling website...")
        page_data = crawl_website(website_url, max_pages=10)

        if not page_data:
            raise Exception("No pages found during crawling.")

        logger.info(f"Crawled {len(page_data)} pages.")

        # Prepare final lists
        all_chunks = []
        all_embeddings = []
        all_metadata = []

        # 2️⃣ For each page: clean → chunk → embed
        for page_url, raw_text in page_data.items():
            logger.info(f"Processing page: {page_url}")

            chunks = process_text_to_chunks(raw_text)

            if not chunks:
                logger.warning(f"No chunks created for page: {page_url}")
                continue

            embeddings = embed_text(chunks)

            # Save metadata for each chunk
            for c, e in zip(chunks, embeddings):
                all_chunks.append(c)
                all_embeddings.append(e)
                all_metadata.append({"page_url": page_url})

        if len(all_chunks) == 0:
            raise Exception("No chunks generated from entire website!")

        # 3️⃣ Save in ChromaDB
        logger.info(f"Saving {len(all_chunks)} chunks to ChromaDB...")
        add_chunks_to_chroma(bot_id, all_chunks, all_embeddings, all_metadata)

        # 4️⃣ Finally mark bot ready
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

    return schemas.BotCreateResponse(
        bot_id=new_bot.bot_id,
        chat_url=f"/chat/{new_bot.bot_id}",
        status=new_bot.status,
    )
