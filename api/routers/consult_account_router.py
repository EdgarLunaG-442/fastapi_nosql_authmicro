import re
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, Body
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, decode_token, verify_token_payload, verify_admin_user, \
    delete_from_dict
from common import TokenEnum, oauth2_scheme, ObjectNotFound
from config import get_db
from models import AuthUserModel

consult_account_router = APIRouter(prefix="/account-consults", tags=["Account consults"])
logger = initiate_logger("account_consults")


def t_t_c_s(txt: str):
    """
    t_t_c_s stand for transform_to_common_str.

    transform to upper case and remove spaces from specific string

    :parameter txt: text before transformation
    :return new_text: text after transformation
    """
    new_text = re.sub(r'[\s]*', '', txt).lower()
    return new_text


@consult_account_router.post("/")
async def consultar_usuarios(max_entries: int = Body(5), search: str = Body(None), token=Depends(oauth2_scheme),
                             db: Database = Depends(get_db)):
    '''Retorna la información de autenticación del usuario objetivo a excepción de la contraseña'''
    auth_collection: Collection = db.get_collection('AccesoUsuario')
    contact_collection: Collection = db.get_collection('ContactoUsuario')
    token_payload = decode_token(token)
    request_user_dict_raw = verify_if_user_exists(auth_collection, token_payload.get('email'), 'log_in')
    request_auth_user_model = AuthUserModel(**request_user_dict_raw)
    request_auth_user_dict_after_model = jsonable_encoder(request_auth_user_model)
    verify_token_payload(token_payload, TokenEnum.LOGIN, request_auth_user_dict_after_model)
    verify_admin_user(token_payload)
    if not search:
        dict_raw_users = auth_collection.find().limit(max_entries)
        model_users = [AuthUserModel(**user) for user in dict_raw_users]
        return [delete_from_dict(jsonable_encoder(user), ['password']) for user in model_users]
    else:
        email_list = [e.get('email') for e in list(auth_collection.aggregate([{"$project": {"email": 1, "_id": 0}}]))]
        name_list = list(
            contact_collection.aggregate([{"$project": {"email": 1, "_id": 0, "name": 1, 'last_name': 1}}]))
        email_best_matches = list(filter(lambda e: t_t_c_s(search) in t_t_c_s(e), email_list))
        name_best_matches = list(
            filter(lambda e: t_t_c_s(search) in t_t_c_s(''.join([e.get('name'), e.get('last_name')])), name_list))
        email_name_best_matches = list(map(lambda u: u.get('email'), name_best_matches))
        best_matches = list(set([*email_best_matches, *email_name_best_matches]))
        if best_matches:
            best_matches_dict = list(auth_collection.find({'email': {'$in': best_matches}}).limit(max_entries))
            best_matches_model = [AuthUserModel(**match) for match in best_matches_dict]
            return [delete_from_dict(jsonable_encoder(user), ['password']) for user in best_matches_model]
        else:
            return []


@consult_account_router.get("/{user_id}")
async def consultar_usuario(user_id: str, token=Depends(oauth2_scheme), db: Database = Depends(get_db)):
    '''Retorna la información de autenticación del usuario objetivo a excepción de la contraseña'''
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
    return delete_from_dict(jsonable_encoder(target_user_model), ['password'])
