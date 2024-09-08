from bson import ObjectId
import json
from models.user import CallData
from dateutil import parser

from routes.call.receive_call import receive_call_data
from routes.email.receive_email import receive_email_data
from routes.social.receive_social import receive_social_data

# Custom JSON encoder class to handle ObjectId objects by converting them to strings
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        # Convert ObjectId to string
        if isinstance(o, ObjectId):
            return str(o)
        # For other types, use the default behavior
        return super(JSONEncoder, self).default(o)

# Asynchronous function to notify clients of a change in a collection document
async def notify_notification_clients_changed(collection, id, name, connected_clients):
    # Retrieve the changed document by its ObjectId from the collection
    changed_document = collection.find_one({"_id": ObjectId(id)})

    # If a changed document is found, proceed with the logic based on the collection name
    if changed_document:   
        # Handling "call" collection updates
        if name == "call":
            # Parse the datetime field and ensure it's in ISO format
            message_datetime = changed_document["datetime"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)

            # Create CallData object and send it using receive_call_data
            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(changed_document["_id"]),
                title=changed_document["title"],
                description=changed_document["description"],
            )
            await receive_call_data(call_data, 'call_messages')
        
        # Handling "email" collection updates
        if name == "email":
            # Parse the datetime field and ensure it's in ISO format
            message_datetime = changed_document["time"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)
                

            # Create CallData object and send it using receive_email_data
            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(changed_document["_id"]),
                title=changed_document["title"],
                description=changed_document["description"],
            )
            await receive_email_data(call_data, 'email_messages')
        
        # Handling "social" collection updates
        if name == "social":
            # Parse the datetime field and ensure it's in ISO format
            message_datetime = changed_document["date"]
            if isinstance(message_datetime, str):
                message_datetime = parser.isoparse(message_datetime)
                

            # Create CallData object and send it using receive_social_data
            call_data = CallData(
                datetime=message_datetime.isoformat(),
                id=str(changed_document["_id"]),
                title=changed_document["title"],
                description=changed_document["description"],
            )
            await receive_social_data(call_data, 'social_messages')

    # If the document change pertains to 'notifications', send a response to all connected clients
    if name == 'notifications':
        # Prepare a response message indicating a change and send it to each connected client
        message = json.dumps({"response": "change"}, cls=JSONEncoder)
        for client in connected_clients:
            await client.send_text(message)
