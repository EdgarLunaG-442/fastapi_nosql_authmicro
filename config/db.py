import os
from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database
from .default import DEFAULT_SETTINGS

MONGODB_URL = os.environ.get("MONGODB_URL", DEFAULT_SETTINGS["MONGODB_URL"])
client: MongoClient = MongoClient(MONGODB_URL)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


def get_db():
    db: Database = client.get_database('auth')
    yield db
