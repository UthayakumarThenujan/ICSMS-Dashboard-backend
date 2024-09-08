from collections import defaultdict
from pymongo import MongoClient
from bson import ObjectId

from config.social_db import (
    social_Comment_collection,
    social_SubComment_collection,
    social_CommentSentiment_collection,
    social_SubCommentSentiment_collection
)

comment_sentiment_threshold = 0.7
sub_comment_sentiment_threshold = 0.4


async def calculate_avg_s_score(post_id: ObjectId) -> dict:
    """
    Calculate the average sentiment score for comments and sub-comments associated with a specific post on a daily basis.

    Args:
        post_id (ObjectId): The unique identifier of the post for which the sentiment analysis is performed.

    Returns:
        dict: A dictionary where the keys are dates, and the values are the average sentiment scores for comments and sub-comments on those dates.
    """

    # Retrieve all comments for the given post
    comments = list(social_Comment_collection.find({"post_id": post_id}))
    comment_ids = [comment["_id"] for comment in comments]

    # Retrieve sentiment scores for all comments
    comment_sentiments = list(social_CommentSentiment_collection.find({"comment_id": {"$in": comment_ids}}))

    # Retrieve all sub-comments for the given comments
    sub_comments = list(social_SubComment_collection.find({"comment_id": {"$in": comment_ids}}))
    sub_comment_ids = [sub_comment["_id"] for sub_comment in sub_comments]

    # Retrieve sentiment scores for all sub-comments
    sub_comment_sentiments = list(social_SubCommentSentiment_collection.find({"sub_comment_id": {"$in": sub_comment_ids}}))

    # Dictionary to hold sentiments grouped by date
    sentiment_by_date = defaultdict(list)

    # Process comment sentiments
    for comment in comments:
        comment_id = comment["_id"]
        comment_date = comment["date"]
        sentiment = next((cs["s_score"] for cs in comment_sentiments if cs["comment_id"] == comment_id), 0)
        sentiment_by_date[comment_date].append(sentiment * comment_sentiment_threshold)

    # Process sub-comment sentiments
    for sub_comment in sub_comments:
        sub_comment_id = sub_comment["_id"]
        sub_comment_date = sub_comment["date"]
        sentiment = next((scs["s_score"] for scs in sub_comment_sentiments if scs["sub_comment_id"] == sub_comment_id), 0)
        sentiment_by_date[sub_comment_date].append(sentiment * sub_comment_sentiment_threshold)

    # Calculate average sentiment by date
    avg_sentiment_by_date = {}
    for date, sentiments in sentiment_by_date.items():
        avg_sentiment_by_date[date] = sum(sentiments) / len(sentiments)

    return avg_sentiment_by_date
