import ollama

from app.core.config import settings


async def embed_text(text: str) -> list[float]:
    client = ollama.AsyncClient(
        host=settings.OLLAMA_BASE_URL,
        timeout=settings.OLLAMA_TIMEOUT_SECONDS,
    )
    response = await client.embed(model=settings.EMBED_MODEL, input=text)
    return response.embeddings[0]
