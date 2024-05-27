import random
from datetime import datetime


def createRespones():
    sentiments = {0: "negative", 2: "neutral", 4: "positive"}

    words = ["good", "bad", "super", "not good", "awesome", "terrible", "excellent", "poor", "great", "awful"]


    sentiment = random.choice(list(sentiments.keys()))
    date = datetime.now()
    word = random.choice(words)
    id_value = random.randint(1, 6000)       
    data = {
            "ID": id_value,
            "Sentiment": sentiment,
            "Date": date.strftime("%a %b %d %H:%M:%S PDT %Y"),
            "Word": word
        }
    return data


