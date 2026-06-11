"""Quiz generation and evaluation orchestration."""

from dataclasses import dataclass


TOPICS: dict[str, str] = {
	"history": "История",
	"science": "Наука",
	"movies": "Кино",
	"music": "Музыка",
}


@dataclass(slots=True)
class QuizQuestion:
	"""One quiz question item."""

	question: str
	expected_answer: str


def available_topics() -> dict[str, str]:
	"""Return quiz topics."""
	return TOPICS


def parse_question_response(raw_text: str) -> QuizQuestion:
	"""Parse model output to question + expected answer."""
	question = ""
	expected = ""

	for line in raw_text.splitlines():
		clean = line.strip()
		if clean.lower().startswith("question:"):
			question = clean.split(":", 1)[1].strip()
		elif clean.lower().startswith("answer:"):
			expected = clean.split(":", 1)[1].strip()

	if not question:
		question = raw_text.strip() or "Не удалось сгенерировать вопрос."
	if not expected:
		expected = "нет ответа"

	return QuizQuestion(question=question, expected_answer=expected)


def is_answer_correct(raw_check_response: str) -> bool:
	"""Parse check result text from model."""
	text = raw_check_response.lower()
	return "result: correct" in text or "correct" == text.strip()
