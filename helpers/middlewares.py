import base64
import json
import os
from schemas import LogInUserSchema
from common import ObjectAlreadyExists, ObjectNotFound, NotAllowed, TokenEnum, AnyCode, NotAvailable
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from config import get_db, DEFAULT_SETTINGS
from pymongo.collection import Collection
from models import AuthUserModel
from typing import List
from config import pika_client
from pika.exceptions import AMQPError
from .logger import print_exception

PUBLISH_QUEUE = os.getenv('PUBLISH_QUEUE', DEFAULT_SETTINGS.get('PUBLISH_QUEUE'))
PUBLISH_EXCHANGE = os.getenv('PUBLISH_EXCHANGE', DEFAULT_SETTINGS.get('PUBLISH_EXCHANGE'))


def delete_from_dict(payload: dict, unwanted_keys: List[str]):
    return dict([(key, value) for key, value in payload.items() if key not in unwanted_keys])


def verify_if_user_exists(collection: Collection, email: str, mode: str):
    found_user = collection.find_one({"email": email})
    if mode == "sign_in" and found_user:
        raise ObjectAlreadyExists(
            "Ya se encuentra registrado un usuario con ese email. Porfavor ingrese un correo alterno.")
    elif mode == "log_in" and not found_user:
        raise ObjectNotFound(f"No existe una cuenta asociada al correo {email}")
    elif mode == "log_in" and found_user:
        return found_user


def verify_if_user_verified(auth_user_model: AuthUserModel):
    if not auth_user_model.verified:
        raise NotAllowed('La cuenta no esta verificada')


def verify_password(user: AuthUserModel, password: str):
    if not user.verify_pass(password):
        raise NotAllowed("El correo o la contraseña no coinciden")


def verify_token_payload(token_payload: dict, token_type: TokenEnum, db_payload: dict = None):
    if token_payload.get('token_type', '') != token_type.value:
        raise NotAllowed('El Token no es valido. Porfavor ingrese un nuevo token')

    filtered_payload = delete_from_dict(token_payload, ['token_type'])
    filtered_db_payload = delete_from_dict(db_payload, ['password'])
    if db_payload and filtered_payload != filtered_db_payload:
        raise NotAllowed('El Token no es valido. Porfavor ingrese un nuevo token')


def enviar_activacion(user: LogInUserSchema, db: Database, logger, sign_in_step:bool = False):
    '''reenvia el correo de activacion'''
    collection: Collection = db.get_collection('AccesoUsuario')
    user_dict = verify_if_user_exists(collection, user.email, 'log_in')
    auth_user_model = AuthUserModel(**user_dict)
    if auth_user_model.verified:
        raise AnyCode('Esta cuenta ya se encuentra verificada', 409)
    verify_password(auth_user_model, user.password)
    out_user_dict = delete_from_dict(jsonable_encoder(auth_user_model), ['password'])
    b64_out_user = base64.b64encode(json.dumps(out_user_dict).encode('utf-8'))
    try:
        pika_client.channel.basic_publish(PUBLISH_EXCHANGE, PUBLISH_QUEUE, b64_out_user)
    except AMQPError as e:
        print_exception(logger, e)
        pika_client.reload_connection()
        if sign_in_step:
            raise AnyCode('La cuenta fue creada pero no se pudo enviar el correo de activación. Porfavor dirigase a '
                          'login, introduzca sus credenciales y siga las instrucciones ahi planteadas para enviar un '
                          'nuevo correo de activación. En caso del que el error persista, comuniquese con '
                          'soporte al usuario.', 201)
        else:
            raise NotAvailable('No se pudo enviar el correo de activación. Intente nuevamente en unos minutos')
    return {
        "msg": "Se envio el correo de activación. Espere unos minutos y revise su correo. "
               "En caso de que no encuentre el correo de activación, vuelva a repetir éste proceso."}
