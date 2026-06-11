"""Handlers for /recommend flow."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.recommendations import (
    recommendations_actions_keyboard,
    recommendations_categories_keyboard,
    recommendations_genres_keyboard,
)
from bot.services.openai_client import OpenAIClient
from bot.services.prompt_factory import recommendations_prompt
from bot.services.recommendation_engine import list_categories, list_genres
from bot.states.chat_states import RecommendationStates
from config import load_settings

router = Router(name=__name__)


def _get_client() -> OpenAIClient | None:
    try:
        return OpenAIClient(load_settings())
    except RuntimeError:
        return None


async def _send_recommendations(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category_id = data.get("recommend_category_id")
    genre_id = data.get("recommend_genre_id")
    category_label = data.get("recommend_category_label", category_id)
    genre_label = data.get("recommend_genre_label", genre_id)
    disliked = data.get("recommend_disliked", [])

    if not category_id or not genre_id:
        await message.answer("Сначала выбери категорию и жанр.")
        return

    client = _get_client()
    if not client:
        await message.answer("OpenAI сейчас не настроен.")
        return

    text = await client.ask_safe(
        system_prompt="Ты даешь рекомендации.",
        user_prompt=recommendations_prompt(
            category=category_label,
            genre=genre_label,
            disliked_items=list(disliked),
        ),
        temperature=0.9,
    )
    await message.answer(text, reply_markup=recommendations_actions_keyboard())


@router.message(Command("recommend"))
async def recommend_start_handler(message: Message, state: FSMContext) -> None:
    """Start recommendations flow."""
    await state.set_state(RecommendationStates.choosing_category)
    await state.update_data(recommend_disliked=[])
    await message.answer(
        "Выбери категорию:",
        reply_markup=recommendations_categories_keyboard(list_categories()),
    )


@router.callback_query(F.data == "menu:recommend")
async def recommend_from_menu_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Open recommendations flow from menu."""
    await state.set_state(RecommendationStates.choosing_category)
    await state.update_data(recommend_disliked=[])
    if callback.message:
        categories_kb = recommendations_categories_keyboard(
            list_categories()
        )
        await callback.message.answer(
            "Выбери категорию:",
            reply_markup=categories_kb,
        )
    await callback.answer()


@router.callback_query(
    RecommendationStates.choosing_category,
    F.data.startswith("recommend:cat:"),
)
async def recommend_category_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Save category and ask for genre."""
    category_id = (callback.data or "").split(":")[-1]
    categories = list_categories()
    if category_id not in categories:
        await callback.answer("Неизвестная категория", show_alert=True)
        return

    await state.update_data(
        recommend_category_id=category_id,
        recommend_category_label=categories[category_id],
    )
    await state.set_state(RecommendationStates.choosing_genre)

    genres = list_genres(category_id)
    if callback.message:
        await callback.message.answer(
            "Выбери жанр:",
            reply_markup=recommendations_genres_keyboard(genres, category_id),
        )
    await callback.answer()


@router.callback_query(
    RecommendationStates.choosing_genre,
    F.data == "recommend:back_to_categories",
)
async def recommend_back_categories_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Back to category selection."""
    await state.set_state(RecommendationStates.choosing_category)
    if callback.message:
        categories_kb = recommendations_categories_keyboard(
            list_categories()
        )
        await callback.message.answer(
            "Выбери категорию:",
            reply_markup=categories_kb,
        )
    await callback.answer()


@router.callback_query(
    RecommendationStates.choosing_genre,
    F.data.startswith("recommend:genre:"),
)
async def recommend_genre_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Save genre and show recommendations."""
    parts = (callback.data or "").split(":")
    if len(parts) != 4:
        await callback.answer("Ошибка формата жанра", show_alert=True)
        return
    _, _, category_id, genre_id = parts

    genres = list_genres(category_id)
    if genre_id not in genres:
        await callback.answer("Неизвестный жанр", show_alert=True)
        return

    await state.update_data(
        recommend_genre_id=genre_id,
        recommend_genre_label=genres[genre_id],
        recommend_disliked=[],
    )
    await state.set_state(RecommendationStates.viewing)

    if callback.message:
        await _send_recommendations(callback.message, state)
    await callback.answer()


@router.callback_query(
    RecommendationStates.viewing,
    F.data == "recommend:dislike",
)
async def recommend_dislike_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Regenerate recommendations and remember previous answer as disliked."""
    if callback.message and callback.message.text:
        data = await state.get_data()
        disliked = list(data.get("recommend_disliked", []))
        disliked.append(callback.message.text[:120])
        await state.update_data(recommend_disliked=disliked[-5:])

    if callback.message:
        await _send_recommendations(callback.message, state)
    await callback.answer()
