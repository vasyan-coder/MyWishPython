from uuid import UUID
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import User as DBUser


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self) -> list[User]:
        # Получение всех пользователей из БД
        db_users = self.db.query(DBUser).all()
        return [User.from_orm(db_user) for db_user in db_users]

    def get_user_by_id(self, id: UUID) -> User:
        # Получение пользователя по ID
        db_user = self.db.query(DBUser).filter(DBUser.id == id).first()
        if not db_user:
            raise KeyError(f"User with id={id} not found")
        return User.from_orm(db_user)

    def get_user_by_login(self, login: str) -> User:
        # Получение пользователя по логину
        db_user = self.db.query(DBUser).filter(DBUser.login == login).first()
        if not db_user:
            raise KeyError(f"User with login={login} not found")
        return User.from_orm(db_user)

    def create_user(self, user: User) -> User:
        # Создание нового пользователя
        existing_user = (
            self.db.query(DBUser)
            .filter((DBUser.id == user.id) | (DBUser.login == user.login))
            .first()
        )
        if existing_user:
            if existing_user.id == user.id:
                raise KeyError(f"User with id={user.id} already exists")
            if existing_user.login == user.login:
                raise KeyError(f"User with login={user.login} already exists")
        
        new_user = DBUser(**user.dict())
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return User.from_orm(new_user)
