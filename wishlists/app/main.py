from fastapi import FastAPI
from app.endpoints.wishlist_router import wishlist_router

app = FastAPI(title="Wishlists Service")

app.include_router(wishlist_router, prefix="/api")
