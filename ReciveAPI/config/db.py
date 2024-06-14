from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


emailDashboard = "mongodb+srv://Main-Dashboard:FE7esG7otgmcAYNi@shareddb.i3egqpc.mongodb.net/?retryWrites=true&w=majority&appName=SharedDB"

# Create a new client and connect to the server
client_emailDashboard = MongoClient(emailDashboard, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client_emailDashboard.admin.command('ping')
    print("Dashboard email","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client_emailDashboard.Email
emailDB_collection = db["GeneratedData"]

callDashboard = "mongodb+srv://Main-Dashboard:FE7esG7otgmcAYNi@shareddb.i3egqpc.mongodb.net/?retryWrites=true&w=majority&appName=SharedDB"

# Create a new client and connect to the server
client_callDashboard = MongoClient(callDashboard, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client_callDashboard.admin.command('ping')
    print("Dashboard call","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client_callDashboard.Call
callDB_collection = db["GeneratedData"]


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
call_collection = client_call_DB["analytics"]


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

read_EmailMessages_collection = client_Email_DB["EmailMessages"]
read_Inquiries_collection = client_Email_DB["Inquiries"]
read_Issues_collection = client_Email_DB["Issues"]