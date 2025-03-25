from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Header
from app.services.wishlist_service import WishlistService
from app.models.wishlist import Wishlist
from app.models.gift import Gift
from app.dto.wishlist_create_request import WishlistCreateRequest
from app.dto.gift_create_request import GiftCreateRequest
from app.dto.gift_edit_request import GiftEditRequest
from app.security.jwt_client import JWTClient

wishlist_router = APIRouter(prefix="/wishlists", tags=["Wishlists"])


@wishlist_router.post("/")
def create_wishlist(
    wishlist_create_request: WishlistCreateRequest,
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> Wishlist:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)

        return wishlist_service.create_wishlist(wishlist_create_request.name, user_id, wishlist_create_request.is_private)
    except KeyError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(403, str(e))


@wishlist_router.delete("/{id}")
def delete_wishlist(
    id: UUID,
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> None:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        wishlist_service.delete_wishlist(id)
        return {"detail": f"Wishlist with id={id} deleted successfully"}
    except KeyError:
        raise HTTPException(404, f"Wishlist with id={id} not found")
    except Exception as e:
        raise HTTPException(400, str(e))


@wishlist_router.patch("/{id}/visibility")
def set_wishlist_visibility(
    id: UUID,
    x_authorization: str = Header(..., description="Bearer token"),
    is_private: bool = Body(...),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> Wishlist:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        return wishlist_service.set_wishlist_visibility(id, is_private)
    except KeyError:
        raise HTTPException(404, f"Wishlist with id={id} not found")
    except Exception as e:
        raise HTTPException(403, e)


@wishlist_router.post("/{wishlist_id}/gifts")
def create_and_add_gift_to_wishlist(
    wishlist_id: UUID,
    gift_create_request: GiftCreateRequest,
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> Gift:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(wishlist_id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        return wishlist_service.create_and_add_gift_to_wishlist(wishlist_id, gift_create_request.name, gift_create_request.link_to_product, gift_create_request.is_private)
    except KeyError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(404, str(e))


@wishlist_router.delete("/gifts/{wishlist_id}/{gift_id}") 
def delete_gift(
    gift_id: UUID,
    wishlist_id: UUID,
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> None:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(wishlist_id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        wishlist_service.delete_gift(wishlist_id, gift_id)
        return {"detail": f"Gift with id={gift_id} deleted successfully"}
    except KeyError:
        raise HTTPException(404, f"Gift with id={gift_id} not found")
    except Exception as e:
        raise HTTPException(403, e)
    

@wishlist_router.get("/get/{wishlist_id}")
def get_wishlist(
    wishlist_id: UUID,
    wishlist_service: WishlistService = Depends(WishlistService)
):
    try:
        return wishlist_service.get_wishlist(wishlist_id)
    except KeyError:
        raise HTTPException(404, f"Wishlist with id={wishlist_id} not found")


@wishlist_router.patch("/gifts/{wishlist_id}/{gift_id}/privacy")
def set_gift_privacy(
    gift_id: UUID,
    wishlist_id: UUID,
    is_private: bool = Body(...),
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> Gift:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(wishlist_id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        return wishlist_service.set_gift_privacy(wishlist_id, gift_id, is_private)
    except KeyError:
        raise HTTPException(404, f"Gift with id={gift_id} not found")
    except Exception as e:
        raise HTTPException(403, e)


@wishlist_router.patch("/gifts/{wishlist_id}/{gift_id}/booking")
def toggle_gift_booking(
    gift_id: UUID,
    wishlist_id: UUID,
    is_booked: bool = Body(...),
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> Gift:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(wishlist_id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        return wishlist_service.toggle_gift_booking(wishlist_id, gift_id, is_booked)
    except KeyError:
        raise HTTPException(404, f"Gift with id={gift_id} not found")
    except Exception as e:
        raise HTTPException(403, e)


@wishlist_router.patch("/gifts/{wishlist_id}/{gift_id}/gifted")
def set_gift_gifted(
    gift_id: UUID,
    wishlist_id: UUID,
    is_gifted: bool = Body(...),
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> Gift:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(wishlist_id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        return wishlist_service.set_gift_gifted(wishlist_id, gift_id, is_gifted)
    except KeyError:
        raise HTTPException(404, f"Gift with id={gift_id} not found")
    except Exception as e:
        raise HTTPException(403, e)


@wishlist_router.put("/gifts/{wishlist_id}/{gift_id}")
def edit_gift(
    gift_id: UUID,
    wishlist_id: UUID,
    gift_edit_request: GiftEditRequest,
    x_authorization: str = Header(..., description="Bearer token"),
    wishlist_service: WishlistService = Depends(WishlistService)
) -> Gift:
    try:
        # Извлечение токена из заголовка x_authorization
        if not x_authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid token format")
        token = x_authorization.split(" ")[1]

        user_id = JWTClient.validate_token(token)
        wishlist = wishlist_service.get_wishlist(wishlist_id)
        if wishlist.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You do not own this wishlist.")
        return wishlist_service.edit_gift(wishlist_id, gift_id, gift_edit_request.name, gift_edit_request.link_to_product)
    except KeyError:
        raise HTTPException(404, f"Gift with id={gift_id} not found")
    except Exception as e:
        raise HTTPException(403, e)
