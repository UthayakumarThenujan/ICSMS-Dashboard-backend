from fastapi import APIRouter
from models.user import (
    UpdateUser,
    LoginUser,
    SingupUser,
    Change_Password,
    ProfileUpdate,
)
from typing import Optional
from config.db import collection_name
from schemas.user import userEntity, usersEntity

# from bson import ObjectId

user = APIRouter(prefix="/authendication", tags=["authendication"])


@user.get("/")
async def find_all_users():
    return usersEntity(collection_name.find())


@user.get("/user/{email}")
async def user_get_from_email(email):
    return usersEntity(collection_name.find({"email": email}))


@user.delete("/{email}")
async def delete_user(email):
    userDetials = usersEntity(collection_name.find({"email": email}))
    if userDetials == []:
        return "Account not exist"
    else:
        userEntity(collection_name.find_one_and_delete({"email": email}))
        return "Deleted"


@user.post("/login")
async def User_Login(user: LoginUser):
    userDetials = usersEntity(collection_name.find({"$and": [dict(user)]}))

    if userDetials == []:
        return "Not username password Found"
    else:
        return userDetials


@user.post("/signup")
async def User_Singup(user: SingupUser):
    userDetials = usersEntity(collection_name.find({"email": user.email}))

    if userDetials == []:
        if user.password == user.ConPassword:
            collection_name.insert_one(dict(user))
            return "Account Created"
        else:
            return "Not match Password and Confirm Password"
    else:
        return "Account Already exist"


@user.put("/{email}/ChangePassword")
async def Change_Password(email, user: Change_Password):
    userDetials = usersEntity(collection_name.find({"email": email}))

    if userDetials != []:
        if user.password == user.ConPassword:
            if userDetials[0]["password"] == user.password:
                return "Try another password"
            else:
                collection_name.update_one({"email": email}, {"$set": dict(user)})
                return "Password Changed"
        else:
            return "Not match Password and Confirm Password"
    else:
        return "Account not exist"


@user.put("/{email}/ProfileUpdate")
async def Profile_Update(email, user: ProfileUpdate):
    userDetials = usersEntity(collection_name.find({"email": email}))

    if userDetials != []:
        collection_name.update_one({"email": email}, {"$set": dict(user)})
        return "Updated"
    else:
        return "Can't update"
