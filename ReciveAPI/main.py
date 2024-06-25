from fastapi import FastAPI
from routes.user import router, watch_all_collections, process_initial_documents, start_async_loop
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from threading import Thread

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    # Create a new asyncio event loop
    loop = asyncio.new_event_loop()
    t = Thread(target=start_async_loop, args=(loop,), daemon=True)
    t.start()

    # Process initial documents
    future = asyncio.run_coroutine_threadsafe(process_initial_documents(), loop)
    future.result()  # Wait for the initial processing to complete

    # Schedule the watch_all_collections coroutine on the new event loop
    asyncio.run_coroutine_threadsafe(watch_all_collections(loop), loop)

    # Specify the host and port here
    uvicorn.run(app, host="127.0.0.1", port=8005)
