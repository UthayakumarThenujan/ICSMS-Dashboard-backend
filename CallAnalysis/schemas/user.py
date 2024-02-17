from fastapi import HTTPException


def callEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "TotalCall": int(item["TotalCall"]),
        "positive": int(item["positive"]),
        "negative": int(item["negative"]),
        "average": int(item["average"]),
    }


def callsEntity(entity) -> list:
    return [callEntity(item) for item in entity]
