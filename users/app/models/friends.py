from uuid import UUID
from pydantic import BaseModel, ConfigDict


class Friends(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user1_id: UUID  # ID пользователя, добавившего в друзья
    user2_id: UUID  # ID пользователя, которого добавили в друзья
