from uuid import UUID
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    login: str
    hash_password: str  # Захэшированный пароль