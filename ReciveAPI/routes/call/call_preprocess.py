# Import the function to calculate sentiment based on the sentiment score
from routes.sentiment_tagging import calculate_sentiment

# Function to process call data and return structured information
def process_call_data(call_message):
    """
    Processes the call data message to extract relevant information 
    such as time, sentiment, keywords, and topics.
    
    Args:
        call_message (dict): A dictionary containing details of the call message 
                             such as sentiment score, call date, keywords, and topics.
    
    Returns:
        dict: A dictionary containing processed information including time of the call, 
              calculated sentiment, sentiment score, keywords, and topics.
    """
    
    # Calculate the sentiment from the sentiment score
    sentiment = calculate_sentiment(call_message['sentiment_score'])
    
    # Return the structured data
    return {
        "time": call_message['call_date'],  # Call date and time
        "Sentiment": {sentiment: call_message['sentiment_score']},  # Sentiment with score
        "keywords": call_message['keywords'],  # Keywords extracted from the call
        "topic": call_message['topics'],  # Topics discussed in the call
    }
