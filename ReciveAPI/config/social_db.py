from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


social_team = "mongodb+srv://team-byte_bridges:backenddb@cluster0.pocr4yq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DBname= "icsms-social_media"
# Create a new client and connect to the server
client_social_team = MongoClient(social_team, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client_social_team.admin.command('ping')
    print("Team email","Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#fetch the collections
client_social_DB = client_social_team[DBname]
social_Comment_collection = client_social_DB["Comment"]
social_IdentifiedKeywords_collection = client_social_DB["IdentifiedKeywords"]
social_IdentifiedProducts_collection = client_social_DB["IdentifiedProducts"]

social_CommentSentiment_collection = client_social_DB["CommentSentiment"]
social_SubComment_collection = client_social_DB["SubComment"]
social_SubCommentSentiment_collection = client_social_DB["SubCommentSentiment"]