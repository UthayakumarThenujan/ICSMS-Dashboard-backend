# Import necessary models and utilities
from models.model import EmailData, CallData, SocialData, Inquiry, Issue
from bson import ObjectId

# Import the functions that handle receiving data for different types
from routes.call.receive_call import receive_call_data
from routes.email.receive_email import receive_email_data
from routes.social.receive_social import receive_social_data

# Import the function to calculate average sentiment score for social media
from socialMediaAveScore import calculate_avg_s_score

import json

# JSON Encoder class to convert ObjectId to string for JSON serialization
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

# Asynchronous function to process a changed document in the specified collection
async def process_changed_document(collection, changed_id, name):
    """
    Processes the document with the given ID that has changed in the specified collection.
    Handles different types of data (calls, emails, social media) and routes them to the appropriate receiver functions.
    
    Args:
        collection (Collection): The MongoDB collection where the change occurred.
        changed_id (str): The ID of the changed document.
        name (str): The name representing the type of data (call_data, email_messages, social_comment, etc.)
    
    Returns:
        None
    """
    
    
    # Find the document with the changed ID in the given collection
    changed_document = collection.find_one({"_id": ObjectId(changed_id)})

    # Check if the document exists
    if changed_document:
        
        # If the changed document is call data, process it using CallData model and receive_call_data function
        if name == "call_data":
            call_data = CallData(
                _id=str(changed_document["_id"]),
                call_id=changed_document["call_id"],
                sentiment_category=changed_document["sentiment_category"],
                keywords=changed_document["keywords"],
                topics=changed_document["topics"],
                summary=changed_document["summary"],
                sentiment_score=changed_document["sentiment_score"],
                call_date=changed_document["call_date"].isoformat(),
            )
            await receive_call_data(call_data)
        
        # If the changed document is an email message, process it using EmailData model and receive_email_data function
        elif name == "email_messages":
            email_data = EmailData(
                time=changed_document["time"].isoformat(),
                our_sentiment_score=changed_document["our_sentiment_score"],
                sender=changed_document["sender"],
                topics=changed_document["topics"],
            )
            await receive_email_data(email_data, name)

        # If the changed document is an email inquiry, process it using Inquiry model and receive_email_data function
        elif name == "email_inquiry":
            email_data = Inquiry(
                time=changed_document["start_time"].isoformat(),
                status=changed_document["status"],
                inquiry_type= changed_document["inquiry_type"],
                sentiment_score= changed_document["sentiment_score"],
                products=changed_document['prodcuts']
            )
            await receive_email_data(email_data)

        # If the changed document is an email issue, process it using Issue model and receive_email_data function
        elif name == "email_issue":
            email_data = Issue(
                time=changed_document["start_time"].isoformat(),
                status=changed_document["status"],
                issue_type= changed_document["issue_type"],
                sentiment_score= changed_document["sentiment_score"],
                products=changed_document['products']
            )
            await receive_email_data(email_data)

        # If the changed document is a social media comment, calculate average sentiment score
        elif name == "social_comment":
            changed_id = changed_document["post_id"]
            # Call calculate_avg_s_score with the changed ID and get the date scores
            date_scores = await calculate_avg_s_score(changed_id)
            
            # Iterate over the date scores and create SocialData instances for each date
            for date, score in date_scores.items():
                social_data = SocialData(
                    time=date.isoformat(),
                    our_sentiment_score=score,
                    keywords=[],
                    products=[]
                )
                await receive_social_data(social_data)

        # If the changed document is related to social media keywords, process it accordingly
        elif name == "social_keywords":
            keywords = changed_document["identified_keyword"]
            
            # Ensure that keywords are a list
            if not isinstance(keywords, list):
                keywords = [keywords]

            social_data = SocialData(
                time=changed_document["date"].isoformat(),
                our_sentiment_score=0.0,
                keywords=keywords,
                products=[]
            )
            await receive_social_data(social_data)

        # If the changed document is related to social media products, process it accordingly
        elif name == "social_products":
            products = changed_document["identified_product"]
            
            # Ensure that products are a list
            if not isinstance(products, list):
                products = [products]

            social_data = SocialData(
                time=changed_document["date"].isoformat(),
                our_sentiment_score=0.0,
                keywords=[],
                products=products
            )
            await receive_social_data(social_data)
