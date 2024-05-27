from fastapi import APIRouter
from typing import Optional
from config.db import collection_name
from schemas.user import userEntity, usersEntity
from starlette.requests import Request
import requests
from bson import ObjectId
from emailAlert import email_alert
from pymongo import DESCENDING
from datetime import datetime
from models.user import Notification,UpdateNoti
# from bson import ObjectId

user = APIRouter(prefix="/Notifications", tags=["Notifications"])

# @user.post("/call-sentiments")
# async def find_all_call(request: UserInput):
#     body = request.emails

#     req = requests.get("http://127.0.0.1:8000/authendication/user/%s" % body)

#     return req.json()

@user.post("/postNotification")
async def notificationSend(notification:Notification):
    notification.created_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    email_alert("iCSMS Alert",notification.alert,notification.email)
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
    # Convert the notification ID from string to ObjectId
    obj_id = ObjectId(notification.id)
    print(id)
    # Update the status of the document in MongoDB
    result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "UNREAD"}})

    # Check if the document was successfully updated
    if result.modified_count == 1:
        return {"message": "Status updated successfully"}
    else:
        return {"message": "Document not found or status not updated"}

@user.post("/Unreadpost")
async def UnreadnotificationPost(notification:UpdateNoti):
    # Convert the notification ID from string to ObjectId
    obj_id = ObjectId(notification.id)
    print(id)
    # Update the status of the document in MongoDB
    result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "READ"}})

    # Check if the document was successfully updated
    if result.modified_count == 1:
        return {"message": "Status updated successfully"}
    else:
        return {"message": "Document not found or status not updated"}


@user.get("/NewnotificationCounts")
async def getNotificationsCounts():
    notifications = usersEntity(collection_name.find({'status': "UNREAD"}))
    return len(notifications)

