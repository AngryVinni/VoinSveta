"""Handlers for /gpt flow."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.services.openai_client import OpenAIClient
from bot.services.prompt_factory import gpt_chat_system_prompt
from bot.states.chat_states import GptStates
from bot.utils.validators import is_valid_user_text, normalize_user_text
from config import load_settings

router = Router(name=__name__)


def _get_client() -> OpenAIClient | None:
    try:
        return OpenAIClient(load_settings())
    except RuntimeError:
        return None


@router.message(Command("gpt"))
async def gpt_start_handler(message: Message, state: FSMContext) -> None:
    """Start free chat mode."""
    await state.set_state(GptStates.waiting_text)
    await message.answer("Режим GPT активен. Напиши текст вопроса.")


@router.callback_query(F.data == "menu:gpt")
async def gpt_from_menu_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Open gpt mode from menu."""
    await state.set_state(GptStates.waiting_text)
    if callback.message:
        await callback.message.answer(
            "Режим GPT активен. Напиши текст вопроса."
        )
    await callback.answer()


@router.message(GptStates.waiting_text)
async def gpt_message_handler(message: Message) -> None:
    """Answer user text with OpenAI."""
    raw = normalize_user_text(message.text)
    if not is_valid_user_text(raw):
        await message.answer(
            "Пустой или слишком длинный текст. Попробуй еще раз."
        )
        return

    client = _get_client()
    if not client:
        await message.answer("OpenAI сейчас не настроен.")
        return

    response = await client.ask_safe(
        system_prompt=gpt_chat_system_prompt(),
        user_prompt=raw,
        temperature=0.7,
    )
    await message.answer(response)
