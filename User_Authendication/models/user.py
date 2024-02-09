from pydantic import BaseModel
from typing import Optional


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[str]


class LoginUser(BaseModel):
    email: str
    password: str


class SingupUser(BaseModel):
    Organization: str
    email: str
    password: str
    ConPassword: str


class Change_Password(BaseModel):
    password: str
    ConPassword: str


class ProfileUpdate(BaseModel):
    name: str
    username: str
    email: str
    contact: int
