"""Response formatting helpers."""


def safe_fallback_message() -> str:
	"""Unified fallback response for temporary issues."""
	return "Упс, сейчас сервис временно недоступен. Попробуй еще раз через пару секунд."


def score_message(correct: int, total: int) -> str:
	"""Build user-facing score string."""
	if total <= 0:
		return "Пока нет результатов."
	return f"Твой счет: {correct}/{total}"
