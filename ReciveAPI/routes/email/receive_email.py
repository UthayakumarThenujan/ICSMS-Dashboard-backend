# Import necessary modules and classes
from models.model import EmailData  # Import the EmailData model
from routes.email.email_preprocess import process_email_data  # Import email data processing function
from config.main_dashboard_db import emailDB_collection  # Import MongoDB collection configuration
from bson import ObjectId  # Import ObjectId for MongoDB document ID handling
import json  # Import JSON for encoding data

# Custom JSON encoder to handle ObjectId serialization
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        # Convert ObjectId to string for JSON serialization
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

# Asynchronous function to receive and process email data
async def receive_email_data(email_message: EmailData, name: str):
    """
    Receives email data, processes it, and stores it in the database.
    
    Args:
        email_message (EmailData): An instance of EmailData containing email details.
        name (str): The type of email data ('email_messages', 'email_inquiry', 'email_issue').
    
    Returns:
        dict: A message indicating the success of the operation.
    """
    
    # Extract the date from the 'time' field (assumes ISO format with 'T')
    date_str = email_message.time.split("T")[0]
    
    # Check if there is already an entry in the database for the given date
    existing_data = emailDB_collection.find_one({"Date": date_str})

    # Process the incoming email data (convert to dictionary and calculate sentiment)
    processed_data = process_email_data(email_message.dict(), name)

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
        if name == 'email_messages':
            return (entry['time'] == new_entry['time'] and
                    entry["Sentiment"] == new_entry['Sentiment'] and
                    entry["sender"] == new_entry['sender'] and
                    entry["topic"] == new_entry['topic'] and
                    entry["inquiry_type"] == [] and
                    entry["issue_type"] == [] and
                    entry["products"] == [])
        
        elif name == 'email_inquiry':
            return (entry['time'] == new_entry['time'] and
                    entry["Sentiment"] == new_entry['Sentiment'] and
                    entry["status"] == new_entry['status'] and
                    entry["inquiry_type"] == new_entry['inquiry_type'] and
                    entry["products"] == new_entry['products'] and
                    entry["topic"] == [] and entry["issue_type"] == [])
        
        elif name == 'email_issue':
            return (entry['time'] == new_entry['time'] and
                    entry["Sentiment"] == new_entry['Sentiment'] and
                    entry["status"] == new_entry['status'] and
                    entry["issue_type"] == new_entry['issue_type'] and
                    entry["products"] == new_entry['products'] and
                    entry["topic"] == [] and entry["inquiry_type"] == [])
    
    # If data for the date exists, check for duplicates before appending new data
    if existing_data:
        # Check if the processed data is already present in the existing data
        data_exists = any(is_duplicate(entry, processed_data) for entry in existing_data['data'])
        
        # If the data is not a duplicate, append it to the existing entry
        if not data_exists:
            existing_data['data'].append(processed_data)
            # Update the database with the new data
            emailDB_collection.update_one(
                {"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data}
            )

    else:
        # If no data exists for the given date, create a new entry
        new_data = {"Date": date_str, "data": [processed_data]}
        # Insert the new entry into the database
        emailDB_collection.insert_one(new_data)

    # Return a success message
    return {"message": "Email data received and processed successfully"}
