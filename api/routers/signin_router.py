from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.collection import Collection
from helpers import initiate_logger, verify_if_user_exists, enviar_activacion
from config import get_db
from models import AuthUserModel, ContactUserModel
from schemas import SignInUserSchema, LogInUserSchema

signin_router = APIRouter(prefix="/auth/signin", tags=["Sign In"])
logger = initiate_logger("sign_in")


@signin_router.post("/")
async def sign_in(user: SignInUserSchema, db: Database = Depends(get_db)):
    '''Crea una instancia de usuario a partir de un email y contraseña dada'''
    # Obtiene las colecciones de MongoDB
    user_collection: Collection = db.get_collection('Usuario')
    user_auth_collection: Collection = db.get_collection('AccesoUsuario')
    user_contact_collection: Collection = db.get_collection('ContactoUsuario')

    # Dispara una excepción si el usuario ya existe
    verify_if_user_exists(user_collection, user.email, 'sign_in')
    verify_if_user_exists(user_auth_collection, user.email, 'sign_in')
    verify_if_user_exists(user_contact_collection, user.email, 'sign_in')

    # Estructura el diccionario a guardar la informacion en sus respectivas colecciones
    user_dict = user.dict()
    ref_user_id = user_collection.insert_one({'email': user.email}).inserted_id
    user_dict['user_id'] = ref_user_id

    # Crea el modelo a guardar en la coleccion de autenticacion y guarda su info en la BD
    auth_user_model = AuthUserModel(**user_dict)
    auth_user_model.encrypt_pass()
    user_auth_collection.insert_one(auth_user_model.dict(by_alias=True))
    # Crea el modelo para guardar en la coleccion de contacto y guarda su info en la BD
    contact_user_model = ContactUserModel(**user_dict)
    user_contact_collection.insert_one(contact_user_model.dict(by_alias=True))
    enviar_activacion(LogInUserSchema(**user.dict()), db, logger, True)
    return {"msg": f"el usuario {user.email} fue creado correctamente"}
