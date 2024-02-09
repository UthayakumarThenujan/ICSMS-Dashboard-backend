from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# con = MongoClient()

uri = "mongodb+srv://user01:user01@cluster0.btrm8ji.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
con = MongoClient(uri, server_api=ServerApi("1"))

# Send a ping to confirm a successful connection
try:
    con.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = con.user_db
collection_name = db["user_collection"]
