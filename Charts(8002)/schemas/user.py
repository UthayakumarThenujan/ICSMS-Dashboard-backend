from fastapi import HTTPException


def callEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "Sentiment": dict(item["Sentiment"]),
        "Date": str(item["Date"]),
        "ID": list(item["ID"]),
        "Word": list(item["Word"]),
    }


def callsEntity(entity) -> list:
    return [callEntity(item) for item in entity]

def WidgetsEntry(item) -> dict:
    return {
        "id": str(item["_id"]),
        "title": str(item["title"]),
        "chartType": str(item["chartType"]),
        "sources": item["sources"],
        "keywords": item["keywords"],
        "email": str(item["email"]),
        "grid": dict(item["grid"]),
    }


def WidgetEntry(entity) -> list:
    return [WidgetsEntry(item) for item in entity]