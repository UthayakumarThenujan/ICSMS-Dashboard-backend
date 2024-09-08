# Import necessary modules and configurations
from config.call_db import call_collection
from config.email_db import read_EmailMessages_collection
from config.social_db import social_Comment_collection
from config.main_dashboard_db import collection_name

# Import schemas and models
from schemas.user import usersEntity
from bson import ObjectId
from pymongo import DESCENDING
from datetime import datetime
from models.user import Notification, UpdateNoti
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import asyncio
from threading import Thread

# Import helper functions for token verification and notification handling
from .token_verification import get_current_user
from .notify import notify_notification_clients_changed
from .initial_process import process_initial_documents

# Create an API router for notifications with a specific prefix and tags
router = APIRouter(prefix="/Notifications", tags=["Notifications"])

# List to hold all connected WebSocket clients
connected_clients = []

# WebSocket endpoint for real-time notifications
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()
    # Add the client to the list of connected clients
    connected_clients.append(websocket)
    try:
        while True:
            # Keep the WebSocket connection alive by receiving messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Remove the client from the connected clients list if disconnected
        connected_clients.remove(websocket)

# API endpoint to post a new notification
@router.post("/postNotification")
async def notificationSend(notification: Notification, email: str = Depends(get_current_user)):
    try:
        # Set the creation date for the notification
        notification.created_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        # Insert the notification into the collection
        collection_name.insert_one(dict(notification))
        return "Account Created"
    except HTTPException:
        # Return an error response if an exception occurs
        return {"success": False}

# API endpoint to get unread notifications
@router.get("/Newnotification")
async def Newnotification():
    # Fetch notifications with status "UNREAD" sorted in descending order by ID
    notifications = usersEntity(collection_name.find({'status': "UNREAD"}).sort("_id", DESCENDING))
    return notifications

# API endpoint to get read notifications for the current user
@router.get("/Readnotification")
async def Readnotification(email: str = Depends(get_current_user)):
    try:
        # Fetch notifications with status "READ" sorted in descending order by ID
        notifications = usersEntity(collection_name.find({'status': "READ"}).sort("_id", DESCENDING))
        return notifications
    except HTTPException:
        # Return an error response if an exception occurs
        return {"success": False}

# API endpoint to mark notifications as unread based on provided IDs
@router.post("/Readpost")
async def ReadnotificationPost(notification: UpdateNoti, email: str = Depends(get_current_user)):
    try:
        modified_count = 0
        # Loop through the provided notification IDs and update their status to "UNREAD"
        for item in notification.id:
            obj_id = ObjectId(item["id"])
            result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "UNREAD"}})
            modified_count += result.modified_count

        # Return a success message if any documents were modified
        if modified_count > 0:
            return {"message": "Status updated successfully"}
        else:
            return {"message": "Document not found or status not updated"}
    except HTTPException:
        # Return an error response if an exception occurs
        return {"success": False}

# API endpoint to mark a notification as read based on provided ID
@router.post("/Unreadpost")
async def UnreadnotificationPost(notification: UpdateNoti, email: str = Depends(get_current_user)):
    try:
        modified_count = 0
        # Update the notification status to "READ" for the given ID
        obj_id = ObjectId(notification.id)
        result = collection_name.update_one({"_id": obj_id}, {"$set": {"status": "READ"}})
        modified_count += result.modified_count

        # Return a success message if the document was modified
        if modified_count > 0:
            return {"message": "Status updated successfully"}
        else:
            return {"message": "Document not found or status not updated"}
    except HTTPException:
        # Return an error response if an exception occurs
        return {"success": False}

# API endpoint to get the count of unread notifications for the current user
@router.get("/NewnotificationCounts")
async def getNotificationsCounts(email: str = Depends(get_current_user)):
    try:
        # Fetch unread notifications and return their count
        notifications = usersEntity(collection_name.find({'status': "UNREAD"}))
        return len(notifications)
    except HTTPException:
        # Return an error response if an exception occurs
        return {"success": False}

# Function to watch a MongoDB collection for changes in a synchronous context
def watch_collection_sync(collection_name, name, loop):
    collection = collection_name
    # Watch the collection for changes using MongoDB's change stream
    change_stream = collection.watch()

    for change in change_stream:
        # If a change includes a document key with an ObjectId, notify clients
        if 'documentKey' in change and '_id' in change['documentKey']:
            changed_id = change['documentKey']['_id']
            try:
                # Run a coroutine to notify clients about the changed document
                asyncio.run_coroutine_threadsafe(
                    notify_notification_clients_changed(collection, changed_id, name, connected_clients), loop
                )
            except Exception as e:
                # Log any errors encountered during the coroutine execution
                print(f"Error running coroutine: {e}")

# Asynchronous wrapper for watching a MongoDB collection
async def watch_collection(collection_name, name, loop):
    await asyncio.get_running_loop().run_in_executor(None, watch_collection_sync, collection_name, name, loop)

# Asynchronously watch all relevant MongoDB collections for changes
async def watch_all_collections(loop):
    tasks = [
        watch_collection(collection_name, 'notifications', loop),
        watch_collection(call_collection, 'call', loop),
        watch_collection(social_Comment_collection, 'social', loop),
        watch_collection(read_EmailMessages_collection, 'email', loop),
    ]
    # Gather and run all tasks concurrently
    await asyncio.gather(*tasks)

# Asynchronous function to process initial data and start watching collections
async def start_async_processes(loop):
    # Process initial documents for analysis
    await process_initial_documents()

    # Start watching all collections for changes
    await watch_all_collections(loop)

# Thread function to run the asyncio event loop
def thread_function(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_async_processes(loop))
    loop.run_forever()  # Keep the loop running for other tasks

# Create a new asyncio event loop
loop = asyncio.new_event_loop()
# Start the thread with the event loop
t = Thread(target=thread_function, args=(loop,), daemon=True)
t.start()
