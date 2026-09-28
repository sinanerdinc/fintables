from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel


class RatingType(str, Enum):
    AL = "al"
    TUT = "tut"
    ENDEKS_USTU = "endeks_ustu"
    ENDEKSE_PARALEL = "endekse_paralel"
    SAT = "sat"
    ENDEKS_ALTI = "endeks_alti"


class Brokerage(BaseModel):
    code: str
    title: str
    logo: str | None = None
    public_company: str | None = None
    short_title: str | None = None
    is_listed: bool = False


class AnalystRating(BaseModel):
    published_at: datetime
    brokerage: Brokerage
    code: str
    price_target: float | None = None
    type: RatingType | str | None = None
    in_model_portfolio: bool = False
    attachments: list[Any] = []


class AnalystRatingList(BaseModel):
    results: list[AnalystRating] = []
