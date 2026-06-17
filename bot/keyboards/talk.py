"""Keyboards for /talk flow."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def talk_persona_keyboard() -> InlineKeyboardMarkup:
	"""Persona choices for /talk flow."""
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="🧠 Эйнштейн", callback_data="talk:persona:einstein"),
				InlineKeyboardButton(text="⚡ Тесла", callback_data="talk:persona:tesla"),
			],
			[
				InlineKeyboardButton(text="🎨 Фрида", callback_data="talk:persona:frida"),
				InlineKeyboardButton(text="Главное меню", callback_data="common:finish"),
			],
		],
	)
