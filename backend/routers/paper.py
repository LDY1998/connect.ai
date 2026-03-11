from fastapi import APIRouter, HTTPException

from services.paper_provider import PaperProvider, StubPaperProvider
from models.requests import ResolveRequest
from models.responses import Paper

router = APIRouter()

# Swap StubPaperProvider for a real implementation when API access is available
_provider: PaperProvider = StubPaperProvider()


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
