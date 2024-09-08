from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


call_team = "mongodb+srv://ErandaAbewardhana:fq3FNNVZeCDqcuKQ@icsms.f7srrct.mongodb.net/?retryWrites=true&w=majority&appName=ICSMS"

# Create a new client and connect to the server
client_call_team = MongoClient(call_team, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client_call_team.admin.command('ping')
    print("Team call","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#fetch the collections
client_call_DB = client_call_team.Call_Recordings
call_collection = client_call_DB["analytics"]

