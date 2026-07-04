from fastapi import HTTPException, status
from app.db import users_collection
from app.utils.security import hash_password, verify_password, create_access_token


async def signup_user(name: str, email: str, password: str) -> dict:
    existing = await users_collection.find_one({"email": email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    hashed = hash_password(password)
    result = await users_collection.insert_one(
        {"name": name, "email": email, "password_hash": hashed}
    )
    user_id = str(result.inserted_id)

    token = create_access_token(user_id)
    return {"access_token": token, "user_id": user_id, "name": name}


async def login_user(email: str, password: str) -> dict:
    user = await users_collection.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    user_id = str(user["_id"])
    token = create_access_token(user_id)
    return {"access_token": token, "user_id": user_id, "name": user["name"]}