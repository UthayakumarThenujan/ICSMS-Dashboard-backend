from pydantic import BaseModel, Field
from typing import Optional
from starlette.requests import Request
from bson import ObjectId

class Notification(BaseModel):
    email: str
    alert : str
    created_at : None
    status: str = "UNREAD" #READ,UNREAD

class UpdateNoti(BaseModel):
    id: str
    # email: str
    # alert: str
    # status: str

    # class Config:
    #     arbitrary_types_allowed = True