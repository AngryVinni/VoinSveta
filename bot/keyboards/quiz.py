"""Keyboards for /quiz flow."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def quiz_topics_keyboard(topics: dict[str, str]) -> InlineKeyboardMarkup:
	"""Build quiz topics keyboard from mapping."""
	rows = []
	for topic_id, topic_label in topics.items():
		rows.append([InlineKeyboardButton(text=topic_label, callback_data=f"quiz:topic:{topic_id}")])

	return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_post_answer_keyboard() -> InlineKeyboardMarkup:
	"""Buttons after answer check."""
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Следующий вопрос", callback_data="quiz:next"),
				InlineKeyboardButton(text="Сменить тему", callback_data="quiz:change_topic"),
			],
			[
				InlineKeyboardButton(text="В главное меню", callback_data="common:finish"),
			],
		],
	)
