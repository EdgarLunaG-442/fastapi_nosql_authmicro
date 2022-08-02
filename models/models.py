import bcrypt
from pydantic import BaseModel, Field, EmailStr, root_validator
from config import PyObjectId
from bson import ObjectId
from common import RoleEnum
from typing import Optional, List
import datetime


class AuthUserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    role: RoleEnum = Field(default=RoleEnum.USER)
    verified: bool = Field(default=False)
    active: bool = Field(default=True)
    created_at: datetime.datetime = Field(default=datetime.datetime.now(tz=datetime.timezone.utc))
    modified_at: datetime.datetime = Field(default=datetime.datetime.now(tz=datetime.timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(kwargs.get('role'), RoleEnum) and kwargs.get('role'):
            self.role = RoleEnum(kwargs.get('role'))

    def encrypt_pass(self):
        bytes_pass = self.password.encode('utf-8')
        self.password = bcrypt.hashpw(bytes_pass, bcrypt.gensalt()).decode('utf-8')

    def verify_pass(self, obt_pass: str):
        return bcrypt.checkpw(obt_pass.encode('utf-8'), self.password.encode('utf-8'))

    def update_mod_date(self):
        self.modified_at = datetime.datetime.now(tz=datetime.timezone.utc)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True
        json_encoders = {ObjectId: str}
