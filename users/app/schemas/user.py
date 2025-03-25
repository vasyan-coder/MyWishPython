from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.schemas.base_schema import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True)
    login = Column(String, nullable=False, unique=True)
    hash_password = Column(String, nullable=False)
