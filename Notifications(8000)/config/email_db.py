from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


email_team = "mongodb+srv://dasboardReadOnly:CqRRCjFAyItANHev@email.vm8njwj.mongodb.net/test?retryWrites=true&w=majority"

# Create a new client and connect to the server
client_email_team = MongoClient(email_team, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client_email_team.admin.command('ping')
    print("Team email","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

client_Email_DB = client_email_team.EmailDB
read_EmailMessages_collection = client_Email_DB["MainDashboardTriggerEvents"]
