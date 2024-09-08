from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


mainDashboard = "mongodb+srv://Main-Dashboard:FE7esG7otgmcAYNi@shareddb.i3egqpc.mongodb.net/?retryWrites=true&w=majority&appName=SharedDB"

# Create a new client and connect to the server
main_dashboard = MongoClient(mainDashboard, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    main_dashboard.admin.command('ping')
    print("Dashboard email","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


#fetch the collections
email_db = main_dashboard.Email
emailDB_collection = email_db["GeneratedData"]

call_db = main_dashboard.Call
callDB_collection = call_db["GeneratedData"]

social_db = main_dashboard.SocialMedia
socialDB_collection = social_db["GeneratedData"]
