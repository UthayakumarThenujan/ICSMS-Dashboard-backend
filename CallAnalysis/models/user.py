from pydantic import BaseModel
from typing import Optional
from starlette.requests import Request


class UserInput(BaseModel):
    email: str


class Call_Value(BaseModel):
    TotalCall: int
    positive: int
    negative: int
    average: int
