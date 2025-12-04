import re
import logging
from typing import List

logger = logging.getLogger(__name__)


# -----------------------------------------------------
# 1. CLEAN RAW TEXT
# -----------------------------------------------------
def clean_text(text: str) -> str:
    """
    Clean scraped text:
    - Remove extra whitespace
    - Remove non-visible characters
    - Normalize newlines
    """
    logger.info("Cleaning scraped text...")

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Normalize newlines
    text = text.strip()

    logger.info(f"Cleaned text length: {len(text)} chars")
    return text


# -----------------------------------------------------
# 2. SPLIT INTO SENTENCES
# -----------------------------------------------------
def split_into_sentences(text: str) -> List[str]:
    """
    Simple sentence splitter using punctuation.
    (Good enough for websites.)
    """
    logger.info("Splitting text into sentences...")

    sentences = re.split(r"(?<=[.!?]) +", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

    logger.info(f"Total sentences: {len(sentences)}")
    return sentences


# -----------------------------------------------------
# 3. CHUNK SENTENCES INTO 500–800 TOKEN-LIKE BLOCKS
# -----------------------------------------------------
def chunk_text(sentences: List[str], max_chunk_size: int = 700) -> List[str]:
    """
    Chunk sentences into blocks of ~700 words (token-like approximation).
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

    logger.info(f"Total chunks created: {len(chunks)}")
    return chunks


# -----------------------------------------------------
# 4. MAIN ENTRY: CLEAN → SENTENCES → CHUNKS
# -----------------------------------------------------
def process_text_to_chunks(raw_text: str) -> List[str]:
    """
    Full pipeline:
    - Clean text
    - Split into sentences
    - Chunk into ~700-word blocks
    """
    cleaned = clean_text(raw_text)
    sentences = split_into_sentences(cleaned)
    chunks = chunk_text(sentences)

    return chunks
