"""Global exception handling middleware."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.utils.formatters import safe_fallback_message

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
	"""Catch unhandled exceptions and send fallback message."""

	async def __call__(
		self,
		handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
		event: TelegramObject,
		data: Dict[str, Any],
	) -> Any:
		try:
			return await handler(event, data)
		except Exception as exc:  # noqa: BLE001
			logger.exception("Unhandled error in update: %s", exc)

			text = safe_fallback_message()
			if isinstance(event, Message):
				await event.answer(text)
			elif isinstance(event, CallbackQuery) and event.message:
				await event.message.answer(text)
				await event.answer()

			return None
