import bcrypt
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any, Union
from bson import ObjectId
from fastapi.security import OAuth2PasswordRequestForm


class PhoneSchema(BaseModel):
    indicative: str
    number: str


class SignInUserSchema(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: str
    phones: List[PhoneSchema]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class LogInUserSchema(BaseModel):
    email: EmailStr = Field(..., alias='username')
    password: str = Field(...)

    def verify_pass(self, obt_pass: str):
        return bool(bcrypt.checkpw(self.password.encode('utf-8'), obt_pass.encode('utf-8')))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True
