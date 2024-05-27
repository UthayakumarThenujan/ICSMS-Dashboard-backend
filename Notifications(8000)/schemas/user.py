from fastapi import HTTPException


def userEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "email": item["email"],
        "alert": item["alert"],
        "status": item["status"],
        "created_at": item["created_at"]
        
    }


def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]


def serializeDict(item) -> dict:
    return {
         "id": str(item["_id"]),
        "email": item["email"],
        "alert": item["alert"],
        "status": item["status"],
        "created_at": item["created_at"]
    }


def serializeList(entity) -> list:
    return [serializeDict(item) for item in entity]


# def serializeDict(a) -> dict:
#     return {
#         **{i: str(a[i]) for i in a if i == "_id"},
#         **{i: a[i] for i in a if i != "_id"},
#     }


# def serializeList(entity) -> list:
#     return [serializeDict(a) for a in entity]
