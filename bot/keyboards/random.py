"""Keyboards for /random flow."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def random_action_keyboard() -> InlineKeyboardMarkup:
	"""Keyboard after random fact response."""
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Хочу еще факт", callback_data="random:more"),
				InlineKeyboardButton(text="Главное меню", callback_data="common:finish"),
			],
			
		],
	)
