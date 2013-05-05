from config import LANGUAGES


def available_languages(locale):
    available_languages = [value for key, value in LANGUAGES.items() if key not in locale]
    return available_languages
