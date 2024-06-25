from pydantic import BaseModel
from typing import Optional,List,Dict
from starlette.requests import Request
from datetime import datetime

class Issue(BaseModel):
    time: str
    status: str=''
    issue_type: str = ''
    sentiment_score: float
    products:List[str]=[]

class Inquiry(BaseModel):
    time: str
    status: str=''
    inquiry_type: str = ''
    sentiment_score: float
    products:List[str]=[]

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
    our_sentiment_score: float=0.0
    sender: str = ''
    topics: List[str] = []

class SocialData(BaseModel):
    time: str
    our_sentiment_score: float = 0.0
    keywords: List[str]= []
    products: List[str]= []