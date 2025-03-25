from uuid import UUID
from app.models.user import User

# Локальное хранилище для пользователей
users: list[User] = []

class UserRepo:
    def get_users(self) -> list[User]:
        return users

    def get_user_by_id(self, id: UUID) -> User:
        for user in users:
            if user.id == id:
                return user
        raise KeyError(f"User with id={id} not found")

    def get_user_by_login(self, login: str) -> User:
        for user in users:
            if user.login == login:
                return user
        raise KeyError(f"User with login={login} not found")

    def create_user(self, user: User) -> User:
        if any(u.id == user.id for u in users):
            raise KeyError(f"User with id={user.id} already exists")
        if any(u.login == user.login for u in users):
            raise KeyError(f"User with login={user.login} already exists")
        users.append(user)
        return user
