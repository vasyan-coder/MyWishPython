from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List
from app.models.gift import Gift


class Wishlist(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    user_id: UUID  # ID пользователя из БД users
    gifts: List["Gift"]  # Список объектов Gift
    is_private: bool  # Приватный или нет
