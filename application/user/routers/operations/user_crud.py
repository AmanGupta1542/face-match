from fastapi import Depends, HTTPException, status, UploadFile
from typing import Union
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi.security import HTTPBearer
import string, random

from ...settings.config import settings
from ...dependencies import common as CDepends
from ...models import common as CModel
from ...schemas import common as CSchemas

key = b'4YVfLQinJYbQE27ZaSDtLmpsbI4OVQ32WaPpjCGB_9E='
fernet = Fernet(key)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token_auth_scheme = HTTPBearer()

def reset_password_token(size=24, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def verify_password(plain_password, password):
    return fernet.decrypt(bytes(password, 'utf-8')).decode() == plain_password

def get_password_hash(password):
    return fernet.encrypt(password.encode())
   
def get_password_from_hash(hash):
    return fernet.decrypt(bytes(hash, 'utf-8')).decode()

def get_user(username: str):
    try:
        existing_user = CModel.User.get(CModel.User.username == username)
        return existing_user
    except:
        return False

def get_user_by_id(id: int):
    try:
        existing_user = CModel.User.get(CModel.User.id == id)
        return existing_user
    except:
        return False

def authenticate_user(username: str, password: str, dependencies=[Depends(CDepends.get_db)]):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta , None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(token_auth_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        if not CModel.TokenBlocklist.select().where(CModel.TokenBlocklist.token == token.credentials).count():
            payload = jwt.decode(token.credentials, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = CSchemas.TokenData(username=username)
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user == False:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: CSchemas.User = Depends(get_current_user)):
    # if not current_user.isActive:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_user(user: CSchemas.UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = CModel.User(
        username= user.username.strip(),
        password=fake_hashed_password.strip(),
        district_or_city= user.district_or_city.strip(),
        police_station= user.police_station.strip()
        )
    db_user.save()
    return db_user

def create_lost_person(data: CSchemas.LostFoundPerson, current_user):
    person = CModel.LostFoundPerson(**data.dict(), owner=current_user)
    person.save()
    return person

def insert_image(filename, id):
    person = CModel.LostFoundPerson.get(CModel.LostFoundPerson.id == id)
    person.image = f"http://127.0.0.1:8000/staticfiles/images/{filename}"
    person.save()
    return person