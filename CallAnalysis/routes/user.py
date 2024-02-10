from fastapi import APIRouter
from models.user import UserInput
from typing import Optional
from config.db import collection_name
from schemas.user import userEntity, usersEntity
from starlette.requests import Request
import requests, time
from fastapi.background import BackgroundTasks

# from bson import ObjectId

user = APIRouter(prefix="/CallAnalysis", tags=["CallAnalysis"])


@user.post("/call-sentiments")
async def find_call_email(request: UserInput):
    body = request.email

    req = requests.get("http://127.0.0.1:8000/authendication/user/%s" % body)

    return req.json()


@user.get("/call-sentiments")
async def find_all_call():

    req = requests.get("http://127.0.0.1:8000/authendication/")

    return req.json()
