from datetime import datetime
from pydantic import BaseModel


class Memo(BaseModel):
    id: int
    code: str
    created_at: datetime
    updated_at: datetime
    content: str


class MemoCreate(BaseModel):
    code: str
    content: str


class MemoUpdate(BaseModel):
    id: int
    code: str
    content: str
