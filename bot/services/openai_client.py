"""OpenAI service wrapper with retry/timeout strategy."""

from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, OpenAIError, RateLimitError

from config import Settings
from bot.utils.retries import async_retryable


class OpenAIClient:
	"""Tiny wrapper around AsyncOpenAI chat completions API."""

	def __init__(self, settings: Settings) -> None:
		self._model = settings.openai_model
		self._client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=20.0)

	@async_retryable(APIConnectionError, APITimeoutError, RateLimitError)
	async def ask(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
		"""Ask model and return plain text response."""
		response = await self._client.chat.completions.create(
			model=self._model,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt},
			],
			temperature=temperature,
		)
		content = response.choices[0].message.content if response.choices else ""
		return (content or "").strip()

	async def ask_safe(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
		"""Ask model with fallback response on hard failures."""
		try:
			answer = await self.ask(system_prompt=system_prompt, user_prompt=user_prompt, temperature=temperature)
			if answer:
				return answer
			return "Не получилось получить ответ от модели. Попробуй еще раз."
		except OpenAIError:
			return "OpenAI сейчас недоступен. Попробуй позже."
		except Exception:
			return "Сервис временно недоступен. Попробуй еще раз через минуту."
