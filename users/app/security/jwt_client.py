import requests
from uuid import UUID
import os

class JWTClient:
    BASE_URL = os.environ.get("JWT_SERVICE_BASE_URL", "http://jwt_service:8000")

    @staticmethod
    def validate_token(token: str) -> UUID:
        response = requests.post(f"{JWTClient.BASE_URL}/validate", json={"token": token})
        if response.status_code == 200:
            return UUID(response.json()["user_id"])
        response.raise_for_status()
