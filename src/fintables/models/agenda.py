from datetime import date
from typing import Any
from pydantic import BaseModel


class AgendaDataItem(BaseModel):
    label: str
    value: str | None = None


class AgendaItem(BaseModel):
    title: str
    type: str | None = None          # "dividend" | "macro"
    day: date
    time: str | None = None          # "HH:MM" or null
    image_url: str | None = None
    image: str | None = None
    image_fallback_text: str | None = None   # ülke kodu (US, TR, EU …)
    data: list[AgendaDataItem] = []
    model_config = {"extra": "allow"}
