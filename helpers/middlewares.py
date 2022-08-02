import base64
import json
import os
from typing import List
from config import pika_client
from pika.exceptions import AMQPError
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from pymongo.collection import Collection
from faker import Faker
import datetime

from schemas import LogInUserSchema
from common import ObjectAlreadyExists, ObjectNotFound, NotAllowed, TokenEnum, AnyCode, NotAvailable, RoleEnum
from models import AuthUserModel
from .logger import print_exception

ACTIVATION_QUEUE = os.getenv('ACTIVATION_QUEUE')
PASSWORD_RECOVERY_QUEUE = os.getenv('PASSWORD_RECOVERY_QUEUE')
PUBLISH_EXCHANGE = os.getenv('PUBLISH_EXCHANGE')

faker = Faker()


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

def verify_if_user_active(auth_user_model: AuthUserModel):
    if not auth_user_model.active:
        raise NotAllowed('Esta cuenta no está activa. Porfavor comuniquese con soporte al cliente')


def verify_password(user: AuthUserModel, password: str):
    if not user.verify_pass(password):
        raise NotAllowed("El correo o la contraseña no coinciden")


def verify_token_payload(token_payload: dict, token_type: TokenEnum, db_payload: dict = None):
    if token_payload.get('token_type', '') != token_type.value:
        raise NotAllowed('El Token no es valido. Porfavor ingrese un nuevo token')

    filtered_payload = delete_from_dict(token_payload, ['token_type'])
    filtered_db_payload = delete_from_dict(db_payload, ['password', 'active'])
    if db_payload and filtered_payload != filtered_db_payload:
        raise NotAllowed('El Token no es valido. Porfavor ingrese un nuevo token')


def verify_correct_user(token_payload: dict, user_id: str):
    if token_payload.get('user_id') != user_id:
        raise NotAllowed("No tiene los permisos para realizar ésta acción")


def verify_admin_user(token_payload: dict):
    if token_payload.get('role') != RoleEnum.ADMIN.value:
        raise NotAllowed("No tiene los permisos para realizar ésta acción")


def send_activation(user: LogInUserSchema, db: Database, logger, sign_in_step: bool = False):
    '''reenvia el correo de activacion'''
    auth_collection: Collection = db.get_collection('AccesoUsuario')
    contact_collection: Collection = db.get_collection('ContactoUsuario')
    auth_user_dict = verify_if_user_exists(auth_collection, user.email, 'log_in')
    contact_user_dict = verify_if_user_exists(contact_collection, user.email, 'log_in')
    auth_user_model = AuthUserModel(**auth_user_dict)
    if auth_user_model.verified:
        raise AnyCode('Esta cuenta ya se encuentra verificada', 409)
    verify_password(auth_user_model, user.password)
    extended_auth_user_dict = jsonable_encoder(auth_user_model)
    extended_auth_user_dict["name"] = contact_user_dict["name"]
    out_user_dict = delete_from_dict(extended_auth_user_dict, ['password', 'active'])
    b64_out_user = base64.b64encode(json.dumps(out_user_dict).encode('utf-8'))
    for i in list(range(10)):
        try:
            pika_client.channel.basic_publish(PUBLISH_EXCHANGE, ACTIVATION_QUEUE, b64_out_user)
            break
        except AMQPError as e:
            print_exception(logger, e)
            pika_client.reload_connection()
            if i == 9:
                if sign_in_step:
                    raise AnyCode(
                        'La cuenta fue creada pero no se pudo enviar el correo de activación. Porfavor dirigase a '
                        'login, introduzca sus credenciales y siga las instrucciones ahi planteadas para enviar un '
                        'nuevo correo de activación. En caso del que el error persista, comuniquese con '
                        'soporte al usuario.', 201)
                else:
                    raise NotAvailable('No se pudo enviar el correo de activación. Intente nuevamente en unos minutos')
    return {
        "msg": "Se envio el correo de activación. Espere unos minutos y revise su correo. "
               "En caso de que no encuentre el correo de activación, vuelva a repetir éste proceso."}


def verify_recovery_code(email: str, code: int, db: Database, logger):
    recovery_code_collection: Collection = db.get_collection('CodigoUsuario')
    user_code = verify_if_user_exists(recovery_code_collection, email, 'log_in')
    if not user_code or user_code.get('code') != code:
        raise NotAllowed('El código no es correcto. Porfavor ingrese uno nuevo.')
    elif user_code and user_code.get('code') == code and datetime.datetime.now(
            tz=datetime.timezone.utc) > user_code.get('exp').replace(tzinfo=datetime.timezone.utc):
        raise NotAllowed('El código ya no es valido. Porfavor ingrese uno nuevo.')


def send_recovery_code(email: str, db: Database, logger):
    '''reenvia el correo de activacion'''
    contact_collection: Collection = db.get_collection('ContactoUsuario')
    recovery_code_collection: Collection = db.get_collection('CodigoUsuario')
    contact_user_dict = verify_if_user_exists(contact_collection, email, 'log_in')
    user_code = recovery_code_collection.find_one({'email': email})
    contact_interest_keys = ["email", "name", "user_id"]
    recovery_payload = dict([(k, v) for k, v in contact_user_dict.items() if k in contact_interest_keys])
    recovery_code = faker.pyint(100000, 999999)
    recovery_payload['code'] = recovery_code
    recovery_payload['exp'] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=20)
    if not user_code:
        recovery_code_collection.insert_one(recovery_payload)
    else:
        recovery_code_collection.update_one({"email": recovery_payload.get('email')}, {
            "$set": delete_from_dict(recovery_payload, ["_id", *contact_interest_keys])})
    b64_recovery_code = base64.b64encode(
        json.dumps(delete_from_dict(recovery_payload, ["exp", "_id", "user_id"])).encode('utf-8'))
    for i in list(range(10)):
        try:
            pika_client.channel.basic_publish(PUBLISH_EXCHANGE, PASSWORD_RECOVERY_QUEUE, b64_recovery_code)
            break
        except AMQPError as e:
            print_exception(logger, e)
            pika_client.reload_connection()
            if i == 9:
                raise NotAvailable('No se pudo enviar el correo con el código de verificación. '
                                   'Porfavor intente mas tarde o comuniquese con servicio al cliente.')
    return {
        "msg": "Se envio código de verificación. Espere unos minutos y revise su correo. "
               "En caso de que no encuentre en su correo el código de activación, vuelva a repetir éste proceso."}
