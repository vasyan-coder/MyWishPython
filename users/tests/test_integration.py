import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from hashlib import sha256
from fastapi import HTTPException
from app.services.user_service import UserService
from app.models.user import User
import os

BASE_URL_WISHLIST_SERVICE=os.getenv("BASE_URL_WISHLIST_SERVICE")


@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def user_service(mock_db_session):
    return UserService(mock_db_session)

def create_test_user(user_service: UserService, login="testuser", password="secret"):
    """
    Хелпер для создания фейкового пользователя через user_service.
    Реально user_repo.create_user будет замокан, чтобы не было доступа к настоящей БД.
    """
    hashed_password = sha256(password.encode()).hexdigest()
    user = User(
        id=uuid4(),
        login=login,
        hash_password=hashed_password
    )
    user_service.user_repo.create_user = MagicMock(return_value=user)
    return user_service.register_user(login, password)


@patch("requests.post")
def test_integration_register_and_authenticate_user_success(mock_post, user_service: UserService):
    """
    Интеграционный тест:
    1. Регистрируем пользователя через user_service.
    2. Аутентифицируем его, запрашивая токен у JWT-сервиса.
    Ожидаем успешное получение токена.
    """
    # Создаем пользователя через хелпер
    created_user = create_test_user(user_service, "authuser", "strongpass")
    
    # Теперь нужно замокать get_user_by_login, чтобы он вернул нашего созданного пользователя
    user_service.user_repo.get_user_by_login = MagicMock(return_value=created_user)

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "valid_token", "token_type": "bearer"}
    token_data = user_service.authenticate_user("authuser", "strongpass")
    assert token_data["access_token"] == "valid_token"


@patch("requests.post")
def test_integration_authenticate_user_jwt_error(mock_post, user_service: UserService):
    """
    Интеграционный тест:
    Регистрируем пользователя и пытаемся получить токен
    """
    create_test_user(user_service, "jwtfail", "secret")
    mock_post.return_value.status_code = 401
    mock_post.return_value.raise_for_status.side_effect = HTTPException(401, "Invalid token")
    with pytest.raises(HTTPException) as e_info:
        user_service.authenticate_user("jwtfail", "secret")
    assert e_info.value.status_code == 401


@patch("requests.get")
def test_integration_share_wishlist_success(mock_get, user_service: UserService):
    """
    Интеграционный тест:
    Тестируем метод share_wishlist микросервиса users, 
    который обращается к микросервису wishlists (mock requests.get).
    Возвращаем 200 OK от wishlist-сервиса и проверяем успешный ответ.
    """
    mock_get.return_value.status_code = 200
    wishlist_id = uuid4()
    share_link = user_service.share_wishlist(wishlist_id)
    assert f"{BASE_URL_WISHLIST_SERVICE}/api/wishlists/get/" in share_link


@patch("requests.get")
def test_integration_share_wishlist_not_found(mock_get, user_service: UserService):
    """
    Интеграционный тест:
    Тестируем share_wishlist, если wishlist-сервис вернет 404.
    Ожидаем HTTPException(404) от user_service.
    """
    mock_get.return_value.status_code = 404
    wishlist_id = uuid4()
    with pytest.raises(HTTPException) as e_info:
        user_service.share_wishlist(wishlist_id)
    assert e_info.value.status_code == 404


@patch("requests.get")
def test_integration_share_wishlist_unavailable(mock_get, user_service: UserService):
    """
    Интеграционный тест:
    Тестируем share_wishlist, если wishlist-сервис вернет 500 (недоступен).
    По коду user_service также ожидаем HTTPException(404).
    """
    mock_get.return_value.status_code = 500
    mock_get.return_value.raise_for_status.side_effect = HTTPException(500, "Wishlist service error")
    wishlist_id = uuid4()
    with pytest.raises(HTTPException) as e_info:
        user_service.share_wishlist(wishlist_id)
    # Несмотря на 500 от сервиса, в коде user_service это обрабатывается как 404
    assert e_info.value.status_code == 404
