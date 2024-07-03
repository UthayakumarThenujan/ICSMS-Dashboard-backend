from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


uri = "mongodb+srv://Main-Dashboard:FE7esG7otgmcAYNi@shareddb.i3egqpc.mongodb.net/?retryWrites=true&w=majority&appName=SharedDB"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client.Notification
collection_name = db["Notifications"]



call_team = "mongodb+srv://erandaabewardhana:19765320@cluster0.7coezqv.mongodb.net/users?retryWrites=true&w=majority"

# Create a new client and connect to the server
client_call_team = MongoClient(call_team, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client_call_team.admin.command('ping')
    print("Team call","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

client_call_DB = client_call_team.call_recordings
call_collection = client_call_DB["notifications"]