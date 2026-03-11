# connect.ai

A research paper graph explorer with AI-powered concept evolution tracking. Paste any paper URL or DOI and get an interactive citation graph, AI-generated summaries, and a timeline of how key concepts evolved across the literature.

---

## Features

- **Citation Graph** — interactive force-directed graph of papers and their citation relationships
- **AI Paper Analysis** — extracts key concepts and generates summaries for each paper
- **Concept Evolution Tracking** — see how a concept is introduced, refined, challenged, or extended across papers over time
- **AI Chat** — ask natural language questions about the visible graph
- **Concept Explorer** — standalone view to browse a concept's full timeline

---

## Architecture

```
connect.ai/
├── frontend/   # Next.js 14 (TypeScript, Tailwind CSS, shadcn/ui, React Flow)
├── backend/    # FastAPI (Python, Pydantic)
└── plan/       # Phase-by-phase implementation notes
```

The frontend handles all UI and graph rendering. The backend handles paper data fetching, graph construction, and LLM integration. They communicate over HTTP REST, with streaming endpoints for AI chat.

```
Browser (Next.js)  ──HTTP──►  FastAPI Backend  ──►  Paper Provider API
                                               ──►  LLM (Claude / OpenAI)
```

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS v4, shadcn/ui |
| Graph | React Flow |
| Backend | FastAPI, Python 3.11+ |
| AI | Claude / OpenAI via Python SDKs |
| Data | Abstracted `PaperProvider` interface (swap any API) |
| Validation | Zod (frontend), Pydantic (backend) |

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+

### 1. Clone the repo

```bash
git clone https://github.com/your-username/connect.ai.git
cd connect.ai
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=your_key_here
# S2_API_KEY=optional_semantic_scholar_key
```

Run the server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## API Reference

All backend routes are prefixed with `/api/v1`.

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/v1/resolve` | Resolve a URL or DOI to a canonical paper ID |
| `GET` | `/api/v1/paper/{paper_id}` | Fetch full metadata for a paper |
| `POST` | `/api/v1/graph` | Build a citation graph from a seed paper |
| `POST` | `/api/v1/analyze` | Generate AI summary and extract concepts |
| `POST` | `/api/v1/concepts` | Annotate papers with concept evolution roles |
| `POST` | `/api/v1/chat` | Streaming AI chat about the current graph |

---

## Development Notes

### Paper Provider

The backend uses an abstract `PaperProvider` interface (`backend/services/paper_provider.py`). The active provider is `StubPaperProvider`, which returns hardcoded data for development without requiring any API keys.

To switch providers, replace the one line in `backend/routers/paper.py`:

```python
# Current (stub for development)
_provider: PaperProvider = StubPaperProvider()

# Future (real API)
_provider: PaperProvider = SemanticScholarProvider(api_key=settings.s2_api_key)
```

### Implementation Phases

| Phase | Goal | Status |
|---|---|---|
| 1 | Scaffold + URL/DOI input | In progress |
| 2 | Citation graph visualization | Pending |
| 3 | AI paper analysis | Pending |
| 4 | Concept evolution timeline | Pending |
| 5 | AI chat sidebar | Pending |
| 6 | Concept explorer screen | Pending |
| 7 | Polish + performance | Pending |

See `plan/` for detailed notes on each phase.

---

## License

MIT
