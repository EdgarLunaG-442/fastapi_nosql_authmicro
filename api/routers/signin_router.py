from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from bson import ObjectId
from helpers import initiate_logger, verify_if_user_exists, send_activation, delete_from_dict, generate_token
from config import get_db
from models import AuthUserModel
from schemas import SignInUserSchema, LogInUserSchema
from adapters.services import user_contact_service

signin_router = APIRouter(prefix="/signin", tags=["Sign In"])
logger = initiate_logger("sign_in")


@signin_router.post("/")
async def sign_in(user: SignInUserSchema, db: Database = Depends(get_db)):
    '''Crea una instancia de usuario a partir de un email y contraseña dada'''
    # Obtiene las colecciones de MongoDB
    user_auth_collection: Collection = db.get_collection('AccesoUsuario')
    # Dispara una excepción si el usuario ya existe
    verify_if_user_exists(user_auth_collection, user.email, 'sign_in')
    # Estructura el diccionario a guardar la informacion en sus respectivas colecciones
    user_dict = user.dict()
    user_dict_without_pass = delete_from_dict(user_dict, ['password'])
    user_contact_service.ping()
    code, response_data = user_contact_service.crear_contacto_usuario(generate_token(user_dict_without_pass))
    user_dict.update({"user_id": response_data.get('user_id')})
    # Crea el modelo a guardar en la coleccion de autenticacion y guarda su info en la BD
    auth_user_model = AuthUserModel(**user_dict)
    auth_user_model.encrypt_pass()
    user_auth_collection.insert_one(auth_user_model.dict(by_alias=True))
    # Crea el modelo para guardar en la coleccion de contacto y guarda su info en la BD
    send_activation(LogInUserSchema(**user.dict()), db, logger, True)
    return {"msg": f"el usuario {user.email} fue creado correctamente"}
