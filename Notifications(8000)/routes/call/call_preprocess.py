from bson import ObjectId

# Function to process call data and return structured information
def process_call_data(call_message,name):
    if(name=='call_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'call',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }
    if(name=='social_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'social',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }
