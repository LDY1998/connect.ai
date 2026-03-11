# Backend Setup Plan

## Context
The frontend (Next.js 14) is already scaffolded in `frontend/`. The `backend/` directory exists but is completely empty. This plan covers setting up the FastAPI backend — the goal is a running Python API with two initial endpoints: resolve a DOI/URL to a paper ID, and fetch basic paper metadata.

## Directory Structure

```
backend/
├── .env                        # ANTHROPIC_API_KEY, S2_API_KEY (optional), etc.
├── requirements.txt            # Python dependencies
├── main.py                     # FastAPI app entry point + CORS
├── routers/
│   ├── __init__.py
│   └── paper.py                # POST /api/v1/resolve + GET /api/v1/paper/{paper_id}
├── services/
│   ├── __init__.py
│   └── paper_provider.py       # Semantic Scholar API calls
└── models/
    ├── __init__.py
    ├── requests.py             # Pydantic request models
    └── responses.py            # Pydantic response models
```

Only `routers/paper.py` is needed for Phase 1. Routers for graph, analyze, concepts, and chat come in later phases.

## Dependencies (`requirements.txt`)

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
httpx>=0.27.0          # async HTTP client for Semantic Scholar API
pydantic>=2.0.0        # data models + validation
pydantic-settings>=2.0.0  # .env loading
python-dotenv>=1.0.0
```

## Implementation Details

### `main.py`
- Create `FastAPI` app instance
- Add `CORSMiddleware` allowing `http://localhost:3000` (Next.js dev server)
- Include `routers/paper.py` under prefix `/api/v1`
- Health check: `GET /health` → `{ "status": "ok" }`

### `models/requests.py`
```python
class ResolveRequest(BaseModel):
    urlOrDoi: str
```

### `models/responses.py`
```python
class Author(BaseModel):
    name: str
    authorId: str | None = None

class Paper(BaseModel):
    paperId: str
    title: str
    year: int | None = None
    authors: list[Author]
    abstract: str | None = None
    citationCount: int | None = None
    externalIds: dict[str, str] | None = None  # {"DOI": "...", "ArXiv": "..."}
    url: str | None = None
```

### `services/paper_provider.py`
Async class `SemanticScholarProvider` using `httpx.AsyncClient`:

- **`resolve(url_or_doi: str) -> str`** — detects input type, returns S2 `paperId`:
  - DOI (starts with `10.`) → `GET /graph/v1/paper/DOI:{doi}`
  - arXiv ID (`arxiv:NNNN.NNNNN` or bare `NNNN.NNNNN`) → `GET /graph/v1/paper/ARXIV:{id}`
  - URL → extract DOI or arXiv ID from URL, then resolve as above
  - Plain text title → `GET /graph/v1/paper/search?query=...&limit=1`, return first result's `paperId`

- **`get_paper(paper_id: str) -> Paper`** — `GET /graph/v1/paper/{paperId}` with fields:
  `paperId,title,year,authors,abstract,citationCount,externalIds,url`

S2 base URL: `https://api.semanticscholar.org/graph/v1`
No API key required (rate limit: 100 req/5 min). Optional `S2_API_KEY` header via env.

### `services/settings.py` (pydantic-settings)
```python
class Settings(BaseSettings):
    s2_api_key: str = ""
    anthropic_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfig(env_file=".env")
```

### `routers/paper.py`
- `POST /api/v1/resolve` → calls `provider.resolve()`, returns `{ "paperId": "..." }`
- `GET /api/v1/paper/{paper_id}` → calls `provider.get_paper()`, returns `Paper`
- Both use `async def` with `httpx.AsyncClient` as a FastAPI dependency

## Verification

```bash
# 1. Set up environment
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Start server
uvicorn main:app --reload --port 8000

# 3. Health check
curl http://localhost:8000/health
# → {"status":"ok"}

# 4. Resolve a DOI
curl -X POST http://localhost:8000/api/v1/resolve \
  -H "Content-Type: application/json" \
  -d '{"urlOrDoi":"10.48550/arXiv.1706.03762"}'
# → {"paperId":"204e3073870fae3d05bcbc2f6a8e263d1f4da0e6"}

# 5. Fetch paper metadata
curl http://localhost:8000/api/v1/paper/204e3073870fae3d05bcbc2f6a8e263d1f4da0e6
# → full Paper JSON
```
