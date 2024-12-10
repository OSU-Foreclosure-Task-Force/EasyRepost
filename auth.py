from fastapi import FastAPI, Request, HTTPException
from config import APP_TOKEN


def register_authorization_middleware(app: FastAPI):
    @app.middleware("http")
    async def check_token(request: Request, call_next):
        token = request.headers.get("token")
        if token != APP_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid or missing token")
        response = await call_next(request)
        return response
