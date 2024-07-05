from fastapi import APIRouter
from config.db import collection_name,call_collection,social_Comment_collection,read_EmailMessages_collection
from schemas.user import usersEntity,serializeList,serializeListcall
from bson import ObjectId
# from emailAlert import email_alert
from pymongo import DESCENDING
from datetime import datetime
from dateutil import parser
import pytz
from models.user import Notification,UpdateNoti,CallData
user = APIRouter(prefix="/Notifications", tags=["Notifications"])
from dateutil.parser import parse as dateutil_parse
from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends, HTTPException, status
from typing import List
import asyncio
import json
import urllib.request
from bson import ObjectId
from threading import Thread
from fastapi import Header
from jose import jwk, jwt
from jose.utils import base64url_decode
import time

region = 'ap-south-1'
userpool_id = 'ap-south-1_YEH0sqfmB'
app_client_id = '4nql0ttol3en0nir4d56ctdc6i'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']



def verifyToken(event):
    token = event['token']
    
    # Verify the token structure
    if token.count('.') != 2:
        print('Invalid token structure')
        return False
    
    # get the kid from the headers prior to verification
    try:
        headers = jwt.get_unverified_headers(token)
    except jwt.JWTError as e:
        print(f"Error decoding token headers: {e}")
        return False

    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False

    # construct the public key
    public_key = jwk.construct(keys[key_index])

    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        # print('Token was not issued for this audience')
        return False
    # now we can use the claims
    # print(claims)
    return claims



async def get_websocket_user(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    claims = verifyToken({"token": token})
    if not claims:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return claims["email"]


def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]  # Assuming the token is sent as "Bearer <token>"
        claims = verifyToken({"token": token})
        if not claims:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return claims["email"]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is malformed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

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


async def notify_notification_clients(data, name):
    
    if name == 'call':
        call_message = collection_name.find_one({"_id": ObjectId(data["_id"])})
        if not call_message:
            new_data = {
                '_id': ObjectId(call_message["_id"]),
                'title': call_message["title"],
                'description': call_message["description"],
                'sources': 'call',
                'datetime': call_message['datetime'].isoformat(),
                'status': 'UNREAD'
            }
            collection_name.insert_one(new_data)
            print("Call data received and inserted successfully")
        return {"message": "Call data received and inserted successfully"}
    if name == 'notifications':
        message = json.dumps({"response": "change"}, cls=JSONEncoder)
        print(message)
        for client in connected_clients:
            await client.send_text(message)
    if name == 'call_initial':
        call_message = collection_name.find_one({"_id": ObjectId(data.id)})
        if not call_message:
            new_data = {
                '_id': ObjectId(str(data.id)),
                'title': data.title,
                'description': data.description,
                'sources': 'call',
                'datetime': data.datetime,
                'status': 'UNREAD'
            }
            collection_name.insert_one(new_data)
            print("Call data received and inserted successfully")
        return {"message": "Call data received and inserted successfully"}
    if name == 'social_initial':
        call_message = collection_name.find_one({"_id": ObjectId(data.id)})
        if not call_message:
            new_data = {
                '_id': ObjectId(str(data.id)),
                'title': data.title,
                'description': data.description,
                'sources': 'social',
                'datetime': data.datetime,
                'status': 'UNREAD'
            }
            
            collection_name.insert_one(new_data)
            print("Call data received and inserted successfully")
        return {"message": "Call data received and inserted successfully"}
    if name == 'social':
        call_message = collection_name.find_one({"_id": ObjectId(data["_id"])})
        
        new_data = {
            '_id': ObjectId(call_message["_id"]),
            'title': call_message["title"],
            'description': call_message["description"],
            'sources': 'social',
            'datetime': call_message['date'].isoformat(),
            'status': 'UNREAD'
        }
        collection_name.insert_one(new_data)
        print("Call data received and inserted successfully")
        return {"message": "Call data received and inserted successfully"}
    

async def notify_notification_clients_changed(collection,id, name):
    print(f"Processing changed document: {id} in {name}")
    changed_document = collection.find_one({"_id": ObjectId(id)})
    print(changed_document)
    if changed_document:
        print(f"Changed document found: {changed_document}")
        if name == "call":
            message_datetime = changed_document["datetime"]
            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(message["_id"]),
                title=message["title"],
                description=message["description"],
            )
            await receive_call_data(call_data, 'call_messages')
        if name == "email":
            message_datetime = changed_document["time"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)
                
            print(message_datetime)
            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(changed_document["_id"]),
                title=changed_document["title"],
                description=changed_document["description"],
            )
            print("social", call_data.json())
            await receive_email_data(call_data, 'email_messages')
        if name == "social":
            message_datetime = changed_document["date"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)
                
            print(message_datetime)
            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(changed_document["_id"]),
                title=changed_document["title"],
                description=changed_document["description"],
            )
            print("social", call_data.json())
            await receive_social_data(call_data, 'social_messages')

    if name == 'notifications':
        message = json.dumps({"response": "change"}, cls=JSONEncoder)
        print(message)
        for client in connected_clients:
            await client.send_text(message)
    
    
def watch_collection_sync(collection_name, name, loop):
    collection = collection_name
    change_stream = collection.watch()
    print(f"Watching collection: {name}")
    for change in change_stream:
        print(f"Change detected in {name}: {change}")
        if 'documentKey' in change and '_id' in change['documentKey']:
            changed_id = change['documentKey']['_id']
            try:
                asyncio.run_coroutine_threadsafe(
                    notify_notification_clients_changed(collection, changed_id, name), loop
                )
            except Exception as e:
                print(f"Error running coroutine: {e}")



async def watch_collection(collection_name,name,loop):
    await asyncio.get_running_loop().run_in_executor(None, watch_collection_sync, collection_name, name, loop)


# def start_async_loop(loop):
#     asyncio.set_event_loop(loop)
#     loop.run_forever()

async def watch_all_collections(loop):
    tasks = [
        watch_collection(collection_name,'notifications',loop),
        watch_collection(call_collection,'call',loop),
        watch_collection(social_Comment_collection,'social',loop),
        watch_collection(read_EmailMessages_collection,'email',loop),
    ]
    await asyncio.gather(*tasks)

# Create a new asyncio event loop
# loop = asyncio.new_event_loop()
# t = Thread(target=start_async_loop, args=(loop,), daemon=True)
# t.start()

# # Schedule the watch_all_collections coroutine on the new event loop
# asyncio.run_coroutine_threadsafe(watch_all_collections(), loop)

def get_latest_date_with_source(collection, date_field, source_field):
    projection = {date_field: 1, source_field: 1}
    latest_document = collection.find_one({"sources": source_field}, sort=[(date_field, DESCENDING)], projection=projection)
    
    # If a document is found, return a dictionary with the date and the source
    if latest_document:
        return {
            date_field: latest_document.get(date_field),
            source_field: latest_document.get(source_field)
        }
    
    # If no document is found, return None
    return None



def process_call_data(call_message,name):
    if(name=='call_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'call',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }
    if(name=='social_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'social',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }

def process_social_data(call_message,name):
    if(name=='social_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'social',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }
    
def process_email_data(call_message,name):
    if(name=='email_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'email',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }
    
    

async def receive_call_data(call_message, name):
    print(name)
    existing_data = collection_name.find_one({"_id": ObjectId(call_message.id)})
    processed_data = process_call_data(call_message.dict(), name)

    def is_duplicate(entry, new_entry):
        return (
            entry['datetime'] == new_entry['datetime'] and
            entry["title"] == new_entry['title'] and
            entry["description"] == new_entry['description'] and 
            entry["sources"] == new_entry['sources']
        )

    if not existing_data:
        # data_exists = collection_name.find_one({
        #     "datetime": processed_data["datetime"],
        #     "title": processed_data["title"],
        #     "description": processed_data["description"],
        #     "sources": processed_data["sources"]
        # })
        
        # if not data_exists:
        collection_name.insert_one(processed_data)
        print("Call data added")
        # else:
        #     print("Duplicate call data exists, not adding to the collection")
    return {"message": "Call data received and processed successfully"}


async def receive_social_data(call_message, name):
    print(name)
    existing_data = collection_name.find_one({"_id": ObjectId(call_message.id)})
    processed_data = process_social_data(call_message.dict(), name)

    def is_duplicate(entry, new_entry):
        return (
            entry['datetime'] == new_entry['datetime'] and
            entry["title"] == new_entry['title'] and
            entry["description"] == new_entry['description'] and 
            entry["sources"] == new_entry['sources']
        )

    if not existing_data:
        # data_exists = collection_name.find_one({
        #     "datetime": processed_data["datetime"],
        #     "title": processed_data["title"],
        #     "description": processed_data["description"],
        #     "sources": processed_data["sources"]
        # })
        

        # if not data_exists:
        collection_name.insert_one(processed_data)
        print("Social data added")
        # else:
        #     print("Duplicate call data exists, not adding to the collection")
    return {"message": "Call data received and processed successfully"}


async def receive_email_data(call_message, name):
    print(name)
    existing_data = collection_name.find_one({"_id": ObjectId(call_message.id)})
    processed_data = process_email_data(call_message.dict(), name)

    def is_duplicate(entry, new_entry):
        return (
            entry['datetime'] == new_entry['datetime'] and
            entry["title"] == new_entry['title'] and
            entry["description"] == new_entry['description'] and 
            entry["sources"] == new_entry['sources']
        )

    if not existing_data:
        # data_exists = collection_name.find_one({
        #     "datetime": processed_data["datetime"],
        #     "title": processed_data["title"],
        #     "description": processed_data["description"],
        #     "sources": processed_data["sources"]
        # })
        

        # if not data_exists:
        collection_name.insert_one(processed_data)
        print("email data added")
        # else:
        #     print("Duplicate call data exists, not adding to the collection")
    return {"message": "email data received and processed successfully"}


async def process_initial_documents():
    print("Initial data analysis started")
    async def process_call(latest_date):
        query = {"datetime": {"$gte": latest_date}} if latest_date else {}
        call_messages = serializeListcall(call_collection.find(query))
        print(latest_date)
        for message in call_messages:
            # Convert the datetime string to a datetime object if necessary
            message_datetime = message["datetime"]
            if isinstance(message_datetime, str):
                message_datetime = dateutil_parse(message_datetime)

            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(message["_id"]),
                title=message["title"],
                description=message["description"],
            )
            await receive_call_data(call_data, 'call_messages')



    async def process_social(latest_date):
        if(latest_date):
            latest_date = parser.isoparse(latest_date).astimezone(pytz.utc)
            query = {"date": {"$gte": latest_date}} if latest_date else {}
            social_messages_cursor = social_Comment_collection.find(query)
            social_messages = []
        else:
            social_messages_cursor = social_Comment_collection.find()
            social_messages = []
        
        for message in social_messages_cursor:
            social_messages.append(message)
        
        for message in social_messages:
            message_datetime = message["date"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)

            social_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(message["_id"]),
                title=message["title"],
                description=message["description"],
            )
            await receive_social_data(social_data, 'social_messages')

    async def process_email(latest_date):
            if(latest_date):
                latest_date = parser.isoparse(latest_date).astimezone(pytz.utc)
                query = {"time": {"$gte": latest_date}} if latest_date else {}
                social_messages_cursor = read_EmailMessages_collection.find(query)
                social_messages = []
            else:
                social_messages_cursor = read_EmailMessages_collection.find()
                social_messages = []
            
            for message in social_messages_cursor:
                social_messages.append(message)
            
            for message in social_messages:
                message_datetime = message["time"]
                if isinstance(message_datetime, str):
                    message_datetime = parser.isoparse(message_datetime)

                social_data = CallData(
                    datetime=message_datetime.isoformat(),
                    id=str(message["_id"]),
                    title=message["title"],
                    description=message["description"],
                )
                await receive_email_data(social_data, 'email_messages')

    call_latest_date = get_latest_date_with_source(collection_name, "datetime", 'call')
    social_latest_date = get_latest_date_with_source(collection_name, "datetime", 'social')
    email_latest_date = get_latest_date_with_source(collection_name, "datetime", 'email')

    await asyncio.gather(
        process_call(call_latest_date.get("datetime") if call_latest_date else None),
        process_social(social_latest_date.get("datetime") if social_latest_date else None),
        process_email(email_latest_date.get("datetime") if email_latest_date else None)
        
    )


async def start_async_processes(loop):
    await process_initial_documents()
    print("Initial data analysis ended")
    await watch_all_collections(loop)

def thread_function(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_async_processes(loop))
    loop.run_forever()  # Keep the loop running for other tasks

# Create a new asyncio event loop
loop = asyncio.new_event_loop()
# Start the thread with the event loop
t = Thread(target=thread_function, args=(loop,), daemon=True)
t.start()


    

@user.post("/postNotification")
async def notificationSend(notification:Notification,email: str = Depends(get_current_user)):
    try:
        notification.created_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        # email_alert("iCSMS Alert",notification.alert,notification.email)
        collection_name.insert_one(dict(notification))
        return "Account Created"
    except HTTPException:
            return {"success": False}

@user.get("/Newnotification")
async def Newnotification():
    notifications = usersEntity(collection_name.find({'status': "UNREAD"}).sort("_id", DESCENDING))
    return notifications

@user.get("/Readnotification")
async def Readnotification(email: str = Depends(get_current_user)):
    try:
        notifications = usersEntity(collection_name.find({'status': "READ"}).sort("_id", DESCENDING))
        return notifications
    except HTTPException:
            return {"success": False}
    
@user.post("/Readpost")
async def ReadnotificationPost(notification:UpdateNoti,email: str = Depends(get_current_user)):
    try:
        modified_count = 0
        for item in notification.id:
            obj_id = ObjectId(item["id"])
            result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "UNREAD"}})
            modified_count += result.modified_count

        if modified_count > 0:
            return {"message": "Status updated successfully"}
        else:
            return {"message": "Document not found or status not updated"}
    except HTTPException:
        return {"success": False}
    

@user.post("/Unreadpost")
async def UnreadnotificationPost(notification:UpdateNoti,email: str = Depends(get_current_user)):
    try:
        modified_count = 0
        obj_id = ObjectId(notification.id)
        result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "READ"}})
        modified_count += result.modified_count

        if modified_count > 0:
            return {"message": "Status updated successfully"}
        else:
            return {"message": "Document not found or status not updated"}
    except HTTPException:
        return {"success": False}


@user.get("/NewnotificationCounts")
async def getNotificationsCounts(email: str = Depends(get_current_user)):
    try:
        notifications = usersEntity(collection_name.find({'status': "UNREAD"}))
        return len(notifications)
    except HTTPException:
        return {"success": False}

