from uuid import UUID, uuid4
from typing import List
from fastapi import HTTPException
from app.models.wishlist import Wishlist
from app.models.gift import Gift
from app.repositories.local_wishlist_repo import WishlistRepo
from app.repositories.local_gift_repo import GiftRepo


class WishlistService:
    wishlist_repo: WishlistRepo
    gift_repo: GiftRepo

    def __init__(self) -> None:
        self.wishlist_repo = WishlistRepo()
        self.gift_repo = GiftRepo()

    def create_wishlist(self, name: str, user_id: UUID, is_private: bool) -> Wishlist:
        wishlist = Wishlist(
            id=uuid4(),
            name=name,
            user_id=user_id,
            gifts=[],
            is_private=is_private
        )
        return self.wishlist_repo.create_wishlist(wishlist)

    def delete_wishlist(self, wishlist_id: UUID) -> None:
        self.wishlist_repo.delete_wishlist(wishlist_id)

    def set_wishlist_visibility(self, wishlist_id: UUID, is_private: bool) -> Wishlist:
        wishlist = self.wishlist_repo.get_wishlist_by_id(wishlist_id)
        wishlist.is_private = is_private
        return self.wishlist_repo.update_wishlist(wishlist)

    def create_and_add_gift_to_wishlist(self, wishlist_id: UUID, name: str, link_to_product: str, is_private: bool) -> Gift:
        wishlist = self.wishlist_repo.get_wishlist_by_id(wishlist_id)
        gift = Gift(
            id=uuid4(),
            wishlist_id=wishlist_id,
            name=name,
            link_to_product=link_to_product,
            is_private=is_private,
            is_booked=False,
            is_gifted=False,
        )
        if (self._check_gift_data(gift)):
            raise Exception("Зафиксирована ненормативная лексика")

        self.gift_repo.create_gift(gift)
        wishlist.gifts.append(gift)
        self.wishlist_repo.update_wishlist(wishlist)
        return gift

    def delete_gift(self, wishlist_id: UUID, gift_id: UUID) -> None:
        gift = self.gift_repo.get_gift_by_id(gift_id)
        self.gift_repo.delete_gift(gift_id)
        wishlist = self.wishlist_repo.get_wishlist_by_id(gift.wishlist_id)
        wishlist.gifts = [g for g in wishlist.gifts if g.id != gift_id]
        
        if gift.wishlist_id != wishlist_id:
            raise HTTPException(403, "You are not the owner of this wishlist")

        self.wishlist_repo.update_wishlist(wishlist)

    def _check_gift_data(self, gift: Gift) -> bool:
        # проверкой занимается другой микросервис, который не является частью этой практической
        if (gift.name == "blya"):
            return True
        return False

    def get_wishlist(self, id: UUID) -> Wishlist:
        wishlist = self.wishlist_repo.get_wishlist_by_id(id)
        return wishlist

    def set_gift_privacy(self, wishlist_id: UUID, gift_id: UUID, is_private: bool) -> Gift:
        gift = self.gift_repo.get_gift_by_id(gift_id)
        gift.is_private = is_private

        if gift.wishlist_id != wishlist_id:
            raise HTTPException(403, "You are not the owner of this wishlist")

        return self.gift_repo.update_gift(gift)

    def toggle_gift_booking(self, wishlist_id: UUID, gift_id: UUID, is_booked: bool) -> Gift:
        gift = self.gift_repo.get_gift_by_id(gift_id)
        gift.is_booked = is_booked
        
        if gift.wishlist_id != wishlist_id:
            raise HTTPException(403, "You are not the owner of this wishlist")

        return self.gift_repo.update_gift(gift)

    def set_gift_gifted(self, wishlist_id: UUID, gift_id: UUID, is_gifted: bool) -> Gift:
        gift = self.gift_repo.get_gift_by_id(gift_id)
        gift.is_gifted = is_gifted

        if gift.wishlist_id != wishlist_id:
            raise HTTPException(403, "You are not the owner of this wishlist")
        
        return self.gift_repo.update_gift(gift)

    def edit_gift(self, wishlist_id: UUID, gift_id: UUID, name: str, link_to_product: str) -> Gift:
        gift = self.gift_repo.get_gift_by_id(gift_id)
        gift.name = name
        gift.link_to_product = link_to_product

        if gift.wishlist_id != wishlist_id:
            raise HTTPException(403, "You are not the owner of this wishlist")

        return self.gift_repo.update_gift(gift)
    
    def check_wishlist_owner(self, wishlist_id: UUID, user_id: UUID) -> bool:
        wishlist = self.wishlist_repo.get_wishlist_by_id(wishlist_id)
        if wishlist.user_id != user_id:
            raise HTTPException(403, "You are not the owner of this wishlist")
        return True

