import chromadb
import os
import logging
import shutil  # <-- add at top


logger = logging.getLogger(__name__)

BASE_CHROMA_DIR = "app/data/chroma/bots"


def get_chroma_client(bot_id: str):
    """
    Returns (and creates if needed) a persistent Chroma client for this bot.
    Each bot gets its own Chroma directory.
    """
    bot_dir = os.path.join(BASE_CHROMA_DIR, bot_id)
    os.makedirs(bot_dir, exist_ok=True)

    client = chromadb.PersistentClient(path=bot_dir)
    return client


def get_or_create_collection(client, collection_name: str = "docs"):
    """
    Each bot gets one named collection in its Chroma DB.
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def add_chunks_to_chroma(bot_id: str, chunks: list, embeddings: list, metadatas: list):
    """
    Save embeddings + text chunks + metadata into Chroma for this bot.
    """
    if len(chunks) != len(embeddings) or len(chunks) != len(metadatas):
        raise ValueError("chunks, embeddings, metadatas must have same length")

    client = get_chroma_client(bot_id)
    collection = get_or_create_collection(client)

    ids = [f"{bot_id}_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    logger.info(f"Stored {len(chunks)} chunks for bot {bot_id} in Chroma.")
    return True


def retrieve_chunks(bot_id: str, query_vector, top_k: int = 3):
    """
    Query Chroma using an embedding vector.
    Returns: (documents, metadatas)
    """
    client = get_chroma_client(bot_id)
    collection = get_or_create_collection(client)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    docs = results.get("documents", [[]])
    metas = results.get("metadatas", [[]])

    if not docs or not docs[0]:
        logger.warning(f"No documents found for bot {bot_id} in Chroma.")
        return [], []

    return docs[0], metas[0]

def reset_chroma_for_bot(bot_id: str):
    """
    Logically reset Chroma for this bot by deleting all collections
    in its persistent directory (instead of deleting files on disk).

    This avoids PermissionError on Windows when files are locked.
    """
    bot_dir = os.path.join(BASE_CHROMA_DIR, bot_id)

    if not os.path.exists(bot_dir):
        logger.info(f"No existing Chroma directory for bot {bot_id}, nothing to reset.")
        return

    try:
        # Open the existing Chroma client at this path
        client = chromadb.PersistentClient(path=bot_dir)

        # Delete all collections associated with this bot
        collections = client.list_collections()
        if not collections:
            logger.info(f"No collections found for bot {bot_id} in {bot_dir}.")
            return

        for coll in collections:
            logger.info(f"Deleting Chroma collection '{coll.name}' for bot {bot_id}")
            client.delete_collection(name=coll.name)

        logger.info(f"Successfully cleared Chroma collections for bot {bot_id} in {bot_dir}")

    except Exception as e:
        logger.exception(f"Failed to reset Chroma for bot {bot_id}: {e}")
