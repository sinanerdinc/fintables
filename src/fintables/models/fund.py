from pydantic import BaseModel, Field

class ManagementCompany(BaseModel):
    code: str
    title: str
    logo: str | None = None

class FundCategory(BaseModel):
    title: str
    slug: str | None = None

class Fund(BaseModel):
    code: str
    fund_type: str
    title: str
    type: str | None = None
    management_company: ManagementCompany | None = None
    categories: list[FundCategory | str] = Field(default_factory=list)
    has_portfolio: bool = False
    is_byf: bool = False
    feed_companies: list[str] = Field(default_factory=list)

class PortfolioItem(BaseModel):
    code: str
    weight: float
    nominal: float

class Portfolio(BaseModel):
    date: str
    news_id: str | None = None
    items: list[PortfolioItem] = Field(default_factory=list)
    year: int | None = None
    month: int | None = None
    week: int | None = None

class BarDataPoint(BaseModel):
    date: str
    value: float

class BarFormat(BaseModel):
    suffix: str | None = None
    thousand: bool | None = None

class Bar(BaseModel):
    title: str
    data: list[BarDataPoint] = Field(default_factory=list)
    format: BarFormat | None = None

class YieldDataPoint(BaseModel):
    max: float | None = None
    min: float | None = None
    yield_: float | None = Field(default=None, alias="yield")

class YieldData(BaseModel):
    one_m: YieldDataPoint | None = Field(default=None, alias="1m")
    three_m: YieldDataPoint | None = Field(default=None, alias="3m")
    six_m: YieldDataPoint | None = Field(default=None, alias="6m")
    one_y: YieldDataPoint | None = Field(default=None, alias="1y")
    three_y: YieldDataPoint | None = Field(default=None, alias="3y")
    five_y: YieldDataPoint | None = Field(default=None, alias="5y")
    ytd: YieldDataPoint | None = None

class AssetAllocation(BaseModel):
    title: str
    value: float

class FundInfo(BaseModel):
    description: str | None = None
    management_fee: float | None = None
    tax: float | None = None
    tax_info: str | None = None
    risk: int | None = None
    shares_total: int | float | None = None
    shares_active: int | float | None = None
    investor_count: int | None = None
    market_share: float | None = None
    buy_valor: int | None = None
    sell_valor: int | None = None
    price: float | None = None
    latest_portfolio: Portfolio | None = None
    prev_portfolio: Portfolio | None = None
    tefas: bool = False
    cashflow: float | None = None
    bars: list[Bar] = Field(default_factory=list)
    yield_: YieldData | None = Field(default=None, alias="yield")
    last_asset: list[AssetAllocation] = Field(default_factory=list)
    last_asset_date: str | None = None
