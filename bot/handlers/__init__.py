"""Handlers package and router wiring."""

from aiogram import Dispatcher

from bot.handlers.gpt_interface import router as gpt_router
from bot.handlers.quiz import router as quiz_router
from bot.handlers.random_fact import router as random_router
from bot.handlers.recommendations import router as recommendations_router
from bot.handlers.start import router as start_router
from bot.handlers.talk_persona import router as talk_router
from bot.handlers.translator import router as translator_router


def setup_routers(dispatcher: Dispatcher) -> None:
	"""Register all feature routers in a predictable order."""
	dispatcher.include_router(start_router)
	dispatcher.include_router(random_router)
	dispatcher.include_router(gpt_router)
	dispatcher.include_router(talk_router)
	dispatcher.include_router(quiz_router)
	dispatcher.include_router(translator_router)
	dispatcher.include_router(recommendations_router)
