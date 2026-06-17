import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.db import connect


def reset_rate_limits() -> None:
    with connect() as conn:
        conn.execute("DELETE FROM rate_limits")


def _client_key(request: Request) -> str:
    api_key = request.headers.get("x-api-key")
    if api_key:
        return f"key:{api_key[-12:]}"

    if settings.TRUST_PROXY_HEADERS:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

    client = request.client.host if request.client else "unknown"
    return f"ip:{client}"


async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path == "/health":
        return await call_next(request)

    now = time.time()
    key = _client_key(request)

    with connect() as conn:
        row = conn.execute(
            "SELECT window_start, request_count FROM rate_limits WHERE key = ?",
            (key,),
        ).fetchone()

        if not row or now - row["window_start"] >= settings.RATE_LIMIT_WINDOW_SECONDS:
            conn.execute(
                """
                INSERT INTO rate_limits (key, window_start, request_count)
                VALUES (?, ?, 1)
                ON CONFLICT(key) DO UPDATE SET
                    window_start = excluded.window_start,
                    request_count = excluded.request_count
                """,
                (key, now),
            )
        elif row["request_count"] >= settings.RATE_LIMIT_REQUESTS:
            retry_after = max(
                1,
                int(settings.RATE_LIMIT_WINDOW_SECONDS - (now - row["window_start"])),
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after)},
            )
        else:
            conn.execute(
                "UPDATE rate_limits SET request_count = request_count + 1 WHERE key = ?",
                (key,),
            )

    return await call_next(request)
