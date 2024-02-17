from fastapi import APIRouter, Depends, status, Request
from fastapi.exceptions import HTTPException
from models.user import (
    AddNewUSer,
    LoginUser,
    SingupUser,
    Change_Password,
    ProfileUpdate,
)
from typing import Optional, List
from config.db import collection_name
from schemas.user import userEntity, usersEntity
from jwt_handler import signJWT, decodeJWT
from jwt_bearer import JWTBearer
from werkzeug.security import generate_password_hash, check_password_hash


current_user_payload: any

user = APIRouter(prefix="/authendication", tags=["authendication"])


def get_current_user_id(token: str = Depends(JWTBearer())):
    try:
        payload = decodeJWT(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid user ID in token")
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@user.get("/user/{email}")
async def user_get_from_email(email):
    return usersEntity(collection_name.find({"email": email}))


@user.delete("/{email}")
async def delete_user(email, current_user_id: str = Depends(get_current_user_id)):

    userDetials = usersEntity(collection_name.find({"email": email}))
    currentUser = usersEntity(collection_name.find({"email": current_user_id}))
    if userDetials == []:
        return "Account not exist"
    else:
        if "admin" in currentUser[0]["role"]:
            userEntity(collection_name.find_one_and_delete({"email": email}))
            return "Deleted"
        else:
            return "Admin Only can Delete"


@user.post("/login")
async def User_Login(user: LoginUser):

    userDetials = usersEntity(collection_name.find({"email": user.email}))
    if userDetials == []:
        return "Not username password Found"
    else:
        if check_password_hash(userDetials[0]["password"], user.password):
            current_user_payload = signJWT(user.email)
            return current_user_payload
        else:
            return "Password is not correct"


@user.post("/signup")
async def User_Singup(user: SingupUser):
    userDetials = usersEntity(collection_name.find({"email": user.email}))

    if userDetials == []:
        if user.password == user.conpassword:
            user.password = generate_password_hash(user.password)
            collection_name.insert_one(dict(user))
            return "Account Created"
        else:
            return "Not match Password and Confirm Password"
    else:
        return "Account Already exist"


@user.put("/{email}/ChangePassword")
async def Change_password(
    email, user: Change_Password, current_user_id: str = Depends(get_current_user_id)
):
    userDetials = usersEntity(collection_name.find({"email": email}))

    if userDetials != []:
        if user.password == user.conpassword:
            if check_password_hash(userDetials[0]["password"], user.password):
                return "Try another password"
            else:
                user.password = generate_password_hash(user.password)
                collection_name.update_one({"email": email}, {"$set": dict(user)})
                return "Password Changed"
        else:
            return "Not match Password and Confirm Password"
    else:
        return "Account not exist"


@user.put("/{email}/ProfileUpdate")
async def Profile_Update(
    email, user: ProfileUpdate, current_user_id: str = Depends(get_current_user_id)
):
    userDetials = usersEntity(collection_name.find({"email": email}))
    # return userDetials
    if userDetials != []:
        if user.name:
            collection_name.update_one({"email": email}, {"$set": {"name": user.name}})
        if user.contact:
            collection_name.update_one(
                {"email": email}, {"$set": {"contact": user.contact}}
            )
        if user.email:
            collection_name.update_one(
                {"email": email}, {"$set": {"email": user.email}}
            )
        if user.username:
            collection_name.update_one(
                {"email": email}, {"$set": {"username": user.username}}
            )
        return "Updated"
    else:
        return "Can't update"


@user.get("/appsettting/users")
async def all_users(current_user_id: str = Depends(get_current_user_id)):
    return usersEntity(collection_name.find())


@user.post("/appsettting/users/addnewusers")
async def addNewUser(
    user: AddNewUSer, current_user_id: str = Depends(get_current_user_id)
):
    currentUser = usersEntity(collection_name.find({"email": current_user_id}))
    userDetials = usersEntity(collection_name.find({"email": user.email}))
    userOrganization = currentUser[0]["organization"]
    user.organization = userOrganization

    if "admin" in currentUser[0]["role"]:
        if userDetials == []:
            if user.password == user.conpassword:
                user.password = generate_password_hash(user.password)
                collection_name.insert_one(dict(user))
                return "Account Created"
            else:
                return "Not match Password and Confirm Password"
        else:
            role = userDetials[0]["role"].copy()
            role = role.append(user.role[0])
            user.role = role
            collection_name.update_one({"email": user.email}, {"$set": dict(user)})
            return "Account Already exist, Profile Updated"
    else:
        return "Admin Only Create New Users"
