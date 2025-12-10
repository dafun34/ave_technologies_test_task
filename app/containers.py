from dependency_injector import containers, providers

from app.config import Settings

from app.services.clients.redis import RedisClient
from app.logger import Logger


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.api"])
    config = providers.Singleton(Settings)
    logger = providers.Singleton(Logger)
    redis_client = providers.Singleton(
        RedisClient,
        host=providers.Callable(lambda cfg: cfg.redis_host, config),
        port=providers.Callable(lambda cfg: cfg.redis_port, config),
        db=providers.Callable(lambda cfg: cfg.redis_db, config),
        logger=logger,
    )
