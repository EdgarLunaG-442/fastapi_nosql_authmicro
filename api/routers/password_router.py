import os
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, decode_token, verify_token_payload, send_activation, \
    verify_correct_user, verify_password, delete_from_dict, generate_token, verify_recovery_code, send_recovery_code
from common import TokenEnum, token_schema, AnyCode, oauth2_scheme
from config import get_db
from models import AuthUserModel
from schemas import ChangePasswordSchema, RecoverPasswordSchema

password_router = APIRouter(prefix="/password", tags=["Password Commands"])
logger = initiate_logger("password_commands")


@password_router.put("/change/{user_id}")
async def cambiar(user_id: str,
                  passwords: ChangePasswordSchema,
                  token=Depends(oauth2_scheme),
                  db: Database = Depends(get_db)):
    '''Modifica la contraseña del usuario que viene como parametro'''
    collection: Collection = db.get_collection('AccesoUsuario')
    token_payload = decode_token(token)
    token_email = token_payload.get('email')
    user_dict_raw = verify_if_user_exists(collection, token_email, 'log_in')
    verify_correct_user(token_payload, user_id)
    auth_user_model = AuthUserModel(**user_dict_raw)
    auth_user_dict_after_model = jsonable_encoder(auth_user_model)
    verify_token_payload(token_payload, TokenEnum.LOGIN, auth_user_dict_after_model)
    verify_password(auth_user_model, passwords.old_password)
    if auth_user_model.verify_pass(passwords.new_password):
        raise AnyCode("La nueva contraseña no puede ser la utilizada actualmente.", 409)
    auth_user_model.password = passwords.new_password
    auth_user_model.encrypt_pass()
    auth_user_model.update_mod_date()
    auth_user_dict_after_model = dict(
        [(k, v) for k, v in jsonable_encoder(auth_user_model).items() if k in ["password", "modified_at"]])
    collection.update_one({'user_id': ObjectId(user_id)}, {"$set": auth_user_dict_after_model})
    token = generate_token(delete_from_dict(jsonable_encoder(auth_user_model), ['password']))
    return {"access_token": token, "token_type": "bearer"}


@password_router.put("/recover")
async def recuperar(recover_user: RecoverPasswordSchema, db: Database = Depends(get_db)):
    '''
    Modifica la contraseña del usuario una vez validado el código de verificación \n
    solo email: Envia el código de verificación.\n
    email, code y new_password: Verifica el código y modifica la contraseña.
    '''
    if recover_user.code and recover_user.new_password:
        verify_recovery_code(recover_user.email, recover_user.code, db, logger)
        auth_collection: Collection = db.get_collection('AccesoUsuario')
        auth_user_dict = verify_if_user_exists(auth_collection, recover_user.email, 'log_in')
        auth_user_model = AuthUserModel(**auth_user_dict)
        if auth_user_model.verify_pass(recover_user.new_password):
            raise AnyCode('La nueva contraseña debe ser distinta a la actual.', 409)
        auth_user_model.password = recover_user.new_password
        auth_user_model.encrypt_pass()
        auth_user_model.update_mod_date()
        auth_collection.update_one({'user_id': ObjectId(auth_user_model.user_id)},
                                   {"$set": {'password': auth_user_model.password,
                                             "modified_at": auth_user_model.modified_at}})
        return {"msg": "La contraseña fue cambiada exitosamente."}
    elif recover_user.code and not recover_user.new_password:
        raise AnyCode("Debe ingresar una nueva contraseña.", 409)
    elif recover_user.new_password and not recover_user.code:
        raise AnyCode("Debe ingresar un código de verificación.", 409)
    else:
        return send_recovery_code(recover_user.email, db, logger)
