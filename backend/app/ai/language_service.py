from langdetect import LangDetectException, detect

from app.core.logging import get_logger

logger = get_logger(__name__)

_LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "pt": "Portuguese",
    "zh-cn": "Chinese",
    "ja": "Japanese",
    "ar": "Arabic",
    "ru": "Russian",
    "it": "Italian",
    "ko": "Korean",
}


def detect_language(text: str) -> str:
    """Detect the ISO 639-1 language code of a piece of text.

    Falls back to 'en' if detection fails (e.g. text too short or ambiguous),
    since defaulting to English is a safer failure mode than crashing.
    """
    try:
        return detect(text)
    except LangDetectException:
        logger.warning("Language detection failed for text, defaulting to English")
        return "en"


def get_language_name(language_code: str) -> str:
    """Return a human-readable language name for a given ISO code."""
    return _LANGUAGE_NAMES.get(language_code, "the same language as the question")


def build_language_instruction(text: str) -> str:
    """Build a system-prompt addition instructing the LLM to respond in the detected language."""
    language_code = detect_language(text)
    language_name = get_language_name(language_code)

    if language_code == "en":
        return ""

    return f"\n\nIMPORTANT: The employee's question is in {language_name}. Respond in {language_name}, not English."