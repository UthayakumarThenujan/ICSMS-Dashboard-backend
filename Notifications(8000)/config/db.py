from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


uri = "mongodb+srv://Main-Dashboard:FE7esG7otgmcAYNi@shareddb.i3egqpc.mongodb.net/?retryWrites=true&w=majority&appName=SharedDB"

# Create a new client 
# and connect to the server
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



social_team = "mongodb+srv://team-byte_bridges:backenddb@cluster0.pocr4yq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DBname= "icsms-social_media"
# Create a new client and connect to the server
client_social_team = MongoClient(social_team, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client_social_team.admin.command('ping')
    print("Team social","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

client_social_DB = client_social_team[DBname]

social_Comment_collection = client_social_DB["Notification"]


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