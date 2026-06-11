"""Handlers for /quiz flow."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.quiz import quiz_post_answer_keyboard, quiz_topics_keyboard
from bot.services.openai_client import OpenAIClient
from bot.services.prompt_factory import quiz_check_prompt, quiz_question_prompt
from bot.services.quiz_engine import (
    available_topics,
    is_answer_correct,
    parse_question_response,
)
from bot.states.chat_states import QuizStates
from bot.utils.formatters import score_message
from bot.utils.validators import is_valid_user_text, normalize_user_text
from config import load_settings

router = Router(name=__name__)


def _get_client() -> OpenAIClient | None:
    try:
        return OpenAIClient(load_settings())
    except RuntimeError:
        return None


async def _generate_next_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    topic_id = data.get("quiz_topic_id")
    topic_label = data.get("quiz_topic_label", topic_id)
    if not topic_id:
        await message.answer("Сначала выбери тему викторины.")
        return

    client = _get_client()
    if not client:
        await message.answer("OpenAI сейчас не настроен.")
        return

    raw = await client.ask_safe(
        system_prompt="Ты генератор викторин.",
        user_prompt=quiz_question_prompt(topic_label),
        temperature=0.8,
    )
    question = parse_question_response(raw)
    await state.update_data(
        quiz_question=question.question,
        quiz_expected_answer=question.expected_answer,
    )
    await message.answer(
        f"Вопрос по теме '{topic_label}':\n{question.question}"
    )


@router.message(Command("quiz"))
async def quiz_start_handler(message: Message, state: FSMContext) -> None:
    """Start quiz topic selection."""
    await state.set_state(QuizStates.choosing_topic)
    await state.update_data(quiz_correct=0, quiz_total=0)
    await message.answer(
        "Выбери тему викторины:",
        reply_markup=quiz_topics_keyboard(available_topics()),
    )


@router.callback_query(F.data == "menu:quiz")
async def quiz_from_menu_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Open quiz flow from menu."""
    await state.set_state(QuizStates.choosing_topic)
    await state.update_data(quiz_correct=0, quiz_total=0)
    if callback.message:
        await callback.message.answer(
            "Выбери тему викторины:",
            reply_markup=quiz_topics_keyboard(available_topics()),
        )
    await callback.answer()


@router.callback_query(
    QuizStates.choosing_topic,
    F.data.startswith("quiz:topic:"),
)
async def quiz_topic_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Save selected topic and ask first question."""
    topic_id = (callback.data or "").split(":")[-1]
    topics = available_topics()
    if topic_id not in topics:
        await callback.answer("Неизвестная тема", show_alert=True)
        return

    await state.update_data(
        quiz_topic_id=topic_id,
        quiz_topic_label=topics[topic_id],
    )
    await state.set_state(QuizStates.answering)

    if callback.message:
        await _generate_next_question(callback.message, state)
    await callback.answer()


@router.message(QuizStates.answering)
async def quiz_answer_handler(message: Message, state: FSMContext) -> None:
    """Check user answer and update score."""
    user_answer = normalize_user_text(message.text)
    if not is_valid_user_text(user_answer):
        await message.answer(
            "Ответ пустой или слишком длинный. Попробуй еще раз."
        )
        return

    data = await state.get_data()
    question = data.get("quiz_question", "")
    expected = data.get("quiz_expected_answer", "")
    topic_label = data.get("quiz_topic_label", "общая")

    client = _get_client()
    if not client:
        await message.answer("OpenAI сейчас не настроен.")
        return

    check_raw = await client.ask_safe(
        system_prompt="Ты проверяешь ответы в викторине.",
        user_prompt=quiz_check_prompt(
            topic_label,
            question,
            expected,
            user_answer,
        ),
        temperature=0.0,
    )
    correct = is_answer_correct(check_raw)

    total = int(data.get("quiz_total", 0)) + 1
    correct_count = int(data.get("quiz_correct", 0)) + (1 if correct else 0)
    await state.update_data(quiz_total=total, quiz_correct=correct_count)

    if correct:
        text = "✅ Верно!"
    else:
        text = f"❌ Неверно. Правильный ответ: {expected}"

    await message.answer(
        f"{text}\n{score_message(correct_count, total)}",
        reply_markup=quiz_post_answer_keyboard(),
    )


@router.callback_query(QuizStates.answering, F.data == "quiz:next")
async def quiz_next_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Ask next question in same topic."""
    if callback.message:
        await _generate_next_question(callback.message, state)
    await callback.answer()


@router.callback_query(QuizStates.answering, F.data == "quiz:change_topic")
async def quiz_change_topic_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Back to topic selection."""
    await state.set_state(QuizStates.choosing_topic)
    if callback.message:
        await callback.message.answer(
            "Выбери новую тему:",
            reply_markup=quiz_topics_keyboard(available_topics()),
        )
    await callback.answer()
