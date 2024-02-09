from pydantic import BaseModel
from typing import Optional
from starlette.requests import Request


class UserInput(BaseModel):
    email: str
