from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.user import EmailData,CallData
from typing import Optional, List
from config.db import callDB_collection,emailDB_collection, read_EmailMessages_collection, read_Inquiries_collection, read_Issues_collection, call_collection
from schemas.user import userEntity, usersEntity
from starlette.requests import Request
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from bson import ObjectId
from threading import Thread
import time
import asyncio
import json
import re

router = APIRouter(prefix="/data", tags=["data"])

def calculate_sentiment(score):
    if score > 0.3:
        return "Positive"
    elif score < -0.3:
        return "Negative"
    else:
        return "Neutral"

def process_email_data(email_message):
    sentiment = calculate_sentiment(email_message['our_sentiment_score'])
    return {
        "time": email_message['time']['$date'],
        "sentiment": {sentiment: email_message['our_sentiment_score']},
        "sender": email_message['sender'],
        "topics": email_message['topics']
    }

def process_call_data(call_message):
    sentiment = calculate_sentiment(call_message['sentiment_score'])
    return {
        "time": call_message['call_date'],
        "sentiment": {sentiment: call_message['sentiment_score']},
        "keywords": call_message['keywords'],
        "topics": call_message['topics']
    }

async def receive_email_data(email_message: EmailData):
    date_str = email_message.time.split("T")[0]
    existing_data = emailDB_collection.find_one({"Date": date_str})

    processed_data = process_email_data(email_message.dict())

    if existing_data:
        existing_data['data'].append(processed_data)
        emailDB_collection.update_one({"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data})
    else:
        new_data = {
            "Date": date_str,
            "data": [processed_data]
        }
        emailDB_collection.insert_one(new_data)

    return {"message": "Email data received and processed successfully"}

async def receive_call_data(call_message: CallData):
    date_str = call_message.call_date.split("T")[0]
    existing_data = callDB_collection.find_one({"Date": date_str})

    processed_data = process_call_data(call_message.dict())

    if existing_data:
        existing_data['data'].append(processed_data)
        callDB_collection.update_one({"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data})
    else:
        new_data = {
            "Date": date_str,
            "data": [processed_data]
        }
        callDB_collection.insert_one(new_data)

    return {"message": "Call data received and processed successfully"}

connected_clients = []

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

async def notify_clients(name):
    message = json.dumps({
        "response": 'data',
        "name": name
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

async def widget_notify():
    message = json.dumps({
        "response": 'widget',
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

def watch_collection_sync(collection_name, name):
    collection = collection_name
    change_stream = collection.watch()
    print(name)
    for change in change_stream:
        print(f"Change detected in {collection_name}: {change}")
        if 'documentKey' in change and '_id' in change['documentKey']:
            changed_id = change['documentKey']['_id']
            asyncio.run_coroutine_threadsafe(process_changed_document(collection, changed_id,name), loop)
        if name == 'widget':
            asyncio.run_coroutine_threadsafe(widget_notify(), loop)
        else:
            asyncio.run_coroutine_threadsafe(notify_clients(name), loop)

async def process_changed_document(collection, changed_id,name):
    changed_document = collection.find_one({"_id": ObjectId(changed_id)})
    
    if changed_document:
        if name=='email_messages' or name=='email_inquiries' or name=='email_issues':
            call_data = CallData(
                _id=str(changed_document['_id']),
                call_id=changed_document['call_id'],
                sentiment_category=changed_document['sentiment_category'],
                keywords=changed_document['keywords'],
                topics=changed_document['topics'],
                summary=changed_document['summary'],
                sentiment_score=changed_document['sentiment_score'],
                call_date=changed_document['call_date']
            )
            await receive_call_data(call_data)
        elif name=='call_data':
            email_data = EmailData(
                time=changed_document['time']['$date'],
                our_sentiment_score=changed_document['our_sentiment_score'],
                sender=changed_document['sender'],
                topics=changed_document['topics']
            )
            await receive_email_data(email_data)

async def watch_collection(collection_name, name):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, watch_collection_sync, collection_name, name)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def watch_all_collections():
    tasks = [
        watch_collection(read_EmailMessages_collection, 'email_messages'),
        watch_collection(read_Inquiries_collection, 'email_inquiries'),
        watch_collection(read_Issues_collection, 'email_issues'),
        watch_collection(call_collection, 'call_data'),
    ]
    await asyncio.gather(*tasks)

# Create a new asyncio event loop
loop = asyncio.new_event_loop()
t = Thread(target=start_async_loop, args=(loop,), daemon=True)
t.start()

# Schedule the watch_all_collections coroutine on the new event loop
asyncio.run_coroutine_threadsafe(watch_all_collections(), loop)
