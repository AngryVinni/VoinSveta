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
	rows.append([
		InlineKeyboardButton(
			text="В главное меню",
			callback_data="common:finish",
		),
	])

	return InlineKeyboardMarkup(inline_keyboard=rows)


def translator_post_translation_keyboard() -> InlineKeyboardMarkup:
	"""Actions after translation response."""
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(
					text="В главное меню",
					callback_data="common:finish",
				),
			],
		],
	)
