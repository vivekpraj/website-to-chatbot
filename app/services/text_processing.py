import re
import logging
from typing import List

# ✅ use the cleaner we created in app/services/cleaner.py
from app.services.cleaner import clean_scraped_text as clean_raw_text

logger = logging.getLogger(__name__)


# -----------------------------------------------------
# 1. SPLIT INTO SENTENCES
# -----------------------------------------------------
def split_into_sentences(text: str) -> List[str]:
    """
    Rough sentence splitter using punctuation.
    Not perfect, but good enough for chunking.
    """
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    # Split on punctuation followed by space
    sentences = re.split(r"(?<=[.!?])\s+", text)
    # Remove empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


# -----------------------------------------------------
# 2. OPTIONAL: LEGACY CHUNKING (not used by pipeline now)
# -----------------------------------------------------
def chunk_text(sentences: List[str], max_chunk_size: int = 700) -> List[str]:
    """
    Legacy helper: chunk sentences into blocks of ~700 words.
    (Kept for reference; main pipeline uses process_text_to_chunks.)
    """
    logger.info("Chunking sentences into word blocks...")

    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence.split())

        # If adding this sentence exceeds limit → start new chunk
        if current_len + sentence_len > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0

        current_chunk.append(sentence)
        current_len += sentence_len

    # Last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    logger.info(f"Total chunks created (legacy): {len(chunks)}")
    return chunks


# -----------------------------------------------------
# 3. MAIN ENTRY: CLEAN → SENTENCES → OVERLAPPING CHUNKS
# -----------------------------------------------------
def process_text_to_chunks(
    text: str,
    max_words: int = 220,
    overlap_words: int = 40,
) -> List[str]:
    """
    Convert raw page text into overlapping chunks.

    Pipeline:
    1. Clean raw HTML text using cleaner.clean_text()
    2. Split into sentences
    3. Build overlapping word-window chunks

    - max_words:     target size of each chunk (approx tokens)
    - overlap_words: how many words to overlap between consecutive chunks
    """

    logger.info("Starting text cleaning + chunking...")

    # 1️⃣ Clean raw scraped text (remove navbar/footer/junk/repeats/etc.)
    cleaned = clean_raw_text(text)
    logger.info(f"Cleaned text length after cleaner: {len(cleaned)} chars")

    if not cleaned.strip():
        logger.warning("Cleaned text is empty after cleaning.")
        return []

    # 2️⃣ Sentence split
    sentences = split_into_sentences(cleaned)
    logger.info(f"Total sentences after split: {len(sentences)}")

    if not sentences:
        return []

    # 3️⃣ Build overlapping chunks
    chunks: List[str] = []
    current_words: List[str] = []

    for sent in sentences:
        sent_words = sent.split()

        # If a single sentence is longer than max_words, put it as its own chunk
        if len(sent_words) >= max_words:
            if current_words:
                chunks.append(" ".join(current_words))
                current_words = []
            chunks.append(" ".join(sent_words))
            continue

        # If adding this sentence would exceed max_words, flush current chunk
        if len(current_words) + len(sent_words) > max_words:
            if current_words:
                chunks.append(" ".join(current_words))
                # Overlap: keep last N words for next chunk
                if overlap_words > 0:
                    current_words = current_words[-overlap_words:]
                else:
                    current_words = []

        # Add this sentence's words to the buffer
        current_words.extend(sent_words)

    # Last chunk
    if current_words:
        chunks.append(" ".join(current_words))

    logger.info(f"Total chunks created: {len(chunks)}")
    return chunks
