from typing import Any
from pydantic import BaseModel


class RatioItem(BaseModel):
    key: str
    name: str
    allowed: bool


class RatioType(BaseModel):
    name: str
    key: str
    data: list[RatioItem] = []


class Company(BaseModel):
    code: str
    title: str
    logo: str | None = None
    cover: str | None = None
    price: float | None = None
    description: str | None = None
    enflasyon: bool = False
    in_katilim_index: bool = False
    has_meta: bool = False
    has_buybacks: bool = False
    has_participation: bool = False
    has_business_contracts: bool = False
    has_sectoral_data_types: bool = False
    ratio_types: list[RatioType] = []
    sectors: list[int] = []
    is_new_ipo: bool = False
    sheet_template: str | None = "default"
    sectoral_template: str | None = None
    fiscal_period_start_date: str | None = None
    fiscal_period_end_date: str | None = None
    next_financial_statement_date: str | None = None
    functional_currency: str | None = None
    administrative_measures: list[Any] = []
