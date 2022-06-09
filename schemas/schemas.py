from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List


class SignInUserSchema(BaseModel):
    name: Optional[str]
    age: Optional[int]
    addresses: Optional[List[str]]
    sex: Optional[str]
    email: EmailStr
    password: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
