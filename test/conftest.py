import pytest
import pytest_asyncio
from fakeredis import FakeAsyncRedis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api.router import app_router
from app.config import Settings
from app.containers import Container
from app.data_classes.http import ErrorResult, ResponseFailure
from app.exceptions import BaseApiError
from app.logger import Logger
from app.services.clients.redis import RedisClient


@pytest.fixture(scope="session")
def settings():
    """Создаёт настройки приложения из файла .env.test."""
    return Settings(_env_file="test/.env.test")


@pytest.fixture(scope="session")
def logger():
    return Logger()


@pytest.fixture(scope="session")
def test_container(settings, redis_client, logger):
    """Создаёт контейнер зависимостей для тестов."""
    container = Container()
    container.config.override(settings)
    container.redis_client.override(redis_client)
    container.logger.override(logger)

    yield container


@pytest_asyncio.fixture(scope="session")
async def redis_client(logger):
    # создаём инстанс твоего RedisClient, но подменяем клиент на фейковый
    client = RedisClient(host="localhost", port=6379, db=0, logger=logger)
    client.client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.close()


@pytest.fixture(scope="session")
def test_app(test_container):
    """Создаёт экземпляр FastAPI приложения с зависимостями."""
    app = FastAPI()
    app.container = test_container  # wiring для dependency-injector
    app.include_router(app_router)

    @app.exception_handler(BaseApiError)
    async def core_exception_handler(request: Request, exc: BaseApiError) -> JSONResponse:
        result = ErrorResult.from_exception(exception=exc)
        return JSONResponse(
            content=ResponseFailure(result=result).model_dump(mode="json"),
            status_code=exc.http_status_code,
        )

    yield app


@pytest.fixture
def client(test_app):
    """Создаёт тестовый клиент для FastAPI приложения."""
    with TestClient(test_app) as c:
        yield c


@pytest_asyncio.fixture(autouse=True)
async def clear_redis_between_tests(redis_client):
    """
    Очищает Redis до и после каждого теста.
    """
    # очистка перед тестом
    await redis_client.client.flushall()
    try:
        yield
    finally:
        # очистка после теста
        await redis_client.client.flushall()
