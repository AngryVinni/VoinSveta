"""Keyboards for translator flow."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def translator_languages_keyboard(languages: dict[str, str]) -> InlineKeyboardMarkup:
	"""Build language selection keyboard."""
	rows = []
	for language_id, language_label in languages.items():
		rows.append([
			InlineKeyboardButton(
				text=language_label,
				callback_data=f"translator:lang:{language_id}",
			),
		])

	return InlineKeyboardMarkup(inline_keyboard=rows)
