from pydantic import BaseModel, EmailStr, Field
import peewee
from pydantic.utils import GetterDict
from typing import Any, List
from cryptography.fernet import Fernet

key = b'4YVfLQinJYbQE27ZaSDtLmpsbI4OVQ32WaPpjCGB_9E='
fernet = Fernet(key)

class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        if key == 'password':
            return fernet.decrypt(bytes(res, 'utf-8')).decode()
        return res

class UserBase(BaseModel):
    username: str
    password: str
    
class User(UserBase):
    id: int
    password: str
    police_station: str
    district_or_city: str
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class UsersDetail(BaseModel):
    data: List[User]
    status: str
    current_page: int
    total_pages: int
    first_page: bool
    last_page: bool
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class EmailConfig(BaseModel):
    id: int
    username: str
    password: str
    fromEmail: str
    port: int
    server: str
    tls: bool
    ssl: bool
    use_credentials: bool
    validate_certs: bool
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class ChangePass(BaseModel):
    userId: int
    newPassword: str = Field(min_length=6)

class ChangePassRes(BaseModel):
    status: str
    message: str
    user: User