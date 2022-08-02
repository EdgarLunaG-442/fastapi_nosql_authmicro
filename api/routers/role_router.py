import os
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, decode_token, verify_token_payload, verify_admin_user
from common import TokenEnum, AnyCode, oauth2_scheme, RoleEnum, ObjectNotFound
from config import get_db
from models import AuthUserModel

role_router = APIRouter(prefix="/role", tags=["Role Commands"])
logger = initiate_logger("role_commands")


@role_router.put("/change/{user_id}")
async def cambiar_rol(user_id: str, new_role: int, token=Depends(oauth2_scheme), db: Database = Depends(get_db)):
    '''Modifica el rol del usuario. Solamente un usuario administrador puede realizar ésta acción'''
    collection: Collection = db.get_collection('AccesoUsuario')
    token_payload = decode_token(token)
    token_email = token_payload.get('email')
    request_user_dict_raw = verify_if_user_exists(collection, token_email, 'log_in')
    request_auth_user_model = AuthUserModel(**request_user_dict_raw)
    request_auth_user_dict_after_model = jsonable_encoder(request_auth_user_model)
    verify_token_payload(token_payload, TokenEnum.LOGIN, request_auth_user_dict_after_model)
    verify_admin_user(token_payload)
    try:
        new_role_enum = RoleEnum(new_role)
    except ValueError as e:
        raise AnyCode('No existe ese rol.', 409)
    target_user_dict_raw = collection.find_one({"user_id": ObjectId(user_id)})
    if not target_user_dict_raw:
        raise ObjectNotFound('El usuario objetivo no existe.')
    target_user_model = AuthUserModel(**target_user_dict_raw)
    if target_user_model.role != new_role_enum:
        if target_user_model.role == RoleEnum.ADMIN:
            raise AnyCode('Un usuario administrador no puede degradar a otro usuario administrador. '
                          'Comuniquese con el administrador del sistema en caso de ser necesario', 409)
        target_user_model.role = new_role_enum
        target_user_model.update_mod_date()
        collection.update_one({'user_id': ObjectId(user_id)}, {"$set": {'modified_at': target_user_model.modified_at,
                                                                        'role': target_user_model.role.value}})
        return {'msg': 'El usuario fue modificado correctamente.'}
    else:
        return {'msg': 'El usuario ya tiene ese rol'}
