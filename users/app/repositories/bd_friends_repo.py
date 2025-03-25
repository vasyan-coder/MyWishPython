from uuid import UUID
from sqlalchemy.orm import Session
from app.models.friends import Friends  # Pydantic-модель для API
from app.schemas.friends import Friends as DBFriends  # SQLAlchemy-модель для БД


class FriendsRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_friends(self) -> list[Friends]: # TODO: add to service
        # Получение всех дружеских связей из БД
        db_friends = self.db.query(DBFriends).all()
        return [Friends.from_orm(db_friend) for db_friend in db_friends]

    def get_friend_by_users(self, user1_id: UUID, user2_id: UUID) -> Friends:
        # Поиск дружеской связи по двум пользователям
        db_friend = (
            self.db.query(DBFriends)
            .filter(
                (DBFriends.user1_id == user1_id and DBFriends.user2_id == user2_id)
                | (DBFriends.user1_id == user2_id and DBFriends.user2_id == user1_id)
            )
            .first()
        )
        if not db_friend:
            raise KeyError(f"Friendship between user1_id={user1_id} and user2_id={user2_id} not found")
        return Friends.from_orm(db_friend)

    def create_friend(self, friend: Friends) -> Friends:
        # Проверка на существование дружеской связи
        existing_friend = (
            self.db.query(DBFriends)
            .filter(
                (DBFriends.user1_id == friend.user1_id and DBFriends.user2_id == friend.user2_id)
                | (DBFriends.user1_id == friend.user2_id and DBFriends.user2_id == friend.user1_id)
            )
            .first()
        )
        if existing_friend:
            raise KeyError("Friendship already exists")

        new_friend = DBFriends(**friend.dict())
        self.db.add(new_friend)
        self.db.commit()
        self.db.refresh(new_friend)
        return Friends.from_orm(new_friend)

    def delete_friend(self, id: UUID) -> None:
        # Удаление дружеской связи по ID
        db_friend = self.db.query(DBFriends).filter(DBFriends.id == id).first()
        if not db_friend:
            raise KeyError(f"Friendship with id={id} not found")

        self.db.delete(db_friend)
        self.db.commit()
