from enum import Enum
from typing import Annotated

from fastapi import Request, Query


class LanguageEnum(str, Enum):
    en = "en"
    fa = "fa"

DEFAULT_LANGUAGE = LanguageEnum.en


def get_prefered_language(
    request: Request,
    lang: Annotated[LanguageEnum|None, Query(description="select language between 'en:english', 'fa:farsi'")] = None
) -> LanguageEnum:
    # first priority: reading language from query
    if lang:
        return lang
    # second priority: reading from header
    accept_language = request.headers.get("accept-language")
    if accept_language:
        languages = accept_language.split(",")
        for lang_entry in languages:
            lang_code = lang_entry.split(";")[0].strip()
            lang_code = lang_code.split("-")[0].lower()
            try:
                return LanguageEnum(lang_code)
            except ValueError:
                continue
    # third priority: default language -> en
    return DEFAULT_LANGUAGE