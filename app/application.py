import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.containers import Container
from app.api.router import app_router
from time import time

from app.data_classes.http import ErrorResult, ResponseFailure
from app.exceptions import BaseApiError


def create_app() -> FastAPI:
    """Создает экземпляр FastAPI приложения с зависимостями и маршрутизаторами."""
    container = Container()
    logger = container.logger()
    app = FastAPI(title="Phone Address API")
    app.container = container
    app.include_router(app_router)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time()
        response = await call_next(request)
        duration = time() - start

        logger.info(
            "HTTP Request",
            method=request.method,
            url=str(request.url),
            status=response.status_code,
            duration=f"{duration:.3f}s",
        )

        return response

    @app.exception_handler(BaseApiError)
    async def core_exception_handler(request: Request, exc: BaseApiError) -> JSONResponse:
        result = ErrorResult.from_exception(exception=exc)
        return JSONResponse(
            content=ResponseFailure(result=result).model_dump(mode="json"),
            status_code=exc.http_status_code,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    settings = app.container.config()
    logger = app.container.logger()
    logger.info(f"Service started on {settings.app_host}:{settings.app_port}")
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
