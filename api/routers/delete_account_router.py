from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, decode_token, verify_token_payload, verify_admin_user
from common import TokenEnum, AnyCode, oauth2_scheme, ObjectNotFound, RoleEnum
from config import get_db
from models import AuthUserModel

delete_account_router = APIRouter(prefix="/account-delete", tags=["Logic Account Delete"])
logger = initiate_logger("account_commands")


@delete_account_router.delete("/")
async def eliminar_cuenta(token=Depends(oauth2_scheme),
                          db: Database = Depends(get_db)):
    '''Elimina el usuario modificando el estado de activo a inactivo. Una vez inactivo el usuario no podra loguearse'''
    collection: Collection = db.get_collection('AccesoUsuario')
    token_payload = decode_token(token)
    user_dict_raw = verify_if_user_exists(collection, token_payload.get('email'), 'log_in')
    auth_user_model = AuthUserModel(**user_dict_raw)
    auth_user_dict_after_model = jsonable_encoder(auth_user_model)
    verify_token_payload(token_payload, TokenEnum.LOGIN, auth_user_dict_after_model)
    auth_user_model.update_mod_date()
    auth_user_model.active = False
    collection.update_one({'user_id': auth_user_model.user_id}, {"$set": {'active': auth_user_model.active,
                                                                          "modified_at": auth_user_model.modified_at}})
    return {"msg": "La cuenta fue deshabilitada correctamente."}


@delete_account_router.delete("/{user_id}")
async def eliminar_cuenta_objetivo(user_id: str, token=Depends(oauth2_scheme), db: Database = Depends(get_db)):
    '''Elimina un usuario objetivo modificando el estado de activo a inactivo.
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
        raise AnyCode('El usuario objetivo ya se encuentra deshabilitado', 409)
    if target_user_model.role.value < RoleEnum.ADMIN.value:
        target_user_model.update_mod_date()
        target_user_model.active = False
        collection.update_one({'user_id': target_user_model.user_id},
                              {"$set": {'active': target_user_model.active,
                                        "modified_at": target_user_model.modified_at}})
        return {"msg": "La cuenta objetivo fue deshabilitado correctamente."}
    else:
        raise AnyCode('Un usuario administrador no puede deshabilitar a otro usuario administrador. '
                      'Comuniquese con el administrador del sistema en caso de ser necesario', 409)
