from pydantic import BaseModel
from uuid import UUID


class GiftEditRequest(BaseModel):
    name: str
    link_to_product: str
