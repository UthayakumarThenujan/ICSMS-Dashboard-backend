from pydantic import BaseModel, EmailStr
from typing import Optional,List
from starlette.requests import Request


class UserInput(BaseModel):
    email: str


class Call_Value(BaseModel):
    positive: int
    negative: int
    average: int

class Widget(BaseModel):
    title : str
    chartType : str
    sources : List[str]
    keywords : List[str]
    grid:dict

class WidgetRequest(BaseModel):
    widget: Widget
    email: str

class Token(BaseModel):
    token:str