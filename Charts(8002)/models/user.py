from pydantic import BaseModel
from typing import Optional,List,Dict

class Widget(BaseModel):
    title: str
    chartType: str
    xAxis: Optional[str] = None
    yAxis: Optional[str] = None
    topics: Optional[List[str]] = None
    sources: List[str]
    keywords: List[str]
    grid: Dict
    status:str

class WidgetRequest(BaseModel):
    widget: Widget


class GridItemUpdateRequest(BaseModel):
    id: str
    cols: int
    rows: int
    x: int
    y: int

class GridItemsUpdateRequest(BaseModel):
    items: List[GridItemUpdateRequest]

class GridStatusUpdateRequest(BaseModel):
    id:str
    status:str