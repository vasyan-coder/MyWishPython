from uuid import UUID
from app.models.wishlist import Wishlist

# Локальное хранилище для wishlists
wishlists: list[Wishlist] = []

class WishlistRepo:
    def get_wishlists(self) -> list[Wishlist]:
        return wishlists

    def get_wishlist_by_id(self, id: UUID) -> Wishlist:
        for wishlist in wishlists:
            if wishlist.id == id:
                return wishlist
        raise KeyError(f"Wishlist with id={id} not found")

    def create_wishlist(self, wishlist: Wishlist) -> Wishlist:
        if any(w.id == wishlist.id for w in wishlists):
            raise KeyError(f"Wishlist with id={wishlist.id} already exists")
        wishlists.append(wishlist)
        return wishlist

    def update_wishlist(self, wishlist: Wishlist) -> Wishlist:
        for i, w in enumerate(wishlists):
            if w.id == wishlist.id:
                wishlists[i] = wishlist
                return wishlist
        raise KeyError(f"Wishlist with id={wishlist.id} not found")

    def delete_wishlist(self, id: UUID) -> None:
        global wishlists
        wishlists = [w for w in wishlists if w.id != id]
