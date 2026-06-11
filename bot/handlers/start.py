"""Handlers for /start and common finish action."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.random_fact import _send_random_fact
from bot.keyboards.common import main_menu_keyboard
from bot.keyboards.quiz import quiz_topics_keyboard
from bot.keyboards.recommendations import recommendations_categories_keyboard
from bot.keyboards.talk import talk_persona_keyboard
from bot.keyboards.translator import translator_languages_keyboard
from bot.services.quiz_engine import available_topics
from bot.services.recommendation_engine import list_categories
from bot.services.translation_engine import list_languages
from bot.states.chat_states import (
    GptStates,
    QuizStates,
    RecommendationStates,
    TalkStates,
    TranslatorStates,
)

router = Router(name=__name__)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """Reset state and show main menu."""
    await state.clear()
    await message.answer(
        "Привет! Я Воин Света - Telegram-бот. Выбери режим ниже.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "common:finish")
async def finish_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Finish current flow and return user to menu."""
    await state.clear()
    if callback.message:
        await callback.message.answer(
            "Mkay, закончили. Можешь выбрать другой режим.",
            reply_markup=main_menu_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("menu:"))
async def menu_hint_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Handle menu callbacks and open modes directly."""
    action = (callback.data or "").split(":", 1)[-1]
    if callback.message:
        if action == "random":
            await _send_random_fact(callback.message)
        elif action == "gpt":
            await state.set_state(GptStates.waiting_text)
            await callback.message.answer(
                "Режим GPT активен. Напиши текст вопроса."
            )
        elif action == "talk":
            await state.set_state(TalkStates.choosing_persona)
            await callback.message.answer(
                "Выбери персону для диалога:",
                reply_markup=talk_persona_keyboard(),
            )
        elif action == "quiz":
            await state.set_state(QuizStates.choosing_topic)
            await state.update_data(quiz_correct=0, quiz_total=0)
            await callback.message.answer(
                "Выбери тему викторины:",
                reply_markup=quiz_topics_keyboard(available_topics()),
            )
        elif action == "translator":
            await state.set_state(TranslatorStates.choosing_language)
            await callback.message.answer(
                "Выбери язык перевода:",
                reply_markup=translator_languages_keyboard(list_languages()),
            )
        elif action == "recommend":
            await state.set_state(RecommendationStates.choosing_category)
            await state.update_data(recommend_disliked=[])
            categories_kb = recommendations_categories_keyboard(
                list_categories()
            )
            await callback.message.answer(
                "Выбери категорию:",
                reply_markup=categories_kb,
            )
        else:
            await callback.message.answer("Рукожоп, Используй /start")
    await callback.answer()
