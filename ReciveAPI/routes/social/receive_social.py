# Import necessary modules and classes
from models.model import SocialData  # Import the SocialData model
from bson import ObjectId  # Import ObjectId for MongoDB document ID handling
from routes.social.social_preprocess import process_social_data  # Import function to process social data
import json  # Import JSON for encoding data

# Custom JSON encoder to handle ObjectId serialization
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        # Convert ObjectId to string for JSON serialization
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

# Import MongoDB collection configuration for storing social data
from config.main_dashboard_db import socialDB_collection

# Asynchronous function to receive and process social media data
async def receive_social_data(social_message: SocialData):
    """
    Receives social media data, processes it, and stores it in the database.
    
    Args:
        social_message (SocialData): An instance of SocialData containing social media details.
    
    Returns:
        dict: A message indicating the success of the operation.
    """
    
    # Extract the date from the 'time' field (assumes ISO format with 'T')
    date_str = social_message.time.split("T")[0]
    
    # Check if there is already an entry in the database for the given date
    existing_data = socialDB_collection.find_one({"Date": date_str})

    # Process the incoming social data (convert to dictionary and calculate sentiment, etc.)
    processed_data = process_social_data(social_message.dict())

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
                entry['products'] == new_entry['products']
                )
    
    # If data for the date exists, check for duplicates before appending new data
    if existing_data:
        # Check if the processed data is already present in the existing data
        data_exists = any(is_duplicate(entry, processed_data) for entry in existing_data['data'])
        
        # If the data is not a duplicate, append it to the existing entry
        if not data_exists:
            existing_data['data'].append(processed_data)
            # Update the database with the new data
            socialDB_collection.update_one(
                {"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data}
            )
        
    else:
        # If no data exists for the given date, create a new entry
        print(f"No existing data found for date: {date_str}, creating new entry")
        new_data = {"Date": date_str, "data": [processed_data]}
        # Insert the new entry into the database
        socialDB_collection.insert_one(new_data)

    # Return a success message
    return {"message": "Social data received and processed successfully"}
