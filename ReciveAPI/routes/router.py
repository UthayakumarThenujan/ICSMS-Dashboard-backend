from fastapi import APIRouter, HTTPException
from threading import Thread
from schemas.schema import usersEntity

import asyncio

# Importing functions to handle initial data processing and changed document processing
from .initial_process import process_initial_documents
from .changed_data_handel import process_changed_document

# Importing MongoDB collections for various data types
from config.email_db import read_EmailMessages_collection, read_Inquiries_collection, read_Issues_collection
from config.social_db import social_Comment_collection, social_IdentifiedKeywords_collection, social_IdentifiedProducts_collection
from config.call_db import call_collection

# Creating a FastAPI router for data-related endpoints
router = APIRouter(prefix="/data", tags=["data"])

@router.get("/comments")
def get_all_comments():
    try:
        comments = usersEntity(social_Comment_collection.find())
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
def watch_collection_sync(collection_name, name, loop):
    collection = collection_name
    change_stream = collection.watch()  # Watching for changes in the collection

    for change in change_stream:
        if 'documentKey' in change and '_id' in change['documentKey']:
            changed_id = change['documentKey']['_id']  # Extracting the changed document ID

            # Running the process_changed_document coroutine in the event loop for the changed document
            asyncio.run_coroutine_threadsafe(
                process_changed_document(collection, changed_id, name), loop
            )

async def watch_collection(collection_name, name, loop):
    # Running the synchronous watch_collection_sync function in an executor
    await asyncio.get_running_loop().run_in_executor(None, watch_collection_sync, collection_name, name, loop)

async def watch_all_collections(loop):
    # Setting up tasks to watch all relevant collections concurrently
    tasks = [
        watch_collection(read_EmailMessages_collection, 'email_messages', loop),
        watch_collection(call_collection, 'call_data', loop),
        watch_collection(social_Comment_collection, "social_comment", loop),
        watch_collection(social_IdentifiedKeywords_collection, 'social_keywords', loop),
        watch_collection(social_IdentifiedProducts_collection, 'social_products', loop),
        watch_collection(read_Inquiries_collection, 'email_inquiry', loop),
        watch_collection(read_Issues_collection, 'email_issue', loop),
    ]
    await asyncio.gather(*tasks)  # Running all collection watching tasks concurrently

async def start_async_processes(loop):
    # Starting the initial data processing and watching all collections
    await process_initial_documents()

    await watch_all_collections(loop)

# Creating a new event loop for async processing
loop = asyncio.new_event_loop()
# Starting a new thread to run the async processes
t = Thread(target=lambda: asyncio.run(start_async_processes(loop)), daemon=True)
t.start()
