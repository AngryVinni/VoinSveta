"""Common keyboard builders."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
	"""Main navigation menu."""
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="🎲 Random fact", callback_data="menu:random"),
				InlineKeyboardButton(text="💬 GPT", callback_data="menu:gpt"),
			],
			[
				InlineKeyboardButton(text="🎭 Talk", callback_data="menu:talk"),
				InlineKeyboardButton(text="🧠 Quiz", callback_data="menu:quiz"),
			],
			[
				InlineKeyboardButton(text="🌍 Translator", callback_data="menu:translator"),
				InlineKeyboardButton(text="🎁 Recommend", callback_data="menu:recommend"),
			],
		],
	)
