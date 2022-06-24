import os
import datetime
import jwt
from config import DEFAULT_SETTINGS
from common import TokenEnum
from common.error_handling import NotAllowed

JWT_SECRET = os.getenv('JWT_SECRET', DEFAULT_SETTINGS.get("JWT_SECRET"))


def generate_token(payload: dict, activation_token: bool = False):
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
