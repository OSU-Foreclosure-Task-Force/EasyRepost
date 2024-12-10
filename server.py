from fastapi import FastAPI
from auth import register_authorization_middleware
from config import APP_TOKEN
app = FastAPI()
if APP_TOKEN is not None:
    register_authorization_middleware(app)


