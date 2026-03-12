from pydantic import BaseModel


class ResolveRequest(BaseModel):
    urlOrDoi: str


class GraphRequest(BaseModel):
    seedPaperId: str
    depth: int = 1
    limit: int = 60
