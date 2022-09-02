from fastapi import APIRouter, HTTPException, status
from ..schemas import common as CSchemas
from typing import List
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from math import ceil

from ...user.models.common import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
key = b'4YVfLQinJYbQE27ZaSDtLmpsbI4OVQ32WaPpjCGB_9E='
fernet = Fernet(key)

router = APIRouter(
    # dependencies=[Depends(CDepends.get_db)],
    responses={404: {"description": "Not found"}},
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return fernet.encrypt(password.encode())

@router.get("/user-details", response_model=List[CSchemas.User])
def get_users(skip: int = 0, limit: int = 120):
    return list(User.select().offset(skip).limit(limit))

@router.get("/user-details-pagination/{page}", response_model=CSchemas.UsersDetail)
def get_users(page: int):
    row_limit = 2
    row_skip = 0 if page == 1 else row_limit*(page-1)
    data_records = User.select()
    total_pages = ceil(data_records.count()/row_limit)
    if data_records.count() <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No records available"
        ) 
    if page < 1 or page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Out of range",
        ) 

    return {
        "data": list(data_records.offset(row_skip).limit(row_limit).order_by(User.district_or_city)),
        "status": "success",
        "current_page": page,
        "total_pages": total_pages,
        "first_page": True if page == 1 else False,
        "last_page": True if total_pages == page else False
        }

def get_user_by_id(id: int):
    try:
        existing_user = User.get(User.id == id)
        return existing_user
    except:
        return False
    
def get_user_by_username(username: str):
    try:
        existing_user = User.get(User.username == username.strip())
        return existing_user
    except:
        return False

@router.get("/validate-username/{username}")
def validate_username(username: str):
    user = get_user_by_username(username)
    print(user)
    if user: 
        return {'status': 'error', 'message': 'Username already exist'}
    else:
        return {'status': 'success', 'message': 'Username is allowed'}


@router.patch("/change-user-password", response_model=CSchemas.ChangePassRes)
def change_password(data: CSchemas.ChangePass):
    
    user = get_user_by_id(data.userId)
    if user : 
        user.password = get_password_hash(data.newPassword)
        user.save()
        return {
            "status": "success", 
            "message": "Password changes successfully", 
            "user": {
                "username": user.username,
                "password": fernet.decrypt(user.password).decode(),
                "id": user.id,
                "police_station": user.police_station,
                "district_or_city": user.district_or_city
            }}
    else:
        print('else')
        raise HTTPException(status_code=404, detail="User not found")

