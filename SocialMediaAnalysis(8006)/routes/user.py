from fastapi import APIRouter
from models.user import UserInput
from typing import Optional
from config.db import collection
from schemas.user import userEntity, usersEntity
from starlette.requests import Request
import requests
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from bson import ObjectId
#8005
# from bson import ObjectId

user = APIRouter(prefix="/social", tags=["social"])

class EmailData(BaseModel):
    ID: int
    Sentiment: int
    Date: str
    Word: str

@user.post("/data")
async def receive_email_data(data: EmailData):
    current_date = datetime.strptime(data.Date, "%a %b %d %H:%M:%S PDT %Y").date()

    # Fetch existing data for the current day
    existing_data = collection.find_one({"Date": current_date.strftime("%a %b %d %Y")})

    if existing_data:
        # Update the existing data
        existing_data['ID'].append(data.ID)
        existing_data['Word'].append(data.Word)
        
        # Update sentiment counts
        existing_data['Sentiment']['positive'] += 1 if data.Sentiment == 4 else 0
        existing_data['Sentiment']['negative'] += 1 if data.Sentiment == 0 else 0
        existing_data['Sentiment']['neutral'] += 1 if data.Sentiment == 2 else 0

        # Save the updated document back to MongoDB
        collection.update_one({"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data})
    else:
        # Create a new entry for the day
        new_data = {
            "ID": [data.ID],
            "Sentiment": {'positive': 0, 'negative': 0, 'neutral': 0},
            "Date": current_date.strftime("%a %b %d %Y"),
            "Word": [data.Word]
        }

        # Initialize sentiment counts
        new_data['Sentiment']['positive'] += 1 if data.Sentiment == 4 else 0
        new_data['Sentiment']['negative'] += 1 if data.Sentiment == 0 else 0
        new_data['Sentiment']['neutral'] += 1 if data.Sentiment == 2 else 0

        # Insert the new document into MongoDB
        collection.insert_one(new_data)

        # try:
        #     req = requests.post("http://127.0.0.1:8002/charts/getUpdate", json=new_data)
        #     print("Success")
        # except requests.RequestException as e:
        #     print(f"Request failed: {e}")

    return {"message": "Data received and processed successfully"}


