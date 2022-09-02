from math import ceil
from urllib import response
from fastapi import APIRouter, Depends, HTTPException, Path, status, Body,Form,  BackgroundTasks, Request, File, UploadFile
from fastapi_mail import FastMail, MessageSchema
from fastapi.requests import Request
from datetime import datetime, timedelta
from typing import List

from ..dependencies import common as CDepends
from ..schemas import common as CSchemas
from ..settings import config
from .operations import user_crud as UserO
from ..models import common as CModels

image= None
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(CDepends.get_db)],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=CSchemas.Token)
def login(login_data: CSchemas.LoginData = Body()):
    user = UserO.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = UserO.create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=config.settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/logout")
def logout(request: Request, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    try:
        CModels.TokenBlocklist(token=request.headers['Authorization'].split(' ')[-1].strip()).save()
        return {"status":"success", "message": "logout successful"}
    except:
        return {"status":"error", "message": "Internal server error"}

@router.get(
    "/profile", response_model=CSchemas.User, dependencies=[Depends(CDepends.get_db)]
)
def read_user(current_user: CSchemas.User = Depends(UserO.get_current_active_user)):
    db_user = UserO.get_user(current_user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/create", response_model=CSchemas.User, dependencies=[Depends(CDepends.get_db)])
def create_user(user: CSchemas.UserCreate):
    db_user = UserO.get_user(username=user.username.strip())
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return UserO.create_user(user=user)

@router.patch("/change-password")
def change_password(passwords: CSchemas.ChangePass, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    is_password = UserO.verify_password(passwords.oldPassword, current_User.password)
    if is_password : 
        current_User.password = UserO.get_password_hash(passwords.newPassword)
        current_User.save()
        return {"status": "success", "message": "Password changes successfully"}
    else:
        return {"status": "error", "message": "Old password is not correct"}


@router.post("/upload-person-data", response_model = CSchemas.LostFoundPerson1)
def upload_person_data(data: CSchemas.LostFoundPerson, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    return UserO.create_lost_person(data, current_User)
     
@router.get("/all-person-data/{page}", response_model= CSchemas.LostFoundPerson2)
def get_person_data(page: int, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    row_limit = 2
    row_skip = 0 if page == 1 else row_limit*(page-1)
    total_pages = ceil(CModels.LostFoundPerson.select().count()/row_limit)

    if page < 1 or page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Out of range",
        ) 
    
    return {
        "data": list(CModels.LostFoundPerson.select().offset(row_skip).limit(row_limit)),
        "status": "success",
        "current_page": page,
        "total_pages": ceil(CModels.LostFoundPerson.select().count()/row_limit),
        "first_page": True if page == 1 else False,
        "last_page": True if ceil(CModels.LostFoundPerson.select().count()/row_limit) == page else False
        }
        
@router.get("/lost-person-data/{page}", response_model= CSchemas.LostFoundPerson2)
def get_person_data(page: int, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    row_limit = 2
    row_skip = 0 if page == 1 else row_limit*(page-1)
    print('lost', ceil(CModels.LostFoundPerson.select().where(CModels.LostFoundPerson.lost_or_found==False).count()))
    total_pages = ceil(CModels.LostFoundPerson.select().where(CModels.LostFoundPerson.lost_or_found==False).count()/row_limit)

    if page < 1 or page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Out of range",
        ) 

    return {
        "data": list(CModels.LostFoundPerson.select().where(CModels.LostFoundPerson.lost_or_found==False).offset(row_skip).limit(row_limit)),
        "status": "success",
        "current_page": page,
        "total_pages": total_pages,
        "first_page": True if page == 1 else False,
        "last_page": True if total_pages == page else False
        }
        
@router.get("/found-person-data/{page}", response_model= CSchemas.LostFoundPerson2)
def get_person_data(page: int, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    row_limit = 2
    row_skip = 0 if page == 1 else row_limit*(page-1)
    total_pages = ceil(CModels.LostFoundPerson.select().where(CModels.LostFoundPerson.lost_or_found==True).count()/row_limit)
    print('found', ceil(CModels.LostFoundPerson.select().where(CModels.LostFoundPerson.lost_or_found==True).count()))
    if page < 1 or page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Out of range",
        ) 

    return {
        "data": list(CModels.LostFoundPerson.select().where(CModels.LostFoundPerson.lost_or_found==True).offset(row_skip).limit(row_limit)),
        "status": "success",
        "current_page": page,
        "total_pages": total_pages,
        "first_page": True if page == 1 else False,
        "last_page": True if total_pages == page else False
        }
    
    

@router.get("/unmatch-person-data/{page}", response_model= CSchemas.LostFoundPerson2)
def get_person_data(page: int, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    row_limit = 2
    row_skip = 0 if page == 1 else row_limit*(page-1)
    data_records = CModels.LostFoundPerson.select().where(CModels.LostFoundPerson.is_matched==False)
    total_pages = ceil(data_records.count()/row_limit)
    
    if data_records.count() <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No records available"
        ) 
    print('unmatched', ceil(data_records.count()))
    if page < 1 or page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Out of range",
        ) 

    return {
        "data": list(data_records.offset(row_skip).limit(row_limit)),
        "status": "success",
        "current_page": page,
        "total_pages": total_pages,
        "first_page": True if page == 1 else False,
        "last_page": True if total_pages == page else False
        }
    
@router.get("/match-person-data/{page}", response_model= CSchemas.MatchedPeople) # , response_model= CSchemas.MatchedPeople
def get_person_data(page: int, current_User: CSchemas.User = Depends(UserO.get_current_active_user)):
    row_limit = 2
    row_skip = 0 if page == 1 else row_limit*(page-1)
    data_records = CModels.MatchedPeople.select()
    print(data_records)
    total_pages = ceil(data_records.count()/row_limit)
    
    if data_records.count() <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No records available"
        ) 
    print('unmatched', ceil(data_records.count()))
    if page < 1 or page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Out of range",
        ) 
    return {
        "data": list(data_records.offset(row_skip).limit(row_limit)),
        "status": "success",
        "current_page": page,
        "total_pages": total_pages,
        "first_page": True if page == 1 else False,
        "last_page": True if total_pages == page else False
        }


@router.post("/uploadfile/{id}", response_model = CSchemas.LostFoundIPerson)
async def create_upload_file(id: int, image: UploadFile):
    dir_path = 'staticfiles/images/'
    person = UserO.insert_image(image.filename, id)
    with open (dir_path+image.filename, 'wb+') as f:
            f.write(image.file.read())

    # image matching step
    # is_matched = UserO.image_matching(dir_path+image.filename)

    return person