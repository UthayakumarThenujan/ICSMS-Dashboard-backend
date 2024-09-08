from pymongo import DESCENDING
import asyncio

# Importing data models for email, call, and social data as well as inquiries and issues
from models.model import EmailData, CallData, SocialData, Inquiry, Issue

# Importing collections for reading data from email, social, and call databases
from config.email_db import read_EmailMessages_collection, read_Inquiries_collection, read_Issues_collection
from config.social_db import social_Comment_collection, social_IdentifiedKeywords_collection, social_IdentifiedProducts_collection
from config.call_db import call_collection
from config.main_dashboard_db import callDB_collection, emailDB_collection, socialDB_collection

# Importing functions to handle API requests for processing email, call, and social data
from routes.call.receive_call import receive_call_data
from routes.email.receive_email import receive_email_data
from routes.social.receive_social import receive_social_data

# Importing a function to calculate the average sentiment score for social media posts
from socialMediaAveScore import calculate_avg_s_score

# Function to get the latest date from the collection based on the date_field
def get_latest_date(collection, date_field):
    latest_document = collection.find_one(sort=[(date_field, DESCENDING)])
    if latest_document and date_field in latest_document:  
        return latest_document[date_field]
    return None 

# Asynchronous function to process initial documents from the databases
async def process_initial_documents():

    # Function to process email messages that are newer than the latest_date
    async def process_email(latest_date):
        query = {"datetime": {"$gte": latest_date}} if latest_date else {}  
        email_messages = read_EmailMessages_collection.find(query) 
        for message in email_messages:
            email_data = EmailData(  
                time=message["datetime"].isoformat(),
                our_sentiment_score=message["our_sentiment_score"],
                sender=message["sender"],
                topics=message["topics"],
            )
            await receive_email_data(email_data, 'email_messages')  

    # Function to process call data newer than the latest_date
    async def process_calls(latest_date):
        query = {"call_date": {"$gte": latest_date}} if latest_date else {}  
        call_messages = call_collection.find(query)  
        for message in call_messages:
            call_data = CallData(  
                _id=str(message["_id"]),
                call_id=message["call_id"],
                sentiment_category=message["sentiment_category"],
                keywords=message["keywords"],
                topics=message["topics"],
                summary=message["summary"],
                sentiment_score=message["sentiment_score"],
                call_date=message["call_date"].isoformat(),
            )
            await receive_call_data(call_data)

    # Function to process social media comments newer than the latest_date
    async def process_social_comments(latest_date):
        query = {"date": {"$gte": latest_date}} if latest_date else {}  
        projection = {"post_id": 1}  
        social_comments = social_Comment_collection.find(query, projection)  
        
        for comment in social_comments:
            if "post_id" in comment:
                post_id = comment["post_id"] 
                date_scores = await calculate_avg_s_score(post_id)
            if date_scores: 
                for date, score in date_scores.items():
                    social_data = SocialData( 
                        time=date.isoformat(),
                        our_sentiment_score=score,
                        keywords=[],
                        products=[]
                    )
                    await receive_social_data(social_data) 

    # Function to process social media keywords newer than the latest_date
    async def process_social_keywords(latest_date):
        query = {"date": {"$gte": latest_date}} if latest_date else {}  
        social_keywords = social_IdentifiedKeywords_collection.find(query) 
        for keyword in social_keywords:
            if "identified_keyword" in keyword:
                keywords = keyword["identified_keyword"]
                if not isinstance(keywords, list):
                    keywords = [keywords]

                social_data = SocialData( 
                    time=keyword["date"].isoformat(),
                    our_sentiment_score=0.0,
                    keywords=keywords,
                    products=[]
                )
                await receive_social_data(social_data) 
            else:
                print(f"Skipping document without 'identified_keyword': {keyword}")

    # Function to process social media products newer than the latest_date
    async def process_social_products(latest_date):
        query = {"date": {"$gte": latest_date}} if latest_date else {} 
        social_products = social_IdentifiedProducts_collection.find(query)
        for product in social_products:
            if "identified_product" in product:
                products = product["identified_product"]  
                if not isinstance(products, list):
                    products = [products] 

                social_data = SocialData( 
                    time=product["date"].isoformat(),
                    our_sentiment_score=0.0,
                    keywords=[],
                    products=products
                )
                await receive_social_data(social_data)  
            else:
                print(f"Skipping document without 'identified_product': {product}")

    # Function to process email issues newer than the latest_date
    async def process_email_issue(latest_date):
        query = {"start_time": {"$gte": latest_date}} if latest_date else {} 
        email_issues = read_Issues_collection.find(query)  
        for issue in email_issues:
            email_data = Issue( 
                time=issue["start_time"].isoformat(),
                status=issue["status"],
                issue_type=issue["issue_type"],
                sentiment_score=issue["sentiment_score"],
                products=issue["products"],
            )
            await receive_email_data(email_data, 'email_issue')

    # Function to process email inquiries newer than the latest_date
    async def process_email_inquiry(latest_date):
        query = {"start_time": {"$gte": latest_date}} if latest_date else {} 
        email_inquiries = read_Inquiries_collection.find(query) 
        for inquiry in email_inquiries:
            email_data = Inquiry( 
                time=inquiry["start_time"].isoformat(),
                status=inquiry["status"],
                inquiry_type=inquiry["inquiry_type"],
                sentiment_score=inquiry["sentiment_score"],
                products=inquiry["products"]
            )
            await receive_email_data(email_data, 'email_inquiry') 

    # Get the latest dates from the email, call, and social collections
    latest_email_date = get_latest_date(emailDB_collection, "datetime")
    latest_call_date = get_latest_date(callDB_collection, "call_date")
    latest_social_date = get_latest_date(socialDB_collection, "date")

    # Gather the processing tasks for email, call, and social data concurrently
    await asyncio.gather(
        process_email(latest_email_date),
        process_calls(latest_call_date),
        process_social_comments(latest_social_date),
        process_social_keywords(latest_social_date),
        process_social_products(latest_social_date),
        process_email_issue(latest_email_date),
        process_email_inquiry(latest_email_date)
    )
