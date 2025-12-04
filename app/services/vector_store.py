import chromadb
import os
import logging

logger = logging.getLogger(__name__)

BASE_CHROMA_DIR = "app/data/chroma/bots"


def get_chroma_client(bot_id: str):
    """
    Returns (and creates if needed) a persistent Chroma client for this bot.
    """
    bot_dir = os.path.join(BASE_CHROMA_DIR, bot_id)
    os.makedirs(bot_dir, exist_ok=True)

    client = chromadb.PersistentClient(path=bot_dir)
    return client


def get_or_create_collection(client, collection_name="docs"):
    """
    Each bot gets one named collection.
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def add_chunks_to_chroma(bot_id, chunks, embeddings, metadatas):
    """
    Save embeddings and text chunks into Chroma for this bot.
    """
    client = get_chroma_client(bot_id)
    collection = get_or_create_collection(client)

    ids = [f"{bot_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"bot_id": bot_id, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,   # <-- FIXED, now defined
        ids=ids
    )

    logger.info(f"Stored {len(chunks)} chunks inside Chroma for bot {bot_id}.")
    return True


# -------------------------------------------------------------
# NEW: Retrieve chunks for RAG
# -------------------------------------------------------------
def retrieve_chunks(bot_id: str, query_vector, top_k=3):
    """
    Query Chroma using embedding vector.
    Returns: (documents, metadatas)
    """
    client = get_chroma_client(bot_id)
    collection = get_or_create_collection(client)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas"]
    )

    if not results or "documents" not in results:
        return [], []

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    return docs, metas
