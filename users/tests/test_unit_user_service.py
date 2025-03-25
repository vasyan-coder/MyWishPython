import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from hashlib import sha256
from fastapi import HTTPException
from app.services.user_service import UserService
from app.models.user import User
from app.models.friends import Friends


@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def user_service(mock_db_session):
    return UserService(mock_db_session)


def test_register_user_success(user_service: UserService):
    """
    Тест успешной регистрации пользователя.
    Проверяем, что пользователь успешно создается и возвращается объект User.
    """
    mock_user_repo = user_service.user_repo
    mock_user_repo.create_user = MagicMock()
    login = "new_user"
    password = "password123"
    hashed_password = sha256(password.encode()).hexdigest()
    new_user = User(
        id=uuid4(),
        login=login,
        hash_password=hashed_password
    )
    mock_user_repo.create_user.return_value = new_user

    created_user = user_service.register_user(login, password)
    assert created_user.login == login
    assert created_user.hash_password == hashed_password
    mock_user_repo.create_user.assert_called_once()


def test_register_user_duplicate_login(user_service: UserService):
    """
    Тест регистрации пользователя с логином, который уже существует.
    Ожидаем KeyError.
    """
    mock_user_repo = user_service.user_repo
    mock_user_repo.create_user = MagicMock(side_effect=KeyError("User with login=existing_user already exists"))
    login = "existing_user"
    password = "123"

    with pytest.raises(KeyError) as e_info:
        user_service.register_user(login, password)
    assert "already exists" in str(e_info.value)


@patch("requests.post")
def test_authenticate_user_success(mock_post, user_service: UserService):
    """
    Тест аутентификации пользователя с корректными данными.
    Ожидаем, что вернется токен.
    """
    mock_user_repo = user_service.user_repo
    password = "secret"
    hashed_password = sha256(password.encode()).hexdigest()
    user_id = uuid4()
    user = User(
        id=user_id,
        login="test_user",
        hash_password=hashed_password
    )
    mock_user_repo.get_user_by_login = MagicMock(return_value=user)
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "valid_token", "token_type": "bearer"}

    token_data = user_service.authenticate_user("test_user", password)
    assert token_data["access_token"] == "valid_token"
    assert token_data["token_type"] == "bearer"


def test_authenticate_user_invalid_credentials(user_service: UserService):
    """
    Тест аутентификации с несуществующим пользователем
    Ожидаем HTTPException(404).
    """
    mock_user_repo = user_service.user_repo
    mock_user_repo.get_user_by_login = MagicMock(side_effect=KeyError("User with login=not_exists not found"))

    with pytest.raises(HTTPException) as e_info:
        user_service.authenticate_user("not_exists", "wrong_pass")
    assert e_info.value.status_code == 404
    assert "User with login=not_exists" in str(e_info.value.detail)


def test_add_friend_user_not_found(user_service: UserService):
    """
    Тест добавления друга с несуществующим пользователем.
    Ожидаем 404 ошибку.
    """
    mock_user_repo = user_service.user_repo
    mock_friends_repo = user_service.friends_repo
    user1_id = uuid4()
    user2_id = uuid4()
    mock_user_repo.get_user_by_id = MagicMock(return_value=None)  # Другой пользователь не найден

    with pytest.raises(HTTPException) as e_info:
        user_service.add_friend(user1_id, user2_id)
    assert e_info.value.status_code == 404
    assert "not found" in str(e_info.value.detail)
