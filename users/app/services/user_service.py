from uuid import UUID, uuid4
from hashlib import sha256
from fastapi import HTTPException
from app.models.user import User
from sqlalchemy.orm import Session
from app.models.friends import Friends
from app.repositories.bd_user_repo import UserRepo
from app.repositories.bd_friends_repo import FriendsRepo
from app.database import get_db
import requests
import os

BASE_URL_WISHLIST_SERVICE = os.environ.get("BASE_URL_WISHLIST_SERVICE", "http://wishlists_service:8000")
BASE_URL_JWT_SERVICE = os.environ.get("JWT_SERVICE_BASE_URL", "http://jwt_service:8000")

class UserService:
    user_repo: UserRepo
    friends_repo: FriendsRepo

    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepo(db)
        self.friends_repo = FriendsRepo(db)

    def register_user(self, login: str, password: str) -> User:
        hashed_password = sha256(password.encode()).hexdigest()  # Захэшируем пароль
        user = User(
            id=uuid4(),
            login=login,
            hash_password=hashed_password
        )
        return self.user_repo.create_user(user)

    def authenticate_user(self, login: str, password: str) -> dict:
        hashed_password = sha256(password.encode()).hexdigest()
        try:
            user = self.user_repo.get_user_by_login(login)
            if user and user.hash_password == hashed_password:
                # Генерация токена через jwt_service
                token_response = requests.post(f"{BASE_URL_JWT_SERVICE}/token/{user.id}")
                if token_response.status_code == 200:
                    return token_response.json()
                else:
                    raise HTTPException(500, "Failed to generate token")
        except KeyError as e:
            raise HTTPException(404, e)
        except Exception as e:
            raise HTTPException(401, f"Invalid login or password {e}")

    def add_friend(self, user1_id: UUID, user2_id: UUID) -> Friends:
        friend = Friends(
            id=uuid4(),
            user1_id=user1_id,
            user2_id=user2_id
        )

        # проверяем существование друга
        user2 = self.user_repo.get_user_by_id(user2_id)
        if not user2:
            raise HTTPException(404, f"Friend with id: {user2_id} not found")

        return self.friends_repo.create_friend(friend)

    def delete_friend(self, user1_id: UUID, user2_id: UUID) -> None:
        friend = self.friends_repo.get_friend_by_users(user1_id, user2_id)
        self.friends_repo.delete_friend(friend.id)

    def share_wishlist(self, wishlist_id: UUID) -> dict:
        url = f"{BASE_URL_WISHLIST_SERVICE}/api/wishlists/get/{wishlist_id}"
        response = requests.get(url)
        if (response.status_code == 200):
            return url
        raise HTTPException(status_code=404, detail=f"Wishlist with ID {wishlist_id} not found")
