import asyncio
import chromadb
from app.core.config import settings
from app.services.embedder import embed_text

_lock = asyncio.Lock()
_client = None
_collection = None

SIMILARITY_THRESHOLD = 0.75  # cosine distance — lower = more similar; nomic-embed works well at 0.75


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name="knowledge",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


async def add_chunks(user_id: str, doc_id: str, chunks: list[str], metadata: dict) -> None:
    embeddings = [await embed_text(chunk) for chunk in chunks]
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {**metadata, "chunk_index": i, "doc_id": doc_id, "user_id": user_id}
        for i in range(len(chunks))
    ]

    collection = _get_collection()
    async with _lock:
        collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)


async def search(user_id: str, query: str, n_results: int = 3) -> list[dict]:
    collection = _get_collection()
    total = collection.count()
    if total == 0:
        return []

    query_embedding = await embed_text(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, total),
        where={"user_id": user_id},
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist < SIMILARITY_THRESHOLD:
            hits.append({"content": doc, "metadata": meta, "distance": dist})
    return hits


async def delete_doc_chunks(user_id: str, doc_id: str) -> None:
    collection = _get_collection()
    async with _lock:
        collection.delete(where={"$and": [{"user_id": user_id}, {"doc_id": doc_id}]})


async def total_chunks(user_id: str | None = None) -> int:
    collection = _get_collection()
    if user_id is None:
        return collection.count()
    result = collection.get(where={"user_id": user_id}, include=[])
    return len(result["ids"])
