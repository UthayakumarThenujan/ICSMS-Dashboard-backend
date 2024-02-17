from fastapi import APIRouter, HTTPException
from models.user import UserInput, Call_Value
from typing import Optional
from config.db import collection_name
from schemas.user import callEntity, callsEntity
from starlette.requests import Request
import requests, time
from fastapi.background import BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# from bson import ObjectId

user = APIRouter(prefix="/CallAnalysis", tags=["CallAnalysis"])


@user.post("/call-sentiments")
async def find_call_email(request: UserInput):
    body = request.email

    req = requests.get("http://127.0.0.1:8000/authendication/user/%s" % body)

    return req.json()


@user.post("/Call_Sentimet_Values")
async def Call_Values(Calls: Call_Value):

    try:
        result = collection_name.insert_one(jsonable_encoder(Calls))
        inserted_id = str(result.inserted_id)
        return {"message": "Data inserted successfully", "inserted_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # return collection_name.insert_one(jsonable_encoder(Calls))


@user.get("/Call_Sentimet_Values")
async def get_call():
    values = Call_Value(TotalCall=0, positive=0, negative=0, average=0)

    calls = callsEntity(collection_name.find())
    for x in calls:
        values.TotalCall += x["TotalCall"]
        values.positive += x["positive"]
        values.negative += x["negative"]
        values.average += x["average"]
    return dict(values)


@user.get("/call-sentiments")
async def find_all_call():

    req = requests.get("http://127.0.0.1:8000/authendication/")

    return req.json()
