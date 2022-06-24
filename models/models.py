import bcrypt
from pydantic import BaseModel, Field, EmailStr, root_validator
from config import PyObjectId
from bson import ObjectId
from common import RoleEnum
from typing import Optional, List
from datetime import datetime


class AuthUserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(...)
    email: EmailStr = Field(...)
    name: str = Field(...)
    password: str = Field(...)
    role: RoleEnum = Field(default=RoleEnum.USER)
    verified: bool = Field(default=False)
    created_at: str = Field(default=f'{datetime.utcnow()}')
    modified_at: str = Field(default=f'{datetime.utcnow()}')

    def encrypt_pass(self):
        bytes_pass = self.password.encode('utf-8')
        self.password = bcrypt.hashpw(bytes_pass, bcrypt.gensalt()).decode('utf-8')

    def verify_pass(self, obt_pass: str):
        return bcrypt.checkpw(obt_pass.encode('utf-8'), self.password.encode('utf-8'))

    def update_mod_date(self):
        self.modified_at = f'{datetime.utcnow()}'

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True
        json_encoders = {ObjectId: str}


class ContactUserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(...)
    name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    phones: List[dict] = Field(...)
    created_at: str = Field(default=f'{datetime.utcnow()}')
    modified_at: str = Field(default=f'{datetime.utcnow()}')
    addresses: Optional[List[dict]]
    cc: Optional[str]
    extras: Optional[dict]

    def update_mod_date(self):
        self.modified_at = f'{datetime.utcnow()}'

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
