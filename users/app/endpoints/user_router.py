from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Header
from app.services.user_service import UserService
from app.models.user import User
from app.models.friends import Friends
from app.dto.credentials import CredentialsRequest
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.jwt_client import JWTClient


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/register")
def register_user(
    request: CredentialsRequest,
    db: Session = Depends(get_db)
) -> User:
    user_service = UserService(db)
    try:
        return user_service.register_user(request.login, request.password)
    except KeyError as e:
        raise HTTPException(400, str(e))


@user_router.post("/login")
def authenticate_user(
    request: CredentialsRequest,
    db: Session = Depends(get_db)
) -> dict:
    try:
        user_service = UserService(db)
        return user_service.authenticate_user(request.login, request.password)
    except Exception as e:
        raise HTTPException(401, f"Auth error: {e}")


@user_router.post("/{friend_id}/friends")
def add_friend(
    friend_id: UUID,
    x_authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_db)
) -> Friends:
    try:
        user_service = UserService(db)
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)

        return user_service.add_friend(user_id, friend_id)
    except KeyError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(401, str(e))


@user_router.delete("/friends/{friend_id}")
def delete_friend(
    friend_id: UUID,
    x_authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_db)
) -> dict:
    user_service = UserService(db)
    try:
        user_service = UserService(db)
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        user_service.delete_friend(user_id, friend_id)
        return {"detail": f"Friendship between users {user_id} and {friend_id} deleted successfully"}
    except KeyError:
        raise HTTPException(404, f"Friendship between users {user_id} and {friend_id} not found")
    except Exception as e:
        raise HTTPException(401, str(e))


@user_router.get("/check_interests")
def check_interests(
    interests: str = Body(...),
    x_authorization: str = Header(..., description="Bearer token"),
) -> dict:
    # Извлечение токена из заголовка x_authorization
    if not x_authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid token format")
    
    return {"detail": f"Your interests: {interests}"}


@user_router.patch("/change_interests")
def change_interests(
    interests: str = Body(...),
    x_authorization: str = Header(..., description="Bearer token"),
) -> dict:
    # Извлечение токена из заголовка x_authorization
    if not x_authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid token format")
    return {"detail": f"Your changed interests: {interests}"}

@user_router.get("/{wishlist_id}")
def get_wishlist(
    wishlist_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    user_service = UserService(db)
    try:
        user_service.share_wishlist(wishlist_id)
    except KeyError:
        raise HTTPException(404, f"Wishlist {wishlist_id} not found")
    except:
        raise HTTPException(404, f"Wishlist {wishlist_id} not found")


@user_router.get("/{wishlist_id}/share")
def share_wishlist(
    wishlist_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    user_service = UserService(db)
    try:
        # из user_service делается запрос в wishlist_service
        # и проверяется, что wishlist с указанным id существует
        share_link = user_service.share_wishlist(wishlist_id)
        return {"share_link": share_link}
    except KeyError:
        raise HTTPException(404, f"Wishlist {wishlist_id} not found")