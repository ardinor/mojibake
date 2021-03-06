# -*- coding: utf-8 -*-

from mojibake.settings import LANGUAGES


def available_languages(locale):
    if locale:
        available_languages = [(key, value) for key, value in LANGUAGES.items() if key not in locale]
        if available_languages[0][1] == '日本語':
            return ('ja', '日本語で')
        elif available_languages[0][1] == 'English':
            return ('en', 'In English')
        return available_languages[0][1]
    else:
        # If we couldn't get the session's language, assume we're in English
        return ('ja', '日本語で')
