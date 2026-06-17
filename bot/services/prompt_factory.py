"""Prompt factory for all bot scenarios."""


def random_fact_system_prompt() -> str:
	"""Prompt for random fact generation."""
	return (
		"Ты полезный ассистент. Дай один короткий интересный факт на русском языке. "
		"Факт должен быть 1-2 предложения, без воды."
	)


def gpt_chat_system_prompt() -> str:
	"""General prompt for free chat."""
	return "Ты дружелюбный AI-помощник. Отвечай понятно и коротко."


def quiz_question_prompt(
	topic: str,
	recent_questions: list[str] | None = None,
) -> str:
	"""Prompt for one quiz question, optionally excluding recent questions."""
	base = (
		f"Сгенерируй один новый вопрос викторины по теме '{topic}'. "
		"Формат строго: QUESTION: <вопрос>\\nANSWER: <краткий ответ>."
	)

	if not recent_questions:
		return base

	recent = "\n".join(f"- {question}" for question in recent_questions)
	return (
		f"{base}\n"
		"Не повторяй дословно вопросы из списка ниже:\n"
		f"{recent}"
	)


def quiz_check_prompt(
	topic: str,
	question: str,
	expected_answer: str,
	user_answer: str,
) -> str:
	"""Prompt for quiz answer validation."""
	return (
		f"Тема: {topic}. Вопрос: {question}. Эталонный ответ: {expected_answer}. "
		f"Ответ пользователя: {user_answer}. "
		"Оцени как верно или неверно. Верни строго: RESULT: correct или RESULT: wrong."
	)


def translation_prompt(target_language: str, text: str) -> str:
	"""Prompt for translation."""
	return (
		f"Переведи на язык '{target_language}' следующий текст. "
		"Верни только перевод, без пояснений: "
		f"{text}"
	)


def recommendations_prompt(category: str, genre: str, disliked_items: list[str]) -> str:
	"""Prompt for recommendations."""
	disliked = ", ".join(disliked_items) if disliked_items else "нет"
	return (
		f"Дай 3 рекомендации в категории '{category}' и жанре '{genre}'. "
		f"Избегай следующих вариантов: {disliked}. "
		"Ответ в 3 пунктах списком."
	)
