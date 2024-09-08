def calculate_sentiment(score):
    """
    Calculates the sentiment based on the given score.

    Args:
        score (float): The sentiment score to evaluate.

    Returns:
        str: The sentiment label ("Positive", "Negative", or "Neutral").
    """
    if score > 0.3:
        # If the score is greater than 0.3, classify as "Positive"
        return "Positive"
    elif score < -0.3:
        # If the score is less than -0.3, classify as "Negative"
        return "Negative"
    else:
        # If the score is between -0.3 and 0.3, classify as "Neutral"
        return "Neutral"
