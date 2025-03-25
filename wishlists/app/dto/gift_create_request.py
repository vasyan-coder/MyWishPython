from pydantic import BaseModel
from uuid import UUID


class GiftCreateRequest(BaseModel):
    name: str
    link_to_product: str
    is_private: bool
