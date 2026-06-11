"""Handlers for /talk persona flow."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.talk import talk_persona_keyboard
from bot.services.openai_client import OpenAIClient
from bot.services.persona_engine import resolve_persona
from bot.states.chat_states import TalkStates
from bot.utils.validators import is_valid_user_text, normalize_user_text
from config import load_settings

router = Router(name=__name__)


def _get_client() -> OpenAIClient | None:
    try:
        return OpenAIClient(load_settings())
    except RuntimeError:
        return None


@router.message(Command("talk"))
async def talk_start_handler(message: Message, state: FSMContext) -> None:
    """Start persona selection."""
    await state.set_state(TalkStates.choosing_persona)
    await message.answer(
        "Выбери персону для диалога:",
        reply_markup=talk_persona_keyboard(),
    )


@router.callback_query(F.data == "menu:talk")
async def talk_from_menu_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Open talk mode from menu."""
    await state.set_state(TalkStates.choosing_persona)
    if callback.message:
        await callback.message.answer(
            "Выбери персону для диалога:",
            reply_markup=talk_persona_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    TalkStates.choosing_persona,
    F.data.startswith("talk:persona:"),
)
async def talk_choose_persona_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Save selected persona and switch to talking state."""
    persona_id = (callback.data or "").split(":")[-1]
    persona = resolve_persona(persona_id)
    await state.update_data(
        persona_id=persona_id,
        persona_prompt=persona.system_prompt,
    )
    await state.set_state(TalkStates.talking)
    if callback.message:
        await callback.message.answer(
            f"Персона выбрана: {persona.display_name}. Напиши сообщение.")
    await callback.answer()


@router.message(TalkStates.talking)
async def talk_message_handler(message: Message, state: FSMContext) -> None:
    """Talk in selected persona mode."""
    user_text = normalize_user_text(message.text)
    if not is_valid_user_text(user_text):
        await message.answer(
            "Пустой или слишком длинный текст. Попробуй еще раз."
        )
        return

    data = await state.get_data()
    system_prompt = data.get("persona_prompt", "Ты дружелюбный ассистент.")

    client = _get_client()
    if not client:
        await message.answer("OpenAI сейчас не настроен.")
        return

    response = await client.ask_safe(
        system_prompt=system_prompt,
        user_prompt=user_text,
        temperature=0.8,
    )
    await message.answer(response)
