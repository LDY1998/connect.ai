import asyncio

from fastapi import APIRouter, HTTPException

from services.paper_provider import PaperProvider, OpenAlexProvider
from services.graph_builder import build_graph
from models.requests import GraphRequest
from models.responses import GraphData
from config import get_settings

router = APIRouter()

settings = get_settings()
_provider: PaperProvider = OpenAlexProvider(email=settings.openalex_email)


@router.post("/graph", response_model=GraphData)
async def get_graph(body: GraphRequest):
    try:
        seed, citations, references = await asyncio.gather(
            _provider.get_paper(body.seedPaperId),
            _provider.get_citations(body.seedPaperId, limit=body.limit),
            _provider.get_references(body.seedPaperId, limit=body.limit),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")

    return build_graph(seed, citations, references)
