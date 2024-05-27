import pandas as pd

def lineChartFun(data):
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)
    
    # Convert the 'Date' column to datetime
    df["Date"] = pd.to_datetime(df['Date'])
    
    # Extract month and year information to create a new column for grouping
    df['Month_Year'] = df['Date'].dt.to_period('M')
    
    # Group by month and sentiment, and calculate counts
    grouped_data = df.groupby(['Month_Year', 'Sentiment']).size().unstack(fill_value=0)
    
    # Calculate total positive, negative, and neutral counts for each month
    grouped_data['Total_Positive'] = grouped_data.get(4, 0)
    grouped_data['Total_Negative'] = grouped_data.get(0, 0)
    grouped_data['Total_Neutral'] = grouped_data.get(2, 0)
    
    # Reset index to make the Date column accessible
    grouped_data = grouped_data.reset_index()
    
    # Convert to JSON format
    result = []
    for index, row in grouped_data.iterrows():
        month_year = row['Month_Year'].strftime('%B %Y')
        positive = row['Total_Positive']
        negative = row['Total_Negative']
        neutral = row['Total_Neutral']
        result.append({"Date": month_year, "positive": positive, "negative": negative, "neutral": neutral})
    
    return result
