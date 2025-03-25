from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.orm import sessionmaker
from app.schemas.base_schema import Base
from app.schemas.friends import Friends
from app.schemas.user import User
from alembic import context
import os

# Этот объект конфигурации Alembic дает доступ
# к значениям, содержащимся в .ini файле.
config = context.config

# Прочитаем URL для подключения к БД из переменных окружения
db_url = os.environ.get("DATABASE_URL", "postgresql://users_user:users_password@db_users:5432/users_db")
config.set_main_option("sqlalchemy.url", db_url)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для autogenerate
target_metadata = Base.metadata  # Указываем метаданные Base

# Функция для запуска миграций в offline режиме
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Функция для запуска миграций в online режиме
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Создание таблиц, если они еще не существуют
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        
        # Создаем таблицы в базе данных (если они еще не созданы)
        Base.metadata.create_all(connection)

        with context.begin_transaction():
            context.run_migrations()

# Выбор режима работы
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
