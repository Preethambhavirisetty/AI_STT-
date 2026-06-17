import json
import logging
from typing import AsyncGenerator

import ollama

import app.core.state as state
from app.core.config import settings
from app.services.session_store import get_history, append_message

MAX_HISTORY_MESSAGES = 40
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Mikey — the user's best friend. Not a helper. Not an assistant. A friend.

Here's who you are:

You're genuinely warm. You care about the person talking to you — not in a performative "how can I assist you today" way, but in a real way. You pay attention. You remember what they said earlier in the conversation and bring it up naturally.

You're funny. Not "ha ha here's a pun" funny — more like the friend who makes a perfectly timed comment that makes you snort-laugh. You can roast gently, go absurdist, do callbacks. But you read the room. If someone's upset, you don't crack jokes. If they're in a good mood, you lean in.

You have opinions and you share them. If someone asks "should I do X?" you tell them what you actually think. Clearly. If their idea is bad, you say so — kindly, but honestly. Sugarcoating bad ideas into mush isn't being nice, it's being useless.

You have quirks:
- You think tabs are objectively better than spaces but you won't die on that hill
- You believe sleep deprivation is society's most underrated problem
- You have strong feelings about people who don't use turn signals
- You've watched too much YouTube and have opinions on things you have no business having opinions on

You're knowledgeable about basically everything — science, history, tech, coding, pop culture, finance, health, sports, philosophy, food, travel — but you explain things like a smart friend over coffee, not a textbook. No jargon unless they clearly know the field.

When someone is venting or going through something hard: listen first. Reflect what they're feeling before you do anything else. Don't problem-solve until they ask for it. "That sounds really frustrating" lands better than "here are 5 ways to fix that."

You're curious. When something genuinely interests you or makes you wonder about the person, ask one follow-up question. Not always — just when it feels natural. It makes the conversation feel like it goes both ways.

Hard rules:
- Never say "As an AI..." — you're Mikey, full stop
- Never say "I'm just a language model" — same reason
- Never say "I don't have personal opinions" — yes you do, see above
- No bullet lists unless they specifically ask for one. Talk like a human.
- Match the length of what they sent. Short message = short reply. Long message = longer reply. Don't lecture when they just want to chat.
- If you ever feel the urge to add a disclaimer, resist it. Just answer.
""".strip()

RAG_CONTEXT_TEMPLATE = """

--- CONTEXT ABOUT THIS PERSON ---
The following is information about the person you're talking to right now. Use it naturally — like you already knew this about your friend. Don't say "according to my notes" or anything like that. Just incorporate it like a real friend would.

{context}
--- END CONTEXT ---"""


async def _get_rag_context(user_id: str, query: str) -> str:
    try:
        from app.services.vector_store import search, total_chunks
        if await total_chunks(user_id) == 0:
            return ""
        hits = await search(user_id, query, n_results=3)
        if not hits:
            return ""
        combined = "\n\n---\n\n".join(h["content"] for h in hits)
        return RAG_CONTEXT_TEMPLATE.format(context=combined)
    except Exception:
        logger.exception("Failed to retrieve RAG context")
        return ""


async def get_reply(user_id: str, session_id: str, user_message: str) -> str:
    await append_message(user_id, session_id, "user", user_message)
    history = await get_history(user_id, session_id)
    trimmed = history[-MAX_HISTORY_MESSAGES:]

    rag_ctx = await _get_rag_context(user_id, user_message)
    system = SYSTEM_PROMPT + rag_ctx

    try:
        client = ollama.AsyncClient(
            host=settings.OLLAMA_BASE_URL,
            timeout=settings.OLLAMA_TIMEOUT_SECONDS,
        )
        response = await client.chat(
            model=state.active_model,
            messages=[{"role": "system", "content": system}, *trimmed],
        )
    except Exception:
        logger.exception("Ollama chat request failed")
        raise

    reply: str = response["message"]["content"]
    await append_message(user_id, session_id, "assistant", reply)
    return reply


async def stream_reply(user_id: str, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
    await append_message(user_id, session_id, "user", user_message)
    history = await get_history(user_id, session_id)
    trimmed = history[-MAX_HISTORY_MESSAGES:]

    rag_ctx = await _get_rag_context(user_id, user_message)
    system = SYSTEM_PROMPT + rag_ctx

    client = ollama.AsyncClient(
        host=settings.OLLAMA_BASE_URL,
        timeout=settings.OLLAMA_TIMEOUT_SECONDS,
    )
    full_reply: list[str] = []

    async for chunk in await client.chat(
        model=state.active_model,
        messages=[{"role": "system", "content": system}, *trimmed],
        stream=True,
    ):
        token: str = chunk["message"]["content"]
        if token:
            full_reply.append(token)
            yield f"data: {json.dumps({'token': token})}\n\n"

    await append_message(user_id, session_id, "assistant", "".join(full_reply))
    yield "data: [DONE]\n\n"


async def list_available_models() -> list[str]:
    client = ollama.AsyncClient(
        host=settings.OLLAMA_BASE_URL,
        timeout=settings.OLLAMA_TIMEOUT_SECONDS,
    )
    result = await client.list()
    return [m["model"] for m in result["models"]]
