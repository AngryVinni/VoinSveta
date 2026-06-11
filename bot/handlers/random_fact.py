"""Handler for /random command and repeat action."""

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.keyboards.random import random_action_keyboard
from bot.services.openai_client import OpenAIClient
from bot.services.prompt_factory import random_fact_system_prompt
from config import load_settings

router = Router(name=__name__)


def _random_image() -> FSInputFile | None:
    image_path = Path("assets/images/random.jpg")
    if image_path.exists():
        return FSInputFile(image_path)
    return None


def _build_openai_client() -> OpenAIClient | None:
    try:
        settings = load_settings()
    except RuntimeError:
        return None
    return OpenAIClient(settings)


async def _send_random_fact(message: Message) -> None:
    image = _random_image()
    if image:
        await message.answer_photo(photo=image, caption="Случайный факт")

    client = _build_openai_client()
    if not client:
        await message.answer("OpenAI сейчас не настроен.")
        return

    fact = await client.ask_safe(
        system_prompt=random_fact_system_prompt(),
        user_prompt="Дай интересный факт",
        temperature=0.9,
    )
    await message.answer(fact, reply_markup=random_action_keyboard())


@router.message(Command("random"))
async def random_handler(message: Message) -> None:
    """Start /random flow."""
    await _send_random_fact(message)


@router.callback_query(F.data == "random:more")
async def random_more_handler(callback: CallbackQuery) -> None:
    """Repeat random fact generation."""
    if callback.message:
        await _send_random_fact(callback.message)
    await callback.answer()