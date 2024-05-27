import asyncio
from fastapi import FastAPI, APIRouter
from models.user import UserInput
from typing import Optional
from config.db import collection_name
from schemas.user import userEntity, usersEntity
from starlette.requests import Request
import requests
import random
from jsonCreate import createRespones
# from bson import ObjectId
#8004
user = APIRouter(prefix="/CallAnalysis", tags=["CallAnalysis"])
urls =["http://127.0.0.1:8005/email/data","http://127.0.0.1:8007/call/data","http://127.0.0.1:8006/social/data"]

async def call_email_sentiments():
    while True:
        response = createRespones()
        try:
            print(response)
            req = requests.post(random.choice(urls), json=response)
            print(req.json())
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        await asyncio.sleep(30)

# Start the periodic task on startup
@user.on_event("startup")
async def startup_event():
    asyncio.create_task(call_email_sentiments())

# Optional route for testing purposes
# @user.post("/email-sentiments")
# async def find_all_call():
#     response = createRespones()
#     req = requests.post("http://127.0.0.1:8005/email/data", json=response)
#     return req.json()
