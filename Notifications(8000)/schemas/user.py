from fastapi import HTTPException
from datetime import datetime

def format_datetime(date_str):
    # Assuming date_str is in the format 'YYYY-MM-DDTHH:MM:SS'
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%B %d, %Y %I:%M %p")  # Format as 'Month day, Year HH:MM AM/PM'

def userEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "title": item["title"],
        "description": item["description"],
        "datetime": format_datetime(item["datetime"]),
        "sources": item["sources"],
        "status": item["status"]
    }


def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]


def serializeDict(item) -> dict:
    return {
        "_id": str(item["_id"]),
        "title": str(item["title"]),
        "description": str(item["description"]),
        "datetime": str(item["date"]),  # Accessing the date field inside the object
    }


def serializeList(entity) -> list:
    return [serializeDict(item) for item in entity]

def serializeDictcall(item) -> dict:
    return {
        "_id": str(item["_id"]),
        "title": str(item["title"]),
        "description": str(item["description"]),
        "datetime": str(item["datetime"]),
    }


def serializeListcall(entity) -> list:
    return [serializeDictcall(item) for item in entity]

# def serializeDict(a) -> dict:
#     return {
#         **{i: str(a[i]) for i in a if i == "_id"},
#         **{i: a[i] for i in a if i != "_id"},
#     }


# def serializeList(entity) -> list:
#     return [serializeDict(a) for a in entity]
