from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, decode_token, verify_token_payload, verify_admin_user
from common import TokenEnum, AnyCode, oauth2_scheme, ObjectNotFound
from config import get_db
from models import AuthUserModel

enable_account_router = APIRouter(prefix="/account-enable", tags=["Logic Account enable"])
logger = initiate_logger("account_commands")


@enable_account_router.put("/{user_id}")
async def habilitar_cuenta_objetivo(user_id: str, token=Depends(oauth2_scheme), db: Database = Depends(get_db)):
    '''Habilita un usuario objetivo modificando el estado de inactivo a activo.
    Una vez inactivo el usuario no podra loguearse'''
    collection: Collection = db.get_collection('AccesoUsuario')
    token_payload = decode_token(token)
    request_user_dict_raw = verify_if_user_exists(collection, token_payload.get('email'), 'log_in')
    request_auth_user_model = AuthUserModel(**request_user_dict_raw)
    request_auth_user_dict_after_model = jsonable_encoder(request_auth_user_model)
    verify_token_payload(token_payload, TokenEnum.LOGIN, request_auth_user_dict_after_model)
    verify_admin_user(token_payload)
    target_user_dict_raw = collection.find_one({"user_id": ObjectId(user_id)})
    if not target_user_dict_raw:
        raise ObjectNotFound('El usuario objetivo no existe.')
    target_user_model = AuthUserModel(**target_user_dict_raw)
    if not target_user_model.active:
        target_user_model.update_mod_date()
        target_user_model.active = True
        collection.update_one({'user_id': target_user_model.user_id},
                              {"$set": {'active': target_user_model.active,
                                        "modified_at": target_user_model.modified_at}})
        return {"msg": "La cuenta objetivo fue habilitada correctamente."}
    else:
        raise AnyCode('La cuenta objetivo ya se encuentra activa', 409)
