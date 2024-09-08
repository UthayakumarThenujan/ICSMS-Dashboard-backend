from pydantic import BaseModel, Field
from bson import ObjectId


class Notification(BaseModel): # front end notification data structure
    email: str
    alert : str
    created_at : None
    status: str = "UNREAD" #READ,UNREAD

class UpdateNoti(BaseModel): #upadate notifications data structure
    id: str

class CallData(BaseModel): # Call team data notification structure
    id: str = Field(default_factory=lambda: str(ObjectId()))
    title: str
    description: str
    datetime: str
