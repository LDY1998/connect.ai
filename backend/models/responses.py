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
