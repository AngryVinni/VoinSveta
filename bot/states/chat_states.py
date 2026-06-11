"""FSM states for all bot interaction modes."""

from aiogram.fsm.state import State, StatesGroup


class GptStates(StatesGroup):
	"""States for free GPT chat mode."""

	waiting_text = State()


class TalkStates(StatesGroup):
	"""States for roleplay dialogue mode."""

	choosing_persona = State()
	talking = State()


class QuizStates(StatesGroup):
	"""States for quiz scenario."""

	choosing_topic = State()
	answering = State()


class TranslatorStates(StatesGroup):
	"""States for translator scenario."""

	choosing_language = State()
	waiting_text = State()


class RecommendationStates(StatesGroup):
	"""States for recommendation scenario."""

	choosing_category = State()
	choosing_genre = State()
	viewing = State()
