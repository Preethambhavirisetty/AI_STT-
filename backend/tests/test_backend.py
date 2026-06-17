import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.rate_limit import reset_rate_limits
from app.main import app
from app.services.db import init_db
from app.services.doc_registry import get_doc, list_docs, register, remove_doc
from app.services.session_store import append_message, clear_history, get_history


class BackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.previous_db = settings.DATABASE_PATH
        self.previous_api_key = settings.API_KEY
        self.previous_require_auth = settings.REQUIRE_AUTH
        self.previous_rate_limit_requests = settings.RATE_LIMIT_REQUESTS
        settings.DATABASE_PATH = str(Path(self.tmpdir.name) / "test.sqlite3")
        settings.API_KEY = None
        settings.REQUIRE_AUTH = False
        settings.RATE_LIMIT_REQUESTS = 120
        init_db()
        reset_rate_limits()

    def tearDown(self) -> None:
        settings.DATABASE_PATH = self.previous_db
        settings.API_KEY = self.previous_api_key
        settings.REQUIRE_AUTH = self.previous_require_auth
        settings.RATE_LIMIT_REQUESTS = self.previous_rate_limit_requests
        self.tmpdir.cleanup()

    def test_chat_history_persists_in_sqlite(self) -> None:
        async def run() -> None:
            await append_message("development", "s1", "user", "hello")
            await append_message("development", "s1", "assistant", "hey")
            self.assertEqual(
                await get_history("development", "s1"),
                [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "hey"},
                ],
            )
            await clear_history("development", "s1")
            self.assertEqual(await get_history("development", "s1"), [])

        asyncio.run(run())

    def test_document_registry_persists_in_sqlite(self) -> None:
        async def run() -> None:
            record = await register("development", "doc-1", "My Doc", "doc.txt", 2)
            self.assertEqual((await get_doc("development", "doc-1"))["title"], record["title"])
            self.assertEqual(len(await list_docs("development")), 1)
            self.assertIsNone(await get_doc("other-user", "doc-1"))
            self.assertTrue(await remove_doc("development", "doc-1"))
            self.assertIsNone(await get_doc("development", "doc-1"))

        asyncio.run(run())

    def test_api_key_blocks_protected_routes_when_configured(self) -> None:
        settings.API_KEY = "secret"
        settings.REQUIRE_AUTH = True
        init_db()
        with TestClient(app) as client:
            response = client.get("/api/v1/chat/history/test")
            self.assertEqual(response.status_code, 401)

            response = client.get(
                "/api/v1/chat/history/test",
                headers={"X-API-Key": "secret"},
            )
            self.assertEqual(response.status_code, 200)

    def test_message_endpoint_returns_mocked_reply(self) -> None:
        with patch("app.api.v1.chat.get_reply", return_value="hello back"):
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/chat/message",
                    json={"session_id": "s1", "message": "hello"},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"reply": "hello back", "session_id": "s1"})

    def test_rate_limit_blocks_excess_requests(self) -> None:
        settings.RATE_LIMIT_REQUESTS = 1
        with TestClient(app) as client:
            self.assertEqual(client.get("/api/v1/chat/history/test").status_code, 200)
            response = client.get("/api/v1/chat/history/test")
            self.assertEqual(response.status_code, 429)

    def test_upload_rejects_large_file(self) -> None:
        previous_limit = settings.MAX_UPLOAD_BYTES
        settings.MAX_UPLOAD_BYTES = 4
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/knowledge/upload",
                    files={"file": ("big.txt", b"too large", "text/plain")},
                )
            self.assertEqual(response.status_code, 413)
        finally:
            settings.MAX_UPLOAD_BYTES = previous_limit


if __name__ == "__main__":
    unittest.main()
