from pydantic import BaseModel
from fintables.models.symbol import Period


class SheetPeriod(BaseModel):
    year: int
    month: int
    is_inflation_adjusted: bool = False
    is_consolidated: bool = False
    source_period: Period | None = None


class SheetRow(BaseModel):
    label: str
    level: int | None = None
    values: list[float | None] = []
    quarter_values: list[float | None] = []


class Sheet(BaseModel):
    periods: list[SheetPeriod] = []
    rows: list[SheetRow] = []


class Sheets(BaseModel):
    balance: Sheet
    income: Sheet
    cashflow: Sheet
