from datetime import datetime
import peewee

from ..database.database import db

class BaseModel(peewee.Model):
    class Meta: 
        database = db

class User(BaseModel):
    username = peewee.CharField(max_length=255)
    password = peewee.CharField(max_length=255)
    district_or_city = peewee.CharField(max_length=255)
    police_station = peewee.CharField(max_length=255)
    is_admin = peewee.BooleanField(default=False)
    createdAt = peewee.DateTimeField(default=datetime.now())

class LostFoundPerson(BaseModel):
    lost_person = peewee.CharField(max_length=255)
    image = peewee.CharField(max_length=255)
    contact_person_of_lost_person = peewee.CharField(max_length=255)
    ph_contact_person_of_lost_person = peewee.CharField(max_length=255)
    gd_or_case_number = peewee.CharField(max_length=255)
    enroll_officer_name = peewee.CharField(max_length=255)
    enroll_officer_bp_no = peewee.CharField(max_length=255)
    enroll_officer_ph_no = peewee.CharField(max_length=255)
    remarks = peewee.CharField(max_length=255)
    lost_or_found = peewee.BooleanField()
    owner = peewee.ForeignKeyField(User, on_delete="CASCADE")
    is_matched= peewee.BooleanField(default=False)
    createdAt = peewee.DateTimeField(default=datetime.now())

class MatchedPeople(BaseModel):
    lost = peewee.ForeignKeyField(LostFoundPerson, on_delete="CASCADE")
    found = peewee.ForeignKeyField(LostFoundPerson, on_delete="CASCADE")
    createdAt = peewee.DateTimeField(default=datetime.now())
    
class ResetPasswordToken(BaseModel):
    owner = peewee.ForeignKeyField(User, on_delete="CASCADE")
    token = peewee.CharField(index=True)
    createdAt = peewee.DateTimeField(default=datetime.now())
    isExpire = peewee.BooleanField(default=False)

class MailConfig(BaseModel):
    username= peewee.CharField()
    password= peewee.CharField()
    fromEmail = peewee.CharField()
    port= peewee.IntegerField()
    server= peewee.CharField()
    tls= peewee.BooleanField()
    ssl= peewee.BooleanField()
    use_credentials = peewee.BooleanField()
    validate_certs = peewee.BooleanField()

class TokenBlocklist(BaseModel):
    token = peewee.CharField()
    inserted_at = peewee.DateTimeField(default=datetime.now())