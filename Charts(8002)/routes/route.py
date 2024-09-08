from models.user import WidgetRequest,GridItemsUpdateRequest,GridStatusUpdateRequest
from config.db import call_collection,email_collection,social_collection,widget_collection
from schemas.user import WidgetEntry,EmailcallsEntity
from bson import ObjectId
from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends, HTTPException
from threading import Thread
from pymongo import ASCENDING
from notify import *
from token_verification import get_current_user
import asyncio


user = APIRouter(prefix="/charts", tags=["charts"])

gridChange = False
connected_clients = []

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

@user.get("/widgetsUser")
async def widgetsUser(email: str = Depends(get_current_user)):
    global gridChange
    try:
        widgets_details = WidgetEntry(widget_collection.find({"email": email}))
        if(len(widgets_details)==0):
            default_widgets = [
                {
                  "title": "line-all",
                  "email": email,
                  "chartType": "Line Chart",
                  "grid": { "cols": 4, "rows": 3, "x": 0 , "y": 0 },
                  "keywords": [],
                  "sources": ["email", "social", "call"],
                  "status": "show",
                  "topics": [],
                  "xAxis": "date",
                  "yAxis": "sentiment-count"
                },
                {
                  "title": "bar-email",
                  "email": email,
                  "chartType": "Bar Chart",
                  "grid": { "cols": 3, "rows": 3, "x": 4 , "y": 3 },
                  "keywords": [],
                  "sources": ["email"],
                  "status": "show",
                  "topics": [],
                  "xAxis": "topics",
                  "yAxis": "sentiment-count"
                },
                {
                  "title": "line-email",
                  "chartType": "Line Chart",
                  "email": email,
                  "grid": { "cols": 4, "rows": 3, "x": 0, "y": 4 },
                  "keywords": [],
                  "sources": ["email"],
                  "status": "show",
                  "topics": [],
                  "xAxis": "date",
                  "yAxis": "sentiment-count"
                },
                {
                  "title": "bar-sources",
                  "chartType": "Bar Chart",
                  "email": email,
                  "grid": { "cols": 3, "rows": 2, "x": 3 },
                  "keywords": [],
                  "sources": ["email", "social", "call"],
                  "status": "show",
                  "topics": [],
                  "xAxis": "topics",
                  "yAxis": "sentiment-count"
                },
            ]
            widget_collection.insert_many(default_widgets)
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

@user.post("/gridStatus")
async def update_grid_items(request: GridStatusUpdateRequest, email: str = Depends(get_current_user)):
    global gridChange
    gridChange =True
    try:
        widget_collection.update_one(
                {"_id": ObjectId(request.id), "email": email},
                {"$set": {"status": request.status}}
            )
        return {"message": "Grid status updated", "success": True}
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
async def delete_widget(id: str,email: str = Depends(get_current_user)):
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


def watch_collection_sync(collection_name,name):
    global gridChange
    collection = collection_name
    change_stream = collection.watch()
    for change in change_stream:
        if(name=='widget'):
            if 'updateDescription' in change and 'updatedFields' in change['updateDescription']:
                updated_fields = change['updateDescription']['updatedFields']
                if any(field.startswith('grid') for field in updated_fields):
                    asyncio.run_coroutine_threadsafe(gridChange_notifiy(connected_clients), loop)
            else:
                asyncio.run_coroutine_threadsafe(widget_notifiy(connected_clients), loop)         
        else:
            asyncio.run_coroutine_threadsafe(notify_clients(name,connected_clients), loop)


async def watch_collection(collection_name,name):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, watch_collection_sync, collection_name,name)

async def watch_all_collections():
    tasks = [
        watch_collection(call_collection,'call'),
        watch_collection(email_collection,'email'),
        watch_collection(social_collection,'social'),
        watch_collection(widget_collection,'widget')
    ]
    await asyncio.gather(*tasks)


def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Create a new asyncio event loop
loop = asyncio.new_event_loop()
t = Thread(target=start_async_loop, args=(loop,), daemon=True)
t.start()

# Schedule the watch_all_collections coroutine on the new event loop
asyncio.run_coroutine_threadsafe(watch_all_collections(), loop)
