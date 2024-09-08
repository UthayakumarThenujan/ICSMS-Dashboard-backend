# Import the function to calculate sentiment from the sentiment_tagging module
from routes.sentiment_tagging import calculate_sentiment

# Function to process social media data and return a structured dictionary
def process_social_data(social_message):
    """
    Processes the incoming social media message and formats it into a structured dictionary.
    
    Args:
        social_message (dict): A dictionary containing social media message details such as time, sentiment score, keywords, and products.
    
    Returns:
        dict: A dictionary containing the processed social media data, including the calculated sentiment.
    """
    
    # Calculate the sentiment based on the 'our_sentiment_score' field in the social message
    sentiment = calculate_sentiment(social_message['our_sentiment_score'])
    
    # Return the processed data in a structured format
    return {
        "time": social_message['time'],  # Time of the social media message
        "Sentiment": {sentiment: social_message['our_sentiment_score']},  # Sentiment and its corresponding score
        "keywords": social_message['keywords'],  # Keywords extracted from the social media message
        "products": social_message['products']  # Products mentioned in the social media message
    }
