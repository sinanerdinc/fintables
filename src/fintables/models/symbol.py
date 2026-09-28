from typing import Any
from pydantic import BaseModel, Field


class Sector(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None = None
    og: str | None = None
    cover: str | None = None


class ValueFormat(BaseModel):
    decimals: int = 2
    abbreviation: bool = False
    null_to_na: bool = Field(False, alias="nullToNa")


class DataItem(BaseModel):
    title: str
    value: Any = None
    type: str
    format: ValueFormat


class DataGroup(BaseModel):
    title: str
    data: list[DataItem] = []


class Period(BaseModel):
    year: int
    month: int


class ChartSeries(BaseModel):
    title: str
    periods: list[Period] = []
    values: list[Any] = []
    format: ValueFormat


class FinancialStatement(BaseModel):
    title: str
    period: Period
    data: list[DataItem] = []


class YieldWindow(BaseModel):
    first: float | None = None
    low: float | None = None
    high: float | None = None


class YieldAnalysis(BaseModel):
    title: str
    data: dict[str, YieldWindow] = {}


class SymbolSummaryData(BaseModel):
    ipo_stats: bool = False
    sectors: list[Sector] = []
    inflation_affected: bool = False
    multipliers: DataGroup
    company_details: DataGroup
    bars: list[ChartSeries] = []
    lines: list[ChartSeries] = []
    income_statement: FinancialStatement
    balance_statement: FinancialStatement
    yield_: YieldAnalysis = Field(..., alias="yield")


class SymbolSummary(BaseModel):
    data: SymbolSummaryData
