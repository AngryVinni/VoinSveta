"""Retry helpers and decorators."""

from collections.abc import Callable
from typing import Any

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


def async_retryable(*exceptions: type[BaseException]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
	"""Create a retry decorator for async functions."""
	if not exceptions:
		exceptions = (Exception,)

	def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
		return retry(
			retry=retry_if_exception_type(exceptions),
			stop=stop_after_attempt(3),
			wait=wait_exponential(multiplier=1, min=1, max=6),
			reraise=True,
		)(func)

	return _decorator
