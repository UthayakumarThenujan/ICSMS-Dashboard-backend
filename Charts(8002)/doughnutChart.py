import pandas as pd

def doughnutChartFun(data):
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    # Count the occurrences of each sentiment value
    sentiment_counts = df['Sentiment'].value_counts()

    # Get the counts for each sentiment (0, 2, 4)
    total_positive = int(sentiment_counts.get(4, 0))
    total_negative = int(sentiment_counts.get(0, 0))
    total_neutral = int(sentiment_counts.get(2, 0))

    summaryTotal = {"negative": total_negative, "positive": total_positive, "neutral": total_neutral }
    return summaryTotal