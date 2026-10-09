import gettext
from pathlib import Path

from core.dependencies import LanguageEnum

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"


def get_translator(language: LanguageEnum):
    translation = gettext.translation(
        "messages",
        localedir=LOCALES_DIR,
        languages=[language.value],
        fallback=True,
    )
    return translation.gettext
