from datetime import date, datetime
from pydantic import BaseModel


class Portfolio(BaseModel):
    id: str
    title: str


class PortfolioPage(BaseModel):
    next: str | None = None
    previous: str | None = None
    results: list[Portfolio] = []


class Position(BaseModel):
    code: str
    amount: float | None = None
    avg_cost: float | None = None
    current_price: float | None = None
    total_cost: float | None = None
    total_value: float | None = None
    gain: float | None = None
    gain_pct: float | None = None
    model_config = {"extra": "allow"}


class PositionPage(BaseModel):
    next: str | None = None
    previous: str | None = None
    results: list[Position] = []


class Transaction(BaseModel):
    id: str | int | None = None
    portfolio: str | None = None
    code: str
    side: str
    amount: float
    price: float
    date: date | datetime | None = None
    model_config = {"extra": "allow"}
