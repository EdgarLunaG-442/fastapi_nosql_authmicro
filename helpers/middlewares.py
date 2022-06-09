from pymongo.collection import Collection
from schemas import SignInUserSchema
from common.error_handling import ObjectAlreadyExists


def verify_if_user_exists(collection: Collection, user: SignInUserSchema):
    if collection.find_one({"email": user.email}):
        raise ObjectAlreadyExists(
            "Ya se encuentra registrado un usuario con ese email. Porfavor ingrese un correo alterno.")
