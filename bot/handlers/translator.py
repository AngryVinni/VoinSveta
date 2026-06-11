"""Handlers for /translator flow."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.translator import translator_languages_keyboard
from bot.services.openai_client import OpenAIClient
from bot.services.prompt_factory import translation_prompt
from bot.services.translation_engine import list_languages, resolve_language
from bot.states.chat_states import TranslatorStates
from bot.utils.validators import is_valid_user_text, normalize_user_text
from config import load_settings

router = Router(name=__name__)


def _get_client() -> OpenAIClient | None:
    try:
        return OpenAIClient(load_settings())
    except RuntimeError:
        return None


@router.message(Command("translator"))
async def translator_start_handler(
    message: Message, state: FSMContext
) -> None:
    """Start translator flow."""
    await state.set_state(TranslatorStates.choosing_language)
    await message.answer(
        "Выбери язык перевода:",
        reply_markup=translator_languages_keyboard(list_languages()),
    )


@router.callback_query(F.data == "menu:translator")
async def translator_from_menu_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Open translator flow from menu."""
    await state.set_state(TranslatorStates.choosing_language)
    if callback.message:
        await callback.message.answer(
            "Выбери язык перевода:",
            reply_markup=translator_languages_keyboard(list_languages()),
        )
    await callback.answer()


@router.callback_query(
    TranslatorStates.choosing_language,
    F.data.startswith("translator:lang:"),
)
async def translator_language_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Store target language and switch to text waiting."""
    language_id = (callback.data or "").split(":")[-1]
    language_name = resolve_language(language_id)
    await state.update_data(
        translator_language_id=language_id,
        translator_language_name=language_name,
    )
    await state.set_state(TranslatorStates.waiting_text)
    if callback.message:
        await callback.message.answer(
            f"Язык выбран: {language_name}. Теперь отправь текст для перевода."
        )
    await callback.answer()


@router.message(TranslatorStates.waiting_text)
async def translator_text_handler(message: Message, state: FSMContext) -> None:
    """Translate user text into selected language."""
    text = normalize_user_text(message.text)
    if not is_valid_user_text(text):
        await message.answer(
            "Пустой или слишком длинный текст. Попробуй снова."
        )
        return

    data = await state.get_data()
    target_language = data.get("translator_language_name", "English")

    client = _get_client()
    if not client:
        await message.answer("OpenAI сейчас не настроен.")
        return

    translated = await client.ask_safe(
        system_prompt="Ты переводчик.",
        user_prompt=translation_prompt(target_language, text),
        temperature=0.2,
    )
    await message.answer(translated)
