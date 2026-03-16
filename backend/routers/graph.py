import asyncio

from fastapi import APIRouter, HTTPException, Query

from services.paper_provider import PaperProvider, OpenAlexProvider
from services.graph_builder import build_graph
from services.pool_builder import build_pools_graph
from models.responses import GraphData
from config import get_settings

router = APIRouter()

settings = get_settings()
_provider: PaperProvider = OpenAlexProvider(email=settings.openalex_email)


@router.get("/graph/{paper_id}/citations", response_model=GraphData)
async def get_citations_graph(paper_id: str, limit: int = Query(default=60, ge=1, le=200)):
    try:
        seed, citations = await asyncio.gather(
            _provider.get_paper(paper_id),
            _provider.get_citations(paper_id, limit=limit),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")

    return build_graph(seed, citations, seed_is_source=False)


@router.get("/graph/{paper_id}/references", response_model=GraphData)
async def get_references_graph(paper_id: str, limit: int = Query(default=60, ge=1, le=200)):
    try:
        seed, references = await asyncio.gather(
            _provider.get_paper(paper_id),
            _provider.get_references(paper_id, limit=limit),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")

    return build_graph(seed, references, seed_is_source=True)


@router.get("/graph/{paper_id}/pools", response_model=GraphData)
async def get_pools_graph(paper_id: str, limit: int = Query(default=30, ge=1, le=100)):
    try:
        seed, citations, references = await asyncio.gather(
            _provider.get_paper(paper_id),
            _provider.get_citations(paper_id, limit=limit),
            _provider.get_references(paper_id, limit=limit),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")
    return await build_pools_graph(seed, citations, references, _provider)
