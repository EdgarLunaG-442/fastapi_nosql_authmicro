import os
import datetime
import jwt
from common import TokenEnum
from common.error_handling import NotAllowed
from .middlewares import delete_from_dict

JWT_SECRET = os.getenv('JWT_SECRET')


def generate_token(payload: dict, activation_token: bool = False):
    payload = delete_from_dict(payload, ['password', 'active'])
    payload["token_type"] = TokenEnum.LOGIN.value
    payload["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
    if activation_token:
        payload["token_type"] = TokenEnum.ACTIVATION.value
        payload["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=3)
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        del payload["exp"]
        return payload
    except jwt.ExpiredSignatureError:
        raise NotAllowed("La sesion ha expirado, porfavor refresque el token")
    except jwt.InvalidSignatureError:
        raise NotAllowed("El token no es valido. Porfavor ingrese uno nuevo.")
