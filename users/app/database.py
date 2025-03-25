import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Конфигурация подключения к базе данных
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://users_user:users_password@db_users:5432/users_db"
)

# Создание ресурса для трассировок
resource = Resource(attributes={
    "service.name": "users-service",
    "db.system": "postgresql"
})

# Настройка провайдера трассировок
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Создание SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Инструментирование SQLAlchemy для трассировки запросов
SQLAlchemyInstrumentor().instrument(engine=engine)

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
