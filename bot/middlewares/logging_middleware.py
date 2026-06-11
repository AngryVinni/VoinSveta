"""Request logging middleware for updates and callbacks."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
	"""Simple update logger for messages/callbacks."""

	async def __call__(
		self,
		handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
		event: TelegramObject,
		data: Dict[str, Any],
	) -> Any:
		if isinstance(event, Message):
			logger.info(
				"message from user_id=%s text=%r",
				event.from_user.id if event.from_user else None,
				event.text,
			)
		elif isinstance(event, CallbackQuery):
			logger.info(
				"callback from user_id=%s data=%r",
				event.from_user.id if event.from_user else None,
				event.data,
			)

		return await handler(event, data)
