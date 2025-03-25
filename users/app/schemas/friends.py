from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.schemas.base_schema import Base


class Friends(Base):
    __tablename__ = 'friends'

    id = Column(UUID(as_uuid=True), primary_key=True)
    user1_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user2_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
