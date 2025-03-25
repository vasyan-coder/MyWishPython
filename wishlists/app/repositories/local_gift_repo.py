from uuid import UUID
from app.models.gift import Gift

# Локальное хранилище для gifts
gifts: list[Gift] = []

class GiftRepo:
    def get_gifts(self) -> list[Gift]:
        return gifts

    def get_gift_by_id(self, id: UUID) -> Gift:
        for gift in gifts:
            if gift.id == id:
                return gift
        raise KeyError(f"Gift with id={id} not found")

    def create_gift(self, gift: Gift) -> Gift:
        if any(g.id == gift.id for g in gifts):
            raise KeyError(f"Gift with id={gift.id} already exists")
        gifts.append(gift)
        return gift

    def delete_gift(self, id: UUID) -> None:
        global gifts
        gifts = [g for g in gifts if g.id != id]

    def update_gift(self, gift: Gift) -> Gift:
        for i, existing_gift in enumerate(gifts):
            if existing_gift.id == gift.id:
                gifts[i] = gift
                return gift
        raise KeyError(f"Gift with id={gift.id} not found")
