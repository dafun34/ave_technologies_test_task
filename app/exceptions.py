from typing import Any


class BaseApiError(Exception):
    """Базовое исключение в работе приложения."""

    def __init__(
        self,
        *args,
        error_data: dict[str, Any] = None,
        http_status_code: int = 400,
        **kwargs,
    ):
        super().__init__(*args)
        self.error_data = error_data | kwargs if error_data else kwargs
        self.http_status_code = http_status_code  # код ответа в случае исключения

    @property
    def description(self) -> dict[str, Any]:
        """Описание исключения в форме json."""
        return {
            "error_type": self.__class__.__name__,
            "error_message": str(self),
            "error_data": self.error_data,
        }


class ReddisClientError(BaseApiError):
    """Ошибка при работе с Redis."""

    http_status_code = 500
