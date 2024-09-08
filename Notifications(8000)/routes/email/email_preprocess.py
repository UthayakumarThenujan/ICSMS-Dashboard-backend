from bson import ObjectId

# Function to process email data based on the type of email (message, inquiry, or issue)
def process_email_data(call_message,name):
    if(name=='email_messages'):
        return {
            "datetime": call_message['datetime'],
            "title": call_message['title'],
            "description": call_message['description'],
            'sources': 'email',
            '_id': ObjectId(call_message["id"]),
            'status': 'UNREAD'
        }
