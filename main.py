"""Entry point for Telegram/ChatGPT bot project."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError, TelegramUnauthorizedError

from bot.handlers import setup_routers
from bot.middlewares.error_middleware import ErrorMiddleware
from bot.middlewares.logging_middleware import LoggingMiddleware
from config import load_settings


def setup_logging() -> None:
    """Configure global logging format and level for the bot process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


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
