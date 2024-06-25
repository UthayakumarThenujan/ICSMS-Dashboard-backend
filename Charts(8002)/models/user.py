from pydantic import BaseModel, EmailStr
from typing import Optional,List,Dict
from starlette.requests import Request


class UserInput(BaseModel):
    email: str


class Call_Value(BaseModel):
    positive: int
    negative: int
    average: int

class Widget(BaseModel):
    title: str
    chartType: str
    xAxis: Optional[str] = None
    yAxis: Optional[str] = None
    topics: Optional[List[str]] = None
    sources: List[str]
    keywords: List[str]
    grid: Dict

class WidgetRequest(BaseModel):
    widget: Widget

class Token(BaseModel):
    token:str

class BarChart(BaseModel):
    collections:List[str]
    date_range:List[str]

class GridItemUpdateRequest(BaseModel):
    id: str
    cols: int
    rows: int
    x: int
    y: int

class GridItemsUpdateRequest(BaseModel):
    items: List[GridItemUpdateRequest]