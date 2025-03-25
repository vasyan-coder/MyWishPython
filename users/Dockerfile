# Базовый образ Python
FROM python:3.10

# Установка рабочей директории
WORKDIR /code

# Копирование зависимостей
COPY ./requirements.txt /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Копирование приложения
COPY ./app /code/app

# Копирование конфигурации alembic
COPY ./alembic.ini /code/alembic.ini

ENV PYTHONPATH=/code

# Открытие порта
EXPOSE 8000

# Команда для запуска приложения
CMD ["/bin/sh", "-c", \
    "alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8080"]