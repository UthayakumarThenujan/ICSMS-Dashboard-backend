from models.user import WidgetRequest,Token,BarChart,GridItemsUpdateRequest
from config.db import call_collection,email_collection,social_collection,widget_collection
from schemas.user import callsEntity,WidgetEntry,bartChartsEntry,EmailcallsEntity
import time
from jose import jwk, jwt
from jose.utils import base64url_decode
import json
import urllib.request
from fastapi import Header
from bson import ObjectId
from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends, HTTPException, status
from threading import Thread
from veritical_bar import bar_chart_extract
from pymongo import ASCENDING


gridChange = False

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



user = APIRouter(prefix="/charts", tags=["charts"])
#8002
region = 'ap-south-1'
userpool_id = 'ap-south-1_YEH0sqfmB'
app_client_id = '4nql0ttol3en0nir4d56ctdc6i'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']


@user.get("/widgetsUser")
async def widgetsUser(email: str = Depends(get_current_user)):
    global gridChange
    try:
        widgets_details = WidgetEntry(widget_collection.find({"email": email}))
        return widgets_details
    except HTTPException:
        return False

@user.post("/gridChanged")
async def update_grid_items(request: GridItemsUpdateRequest, email: str = Depends(get_current_user)):
    global gridChange
    gridChange =True
    try:
        for item in request.items:
            widget_collection.update_one(
                {"_id": ObjectId(item.id), "email": email},
                {"$set": {"grid.cols": item.cols, "grid.rows": item.rows, "grid.x": item.x, "grid.y": item.y}}
            )
        return {"message": "Grid items updated", "success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}

    
@user.get("/chartData")
async def chartData(email: str = Depends(get_current_user)):
    try:
        callData = EmailcallsEntity(call_collection.find().sort("Date", ASCENDING))
        emailData = EmailcallsEntity(email_collection.find().sort("Date", ASCENDING))
        socialData = EmailcallsEntity(social_collection.find().sort("Date", ASCENDING))
        return [{'call':callData , 'email':emailData, 'social':socialData}]
    except HTTPException:
        return False

@user.delete("/gridDeleted/{id}")
async def delete_widget(id: str):
    try:
        object_id = ObjectId(id)
    except:
        return False

    # Perform the deletion
    delete_result = widget_collection.delete_one({"_id": object_id})
    if delete_result.deleted_count == 1:
        return {"message": "Record deleted successfully"}
    else:
        return False


# @user.post("/barChart")
# async def barChart(barChart:BarChart):
#     for source in barChart.collections:
#         data={}
#         if(source=='call'):
#             callData = bartChartsEntry(call_collection.find())
#             data['call']=callData
#         if(source=='email'):
#             emailData = bartChartsEntry(email_collection.find())
#             data['email']=emailData
#         if(source=='social'):
#             socialData = bartChartsEntry(social_collection.find())
#             data['social']=socialData
#     result=bar_chart_extract(barChart.collections, data, barChart.date_range, None)
#     print(result)
#     return result

# def verifyToken(event):
#     print(event)
#     token = event['token']
#     # get the kid from the headers prior to verification
#     headers = jwt.get_unverified_headers(token)
#     print(headers)
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
#     # additionally we can verify the token expiration
#     if time.time() > claims['exp']:
#         print('Token is expired')
#         return False
#     # and the Audience  (use claims['client_id'] if verifying an access token)
#     if claims['aud'] != app_client_id:
#         # print('Token was not issued for this audience')
#         return False
#     # now we can use the claims
#     # print(claims)
#     return claims

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


import asyncio
connected_clients = []

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

async def notify_clients(name):
    message = json.dumps({
        "response": 'data',
        "name":name
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

async def gridChange_notifiy():
    message = json.dumps({
        "response": 'grid',
    }, cls=JSONEncoder)
    print("grid")
    for client in connected_clients:
        await client.send_text(message)

async def widget_notifiy():
    message = json.dumps({
        "response": 'widget',
    }, cls=JSONEncoder)
    print("widgets")
    for client in connected_clients:
        await client.send_text(message)


def watch_collection_sync(collection_name,name):
    global gridChange
    collection = collection_name
    change_stream = collection.watch()
    print(name)
    for change in change_stream:
        print(f"Change detected in {collection_name}: {change}")
        if(name=='widget'):
            if 'updateDescription' in change and 'updatedFields' in change['updateDescription']:
                updated_fields = change['updateDescription']['updatedFields']
                if any(field.startswith('grid') for field in updated_fields):
                    asyncio.run_coroutine_threadsafe(gridChange_notifiy(), loop)
            else:
                asyncio.run_coroutine_threadsafe(widget_notifiy(), loop)         
        else:
            asyncio.run_coroutine_threadsafe(notify_clients(name), loop)


async def watch_collection(collection_name,name):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, watch_collection_sync, collection_name,name)

# @user.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket, email: str = Depends(get_websocket_user)):
#     await websocket.accept()
#     connected_clients.append(websocket)
#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         connected_clients.remove(websocket)

@user.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@user.post("/newWidget")
async def new_widget(request: WidgetRequest, email: str = Depends(get_current_user)):
    try:
        widget_dict = request.widget.dict()
        widget_dict['email'] = email
        widget_collection.insert_one(widget_dict)
        return {"message": "New widget added", "success": True}
    except HTTPException:
        return {"success": False}

# @user.post("/user_email/")
# async def validateAndUsername(token: Token):
#     print(token.token)
#     claims = verifyToken({"token": token.token})
#     if(claims):
#         return claims["email"]
#     else:
#         return False
    

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
