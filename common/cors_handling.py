from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def handle_cors(app: FastAPI):
    origins = [
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost",
        "http://localhost:8080",
        "http://0.0.0.0:8080",
        "http://0.0.0.0:8000",
        "http://0.0.0.0:80"
        "http://adael-project.info"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
