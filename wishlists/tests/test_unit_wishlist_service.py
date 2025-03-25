import pytest
from uuid import uuid4
from fastapi import HTTPException
from app.services.wishlist_service import WishlistService
from app.repositories.local_wishlist_repo import wishlists
from app.repositories.local_gift_repo import gifts
from app.models.wishlist import Wishlist
from app.models.gift import Gift

@pytest.fixture
def wishlist_service():
    # Перед каждым тестом очищаем хранилище
    wishlists.clear()
    gifts.clear()
    service = WishlistService()
    return service

def test_create_wishlist_success(wishlist_service: WishlistService):
    """
    Тест успешного создания вишлиста.
    Проверяем, что вишлист создается с корректными данными и добавляется в хранилище.
    """
    user_id = uuid4()
    created = wishlist_service.create_wishlist(name="Test Wishlist", user_id=user_id, is_private=False)
    assert created.name == "Test Wishlist"
    assert created.user_id == user_id
    assert created.is_private is False
    assert len(wishlists) == 1  # Проверяем, что объект добавлен в хранилище

def test_set_wishlist_visibility_success(wishlist_service: WishlistService):
    """
    Тест изменения приватности вишлиста.
    Создаем вишлист, затем меняем его приватность и проверяем результат.
    """
    user_id = uuid4()
    created = wishlist_service.create_wishlist(name="Visible", user_id=user_id, is_private=False)
    updated = wishlist_service.set_wishlist_visibility(created.id, True)
    assert updated.is_private is True

def test_create_and_add_gift_to_wishlist_success(wishlist_service: WishlistService):
    """
    Тест успешного создания подарка и добавления его в существующий вишлист.
    Проверяем, что подарок добавлен в список подарков вишлиста.
    """
    user_id = uuid4()
    w = wishlist_service.create_wishlist(name="Gifts", user_id=user_id, is_private=False)
    gift = wishlist_service.create_and_add_gift_to_wishlist(w.id, "Laptop", "http://link", False)
    assert gift.name == "Laptop"
    assert gift.wishlist_id == w.id
    updated_wishlist = wishlist_service.get_wishlist(w.id)
    assert len(updated_wishlist.gifts) == 1
    assert updated_wishlist.gifts[0].name == "Laptop"

def test_create_and_add_gift_to_wishlist_offensive_word(wishlist_service: WishlistService):
    """
    Тест создания подарка с "ненормативной лексикой".
    Ожидаем выброс исключения.
    """
    user_id = uuid4()
    w = wishlist_service.create_wishlist(name="BadWordsCheck", user_id=user_id, is_private=False)
    with pytest.raises(Exception) as e_info:
        wishlist_service.create_and_add_gift_to_wishlist(w.id, "blya", "http://link", False)
    assert "ненормативная лексика" in str(e_info.value)

def test_delete_gift_wrong_owner(wishlist_service: WishlistService):
    """
    Тест удаления подарка с неверным владельцем вишлиста.
    Создаем вишлист и подарок, но передаем неверный wishlist_id при удалении.
    Ожидаем HTTPException(403).
    """
    user_id = uuid4()
    w = wishlist_service.create_wishlist(name="OwnerCheck", user_id=user_id, is_private=False)
    gift = wishlist_service.create_and_add_gift_to_wishlist(w.id, "Book", "http://link", False)
    wrong_wishlist_id = uuid4()  # Несоответствующий идентификатор
    with pytest.raises(HTTPException) as e_info:
        wishlist_service.delete_gift(wrong_wishlist_id, gift.id)
    assert e_info.value.status_code == 403
    assert "not the owner" in str(e_info.value.detail)
