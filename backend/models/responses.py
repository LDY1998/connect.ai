from pydantic import BaseModel


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
    externalIds: dict[str, str] | None = None
    url: str | None = None


class GraphNode(BaseModel):
    id: str
    data: Paper
    type: str = "paper"
    pool: str | None = None  # "core" | "related" | "peripheral" | None (seed)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str = "citation"


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    seedPaperId: str
