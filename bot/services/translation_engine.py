"""Translation orchestration service."""

LANGUAGES: dict[str, str] = {
	"en": "English",
	"ru": "Русский",
	"es": "Español",
	"de": "Deutsch",
}


def list_languages() -> dict[str, str]:
	"""Return available target languages."""
	return LANGUAGES


def resolve_language(language_id: str) -> str:
	"""Resolve language id to human-readable name."""
	return LANGUAGES.get(language_id, "English")
