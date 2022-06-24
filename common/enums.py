from enum import Enum


class RoleEnum(Enum):
    USER = 1
    SUPPORT = 2
    ADMIN = 3


class TokenEnum(Enum):
    LOGIN = 1
    ACTIVATION = 2
