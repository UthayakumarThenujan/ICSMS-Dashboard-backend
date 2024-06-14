from fastapi import APIRouter
from config.db import collection_name
from schemas.user import usersEntity
from bson import ObjectId
# from emailAlert import email_alert
from pymongo import DESCENDING
from datetime import datetime
from models.user import Notification,UpdateNoti

user = APIRouter(prefix="/Notifications", tags=["Notifications"])

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from bson import ObjectId
from threading import Thread


connected_clients = []

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)
    
@user.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def notify_notification_clients():

    message = json.dumps({
        "response": "change",
    }, cls=JSONEncoder)
    print(message)
    for client in connected_clients:
        await client.send_text(message)

def watch_collection_sync(collection_name,name):
    change_stream = collection_name.watch()
    print(change_stream)
    for change in change_stream:
        print(f"Change detected in notifications collection: {change}")
        asyncio.run_coroutine_threadsafe(notify_notification_clients(), loop)


async def watch_collection(collection_name,name):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, watch_collection_sync, collection_name,name)


def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def watch_all_collections():
    tasks = [
        watch_collection(collection_name,'notifications'),
    ]
    await asyncio.gather(*tasks)

# Create a new asyncio event loop
loop = asyncio.new_event_loop()
t = Thread(target=start_async_loop, args=(loop,), daemon=True)
t.start()

# Schedule the watch_all_collections coroutine on the new event loop
asyncio.run_coroutine_threadsafe(watch_all_collections(), loop)


@user.post("/postNotification")
async def notificationSend(notification:Notification):
    notification.created_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    # email_alert("iCSMS Alert",notification.alert,notification.email)
    collection_name.insert_one(dict(notification))
    return "Account Created"


@user.get("/Newnotification")
async def Newnotification():
    notifications = usersEntity(collection_name.find({'status': "UNREAD"}).sort("_id", DESCENDING))
    return notifications

@user.get("/Readnotification")
async def Readnotification():
    notifications = usersEntity(collection_name.find({'status': "READ"}).sort("_id", DESCENDING))
    return notifications

@user.post("/Readpost")
async def ReadnotificationPost(notification:UpdateNoti):

    modified_count = 0
    for item in notification.id:
        obj_id = ObjectId(item["id"])
        result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "UNREAD"}})
        modified_count += result.modified_count

    if modified_count > 0:
        return {"message": "Status updated successfully"}
    else:
        return {"message": "Document not found or status not updated"}
    

@user.post("/Unreadpost")
async def UnreadnotificationPost(notification:UpdateNoti):
    modified_count = 0
    for item in notification.id:
        obj_id = ObjectId(item["id"])
        result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "READ"}})
        modified_count += result.modified_count

    if modified_count > 0:
        return {"message": "Status updated successfully"}
    else:
        return {"message": "Document not found or status not updated"}


@user.get("/NewnotificationCounts")
async def getNotificationsCounts():
    notifications = usersEntity(collection_name.find({'status': "UNREAD"}))
    return len(notifications)

