from typing import Any

from pydantic import BaseModel, Field

from app.exceptions import BaseApiError


class ErrorResult(BaseModel):
    error_type: str = Field(description="Тип ошибки")
    error_message: str = Field(description="Описание ошибки")
    error_data: dict[str, Any] | None = Field(description="Данные ошибки")

    @classmethod
    def from_exception(cls, exception: BaseApiError) -> "ErrorResult":
        """
        Создаёт экземпляр ErrorResult на основе исключения BaseApiError.

        :param exception: Исключение типа BaseApiError.
        :return: Экземпляр ErrorResult, заполненный данными из исключения.
        """
        return ErrorResult(**exception.description)


class ResponseModel(BaseModel):
    success: bool = Field(description="Успех выполнения операции")
    result: Any = Field(title="Результат выполнения операции")


class ResponseSuccess(ResponseModel):
    success: bool = Field(default=True, description="Успех выполнения операции")
    result: Any = Field(default={}, title="Результат выполнения операции")


class ResponseFailure(ResponseModel):
    success: bool = Field(default=False, description="Успех выполнения операции")
    result: ErrorResult = Field(title="Результат выполнения операции")
