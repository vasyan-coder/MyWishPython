from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Конфигурация подключения
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://users_user:users_password@db_users:5432/users_db")

# Создание SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
