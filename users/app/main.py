from fastapi import FastAPI
from app.endpoints.user_router import user_router

app = FastAPI(title="Users Service")

app.include_router(user_router, prefix="/api")
