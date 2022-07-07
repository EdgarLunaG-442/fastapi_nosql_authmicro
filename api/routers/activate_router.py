import os
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, decode_token, verify_token_payload, enviar_activacion
from common import TokenEnum, token_schema, AnyCode
from config import get_db
from models import AuthUserModel
from schemas import LogInUserSchema

PUBLISH_QUEUE = os.getenv('PUBLISH_QUEUE')
PUBLISH_EXCHANGE = os.getenv('PUBLISH_EXCHANGE')

activate_router = APIRouter(prefix="/auth/activate", tags=["Activate Account"])
logger = initiate_logger("activate")


@activate_router.put("/")
async def activate(token: HTTPAuthorizationCredentials = Depends(token_schema), db: Database = Depends(get_db)):
    '''Activa una cuenta'''
    collection: Collection = db.get_collection('AccesoUsuario')
    token_payload = decode_token(token.credentials)
    token_email = token_payload.get('email')
    user_dict_raw = verify_if_user_exists(collection, token_email, 'log_in')
    auth_user_model = AuthUserModel(**user_dict_raw)
    if auth_user_model.verified:
        raise AnyCode('Esta cuenta ya se encuentra verificada', 409)
    verify_token_payload(token_payload, TokenEnum.ACTIVATION, jsonable_encoder(auth_user_model))
    auth_user_model.update_mod_date()
    collection.update_one({'_id': auth_user_model.id},
                          {"$set": {'verified': True, 'modified_at': auth_user_model.modified_at}})
    return {"msg": f"La cuenta {token_email} fue activada correctamente"}


@activate_router.post("/send")
async def activate(user: LogInUserSchema, db: Database = Depends(get_db)):
    '''reenvia el correo de activacion'''
    return enviar_activacion(user, db, logger)
