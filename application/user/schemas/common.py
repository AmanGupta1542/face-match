from datetime import datetime
from fastapi import Body, File, Path, UploadFile
from pydantic import BaseModel, EmailStr, Field
import peewee
from cryptography.fernet import Fernet
from pydantic.utils import GetterDict
from typing import Any, Union, List

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

class TokenData(BaseModel):
    username: Union[str , None] = None

class LoginData(BaseModel):
    username: str
    password: str

class StatusSchema(BaseModel):
    status: str

class MessageSchema(StatusSchema):
    message: str

class ResetPassword(BaseModel):
    password: str = Field(
        title="Password of the user", min_length=6
    )

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    username: str
    password: str = Field(
        title="Password of the user", min_length=6
    )
    police_station: str
    district_or_city: str

class User(UserBase):
    id: int
    police_station: str
    district_or_city: str
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class ChangePass(BaseModel):
    oldPassword: str
    newPassword: str = Field(min_length=6)

class LostFoundPerson(BaseModel):
    lost_person: str
    contact_person_of_lost_person: str
    ph_contact_person_of_lost_person: str
    gd_or_case_number: str
    enroll_officer_name: str
    enroll_officer_bp_no: str
    enroll_officer_ph_no: str
    remarks: str
    lost_or_found: bool

class LostFoundPerson1(BaseModel):
    id: int
    lost_person: str
    contact_person_of_lost_person: str
    ph_contact_person_of_lost_person: str
    gd_or_case_number: str
    enroll_officer_name: str
    enroll_officer_bp_no: str
    enroll_officer_ph_no: str
    remarks: str
    lost_or_found: bool
    owner: User
    createdAt: datetime
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class LostFoundIPerson(BaseModel):
    id: int
    lost_person: str
    image: str
    contact_person_of_lost_person: str
    ph_contact_person_of_lost_person: str
    gd_or_case_number: str
    enroll_officer_name: str
    enroll_officer_bp_no: str
    enroll_officer_ph_no: str
    remarks: str
    lost_or_found: bool
    owner: User
    createdAt: datetime
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class GetLostFoundPeople(LostFoundPerson1):
    data: List[LostFoundPerson]

class LostFoundPerson2(BaseModel):
    data: List[LostFoundIPerson]
    status: str
    current_page: int
    total_pages: int
    first_page: bool
    last_page: bool
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class GetPeoples(BaseModel):
    lost_or_found: Union[bool, None]

class LostFound(BaseModel):
    id: int
    lost: LostFoundIPerson
    found: LostFoundIPerson
    createdAt: datetime
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class MatchedPeople(BaseModel):
    data: List[LostFound]
    current_page: int
    total_pages: int
    first_page: bool
    last_page: bool
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict