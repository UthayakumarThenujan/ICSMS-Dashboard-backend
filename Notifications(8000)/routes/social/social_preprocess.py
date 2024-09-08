from bson import ObjectId

# Function to process social media data and return a structured dictionary

def process_social_data(call_message,name):
    if(name=='social_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'social',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }
