from pydantic import BaseModel
from uuid import UUID


class WishlistCreateRequest(BaseModel):
    name: str
    is_private: bool
