from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, decode_token, verify_token_payload, verify_if_user_exists, delete_from_dict
from config import get_db
from models import AuthUserModel
from helpers import generate_token
from common import oauth2_scheme, TokenEnum

sesion_router = APIRouter(prefix="/sesion", tags=["Sesion"])
logger = initiate_logger("sesion")


@sesion_router.post("/")
async def sesion(token: str = Depends(oauth2_scheme), db: Database = Depends(get_db)):
    '''Verifica la validez del token de sesion contra la Base de Datos'''
    collection: Collection = db.get_collection('AccesoUsuario')
    token_payload = decode_token(token)
    token_email = token_payload.get('email')
    user_dict_raw = verify_if_user_exists(collection, token_email, 'log_in')
    auth_user_model = AuthUserModel(**user_dict_raw)
    auth_user_dict_after_model = jsonable_encoder(auth_user_model)
    verify_token_payload(token_payload, TokenEnum.LOGIN, auth_user_dict_after_model)
    token = generate_token(auth_user_dict_after_model)
    return {"access_token": token, "token_type": "bearer"}


@sesion_router.get("/")
async def sesion(token: str = Depends(oauth2_scheme), db: Database = Depends(get_db)):
    '''Verifica la validez del token de sesion contra la Base de Datos'''
    collection: Collection = db.get_collection('AccesoUsuario')
    token_payload = decode_token(token)
    token_email = token_payload.get('email')
    user_dict_raw = verify_if_user_exists(collection, token_email, 'log_in')
    auth_user_model = AuthUserModel(**user_dict_raw)
    auth_user_dict_after_model = jsonable_encoder(auth_user_model)
    verify_token_payload(token_payload, TokenEnum.LOGIN, auth_user_dict_after_model)
    return {"msg": "Token valido"}
