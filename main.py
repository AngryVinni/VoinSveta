"""Entry point for Telegram/ChatGPT bot project."""

import asyncio
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError, TelegramUnauthorizedError

from bot.handlers import setup_routers
from bot.middlewares.error_middleware import ErrorMiddleware
from bot.middlewares.logging_middleware import LoggingMiddleware
from config import load_settings

LOG_FILE_NAME = "LogsFromWorkingTelegobot.txt"
LOG_MAX_SIZE_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 3


class TimestampedRotatingFileHandler(RotatingFileHandler):

    def __init__(
        self,
        filename: Path,
        max_bytes: int,
        backup_count: int,
        encoding: str = "utf-8",
    ) -> None:
        self._base_path = Path(filename)
        super().__init__(
            filename=self._base_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
        )

    def _archive_path(self) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        suffix = self._base_path.suffix
        candidate = self._base_path.with_name(
            f"{self._base_path.stem}_{timestamp}{suffix}"
        )

        attempt = 1
        while candidate.exists():
            candidate = self._base_path.with_name(
                f"{self._base_path.stem}_{timestamp}_{attempt}{suffix}"
            )
            attempt += 1

        return candidate

    def _cleanup_old_archives(self) -> None:
        if self.backupCount <= 0:
            return

        pattern = f"{self._base_path.stem}_*{self._base_path.suffix}"
        archives = sorted(
            self._base_path.parent.glob(pattern),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for obsolete in archives[self.backupCount:]:
            obsolete.unlink(missing_ok=True)

    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None

        active_log = Path(self.baseFilename)
        if active_log.exists():
            active_log.replace(self._archive_path())

        self._cleanup_old_archives()

        if not self.delay:
            self.stream = self._open()


def setup_logging() -> None:
    log_file_path = Path(__file__).resolve().parent / LOG_FILE_NAME
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = TimestampedRotatingFileHandler(
        filename=log_file_path,
        max_bytes=LOG_MAX_SIZE_BYTES,
        backup_count=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)


async def run_bot() -> None:
    """Initialize dependencies and start Telegram long polling."""
    setup_logging()
    try:
        settings = load_settings()
    except RuntimeError as error:
        logging.error("Configuration error: %s", error)
        return

    bot = Bot(token=settings.telegram_token)
    dispatcher = Dispatcher()
    dispatcher.update.middleware(LoggingMiddleware())
    dispatcher.update.middleware(ErrorMiddleware())
    setup_routers(dispatcher)

    logging.info("Bot polling started.")
    try:
        await dispatcher.start_polling(bot)
    except TelegramUnauthorizedError:
        logging.error(
            "Telegram authorization failed. Check TELEGRAM_TOKEN value."
        )
    except TelegramAPIError as error:
        logging.error("Telegram API error: %s", error)


def main() -> None:
    """Synchronous application entry point."""
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
