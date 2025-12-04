import chromadb
import os

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
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

def add_chunks_to_chroma(bot_id: str, chunks: list, embeddings: list):
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
        metadatas=metadatas,
        ids=ids
    )

    return True
