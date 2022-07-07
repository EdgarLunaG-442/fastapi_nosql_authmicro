from fastapi import FastAPI
from .routers import signin_router, sesion_router, login_router, health_router, activate_router
from common import add_custom_errors, handle_cors


def create_app():
    app = FastAPI(openapi_url="/auth/openapi.json", docs_url="/auth/documentation")
    handle_cors(app)
    app.include_router(signin_router)
    app.include_router(login_router)
    app.include_router(sesion_router)
    app.include_router(health_router)
    app.include_router(activate_router)
    add_custom_errors(app)
    return app
