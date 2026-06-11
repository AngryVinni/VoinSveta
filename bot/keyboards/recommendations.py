"""Keyboards for recommendations flow."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def recommendations_categories_keyboard(categories: dict[str, str]) -> InlineKeyboardMarkup:
	"""Build categories keyboard."""
	rows = []
	for category_id, category_label in categories.items():
		rows.append([
			InlineKeyboardButton(
				text=category_label,
				callback_data=f"recommend:cat:{category_id}",
			),
		])
	return InlineKeyboardMarkup(inline_keyboard=rows)


def recommendations_genres_keyboard(genres: dict[str, str], category_id: str) -> InlineKeyboardMarkup:
	"""Build genres keyboard for selected category."""
	rows = []
	for genre_id, genre_label in genres.items():
		rows.append([
			InlineKeyboardButton(
				text=genre_label,
				callback_data=f"recommend:genre:{category_id}:{genre_id}",
			),
		])

	rows.append([InlineKeyboardButton(text="← Назад", callback_data="recommend:back_to_categories")])
	return InlineKeyboardMarkup(inline_keyboard=rows)


def recommendations_actions_keyboard() -> InlineKeyboardMarkup:
	"""Actions after recommendation response."""
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="👎 Не нравится", callback_data="recommend:dislike"),
				InlineKeyboardButton(text="✅ Закончить", callback_data="common:finish"),
			],
		],
	)
