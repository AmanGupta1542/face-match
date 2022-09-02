from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .admin import main as admin_root
from .user import main as user_root

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:4200",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.mount("/api", user_root.app)
app.mount("/admin", admin_root.app)

app.mount("/staticfiles", StaticFiles(directory="staticfiles"), name="staticfiles")