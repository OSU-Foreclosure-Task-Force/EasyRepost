from fastapi import FastAPI
from auth import register_authorization_middleware
from config import APP_TOKEN

app = FastAPI()

if APP_TOKEN is not None:
    register_authorization_middleware(app)

from route.subscription import subscription_router

app.include_router(subscription_router)

from route.download import download_router

app.include_router(download_router)

from route.upload import upload_router

app.include_router(upload_router)
