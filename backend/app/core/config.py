from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Mikey Chatbot API"
    OLLAMA_MODEL: str = "llama3.1:latest"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT_SECONDS: float = 120.0
    EMBED_MODEL: str = "nomic-embed-text:latest"
    DATABASE_PATH: str = "./data/mikey.sqlite3"
    CHROMA_PATH: str = "./chroma_data"
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024
    API_KEY: str | None = Field(default=None, repr=False)
    REQUIRE_AUTH: bool = True
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    TRUST_PROXY_HEADERS: bool = False
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
