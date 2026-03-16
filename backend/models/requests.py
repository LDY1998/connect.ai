from pydantic import BaseModel


class ResolveRequest(BaseModel):
    urlOrDoi: str


