from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, generate_token
from config import get_db
from models import AuthUserModel
from schemas import SignInUserSchema

signin_router = APIRouter(prefix="/signin", tags=["Sign In"])
logger = initiate_logger("sign_in")


@signin_router.post("/")
async def sign_in(user: SignInUserSchema, db: Database = Depends(get_db)):
    '''Crea una instancia de usuario a partir de un email y contraseña dada'''
    collection: Collection = db.get_collection('authuser')
    verify_if_user_exists(collection, user)
    user_dict = user.dict()
    auth_user_model = AuthUserModel(**{k: v for k, v in user_dict.items() if k != "role"})
    auth_user_model.encrypt_pass()
    auth_user_model_dict = auth_user_model.dict()
    del auth_user_model_dict["id"]
    db_user_id = collection.insert_one(auth_user_model_dict).inserted_id
    db_user_dict = collection.find_one({"_id": db_user_id})
    out_user_model = jsonable_encoder(AuthUserModel(**db_user_dict))
    del out_user_model["password"]
    token = generate_token(out_user_model)
    return {"msg": f"el usuario {user.email} fue creado correctamente", "token": token}
