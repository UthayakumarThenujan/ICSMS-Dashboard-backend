from fastapi import FastAPI
from routes.user import router, watch_all_collections, process_initial_documents
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

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

@app.on_event("startup")
async def on_startup():
    # Create an event loop
    loop = asyncio.get_event_loop()

    # Process initial documents
    await process_initial_documents()
    print("initial data analys ended")
    # Start watching collections after initialization is done
    await watch_all_collections(loop)


if __name__ == "__main__":
    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
