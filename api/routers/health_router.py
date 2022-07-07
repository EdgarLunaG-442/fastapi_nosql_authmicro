from fastapi import APIRouter, Depends

health_router = APIRouter(prefix="/auth/health", tags=["Health Check"])


@health_router.get("/")
async def health():
    '''retorna 200 si el microservicio esta activo.'''
    return {"msg": "Auth alive!!!"}
