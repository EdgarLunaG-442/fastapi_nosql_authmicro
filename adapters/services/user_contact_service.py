import os

from adapters import request_http

USER_CONTACT_MICRO_PATH = os.environ.get("USER_CONTACT_MICRO_PATH")


def ping():
    return request_http.get(f"{USER_CONTACT_MICRO_PATH}/health/")


def crear_contacto_usuario(token: str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }
    return request_http.post(f"{USER_CONTACT_MICRO_PATH}/", headers=headers)
