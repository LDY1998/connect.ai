from fastapi import APIRouter, HTTPException

from services.paper_provider import PaperProvider, OpenAlexProvider
from models.requests import ResolveRequest
from models.responses import Paper
from config import get_settings

router = APIRouter()

settings = get_settings()
_provider: PaperProvider = OpenAlexProvider(email=settings.openalex_email)


@router.post("/resolve")
async def resolve_paper(body: ResolveRequest):
    try:
        paper_id = await _provider.resolve(body.urlOrDoi)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")
    return {"paperId": paper_id}


@router.get("/paper/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    try:
        paper = await _provider.get_paper(paper_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")
    return paper


@router.get("/paper/{paper_id}/citations", response_model=list[Paper])
async def get_citations(paper_id: str, limit: int = 60):
    try:
        return await _provider.get_citations(paper_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")


@router.get("/paper/{paper_id}/references", response_model=list[Paper])
async def get_references(paper_id: str, limit: int = 60):
    try:
        return await _provider.get_references(paper_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")
