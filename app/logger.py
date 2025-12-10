import sys

from loguru import logger
from app.config import settings


class Logger:
    def __init__(self):
        logger.remove()  # Удаляем стандартный вывод loguru
        logger.add(
            sys.stdout,
            level=settings.logging_level,
            colorize=True,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{module}</cyan>:<cyan>{line}</cyan> | "
                "<magenta>{message}</magenta> | "
                "<yellow>{extra}</yellow>"
            ),
        )
        self._logger = logger

    def info(self, message, **extra):
        self._logger.bind(**extra).info(message)

    def debug(self, message, **extra):
        self._logger.bind(**extra).debug(message)

    def warning(self, message, **extra):
        self._logger.bind(**extra).warning(message)

    def error(self, message, **extra):
        self._logger.bind(**extra).error(message)

    def critical(self, message, **extra):
        self._logger.bind(**extra).critical(message)
