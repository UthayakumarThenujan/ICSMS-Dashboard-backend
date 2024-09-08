# Import necessary modules and classes
from models.model import CallData  # Import the CallData model
from routes.call.call_preprocess import process_call_data  # Import call data processing function
from config.main_dashboard_db import callDB_collection  # Import MongoDB collection configuration
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
async def receive_call_data(call_message: CallData):
    """
    Receives call data, processes it, and stores it in the main_dashborad database.
    
    Args:
        call_message (CallData): An instance of CallData containing call details.
    
    Returns:
        dict: A message indicating the success of the operation.
    """
    
    # Extract the date from the call_date field (assumes ISO format with 'T')
    date_str = call_message.call_date.split("T")[0]
    
    # Check if there is already an entry in the database for the given date
    existing_data = callDB_collection.find_one({"Date": date_str})

    # Process the incoming call data (convert to dictionary and calculate sentiment)
    processed_data = process_call_data(call_message.dict())

    # Helper function to check if the new entry is a duplicate of an existing one
    def is_duplicate(entry, new_entry):
        """
        Checks if a given entry in the database is a duplicate of the new processed data.
        
        Args:
            entry (dict): An existing entry from the database.
            new_entry (dict): The new processed data to compare.
        
        Returns:
            bool: True if the entries match, False otherwise.
        """
        return (entry['time'] == new_entry['time'] and
                entry['keywords'] == new_entry['keywords'] and
                entry['Sentiment'] == new_entry['Sentiment'] and
                entry['topic'] == new_entry['topic'])

    # If data for the date exists, check for duplicates before appending new data
    if existing_data:
        # Check if the processed data is already present in the existing data
        data_exists = any(is_duplicate(entry, processed_data) for entry in existing_data['data'])
        
        # If the data is not a duplicate, append it to the existing entry
        if not data_exists:
            existing_data['data'].append(processed_data)
            # Update the database with the new data
            callDB_collection.update_one(
                {"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data}
            )
        
    else:
        # If no data exists for the given date, create a new entry
        new_data = {"Date": date_str, "data": [processed_data]}
        # Insert the new entry into the database
        callDB_collection.insert_one(new_data)

    # Return a success message
    return {"message": "Call data received and processed successfully"}
