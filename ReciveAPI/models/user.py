from pydantic import BaseModel
from typing import Optional,List
from starlette.requests import Request


class CallData(BaseModel):
    _id: str
    call_id: str
    sentiment_category: str
    keywords: List[str]
    topics: List[str]
    summary: str
    sentiment_score: float
    call_date: str

class EmailData(BaseModel):
    time: str
    our_sentiment_score: float
    sender: str
    topics: List[str]