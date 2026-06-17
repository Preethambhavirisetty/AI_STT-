from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from app.core.config import settings
from app.core.cors import add_cors
from app.core.logging import configure_logging
from app.core.rate_limit import rate_limit_middleware
from app.core.security import require_api_key
from app.api.v1.chat import router as chat_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.users import router as users_router
from app.services.db import init_db

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.middleware("http")(rate_limit_middleware)
add_cors(app)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}


@app.get("/api/v1/routes", dependencies=[Depends(require_api_key)])
def list_routes():
    from fastapi.routing import APIRoute
    routes = []

    def collect(router_routes):
        for route in router_routes:
            if isinstance(route, APIRoute):
                routes.append({"path": route.path, "methods": sorted(route.methods)})
            elif hasattr(route, "routes"):
                collect(route.routes)

    collect(app.routes)
    return sorted(routes, key=lambda r: r["path"])
