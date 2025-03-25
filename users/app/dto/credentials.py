from pydantic import BaseModel


class CredentialsRequest(BaseModel):
    login: str
    password: str
