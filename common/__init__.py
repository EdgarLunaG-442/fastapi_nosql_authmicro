from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from .error_handling import add_custom_errors, AppErrorBaseClass, ObjectNotFound, ObjectAlreadyExists, NotAllowed, \
    NotReady, AnyCode, NotAvailable
from .cors_handling import handle_cors
from .enums import RoleEnum, TokenEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
token_schema = HTTPBearer()
