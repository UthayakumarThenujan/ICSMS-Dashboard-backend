from fastapi import APIRouter, HTTPException,Depends
from models.user import UserInput, Call_Value , Widget,WidgetRequest
from typing import Optional,Dict
from config.db import call_collection,email_collection,social_collection,widget_collection,data_collection
from schemas.user import callEntity, callsEntity,WidgetEntry
from starlette.requests import Request
import requests, time
from fastapi.background import BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from doughnutChart import doughnutChartFun
from lineChart import lineChartFun
from jwt_handler import signJWT, decodeJWT
from jwt_bearer import JWTBearer
from werkzeug.security import generate_password_hash, check_password_hash
from get_userId import get_current_user_id
from collections import defaultdict
# from bson import ObjectId
from collections import Counter
import random
from datetime import datetime
from pydantic import BaseModel

from jose import jwk, jwt
from jose.utils import base64url_decode
import boto3
import json
import urllib.request
from fastapi import Header


from bson import ObjectId
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from threading import Thread
from typing import List
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import threading
import json

user = APIRouter(prefix="/charts", tags=["charts"])
#8002

@user.get("/widgetsUser")
async def widgetsUser(username: str = Header(...)):
    widgets_details = WidgetEntry(widget_collection.find({"email": username}))  
    return widgets_details

    
@user.get("/chartData")
async def chartData():
    callData = callsEntity(call_collection.find())
    emailData = callsEntity(email_collection.find())
    socialData = callsEntity(social_collection.find())
    return [{'call':callData , 'email':emailData, 'social':socialData}]

# region = 'ap-south-1'
# userpool_id = 'ap-south-1_YEH0sqfmB'
# app_client_id = '4nql0ttol3en0nir4d56ctdc6i'
# keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

# with urllib.request.urlopen(keys_url) as f:
#     response = f.read()
# keys = json.loads(response.decode('utf-8'))['keys']


# def verifyToken(event):
#     token = event['token']
#     # get the kid from the headers prior to verification
#     headers = jwt.get_unverified_headers(token)
#     kid = headers['kid']
#     # search for the kid in the downloaded public keys
#     key_index = -1
#     for i in range(len(keys)):
#         if kid == keys[i]['kid']:
#             key_index = i
#             break
#     if key_index == -1:
#         print('Public key not found in jwks.json')
#         return False

#     # construct the public key
#     public_key = jwk.construct(keys[key_index])

#     # get the last two sections of the token,
#     # message and signature (encoded in base64)
#     message, encoded_signature = str(token).rsplit('.', 1)
#     # decode the signature
#     decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
#     # verify the signature
#     if not public_key.verify(message.encode("utf8"), decoded_signature):
#         print('Signature verification failed')
#         return False
#     print('Signature successfully verified')
#     # since we passed the verification, we can now safely
#     # use the unverified claims
#     claims = jwt.get_unverified_claims(token)
#     print(claims)
#     # additionally we can verify the token expiration
#     if time.time() > claims['exp']:
#         print('Token is expired')
#         return False
#     # and the Audience  (use claims['client_id'] if verifying an access token)
#     if claims['client_id'] != app_client_id:
#         # print('Token was not issued for this audience')
#         return False
#     # now we can use the claims
#     # print(claims)
#     return claims['username']

import asyncio
connected_clients = []

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

async def notify_clients():

    message = json.dumps({
        "response": 'data',
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

async def widget_notifiy():

    message = json.dumps({
        "response": 'widget',
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

def watch_collection_sync(collection_name,name):
    collection = collection_name
    change_stream = collection.watch()
    print(name)
    for change in change_stream:
        print(f"Change detected in {collection_name}: {change}")
        if(name=='widget'):
            asyncio.run_coroutine_threadsafe(widget_notifiy(), loop)
        else:
            asyncio.run_coroutine_threadsafe(notify_clients(), loop)


async def watch_collection(collection_name,name):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, watch_collection_sync, collection_name,name)

@user.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# @user.get("/widgetsUser")
# async def widgetsUser(username: str):
#     widgets_details = WidgetEntry(widget_collection.find({"email": username}))  
#     return widgets_details

@user.post("/newWidget")
async def newWidget(request: WidgetRequest):
    widget_dict = request.widget.dict()
    widget_dict['email'] = request.email
    widget_collection.insert_one(widget_dict)
    print("add table")
    return {"message": "New widget added"}

# @user.get("/chartData")
# async def chartData():
#     call_data = callsEntity(call_collection.find())
#     email_data = callsEntity(email_collection.find())
#     social_data = callsEntity(social_collection.find())
#     return [{"call": call_data, "email": email_data, "social": social_data}]

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def watch_all_collections():
    tasks = [
        watch_collection(call_collection,'call'),
        watch_collection(email_collection,'email'),
        watch_collection(social_collection,'social'),
        watch_collection(widget_collection,'widget')
    ]
    await asyncio.gather(*tasks)

# Create a new asyncio event loop
loop = asyncio.new_event_loop()
t = Thread(target=start_async_loop, args=(loop,), daemon=True)
t.start()

# Schedule the watch_all_collections coroutine on the new event loop
asyncio.run_coroutine_threadsafe(watch_all_collections(), loop)





















# @user.post("/call-sentiments")
# async def find_call_email(request: UserInput):
#     body = request.email

#     req = requests.get("http://127.0.0.1:8000/authendication/user/%s" % body)

#     return req.json()


# @user.post("/Call_Sentimet_Values")
# async def Call_Values(Calls: Call_Value):

#     try:
#         result = collection_name.insert_one(jsonable_encoder(Calls))
#         inserted_id = str(result.inserted_id)
#         return {"message": "Data inserted successfully", "inserted_id": inserted_id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

    # return collection_name.insert_one(jsonable_encoder(Calls))


# @user.get("/Call_Sentimet_Values")
# async def get_call():
#     values = Call_Value(TotalCall=0, positive=0, negative=0, average=0)

#     calls = callsEntity(collection_name.find())
#     for x in calls:
#         values.TotalCall += x["TotalCall"]
#         values.positive += x["positive"]
#         values.negative += x["negative"]
#         values.average += x["average"]
#     return dict(values)


# @user.get("/allWidgets")
# async def allWidgets(background_tasks: BackgroundTasks,current_user_id: str = Depends(get_current_user_id)):
#     widgets = await process_all_widgets(current_user_id)
#     return widgets




# class EmailData(BaseModel):
#     ID: int
#     Sentiment: int
#     Date: str
#     Word: str

# updated = []

# @user.get("/getUpdate")
# async def get_latest_data(data:EmailData):
#    print(data)
#    updated.append(data)


# @user.get("/update")
# async def get_latest_data():
#    if(updated):
#     print(updated)
#     return updated
#    else:
#       return False


# @user.get("/doughnutChart")
# async def doughnutChart():
#     data = callsEntity(call_collection.find())
#     callData=doughnutChartFun(data)
#     data = callsEntity(email_collection.find())
#     emailData=doughnutChartFun(data)
#     data = callsEntity(social_collection.find())
#     socialData=doughnutChartFun(data)
#     return [{'call':callData , 'email':emailData, 'social':socialData}]

# @user.get("/lineChart")
# async def lineChart():
#     data = callsEntity(call_collection.find())
#     CallData = lineChartFun(data)
#     CallData = lineChartExtract(CallData)

#     data = callsEntity(email_collection.find())
#     EmailData = lineChartFun(data)
#     EmailData = lineChartExtract(EmailData)

#     data = callsEntity(social_collection.find())
#     SocialData = lineChartFun(data)
#     SocialData = lineChartExtract(SocialData)

#     return [{'call':CallData , 'email':EmailData, 'social':SocialData}]


# @user.get("/wordCloud")
# async def wordCloud():

#     data = callsEntity(call_collection.find())
#     CallData = wordChartExtract(data)

#     data = callsEntity(email_collection.find())
#     EmailData = wordChartExtract(data)

#     data = callsEntity(social_collection.find())
#     SocialData = wordChartExtract(data)

#     return [{'call':CallData , 'email':EmailData, 'social':SocialData}]
            
# def wordChartExtract(dataset):
#     flat_data = [item for item in dataset]
#     word_counts = Counter(item["Word"] for item in flat_data)
#     output = []
#     for word, count in word_counts.items():
#         word_entry = {"word": word, "weight": count}
#         if random.random() < 0.5:  # 50% chance of assigning a random color
#             word_entry["color"] = "green"
#         output.append(word_entry)
#     return output

# def lineChartExtract(lineChartList):
#     sums_by_date = defaultdict(lambda: {"Date": "", "positive": 0, "negative": 0, "neutral": 0})
#             # Iterate through the list and sum values for each unique date
#     for item in lineChartList:
#         date = item["Date"]
#         sums_by_date[date]["Date"] = date  # Assign the date to the result
#         sums_by_date[date]["positive"] += item["positive"]
#         sums_by_date[date]["negative"] += item["negative"]
#         sums_by_date[date]["neutral"] += item["neutral"]


#     final_result = list(sums_by_date.values())
#     return final_result

# @user.post("/newWidget")
# async def newWidget(widget: Widget, current_user_id: str = Depends(get_current_user_id)):
#     widget_dict: Dict = dict(widget)
#     widget_dict['email'] = current_user_id
#     widget_collection.insert_one(widget_dict)    
#     return "New widget added"


# async def process_all_widgets(current_user_id: str):
#     widgetsDetials = WidgetEntry(widget_collection.find({"email": current_user_id}))
#     widgets =[]
#     for widget in widgetsDetials:

#         if widget['chartType']=='pie-chart':
#             Combination={'negative': 0, 'positive': 0, 'neutral': 0}
#             for source in widget['sources']:
#                 if(source=='email'):
#                     data = callsEntity(email_collection.find())
#                     EmailData=doughnutChartFun(data)
#                     Combination['negative']+=EmailData['negative']
#                     Combination['positive']+=EmailData['positive']
#                     Combination['neutral']+=EmailData['neutral']
#                 if(source=='call'):
#                     data = callsEntity(call_collection.find())
#                     CallData=doughnutChartFun(data)
#                     Combination['negative']+=CallData['negative']
#                     Combination['positive']+=CallData['positive']
#                     Combination['neutral']+=CallData['neutral']
#                 if(source=='social'):
#                     data = callsEntity(social_collection.find())
#                     SocialData=doughnutChartFun(data)
#                     Combination['negative']+=SocialData['negative']
#                     Combination['positive']+=SocialData['positive']
#                     Combination['neutral']+=SocialData['neutral']
#             chart = {"title":widget['title'],"chart": widget['chartType'],"data":Combination}
#             widgets.append(chart)
#             continue

#         if widget['chartType']=='line-chart':
#             lineChartList = []
#             for source in widget['sources']:
#                 if(source=='email'):
#                     data = callsEntity(email_collection.find())
#                     EmailData=lineChartFun(data)
#                     lineChartList.append(EmailData)
#                 if(source=='call'):
#                     data = callsEntity(call_collection.find())
#                     CallData=lineChartFun(data)
#                     lineChartList.append(CallData)
#                 if(source=='social'):
#                     data = callsEntity(social_collection.find())
#                     SocialData=lineChartFun(data)
#                     lineChartList.append(SocialData)

#             sums_by_date = defaultdict(lambda: {"Date": "", "positive": 0, "negative": 0, "neutral": 0})

#             # Iterate through the list and sum values for each unique date
#             for listchart in lineChartList:
#                 for item in listchart:
#                     date = item["Date"]
#                     sums_by_date[date]["Date"] = date  # Assign the date to the result
#                     sums_by_date[date]["positive"] += item["positive"]
#                     sums_by_date[date]["negative"] += item["negative"]
#                     sums_by_date[date]["neutral"] += item["neutral"]

#             # Extract the values from the dictionary to get the final list
#             final_result = list(sums_by_date.values())
#             chart = {"title":widget['title'],"chart": widget['chartType'],"data":final_result}
#             widgets.append(chart)
#             continue

#         # if widget['chartType']=='bar-chart':
#         #     print("bar-chart")
#         # if widget['chartType']=='horizontal-bar-chart':
#         #     print("horizontal-bar-chart")
#         if widget['chartType']=='word-cloud':
#             dataset=[]
#             for source in widget['sources']:
#                 if(source=='email'):
#                     data = callsEntity(email_collection.find())
#                     dataset.append(data)
#                 if(source=='call'):
#                     data = callsEntity(call_collection.find())
#                     dataset.append(data)
#                 if(source=='social'):
#                     data = callsEntity(social_collection.find())
#                     dataset.append(data)

#             flat_data = [item for sublist in dataset for item in sublist]

#             # Count occurrences of each word
#             word_counts = Counter(item["Word"] for item in flat_data)

#             # Prepare the output format
#             output = []
#             for word, count in word_counts.items():
#                 word_entry = {"word": word, "weight": count}
#                 if random.random() < 0.5:  # 50% chance of assigning a random color
#                     word_entry["color"] = "green"
#                 output.append(word_entry)
            
#             chart = {"title":widget['title'],"chart": widget['chartType'],"data":output}
#             widgets.append(chart)
#             continue
#         # if widget['chartType']=='table':
#         #     print("table")   
#     return widgets

# @user.post("/newWidget")
# async def newWidget(widget: Widget, current_user_id: str = Depends(get_current_user_id)):
#     widget_dict = dict(widget)
#     widget_dict['email'] = current_user_id
#     widget_collection.insert_one(widget_dict)
#     return "New widget added"

# @user.get("/call-sentiments")
# async def find_all_call():

#     req = requests.get("http://127.0.0.1:8000/authendication/")

#     return req.json()
