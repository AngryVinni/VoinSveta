"""Recommendations generation orchestration."""

CATEGORIES: dict[str, str] = {
	"movie": "Фильмы",
	"book": "Книги",
	"music": "Музыка",
}

GENRES_BY_CATEGORY: dict[str, dict[str, str]] = {
	"movie": {
		"sci-fi": "Фантастика",
		"comedy": "Комедия",
		"drama": "Драма",
	},
	"book": {
		"detective": "Детектив",
		"fantasy": "Фэнтези",
		"classic": "Классика",
	},
	"music": {
		"rock": "Рок",
		"pop": "Поп",
		"jazz": "Джаз",
	},
}


def list_categories() -> dict[str, str]:
	"""Return recommendation categories."""
	return CATEGORIES


def list_genres(category_id: str) -> dict[str, str]:
	"""Return genres for selected category."""
	return GENRES_BY_CATEGORY.get(category_id, {})
