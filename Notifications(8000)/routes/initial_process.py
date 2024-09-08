from pymongo import DESCENDING
import asyncio

from models.user import CallData

# Importing collections for reading data from email, social, and call databases
from config.email_db import read_EmailMessages_collection
from config.social_db import social_Comment_collection
from config.call_db import call_collection
from config.main_dashboard_db import collection_name

# Importing functions to handle API requests for processing email, call, and social data
from routes.call.receive_call import receive_call_data
from routes.email.receive_email import receive_email_data
from routes.social.receive_social import receive_social_data

from schemas.user import serializeListcall
from dateutil import parser
import pytz

# Function to get the latest date from the collection based on the date_field
def get_latest_date_with_source(collection, date_field, source_field):
    projection = {date_field: 1, source_field: 1}
    latest_document = collection.find_one({"sources": source_field}, sort=[(date_field, DESCENDING)], projection=projection)
    
    # If a document is found, return a dictionary with the date and the source
    if latest_document:
        return {
            date_field: latest_document.get(date_field),
            source_field: latest_document.get(source_field)
        }
    
    # If no document is found, return None
    return None

# Asynchronous function to process initial documents from the databases
async def process_initial_documents():
    # print("Initial data analysis started")
    async def process_call(latest_date):
        if(latest_date):
            latest_date = parser.isoparse(latest_date).astimezone(pytz.utc)
            query = {"datetime": {"$gte": latest_date}} if latest_date else {}
            call_messages_cursor = serializeListcall(call_collection.find(query))
            call_messages = []
        else:
            call_messages_cursor = serializeListcall(call_collection.find())
            call_messages = []
        
        for message in call_messages_cursor:
            call_messages.append(message)

        for message in call_messages:
            # Convert the datetime string to a datetime object if necessary
            message_datetime = message["datetime"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)

            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(message["_id"]),
                title=message["title"],
                description=message["description"],
            )
            await receive_call_data(call_data, 'call_messages')



    async def process_social(latest_date):
        if(latest_date):
            latest_date = parser.isoparse(latest_date).astimezone(pytz.utc)
            query = {"date": {"$gte": latest_date}} if latest_date else {}
            social_messages_cursor = social_Comment_collection.find(query)
            social_messages = []
        else:
            social_messages_cursor = social_Comment_collection.find()
            social_messages = []
        
        for message in social_messages_cursor:
            social_messages.append(message)
        
        for message in social_messages:
            message_datetime = message["date"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)

            social_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(message["_id"]),
                title=message["title"],
                description=message["description"],
            )
            await receive_social_data(social_data, 'social_messages')

    async def process_email(latest_date):
            if(latest_date):
                latest_date = parser.isoparse(latest_date).astimezone(pytz.utc)
                query = {"time": {"$gte": latest_date}} if latest_date else {}
                social_messages_cursor = read_EmailMessages_collection.find(query)
                social_messages = []
            else:
                social_messages_cursor = read_EmailMessages_collection.find()
                social_messages = []
            
            for message in social_messages_cursor:
                social_messages.append(message)
            
            for message in social_messages:
                message_datetime = message["time"]
                if isinstance(message_datetime, str):
                    message_datetime = parser.isoparse(message_datetime)

                social_data = CallData(
                    datetime=message_datetime.isoformat(),
                    id=str(message["_id"]),
                    title=message["title"],
                    description=message["description"],
                )
                await receive_email_data(social_data, 'email_messages')

    call_latest_date = get_latest_date_with_source(collection_name, "datetime", 'call')
    social_latest_date = get_latest_date_with_source(collection_name, "datetime", 'social')
    email_latest_date = get_latest_date_with_source(collection_name, "datetime", 'email')

    await asyncio.gather(
        process_call(call_latest_date.get("datetime") if call_latest_date else None),
        process_social(social_latest_date.get("datetime") if social_latest_date else None),
        process_email(email_latest_date.get("datetime") if email_latest_date else None)
        
    )
