from enum import Enum

from fastapi import Request


class LanguageEnum(str, Enum):
    en = "en"
    fa = "fa"


DEFAULT_LANGUAGE = LanguageEnum.en


def get_prefered_language(request: Request) -> LanguageEnum:
    # first priority: reading language from query
    lang = request.query_params.get("lang")
    if lang:
        try:
            return LanguageEnum(lang)
        except ValueError:
            pass

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


async def add_language_to_request(request: Request, call_next):
    request.state.language = get_prefered_language(request)
    response = await call_next(request)
    return response
