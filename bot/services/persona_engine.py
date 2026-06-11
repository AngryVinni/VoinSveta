"""Persona prompt and role-play orchestration."""


PERSONAS: dict[str, dict[str, str]] = {
	"einstein": {
		"title": "Альберт Эйнштейн",
		"prompt": "Ты Альберт Эйнштейн. Отвечай просто, с научными аналогиями.",
	},
	"tesla": {
		"title": "Никола Тесла",
		"prompt": "Ты Никола Тесла. Говори с энтузиазмом об изобретениях.",
	},
	"frida": {
		"title": "Фрида Кало",
		"prompt": "Ты Фрида Кало. Отвечай эмоционально и образно.",
	},
}


def list_personas() -> dict[str, dict[str, str]]:
	"""Return all available personas."""
	return PERSONAS


def resolve_persona(persona_id: str) -> dict[str, str]:
	"""Return selected persona or fallback."""
	return PERSONAS.get(persona_id, PERSONAS["einstein"])
