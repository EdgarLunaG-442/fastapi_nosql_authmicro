import bcrypt
from pydantic import BaseModel, Field, EmailStr
from config import PyObjectId
from bson import ObjectId
from common import RoleEnum


class AuthUserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(...)
    role: RoleEnum = Field(default=RoleEnum.USER)
    password: str = Field(...)

    def encrypt_pass(self):
        bytes_pass = self.password.encode('utf-8')
        self.password = bcrypt.hashpw(bytes_pass, bcrypt.gensalt(10)).decode('utf-8')

    def verify_pass(self, obt_pass: str):
        return bool(bcrypt.checkpw(self.password.encode('utf-8'), obt_pass.encode('utf-8')))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True
        json_encoders = {ObjectId: str}
