# Import the function to calculate sentiment based on sentiment score
from routes.sentiment_tagging import calculate_sentiment

# Function to process email data based on the type of email (message, inquiry, or issue)
def process_email_data(email_message, name):
    """
    Processes the email data based on the type of email (messages, inquiry, or issue).
    
    Args:
        email_message (dict): A dictionary containing details of the email.
        name (str): A string indicating the type of email data 
                    ('email_messages', 'email_inquiry', or 'email_issue').
    
    Returns:
        dict: A dictionary containing the processed email information.
    """
    
    # Handle email message processing
    if name == 'email_messages':
        sentiment = calculate_sentiment(email_message['our_sentiment_score'])
        return {
            "time": email_message['time'],  # Email time
            "Sentiment": {sentiment: email_message['our_sentiment_score']},  # Sentiment with score
            "sender": email_message['sender'],  # Email sender
            "topic": email_message['topics'],  # Topics related to the email
            "issue_type": [],  # No issue type for general messages
            "inquiry_type": [],  # No inquiry type for general messages
            "products": [],  # No products for general messages
        }
    
    # Handle email inquiry processing
    elif name == 'email_inquiry':
        sentiment = calculate_sentiment(email_message['sentiment_score'])
        return {
            "time": email_message['time'],  # Email time
            "Sentiment": {sentiment: email_message['sentiment_score']},  # Sentiment with score
            "status": email_message['status'],  # Inquiry status
            "issue_type": [],  # No issue type for inquiries
            "inquiry_type": email_message['inquiry_type'],  # Inquiry type
            "products": email_message['products'],  # Products related to the inquiry
            "topic": []  # No topic for inquiries
        }

    # Handle email issue processing
    elif name == 'email_issue':
        sentiment = calculate_sentiment(email_message['sentiment_score'])
        return {
            "time": email_message['time'],  # Email time
            "Sentiment": {sentiment: email_message['sentiment_score']},  # Sentiment with score
            "status": email_message['status'],  # Issue status
            "issue_type": email_message['issue_type'],  # Issue type
            "inquiry_type": [],  # No inquiry type for issues
            "products": email_message['products'],  # Products related to the issue
            "topic": []  # No topic for issues
        }
