from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, generate_token, verify_password, delete_from_dict, \
    verify_if_user_verified
from config import get_db
from models import AuthUserModel
from schemas import LogInUserSchema

login_router = APIRouter(prefix="/login", tags=["Log In"])
logger = initiate_logger("log_in")


@login_router.post("/")
async def log_in(user: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    '''Crea un token a partir de los parametros email y password, si estos son validos'''
    user = LogInUserSchema(**user.__dict__)
    collection: Collection = db.get_collection('AccesoUsuario')
    user_dict = verify_if_user_exists(collection, user.email, 'log_in')
    auth_user_model = AuthUserModel(**user_dict)
    verify_password(auth_user_model, user.password)
    verify_if_user_verified(auth_user_model)
    out_user_model = jsonable_encoder(auth_user_model)
    token = generate_token(jsonable_encoder(delete_from_dict(out_user_model, ['password'])))
    return {"access_token": token, "token_type": "bearer"}
