from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppErrorBaseClass(Exception):
    pass


class ObjectNotFound(AppErrorBaseClass):
    pass


class ObjectAlreadyExists(AppErrorBaseClass):
    pass


class NotAllowed(AppErrorBaseClass):
    pass


class NotReady(AppErrorBaseClass):
    pass


class NotAvailable(AppErrorBaseClass):
    pass


class AnyCode(AppErrorBaseClass):
    pass


def add_custom_errors(app: FastAPI):
    @app.exception_handler(AppErrorBaseClass)
    async def handle_exception_error(request: Request, exc: AppErrorBaseClass):
        return JSONResponse(status_code=500, content={"error": f"Internal server error, error: {exc}"})

    @app.exception_handler(ObjectNotFound)
    async def handle_404_error(request: Request, exc: ObjectNotFound):
        return JSONResponse(status_code=404, content={"error": exc.args[0]})

    @app.exception_handler(NotAllowed)
    async def handle_401_error(request: Request, exc: NotAllowed):
        return JSONResponse(status_code=401, content={"error": exc.args[0]})

    @app.exception_handler(ObjectAlreadyExists)
    async def handle_duplicates(request: Request, exc: ObjectAlreadyExists):
        return JSONResponse(status_code=409, content={"error": exc.args[0]})

    @app.exception_handler(NotAvailable)
    async def handle_503_error(request: Request, exc: NotAllowed):
        return JSONResponse(status_code=503, content={"error": f"{exc}"})

    @app.exception_handler(AnyCode)
    async def handle_any_error(request: Request, exc: AnyCode):
        return JSONResponse(status_code=exc.args[1], content={"error": f"{exc.args[0]}"})
