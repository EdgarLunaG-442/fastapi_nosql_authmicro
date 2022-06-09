from fastapi import FastAPI
from .routers import signin_router
from common import add_custom_errors, handle_cors


def create_app():
    app = FastAPI()
    handle_cors(app)
    app.include_router(signin_router)
    add_custom_errors(app)
    return app
