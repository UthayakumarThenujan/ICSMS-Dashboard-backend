from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from models.user import EmailData, CallData, SocialData,Inquiry,Issue
from datetime import datetime
from pymongo import DESCENDING
from config.db import (
    callDB_collection,
    emailDB_collection,
    read_EmailMessages_collection,
    call_collection,
    social_Comment_collection,
    social_SubComment_collection,
    socialDB_collection,
    social_IdentifiedKeywords_collection,
    social_IdentifiedProducts_collection,
    read_Inquiries_collection,
    read_Issues_collection
)
from schemas.user import usersEntity
from bson import ObjectId
import asyncio
import json

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/comments")
def get_all_comments():
    try:
        comments = usersEntity(social_Comment_collection.find())
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_sentiment(score):
    if score > 0.3:
        return "Positive"
    elif score < -0.3:
        return "Negative"
    else:
        return "Neutral"


def process_email_data(email_message,name):
    if(name=='email_messages'):
        sentiment = calculate_sentiment(email_message['our_sentiment_score'])
        return {
            "time": email_message['time'],
            "Sentiment": {sentiment: email_message['our_sentiment_score']},
            "sender": email_message['sender'],
            "topic": email_message['topics'],
        }
    elif(name=='email_inquiry'):
        sentiment = calculate_sentiment(email_message['sentiment_score'])
        return {
                    "time": email_message['time'],
                    "Sentiment": {sentiment: email_message['sentiment_score']},
                    "status": email_message['status'],
                    "inquiry_type": email_message['inquiry_type'],
                    "products":email_message['products']
                }
    elif(name=='email_issue'):
        sentiment = calculate_sentiment(email_message['sentiment_score'])
        return {
                    "time": email_message['time'],
                    "Sentiment": {sentiment: email_message['sentiment_score']},
                    "status": email_message['status'],
                    "issue_type": email_message['issue_type'],
                    "products":email_message['products']
                }

def process_call_data(call_message):
    sentiment = calculate_sentiment(call_message['sentiment_score'])
    return {
        "time": call_message['call_date'],
        "Sentiment": {sentiment: call_message['sentiment_score']},
        "keywords": call_message['keywords'],
        "topic": call_message['topics'],
    }


def process_social_data(social_message):
    sentiment = calculate_sentiment(social_message['our_sentiment_score'])
    return {
        "time": social_message['time'],
        "Sentiment": {sentiment: social_message['our_sentiment_score']},
        "keywords":social_message['keywords'],
        "products":social_message['products']
    }


async def receive_email_data(email_message: EmailData,name):
    date_str = email_message.time.split("T")[0]
    existing_data = emailDB_collection.find_one({"Date": date_str})
    processed_data = process_email_data(email_message.dict(),name)

    def is_duplicate(entry, new_entry):
        if(name=='email_messages'):
            return {
                entry['time']== new_entry['time'] and
                entry["Sentiment"]== new_entry['Sentiment'] and
                entry["sender"]== new_entry['sender'] and 
                entry["topic"]== new_entry['topic']
            }
        elif(name=='email_inquiry'):
            return {
                entry['time']== new_entry['time'] and
                entry["Sentiment"]== new_entry['Sentiment'] and
                entry["status"]== new_entry['status'] and 
                entry["inquiry_type"]== new_entry['inquiry_type'] and
                entry["products"]== new_entry['products']
                    }
        elif(name=='email_issue'):
            return {
                entry['time']== new_entry['time'] and
                entry["Sentiment"]== new_entry['Sentiment'] and
                entry["status"]== new_entry['status'] and 
                entry["issue_type"]== new_entry['issue_type'] and
                entry["products"]== new_entry['products']
                    }

    if existing_data:
        data_exists = any(is_duplicate(entry, processed_data) for entry in existing_data['data'])
        if not data_exists:
            print("email data added")
            existing_data['data'].append(processed_data)
            emailDB_collection.update_one(
                {"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data}
            )
            
    else:
        new_data = {"Date": date_str, "data": [processed_data]}
        emailDB_collection.insert_one(new_data)

    return {"message": "Email data received and processed successfully"}


async def receive_call_data(call_message: CallData):
    date_str = call_message.call_date.split("T")[0]
    existing_data = callDB_collection.find_one({"Date": date_str})

    processed_data = process_call_data(call_message.dict())

    def is_duplicate(entry, new_entry):
        return (entry['time'] == new_entry['time'] and
                entry['keywords'] == new_entry['keywords'] and
                entry['Sentiment'] == new_entry['Sentiment'] and
                entry['topic'] == new_entry['topic']
                )
    
    if existing_data:
        data_exists = any(is_duplicate(entry, processed_data) for entry in existing_data['data'])
        if not data_exists:
            print("call data added")
            existing_data['data'].append(processed_data)
            callDB_collection.update_one(
            {"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data}
        )
        
    else:
        new_data = {"Date": date_str, "data": [processed_data]}
        callDB_collection.insert_one(new_data)

    return {"message": "Call data received and processed successfully"}


async def receive_social_data(social_message: SocialData):
    date_str = social_message.time.split("T")[0]
    existing_data = socialDB_collection.find_one({"Date": date_str})

    processed_data = process_social_data(social_message.dict())

    def is_duplicate(entry, new_entry):
        return (entry['time'] == new_entry['time'] and
                entry['keywords'] == new_entry['keywords'] and
                entry['Sentiment'] == new_entry['Sentiment'] and
                entry['products'] == new_entry['products']
                )

    if existing_data:
        data_exists = any(is_duplicate(entry, processed_data) for entry in existing_data['data'])
        if not data_exists:
            print("social data added")
            existing_data['data'].append(processed_data)
            socialDB_collection.update_one(
            {"_id": ObjectId(existing_data['_id'])}, {"$set": existing_data}
        )
        
    else:
        print(f"No existing data found for date: {date_str}, creating new entry")
        new_data = {"Date": date_str, "data": [processed_data]}
        socialDB_collection.insert_one(new_data)

    return {"message": "Social data received and processed successfully"}


connected_clients = []


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)


async def notify_clients(name):
    message = json.dumps({"response": "data", "name": name}, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)


async def widget_notify():
    message = json.dumps({"response": "widget"}, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)


def watch_collection_sync(collection_name, name, loop):
    collection = collection_name
    change_stream = collection.watch()
    print(f"Watching collection: {name}")
    for change in change_stream:
        print(f"Change detected in {collection_name}: {change}")
        if 'documentKey' in change and '_id' in change['documentKey']:
            changed_id = change['documentKey']['_id']
            print(f"Change ID: {changed_id}")
            asyncio.run_coroutine_threadsafe(
                process_changed_document(collection, changed_id, name), loop
            )


async def process_changed_document(collection, changed_id, name):
    print(f"Processing changed document: {changed_id} in {name}")
    changed_document = collection.find_one({"_id": ObjectId(changed_id)})

    if changed_document:
        print(f"Changed document found: {changed_document}")
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
        elif name == "email_messages":
            email_data = EmailData(
                time=changed_document["time"].isoformat(),
                our_sentiment_score=changed_document["our_sentiment_score"],
                sender=changed_document["sender"],
                topics=changed_document["topics"],
            )
            await receive_email_data(email_data,name)
        elif name == "email_inquiry":
            email_data = Inquiry(
                time=changed_document["start_time"].isoformat(),
                status=changed_document["status"],
                inquiry_type= changed_document["inquiry_type"],
                sentiment_score= changed_document["sentiment_score"],
                products=changed_document['prodcuts']
            )
            await receive_email_data(email_data)
        elif name == "email_issue":
            email_data = Issue(
                time=changed_document["start_time"].isoformat(),
                status=changed_document["status"],
                issue_type= changed_document["issue_type"],
                sentiment_score= changed_document["sentiment_score"],
                products=changed_document['products']
            )
            await receive_email_data(email_data)
        elif name == "social_comment" or name == "social_subcomment":
            print(changed_document["date"].isoformat())
            social_data = SocialData(
                time=changed_document["date"].isoformat(),
                our_sentiment_score=changed_document["s_score"],
                keywords=[],
                products=[]
            )
            await receive_social_data(social_data)
        elif name == "social_keywords":
            print(changed_document["date"].isoformat())
            keywords = changed_document["identified_keyword"]
            if not isinstance(keywords, list):
                keywords = [keywords]

            social_data = SocialData(
                time=changed_document["date"].isoformat(),
                our_sentiment_score=0.0,
                keywords=keywords,
                products=[]
            )
            await receive_social_data(social_data)
        elif name == "social_products":
            print(changed_document["date"].isoformat())
            products = changed_document["identified_product"]
            if not isinstance(products, list):
                products = [products]

            social_data = SocialData(
                time=changed_document["date"].isoformat(),
                our_sentiment_score=0.0,
                keywords=[],
                products=products
            )
            await receive_social_data(social_data)


async def watch_collection(collection_name, name, loop):
    await asyncio.get_running_loop().run_in_executor(None, watch_collection_sync, collection_name, name, loop)


def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def watch_all_collections(loop):
    tasks = [
        watch_collection(read_EmailMessages_collection, 'email_messages', loop),
        watch_collection(call_collection, 'call_data', loop),
        watch_collection(social_Comment_collection, "social_comment", loop),
        watch_collection(social_SubComment_collection, 'social_subcomment', loop),
        watch_collection(social_IdentifiedKeywords_collection, 'social_keywords', loop),
        watch_collection(social_IdentifiedProducts_collection, 'social_products', loop),
        watch_collection(read_Inquiries_collection, 'email_inquiry', loop),
        watch_collection(read_Issues_collection, 'email_issue', loop),
    ]
    await asyncio.gather(*tasks)


def get_latest_date(collection, date_field):
    latest_document = collection.find_one(sort=[(date_field, DESCENDING)])
    if latest_document and date_field in latest_document:
        return latest_document[date_field]
    return None

# Updated process_initial_documents function
async def process_initial_documents():
    print("initial data analys started")
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

    async def process_social_comments(latest_date):
        query = {"date": {"$gte": latest_date}} if latest_date else {}
        social_comments = social_Comment_collection.find(query)
        for comment in social_comments:
            if "s_score" in comment:
                social_data = SocialData(
                    time=comment["date"].isoformat(),
                    our_sentiment_score=comment["s_score"],
                    keywords=[],
                    products=[]
                )
                await receive_social_data(social_data)

    async def process_social_subcomments(latest_date):
        query = {"date": {"$gte": latest_date}} if latest_date else {}
        social_subcomments = social_SubComment_collection.find(query)
        for subcomment in social_subcomments:
            if "s_score" in subcomment:
                social_data = SocialData(
                    time=subcomment["date"].isoformat(),
                    our_sentiment_score=subcomment["s_score"],
                    keywords=[],
                    products=[]
                )
                await receive_social_data(social_data)

    async def process_social_keywords(latest_date):
        query = {"date": {"$gte": latest_date}} if latest_date else {}
        social_keywords = social_IdentifiedKeywords_collection.find(query)
        for keyword in social_keywords:
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

    async def process_social_products(latest_date):
        query = {"date": {"$gte": latest_date}} if latest_date else {}
        social_products = social_IdentifiedProducts_collection.find(query)
        for product in social_products:
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

    async def process_email_issue(latest_date):
        query = {"start_time": {"$gte": latest_date}} if latest_date else {}
        email_issues = read_Issues_collection.find(query)
        for issue in email_issues:
            email_data = Issue(
                time=issue["start_time"].isoformat(),
                status=issue["status"],
                issue_type=issue["issue_type"],
                sentiment_score=issue["sentiment_score"],
                products=issue["products"]
            )
            await receive_email_data(email_data, 'email_issue')

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

    # Get the latest dates
    latest_email_date = get_latest_date(emailDB_collection, "datetime")
    latest_call_date = get_latest_date(callDB_collection, "call_date")
    latest_social_date = get_latest_date(socialDB_collection, "date")
    # latest_social_subcomment_date = get_latest_date(social_SubComment_collection, "date")
    # latest_social_keyword_date = get_latest_date(social_IdentifiedKeywords_collection, "date")
    # latest_social_product_date = get_latest_date(social_IdentifiedProducts_collection, "date")
    # latest_email_issue_date = get_latest_date(read_Issues_collection, "start_time")
    # latest_email_inquiry_date = get_latest_date(read_Inquiries_collection, "start_time")

    await asyncio.gather(
        process_email(latest_email_date),
        process_calls(latest_call_date),
        process_social_comments(latest_social_date),
        process_social_subcomments(latest_social_date),
        process_social_keywords(latest_social_date),
        process_social_products(latest_social_date),
        process_email_issue(latest_email_date),
        process_email_inquiry(latest_email_date)
    )