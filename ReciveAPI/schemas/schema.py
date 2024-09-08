def userEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
    }

def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]




