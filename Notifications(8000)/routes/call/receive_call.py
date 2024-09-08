# Import necessary modules and classes
from routes.call.call_preprocess import process_call_data  # Import call data processing function
from config.main_dashboard_db import collection_name  # Import MongoDB collection configuration
from bson import ObjectId  # Import ObjectId for MongoDB document ID handling
import json  # Import JSON for encoding data

# Custom JSON encoder to handle ObjectId serialization
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        # Convert ObjectId to string for JSON serialization
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

# Asynchronous function to receive and process call data
async def receive_call_data(call_message, name):
    existing_data = collection_name.find_one({"_id": ObjectId(call_message.id)})
    processed_data = process_call_data(call_message.dict(), name)

    if not existing_data:
        collection_name.insert_one(processed_data)


    return {"message": "Call data received and processed successfully"}