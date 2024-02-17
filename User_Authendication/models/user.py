from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class SingupUser(BaseModel):
    organization: str
    email: EmailStr
    password: str
    conpassword: str
    role: Optional[List] = ["viewer"]
    name: Optional[str] = ""
    username: Optional[str] = ""
    contact: Optional[str] = ""

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "organization": "CodeGen",
                "email": "Johndoe@gmail.com",
                "password": "password",
                "conpassword": "password",
            }
        }


class Change_Password(BaseModel):
    password: str
    conpassword: str


class ProfileUpdate(BaseModel):
    name: Optional[str]
    username: Optional[str]
    email: Optional[EmailStr]
    contact: Optional[str]


class AddNewUSer(BaseModel):
    username: str
    email: EmailStr
    password: str
    conpassword: str
    role: List[str]
    organization: Optional[str] = ""
    name: Optional[str] = ""
    contact: Optional[str] = ""

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "CodeGen",
                "email": "Johndoe@gmail.com",
                "password": "password",
                "conpassword": "password",
                "role": "viewer",
            }
        }
