import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Load embedding model once globally (fast)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

logger.info(f"Loading embedding model: {MODEL_NAME}")
embedding_model = SentenceTransformer(MODEL_NAME)


def embed_text(texts):
    """
    Embed a list of chunk strings into vectors.
    Returns a list of embedding vectors.
    """
    logger.info(f"Embedding {len(texts)} chunks...")
    embeddings = embedding_model.encode(texts, show_progress_bar=False)
    logger.info("Embedding completed.")
    return embeddings
