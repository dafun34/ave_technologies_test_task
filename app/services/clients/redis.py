from redis.asyncio import Redis

from app.exceptions import ReddisClientError
from app.logger import Logger
from redis.exceptions import RedisError, ConnectionError, TimeoutError


class RedisClient:
    phone_address_key = "phone_address_mapping"

    def __init__(self, host: str, port: int, db: int, logger: Logger):
        self.client = Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,  # чтобы сразу строки, а не bytes
        )
        self.logger = logger

    async def get_address_by_phone(self, phone_number: str):
        """Получить адрес по номеру телефона."""
        try:
            return await self.client.get(f"{self.phone_address_key}:{phone_number}")
        except (ConnectionError, TimeoutError) as e:
            self.logger.error("Redis connection failure on GET", key=phone_number, error=repr(e))
            raise ReddisClientError("Redis connection failure", error_data={"error": repr(e)})

        except RedisError as e:
            self.logger.error("Redis error on GET", key=phone_number, error=repr(e))
            raise ReddisClientError("Redis error", error_data={"error": repr(e)})

    async def set_address_by_phone(self, phone_number: str, address: str):
        """Установить адрес по номеру телефона."""
        try:
            await self.client.set(f"{self.phone_address_key}:{phone_number}", address)
        except (ConnectionError, TimeoutError) as e:
            self.logger.error("Redis connection failure on SET", key=phone_number, error=repr(e))
            raise ReddisClientError("Redis connection failure", error_data={"error": repr(e)})

        except RedisError as e:
            self.logger.error("Redis error on SET", key=phone_number, error=repr(e))
            raise ReddisClientError("Redis error", error_data={"error": repr(e)})

    async def delete_address_by_phone(self, phone_number: str) -> bool:
        """Удалить адрес по номеру телефона. Возвращает True, если запись существовала."""
        try:
            deleted_count = await self.client.delete(f"{self.phone_address_key}:{phone_number}")
            return deleted_count > 0
        except (ConnectionError, TimeoutError) as e:
            self.logger.error("Redis connection failure on DELETE", key=phone_number, error=repr(e))
            raise ReddisClientError("Redis connection failure", error_data={"error": repr(e)})
        except RedisError as e:
            self.logger.error("Redis error on DELETE", key=phone_number, error=repr(e))
            raise ReddisClientError("Redis error", error_data={"error": repr(e)})

    async def close(self):
        """Закрывает соединение."""
        await self.client.aclose()
