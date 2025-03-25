from uuid import UUID
from pydantic import BaseModel, ConfigDict


class Gift(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    wishlist_id: UUID  # ID Wishlist, к которому относится
    name: str
    link_to_product: str  # Ссылка на продукт
    is_private: bool
    is_booked: bool # забронирован ли
    is_gifted: bool
