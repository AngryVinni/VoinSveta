"""Input validation helpers."""


def normalize_user_text(text: str | None) -> str:
	"""Normalize text from user input."""
	if text is None:
		return ""
	return " ".join(text.strip().split())


def is_valid_user_text(text: str | None, min_len: int = 1, max_len: int = 2000) -> bool:
	"""Validate user text boundaries."""
	clean = normalize_user_text(text)
	return min_len <= len(clean) <= max_len
