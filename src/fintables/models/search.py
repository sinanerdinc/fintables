from pydantic import BaseModel


class SearchDocument(BaseModel):
    code: str
    id: str
    title: str
    type: str
    flags: list[str] = []
    tags: str = ""
    priority: int | None = None


class SearchHit(BaseModel):
    document: SearchDocument
    text_match: int | float | None = None


class SearchGroup(BaseModel):
    title: str | None = None
    found: int = 0
    hits: list[SearchHit] = []
    out_of: int = 0
    page: int = 1


class SearchResponse(BaseModel):
    results: list[SearchGroup] = []
