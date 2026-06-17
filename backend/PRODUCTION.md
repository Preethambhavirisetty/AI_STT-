# Production Notes

## Required Environment

Set these before deployment:

```bash
API_KEY="replace-with-a-long-secret"
REQUIRE_AUTH=true
OLLAMA_BASE_URL="http://ollama:11434"
DATABASE_PATH="/app/data/mikey.sqlite3"
CHROMA_PATH="/app/chroma_data"
```

The first `API_KEY` becomes the bootstrap admin key. Use it to create additional users:

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"name":"Preetham","api_key":"replace-with-user-secret","is_admin":false}'
```

Then call protected endpoints with:

```bash
X-API-Key: replace-with-user-secret
```

## Docker

```bash
cd backend
export API_KEY="replace-with-a-long-secret"
docker compose up --build
```

Pull the required Ollama models inside the Ollama container:

```bash
docker compose exec ollama ollama pull llama3.1:latest
docker compose exec ollama ollama pull nomic-embed-text:latest
```

## Storage

The default production compose uses persistent Docker volumes for SQLite and Chroma. This is appropriate for a single backend instance. If you run multiple API instances across machines, move rate limiting and relational data to shared managed services before scaling horizontally.

## Security

- Keep `REQUIRE_AUTH=true` outside local development.
- Use long random API keys.
- Put the API behind HTTPS.
- Restrict `CORS_ORIGINS` to your frontend domains.
- Do not expose Ollama publicly.
